# simcereb/core/config/config_manager.py  
"""  
Configuration manager for loading and managing configuration files  
"""  
  
import os  
import yaml  
  
class ConfigManager:  
    """  
    Manages loading and accessing configuration data  
    """  
      
    def __init__(self, config_file=None, version=None):  
        """  
        Initialize the configuration manager  
          
        Args:  
            config_file (str): Path to configuration file, or None for default  
            version (str): Version to load configuration for (learning, research, teaching)  
        """  
        self.config = {}  
        self.version = version  
          
        # Load default configuration  
        default_config_path = os.path.join(  
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),  
            "configs",  
            "default_config.yaml"  
        )  
        self.load_config(default_config_path)  
          
        # Load version-specific configuration if version is provided  
        if version:  
            version_config_path = os.path.join(  
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),  
                "configs",  
                version,  
                "default_config.yaml"  
            )  
            if os.path.exists(version_config_path):  
                self.load_config(version_config_path)  
          
        # Load user configuration if provided  
        if config_file is not None:  
            self.load_config(config_file)  
      
    def load_config(self, config_file):  
        """  
        Load configuration from a file  
          
        Args:  
            config_file (str): Path to configuration file  
        """  
        try:  
            with open(config_file, 'r') as f:  
                config_data = yaml.safe_load(f)  
              
            # Merge with existing configuration  
            self._merge_configs(self.config, config_data)  
              
            print(f"Loaded configuration from {config_file}")  
        except Exception as e:  
            print(f"Error loading configuration from {config_file}: {e}")  
      
    def get_value(self, key_path, default=None):  
        """  
        Get a configuration value using a dot-separated path  
          
        Args:  
            key_path (str): Dot-separated path to the configuration value  
            default: Default value to return if the key doesn't exist  
              
        Returns:  
            The configuration value, or the default if not found  
        """  
        keys = key_path.split('.')  
        value = self.config  
          
        for key in keys:  
            if isinstance(value, dict) and key in value:  
                value = value[key]  
            else:  
                return default  
          
        return value  
      
    def set_value(self, key_path, value):  
        """  
        Set a configuration value using a dot-separated path  
          
        Args:  
            key_path (str): Dot-separated path to the configuration value  
            value: Value to set  
        """  
        keys = key_path.split('.')  
        config = self.config  
          
        # Navigate to the nested dictionary  
        for key in keys[:-1]:  
            if key not in config:  
                config[key] = {}  
            config = config[key]  
          
        # Set the value  
        config[keys[-1]] = value  
      
    def save_config(self, config_file):  
        """  
        Save current configuration to a file  
          
        Args:  
            config_file (str): Path to save configuration file  
        """  
        try:  
            # Ensure directory exists  
            os.makedirs(os.path.dirname(config_file), exist_ok=True)  
              
            with open(config_file, 'w') as f:  
                yaml.dump(self.config, f, default_flow_style=False)  
              
            print(f"Saved configuration to {config_file}")  
        except Exception as e:  
            print(f"Error saving configuration to {config_file}: {e}")  
      
    def _merge_configs(self, base_config, new_config):  
        """  
        Recursively merge new_config into base_config  
          
        Args:  
            base_config (dict): Base configuration to merge into  
            new_config (dict): New configuration to merge from  
        """  
        for key, value in new_config.items():  
            if isinstance(value, dict) and key in base_config and isinstance(base_config[key], dict):  
                # Recursively merge dictionaries  
                self._merge_configs(base_config[key], value)  
            else:  
                # Replace or add value  
                base_config[key] = value