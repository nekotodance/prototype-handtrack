import json
import datetime

# debug code enable
_IS_DEBUG = 1

#for debug
def dbgprint(message):
    if _IS_DEBUG:
        # date time string
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        # print message
        print(f"[{timestamp}] {message}")

def read_value_from_config(config_file, key):
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return config_data.get(key, None)

    except FileNotFoundError:
        print(f"error: File not found: {config_file}")
        return None
    except json.JSONDecodeError:
        print(f"error: Configuration file is not in correct json format: {config_file}")
        return None

def write_value_to_config(config_file, key, value):
    try:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config_data = {}
        config_data[key] = value
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True

    except Exception as e:
        print(f"error: A problem occurred while writing to the file: {e}")
        return False
