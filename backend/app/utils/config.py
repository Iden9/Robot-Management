import os
import yaml

def get_yaml_config():
    """
    Load YAML config from config.yaml in the backend directory.
    Returns a dict. If file or fields missing, returns empty dict or partial dict.
    """
    config_path = 'config.yaml'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}

def get_by_path(d, path, default=None):
    """
    Access nested dict values using dot-separated path, e.g. get_by_path(cfg, 'mysql.user', 'root')
    """
    keys = path.split('.')
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return default
    return d

def get_config_value(path, default=None):
    """
    Load YAML config and get value by dot-path, with default fallback.
    """
    cfg = get_yaml_config()
    return get_by_path(cfg, path, default)
