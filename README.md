# UltraConfiguration

A high-performance, thread-safe configuration management library for Python with async support.

![UltraConfiguration Thumbnail](https://github.com/Kawai-Senpai/UltraConfiguration/blob/8f6cc341d9de40b0e70ae71ce2f8df9d58178746/Assets/Ultraconfiguration%20Thumbnail.png)

## Table of Contents
1. Introduction
2. Installation
3. Usage
   - Basic Example
   - Async Example
4. Advantages
5. Limitations
6. Additional Notes
7. Why UltraConfiguration?
8. Handling Multiple Configuration Formats
9. Documentation

## Introduction
UltraConfiguration is designed to provide a fast, thread-safe configuration manager for Python applications of all sizes. It supports JSON/YAML, async operations, and advanced caching to handle loads efficiently.

## Installation
Use pip:
```
pip install ultraconfiguration
```

## Usage
### Basic Example
```python
# Simple usage example
config = UltraConfig("config.json")
print(config.get("database.host", "127.0.0.1"))
config.set("app.debug", True)
config.save_config("my_config.json")
```

### Async Example
```python
import asyncio
from ultraconfiguration import UltraConfig

async def main():
    config = UltraConfig()
    await config.load_config_async("async_config.json")
    print(config.get("server.port", 8000))
    await config.save_config_async("saved_async.json")

asyncio.run(main())
```

## Features

- Thread-safe singleton configuration manager
- Support for JSON and YAML formats
- Nested configuration access using dot notation
- LRU caching for fast repeated access
- Comprehensive error handling and logging
- Type hints for better IDE support
- Optional schema validation
- Pretty-printing support
- Async/Background operations support
- Memory-efficient caching
- Context manager support

## Advantages
- Thread-safe singleton access
- Async I/O for non-blocking operations
- Schema validation with jsonschema
- Comprehensive logging and error handling

## Limitations
- Inherits file system permission constraints
- Schema validation requires additional CPU overhead
- Global singleton pattern might not suit every use case

## Additional Notes
Refer to the examples in the "Examples" folder for more complex scenarios. Logging can be customized, and caching is easily cleared with `config.clear_cache()`.

## Why UltraConfiguration?
UltraConfiguration goes beyond traditional config management libraries by:
- Offering a thread-safe, singleton architecture to avoid concurrency issues.
- Providing seamless async operations for large-scale applications.
- Supporting schema validation to ensure data integrity without manual checks.
- Integrating environment variable overrides for flexible deployments.
- Simplifying nested structure handling through dot-notation key paths.

## Handling Multiple Configuration Formats
UltraConfiguration supports various file formats, including JSON and YAML:
```python
from ultraconfiguration import UltraConfig

# Load JSON config
json_config = UltraConfig("settings.json")

# Load YAML config
yaml_config = UltraConfig("settings.yaml")

# Both are accessed similarly:
value_from_json = json_config.get("some.key", "default")
value_from_yaml = yaml_config.get("another.key", 123)
```
You can also override values using environment variables or custom logic.  
This flexibility enables you to maintain consistent config handling across different projects.

## Documentation
Below is a quick reference to commonly used methods in UltraConfig:
- **UltraConfig(config_file: Optional[str|Path])**  
  Creates or retrieves the global instance; optionally auto-loads a config file.

- **get(key: str, default: Any = None) → Any**  
  Retrieves a nested config value with LRU caching.

- **set(key: str, value: Any, validate: bool = True) → None**  
  Assigns a new value, optionally validating against a JSON schema.

- **load_config(file_path: str|Path, schema_path: Optional[str] = None) → None**  
  Loads configuration from file, optionally applying an external schema.

- **save_config(file_path: str|Path, pretty: bool = True) → None**  
  Saves current configuration to specified file with optional pretty-print.

- **load_config_async(...)** / **save_config_async(...)**  
  Async versions of load and save operations, allowing non-blocking I/O.

- **load_config_background(...)** / **save_config_background(...)**  
  Launches load/save tasks in background threads.

- **clear_cache()**  
  Clears all cached values to ensure fresh lookups.

- **reset()**  
  Discards all config data, returning to a clean state.

- **has_changes()**  
  Checks if the in-memory config differs from what’s on disk.

## Advanced Usage
Use environment variables for dynamic overrides:
```python
import os
from ultraconfiguration import UltraConfig

os.environ['database.host'] = '10.0.0.2'

config = UltraConfig('config.json')
host = config.get('database.host', '127.0.0.1')
print(f"Host overridden by environment: {host}")
```

Schema validation example:
```python
# ...existing code...
schema_path = 'config_schema.json'
config.load_config('config.json', schema_path=schema_path)
# ...existing code...
```

## Frequently Asked Questions
1. **Does UltraConfig work in multi-process environments?**  
   UltraConfig is primarily designed for single-process usage. For multi-process setups, consider shared memory or database-backed solutions.
   
2. **How do I reset configurations at runtime?**  
   Simply call `config.reset()` to clear the internal dictionaries.

3. **Is there a performance impact with validation?**  
   Yes, validation can add overhead. Disable it when performance is critical and you trust the input.
