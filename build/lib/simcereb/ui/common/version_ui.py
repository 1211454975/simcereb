# simcereb/ui/common/version_ui.py  
"""  
Base classes for version-specific UI components  
"""  
  
from PyQt5.QtWidgets import QWidget  
  
class VersionSpecificWidget(QWidget):  
    """  
    Base class for version-specific widgets  
    Provides common functionality for all version-specific widgets  
    """  
      
    def __init__(self, version_manager, parent=None):  
        """  
        Initialize the version-specific widget  
          
        Args:  
            version_manager: VersionManager instance to check feature availability  
            parent: Parent widget  
        """  
        super().__init__(parent)  
        self.version_manager = version_manager  
          
    def is_feature_enabled(self, feature_name):  
        """  
        Check if a feature is enabled in the current version  
          
        Args:  
            feature_name (str): Name of the feature to check  
              
        Returns:  
            bool: True if the feature is enabled, False otherwise  
        """  
        return self.version_manager.is_feature_enabled(feature_name)  
      
    def get_version(self):  
        """Get the current version"""  
        return self.version_manager.get_version()  
      
    def is_learning_edition(self):  
        """Check if current version is Learning Edition"""  
        return self.get_version() == self.version_manager.LEARNING  
      
    def is_research_edition(self):  
        """Check if current version is Research Edition"""  
        return self.get_version() == self.version_manager.RESEARCH  
      
    def is_teaching_edition(self):  
        """Check if current version is Teaching Edition"""  
        return self.get_version() == self.version_manager.TEACHING