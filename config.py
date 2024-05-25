import json
import os

CONFIG_FILE = 'config.json'
STRATEGY_FOLDER = 'strategias'

def load_config():
    default_config = {
        "api_key": "",
        "api_secret": "",
        "telegram_api_key": "",
        "telegram_chat_id": "",
        "selected_strategy": "",
        "strategies": get_strategies(),
        "parameters": {
            "interval": "",
            "start_date": "",
            "end_date": ""
        },
        "filters": {
            "min_duration_days": 60,
            "min_volatility": 0,
            "min_volume": 0
        }
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
        # Asegúrate de que todos los campos estén presentes en la configuración cargada
        for key, value in default_config.items():
            if key not in config_data:
                config_data[key] = value
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in config_data[key]:
                        config_data[key][sub_key] = sub_value
        return config_data
    else:
        return default_config

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_strategies():
    strategies = [f.split('.')[0] for f in os.listdir(STRATEGY_FOLDER) if f.endswith('.py') and f != '__init__.py']
    return strategies
