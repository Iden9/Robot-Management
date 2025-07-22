import os
import yaml

def get_yaml_config():
    """
    加载配置文件，本地开发优先加载dev.yaml，提交代码git排除了dev.yaml，如果没有则加载config.yaml
    """
    # 本地开发优先加载dev.yaml
    dev_config_path = 'dev.yaml'
    if os.path.exists(dev_config_path):
        with open(dev_config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    # 提交代码git排除了dev.yaml，如果没有则加载config.yaml
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
