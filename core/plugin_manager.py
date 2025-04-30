"""  
Plugin manager for loading and managing plugins  
"""  
  
import importlib  
import inspect  
import os  
import sys  
from ..plugins.base import CerebellumPlugin  
  
class PluginManager:  
    """  
    Manages the loading, initialization, and execution of plugins  
    """  
      
    def __init__(self, config_manager):  
        """  
        Initialize the plugin manager  
          
        Args:  
            config_manager: Configuration manager instance  
        """  
        self.config_manager = config_manager  
        self.plugins = {}  
        self.load_plugins()  
          
    def load_plugins(self):  
        """Load plugins based on configuration"""  
        plugin_configs = self.config_manager.get_value("plugins", {})  
          
        for plugin_name, plugin_config in plugin_configs.items():  
            self.load_plugin(plugin_name, plugin_config)  
              
    def load_plugin(self, plugin_name, plugin_config):  
        """  
        Load a single plugin  
          
        Args:  
            plugin_name (str): Name of the plugin  
            plugin_config (dict): Plugin configuration  
        """  
        plugin_type = plugin_config.get("type")  
        plugin_path = plugin_config.get("path")  
        plugin_params = plugin_config.get("parameters", {})  
          
        if plugin_type is None:  
            print(f"Warning: Plugin {plugin_name} has no type specified")  
            return  
              
        # Try to load built-in plugin first  
        try:  
            module_name = f"simcereb.plugins.{plugin_type.lower()}"  
            module = importlib.import_module(module_name)  
              
            # Find the plugin class in the module  
            for name, obj in inspect.getmembers(module):  
                if (inspect.isclass(obj) and issubclass(obj, CerebellumPlugin) and   
                    obj != CerebellumPlugin):  
                    plugin_class = obj  
                    break  
            else:  
                print(f"Warning: Could not find plugin class in {module_name}")  
                return  
                  
        except ImportError:  
            # If not a built-in plugin, try to load from custom path  
            if plugin_path is None:  
                print(f"Warning: Custom plugin {plugin_name} has no path specified")  
                return  
                  
            try:  
                # Add directory to path  
                plugin_dir = os.path.dirname(plugin_path)  
                if plugin_dir not in sys.path:  
                    sys.path.append(plugin_dir)  
                      
                # Import module  
                module_name = os.path.basename(plugin_path).replace(".py", "")  
                module = importlib.import_module(module_name)  
                  
                # Find the plugin class in the module  
                for name, obj in inspect.getmembers(module):  
                    if (inspect.isclass(obj) and issubclass(obj, CerebellumPlugin) and   
                        obj != CerebellumPlugin):  
                        plugin_class = obj  
                        break  
                else:  
                    print(f"Warning: Could not find plugin class in {module_name}")  
                    return  
                      
            except ImportError as e:  
                print(f"Error loading plugin {plugin_name}: {e}")  
                return  
                  
        # Create plugin instance  
        try:  
            plugin_instance = plugin_class(plugin_params)  
            self.plugins[plugin_name] = plugin_instance  
            print(f"Loaded plugin: {plugin_name}")  
        except Exception as e:  
            print(f"Error instantiating plugin {plugin_name}: {e}")  
              
    def initialize_plugins(self, robot, simulation):  
        """  
        Initialize all plugins with robot and simulation references  
          
        Args:  
            robot: Robot instance  
            simulation: Simulation engine instance  
        """  
        for plugin_name, plugin in self.plugins.items():  
            try:  
                plugin.initialize(robot, simulation)  
                print(f"Initialized plugin: {plugin_name}")  
            except Exception as e:  
                print(f"Error initializing plugin {plugin_name}: {e}")  
                  
    def update_plugins(self, dt):  
        """  
        Update all plugins  
          
        Args:  
            dt (float): Time step  
        """  
        for plugin_name, plugin in self.plugins.items():  
            try:  
                plugin.update(dt)  
            except Exception as e:  
                print(f"Error updating plugin {plugin_name}: {e}")  
                  
    def reset_plugins(self):  
        """Reset all plugins"""  
        for plugin_name, plugin in self.plugins.items():  
            try:  
                plugin.reset()  
                print(f"Reset plugin: {plugin_name}")  
            except Exception as e:  
                print(f"Error resetting plugin {plugin_name}: {e}")  
                  
    def get_plugin(self, plugin_name):  
        """  
        Get a plugin by name  
          
        Args:  
            plugin_name (str): Name of the plugin  
              
        Returns:  
            Plugin instance or None if not found  
        """  
        return self.plugins.get(plugin_name)