# simcereb/core/plugin/base_plugin.py  
class CerebellumPlugin:  
    """Base class for all cerebellum plugins"""  
      
    def __init__(self, config=None):  
        """  
        Initialize the plugin  
          
        Args:  
            config (dict): Plugin configuration  
        """  
        self.config = config or {}  
        self.robot = None  
        self.simulation = None  
        self.enabled = True  
          
    def initialize(self, robot, simulation):  
        """  
        Initialize the plugin with robot and simulation references  
          
        Args:  
            robot: Robot instance  
            simulation: Simulation engine instance  
        """  
        self.robot = robot  
        self.simulation = simulation  
          
    def update(self, dt):  
        """  
        Update the plugin  
          
        Args:  
            dt (float): Time step  
        """  
        pass  
          
    def reset(self):  
        """Reset the plugin state"""  
        pass  
          
    def get_parameters(self):  
        """  
        Get plugin parameters  
          
        Returns:  
            dict: Plugin parameters  
        """  
        return self.config  
          
    def set_parameters(self, params):  
        """  
        Set plugin parameters  
          
        Args:  
            params (dict): Plugin parameters  
        """  
        self.config.update(params)  
          
    def is_enabled(self):  
        """  
        Check if the plugin is enabled  
          
        Returns:  
            bool: True if enabled, False otherwise  
        """  
        return self.enabled  
          
    def enable(self):  
        """Enable the plugin"""  
        self.enabled = True  
          
    def disable(self):  
        """Disable the plugin"""  
        self.enabled = False