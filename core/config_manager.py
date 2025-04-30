"""  
Configuration manager for loading and managing configuration files  
"""  
  
import os  
import yaml  
  
class ConfigManager:  
    """  
    Manages loading and accessing configuration data  
    """  
      
    def __init__(self, config_file=None):  
        """  
        Initialize the configuration manager  
          
        Args:  
            config_file (str): Path to configuration file, or None for default  
        """  
        self.config = {}  
          
        # Load default configuration  
        default_config_path = os.path.join(  
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  
            "configs",  
            "default_config.yaml"  
        )  
        self.load_config(default_config_path)  
          
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
                  
    def get_value(self, key_path, default=None):  
        """  
        Get a configuration value by its key path  
          
        Args:  
            key_path (str): Dot-separated path to the configuration value  
            default: Default value to return if key not found  
              
        Returns:  
            Configuration value or default if not found  
        """  
        keys = key_path.split('.')  
        config = self.config  
          
        for key in keys:  
            if isinstance(config, dict) and key in config:  
                config = config[key]  
            else:  
                return default  
                  
        return config  
          
    def set_value(self, key_path, value):  
        """  
        Set a configuration value by its key path  
          
        Args:  
            key_path (str): Dot-separated path to the configuration value  
            value: Value to set  
        """  
        keys = key_path.split('.')  
        config = self.config  
          
        # Navigate to the parent of the target key  
        for key in keys[:-1]:  
            if key not in config:  
                config[key] = {}  
            config = config[key]  
              
        # Set the value  
        config[keys[-1]] = value  
          
    def get_plugin_config(self, plugin_name):  
        """  
        Get configuration for a specific plugin  
          
        Args:  
            plugin_name (str): Name of the plugin  
              
        Returns:  
            dict: Plugin configuration or empty dict if not found  
        """  
        plugins_config = self.get_value("plugins", {})  
        return plugins_config.get(plugin_name, {})  
          
    def set_plugin_config(self, plugin_name, config):  
        """  
        Set configuration for a specific plugin  
          
        Args:  
            plugin_name (str): Name of the plugin  
            config (dict): Plugin configuration  
        """  
        self.set_value(f"plugins.{plugin_name}", config)  
          
    def get_all_plugin_configs(self):  
        """  
        Get configurations for all plugins  
          
        Returns:  
            dict: All plugin configurations  
        """  
        return self.get_value("plugins", {})