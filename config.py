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
        },
        "analyzed_pairs": [],
        "filter_settings": {
            "VolumePairList": {"number_assets": 0, "sort_key": "quoteVolume"},
            "AgeFilter": {"min_days_listed": 0},
            "PrecisionFilter": {},
            "PriceFilter": {"low_price_ratio": 0},
            "SpreadFilter": {"max_spread_ratio": 0},
            "RangeStabilityFilter": {"lookback_days": 0, "min_rate_of_change": 0, "refresh_period": 0},
            "VolatilityFilter": {"lookback_days": 0, "min_volatility": 0, "max_volatility": 0, "refresh_period": 0},
            "ShuffleFilter": {"seed": 0}
        }
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
        for key, value in default_config.items():
            if key not in config_data:
                config_data[key] = value
            elif isinstance(value, dict):
                if isinstance(config_data[key], dict):
                    for sub_key, sub_value in value.items():
                        if sub_key not in config_data[key]:
                            config_data[key][sub_key] = sub_value
                else:
                    if isinstance(config_data[key], list):
                        for item in config_data[key]:
                            if isinstance(item, dict):
                                for sub_key, sub_value in value.items():
                                    if sub_key not in item:
                                        item[sub_key] = sub_value
        return config_data
    else:
        return default_config

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_strategies():
    strategies = [f.split('.')[0] for f in os.listdir(STRATEGY_FOLDER) if f.endswith('.py') and f != '__init__.py']
    return strategies
