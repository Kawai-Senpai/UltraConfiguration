
import asyncio
from ultraconfig import UltraConfig

async def main():
    config = UltraConfig()
    
    # Async loading
    await config.load_config_async('config.json')
    
    # Do other work while config saves in background
    future = config.save_config_background('output.json')
    print("Config is saving in background...")
    
    # Wait for save to complete if needed
    await asyncio.wrap_future(future)
    print("Save completed!")

if __name__ == "__main__":
    asyncio.run(main())