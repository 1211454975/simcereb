# simcereb/ui/common/theme_manager.py  
"""  
Theme manager for SimCereb  
Handles loading and applying UI themes  
"""  
  
import os  
import json  
import yaml  
from PyQt5.QtGui import QColor, QPalette  
from PyQt5.QtWidgets import QApplication  
  
class ThemeManager:  
    """  
    Manages application themes and styles  
    """  
      
    # Default themes  
    LIGHT = "light"  
    DARK = "dark"  
    BLUE = "blue"  
      
    def __init__(self, config_manager):  
        """  
        Initialize the theme manager  
          
        Args:  
            config_manager: ConfigManager instance to access configuration  
        """  
        self.config_manager = config_manager  
        self.current_theme = self.config_manager.get_value("ui.theme", self.LIGHT)  
        self.themes = self._load_themes()  
          
    def _load_themes(self):  
        """Load all available themes"""  
        themes = {  
            # Default light theme  
            self.LIGHT: {  
                "window": "#F0F0F0",  
                "windowText": "#000000",  
                "base": "#FFFFFF",  
                "alternateBase": "#F7F7F7",  
                "text": "#000000",  
                "button": "#E0E0E0",  
                "buttonText": "#000000",  
                "brightText": "#FFFFFF",  
                "highlight": "#308CC6",  
                "highlightedText": "#FFFFFF",  
                "link": "#0000FF",  
                "midlight": "#E3E3E3",  
                "dark": "#A0A0A0",  
                "mid": "#B8B8B8",  
                "shadow": "#505050",  
                "font": "Segoe UI, 9pt"  
            },  
              
            # Default dark theme  
            self.DARK: {  
                "window": "#2D2D30",  
                "windowText": "#FFFFFF",  
                "base": "#252526",  
                "alternateBase": "#2A2A2C",  
                "text": "#FFFFFF",  
                "button": "#3F3F46",  
                "buttonText": "#FFFFFF",  
                "brightText": "#FFFFFF",  
                "highlight": "#3399FF",  
                "highlightedText": "#FFFFFF",  
                "link": "#3399FF",  
                "midlight": "#3F3F46",  
                "dark": "#2D2D30",  
                "mid": "#3F3F46",  
                "shadow": "#1E1E1E",  
                "font": "Segoe UI, 9pt"  
            },  
              
            # Blue theme  
            self.BLUE: {  
                "window": "#ECF4FA",  
                "windowText": "#000000",  
                "base": "#FFFFFF",  
                "alternateBase": "#F0F7FF",  
                "text": "#000000",  
                "button": "#D0E4F7",  
                "buttonText": "#000000",  
                "brightText": "#FFFFFF",  
                "highlight": "#308CC6",  
                "highlightedText": "#FFFFFF",  
                "link": "#0066CC",  
                "midlight": "#D0E4F7",  
                "dark": "#A0C8EF",  
                "mid": "#B8D8F0",  
                "shadow": "#505050",  
                "font": "Segoe UI, 9pt"  
            }  
        }  
          
        # Load custom themes from files  
        themes_dir = os.path.join(  
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),  
            "resources", "themes"  
        )  
          
        if os.path.exists(themes_dir):  
            for filename in os.listdir(themes_dir):  
                if filename.endswith('.json'):  
                    theme_name = os.path.splitext(filename)[0]  
                    theme_file = os.path.join(themes_dir, filename)  
                    try:  
                        with open(theme_file, 'r', encoding='utf-8') as f:  
                            theme_data = json.load(f)  
                        themes[theme_name] = theme_data  
                        print(f"Loaded theme from {theme_file}")  
                    except Exception as e:  
                        print(f"Error loading theme from {theme_file}: {e}")  
                          
                elif filename.endswith('.yaml') or filename.endswith('.yml'):  
                    theme_name = os.path.splitext(filename)[0]  
                    theme_file = os.path.join(themes_dir, filename)  
                    try:  
                        with open(theme_file, 'r', encoding='utf-8') as f:  
                            theme_data = yaml.safe_load(f)  
                        themes[theme_name] = theme_data  
                        print(f"Loaded theme from {theme_file}")  
                    except Exception as e:  
                        print(f"Error loading theme from {theme_file}: {e}")  
          
        return themes  
      
    def apply_theme(self, theme_name=None):  
        """  
        Apply a theme to the application  
          
        Args:  
            theme_name (str): Name of the theme to apply, or None for current theme  
              
        Returns:  
            bool: True if theme was applied successfully, False otherwise  
        """  
        if theme_name is None:  
            theme_name = self.current_theme  
              
        if theme_name not in self.themes:  
            print(f"Theme {theme_name} not found")  
            return False  
              
        theme = self.themes[theme_name]  
          
        # Create palette  
        palette = QPalette()  
          
        # Set colors  
        palette.setColor(QPalette.Window, QColor(theme.get("window", "#F0F0F0")))  
        palette.setColor(QPalette.WindowText, QColor(theme.get("windowText", "#000000")))  
        palette.setColor(QPalette.Base, QColor(theme.get("base", "#FFFFFF")))  
        palette.setColor(QPalette.AlternateBase, QColor(theme.get("alternateBase", "#F7F7F7")))  
        palette.setColor(QPalette.Text, QColor(theme.get("text", "#000000")))  
        palette.setColor(QPalette.Button, QColor(theme.get("button", "#E0E0E0")))  
        palette.setColor(QPalette.ButtonText, QColor(theme.get("buttonText", "#000000")))  
        palette.setColor(QPalette.BrightText, QColor(theme.get("brightText", "#FFFFFF")))  
        palette.setColor(QPalette.Highlight, QColor(theme.get("highlight", "#308CC6")))  
        palette.setColor(QPalette.HighlightedText, QColor(theme.get("highlightedText", "#FFFFFF")))  
        palette.setColor(QPalette.Link, QColor(theme.get("link", "#0000FF")))  
          
        # Apply palette  
        QApplication.setPalette(palette)  
          
        # Apply stylesheet if available  
        if "stylesheet" in theme:  
            QApplication.setStyleSheet(theme["stylesheet"])  
        else:  
            QApplication.setStyleSheet("")  
              
        # Save current theme  
        self.current_theme = theme_name  
        self.config_manager.set_value("ui.theme", theme_name)  
          
        return True  
      
    def get_available_themes(self):  
        """Get list of available themes"""  
        return list(self.themes.keys())  
      
    def get_current_theme(self):  
        """Get current theme name"""  
        return self.current_theme