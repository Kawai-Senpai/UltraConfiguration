from ultraconfiguration import UltraConfig

def main():
    # Create config instance
    config = UltraConfig()

    # Load from JSON
    config.load_config('config.json')

    # Access nested values
    db_host = config.get('database.host', 'localhost')
    print(f"Database host: {db_host}")

    # Set new values
    config.set('app.debug', True)
    config.set('database.port', 5432)

    # Save configuration
    config.save_config('new_config.json')

if __name__ == "__main__":
    main()
