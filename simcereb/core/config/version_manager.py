# simcereb/core/config/version_manager.py  
"""  
Version management system for SimCereb  
Controls which features are available in different editions  
"""  
  
class VersionManager:  
    """  
    Manages different versions of SimCereb and their feature flags  
    """  
      
    # Version constants  
    LEARNING = "learning"  
    RESEARCH = "research"  
    TEACHING = "teaching"  
      
    def __init__(self, config_manager):  
        """  
        Initialize the version manager  
          
        Args:  
            config_manager: ConfigManager instance to access configuration  
        """  
        self.config_manager = config_manager  
        self.current_version = self.config_manager.get_value("version", self.LEARNING)  
        self.feature_flags = self._load_feature_flags()  
          
    def _load_feature_flags(self):  
        """Load feature flags for the current version"""  
        version_config = self.config_manager.get_value("versions", {})  
        return version_config.get(self.current_version, {}).get("features", {})  
      
    def is_feature_enabled(self, feature_name):  
        """  
        Check if a specific feature is enabled in the current version  
          
        Args:  
            feature_name: Name of the feature to check  
              
        Returns:  
            bool: True if the feature is enabled, False otherwise  
        """  
        return self.feature_flags.get(feature_name, False)  
      
    def get_version(self):  
        """Get the current version"""  
        return self.current_version  
      
    def set_version(self, version):  
        """  
        Set the current version  
          
        Args:  
            version: Version to set (LEARNING, RESEARCH, or TEACHING)  
              
        Returns:  
            bool: True if version was set successfully, False otherwise  
        """  
        if version in [self.LEARNING, self.RESEARCH, self.TEACHING]:  
            self.current_version = version  
            self.feature_flags = self._load_feature_flags()  
            self.config_manager.set_value("version", version)  
            return True  
        return False  
      
    def get_version_name(self):  
        """Get the display name of the current version"""  
        version_names = {  
            self.LEARNING: "学习版",  
            self.RESEARCH: "研究版",  
            self.TEACHING: "教学版"  
        }  
        return version_names.get(self.current_version, "")  
      
    def get_available_features(self):  
        """Get a list of all available features in the current version"""  
        return list(self.feature_flags.keys())