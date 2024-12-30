from __future__ import annotations
import json
import yaml
from threading import Lock
from typing import Any, Dict, Optional, Union
from functools import lru_cache
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, Future
import weakref
from jsonschema import validate, ValidationError
import asyncio

logger = logging.getLogger(__name__)

class ConfigValidationError(Exception):
    """Raised when config validation fails"""
    pass

class UltraConfig:
    """Thread-safe, high-performance configuration manager"""
    _instance: Optional['UltraConfig'] = None  # Fixed type hint syntax
    _lock = Lock()
    _file_lock = Lock()
    _configs_cache = weakref.WeakValueDictionary()  # Memory optimization
    
    def __new__(cls, config_file: Optional[Union[str, Path]] = None) -> 'UltraConfig':
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize(config_file)
        elif config_file:
            # If instance exists but new config_file is provided, load it
            cls._instance.load_config(config_file)
        return cls._instance

    def _initialize(self, config_file: Optional[Union[str, Path]] = None) -> None:
        """Initialize instance attributes"""
        self._configs: Dict[str, Any] = {}
        self._config_schema: Dict[str, Any] = {}
        self._modified = False
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ultraconfig")
        self._setup_logging()
        
        if config_file:
            self.load_config(config_file)

    def _setup_logging(self) -> None:
        """Configure logging for the config manager"""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    @lru_cache(maxsize=128)
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value with caching"""
        try:
            keys = key.split('.')
            value = self._configs
            for k in keys:
                if not isinstance(value, dict):
                    return default
                value = value.get(k)
                if value is None:
                    return default
            return value
        except (KeyError, TypeError, AttributeError) as e:
            logger.debug(f"Error accessing key '{key}': {str(e)}")
            return default

    def _validate_value(self, key: str, value: Any) -> None:
        """Validate a single value against schema"""
        if not self._config_schema:
            return

        schema_path = key.split('.')
        current_schema = self._config_schema
        
        try:
            for path in schema_path:
                if 'properties' in current_schema:
                    current_schema = current_schema['properties'].get(path, {})
                else:
                    return

            if current_schema:
                validate(instance=value, schema=current_schema)
        except ValidationError as e:
            raise ConfigValidationError(f"Validation error for '{key}': {str(e)}")

    def _load_schema(self, schema_path: Union[str, Path]) -> None:
        """Load JSON schema for configuration validation"""
        try:
            schema_path = Path(schema_path)
            with open(schema_path, 'r') as f:
                self._config_schema = json.load(f)
        except Exception as e:
            logger.error(f"Error loading schema: {str(e)}")
            raise

    def set(self, key: str, value: Any, validate: bool = True) -> None:
        """Set a config value with validation"""
        with self._lock:
            try:
                if validate:
                    self._validate_value(key, value)
                
                keys = key.split('.')
                target = self._configs
                
                # Create nested structure
                for k in keys[:-1]:
                    if k not in target or not isinstance(target[k], dict):
                        target[k] = {}
                    target = target[k]
                
                # Set the value
                target[keys[-1]] = value
                self._modified = True
                self.get.cache_clear()
            
            except Exception as e:
                logger.error(f"Error setting key '{key}': {str(e)}")
                raise

    def load_config(self, file_path: Union[str, Path], schema_path: Optional[str] = None) -> None:
        """Load configuration from file with optional schema validation"""
        try:
            file_path = Path(file_path)
            if schema_path:
                self._load_schema(schema_path)

            with self._file_lock:
                content = self._read_file(file_path)
                if self._config_schema:
                    self._validate_config(content)
                self._configs.update(content)
                self.get.cache_clear()

        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise

    async def load_config_async(self, file_path: Union[str, Path], schema_path: Optional[str] = None) -> None:
        """Asynchronously load configuration from file"""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor,
            lambda: self.load_config(file_path, schema_path)
        )

    async def save_config_async(self, file_path: Union[str, Path], pretty: bool = True) -> None:
        """Asynchronously save configuration to file"""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor,
            lambda: self.save_config(file_path, pretty)
        )

    def load_config_background(self, file_path: Union[str, Path], schema_path: Optional[str] = None) -> Future:
        """Load configuration in background thread"""
        return self._executor.submit(self.load_config, file_path, schema_path)

    def save_config_background(self, file_path: Union[str, Path], pretty: bool = True) -> Future:
        """Save configuration in background thread"""
        return self._executor.submit(self.save_config, file_path, pretty)

    def _read_file(self, file_path: Path) -> Dict[str, Any]:
        """Read and parse configuration file"""
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")

        with open(file_path, 'r') as f:
            content = f.read()
            
        if file_path.suffix.lower() == '.json':
            return json.loads(content)
        elif file_path.suffix.lower() in ('.yaml', '.yml'):
            return yaml.safe_load(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def save_config(self, file_path: Union[str, Path], pretty: bool = True) -> None:
        """Save configuration to file with pretty printing option"""
        try:
            file_path = Path(file_path)
            with self._file_lock:
                with open(file_path, 'w') as f:
                    if file_path.suffix.lower() == '.json':
                        json.dump(self._configs, f, 
                                indent=4 if pretty else None,
                                sort_keys=True)
                    elif file_path.suffix.lower() in ('.yaml', '.yml'):
                        yaml.safe_dump(self._configs, f, 
                                     default_flow_style=not pretty)
                self._modified = False
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            raise

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate entire configuration against schema"""
        if not self._config_schema:
            return
            
        try:
            validate(instance=config, schema=self._config_schema)
        except ValidationError as e:
            raise ConfigValidationError(f"Configuration validation failed: {str(e)}")

    def clear_cache(self) -> None:
        """Clear all cached values"""
        self.get.cache_clear()
        self._configs_cache.clear()

    def __enter__(self) -> 'UltraConfig':
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup on context exit"""
        self.clear_cache()
        self._executor.shutdown(wait=False)

    def __del__(self) -> None:
        """Cleanup resources"""
        try:
            self._executor.shutdown(wait=False)
        except Exception:
            pass

    # Additional utility methods
    def reset(self) -> None:
        """Reset configuration to empty state"""
        with self._lock:
            self._configs.clear()
            self.get.cache_clear()

    def has_changes(self) -> bool:
        """Check if configuration has unsaved changes"""
        return self._modified
