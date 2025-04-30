# simcereb/ui/common/language_manager.py  
"""  
Language manager for SimCereb  
Handles loading and managing translations for the UI  
"""  
  
import os  
import json  
import yaml  
  
class LanguageManager:  
    """  
    Manages application language and translations  
    """  
      
    def __init__(self, config_manager):  
        """  
        Initialize the language manager  
          
        Args:  
            config_manager: ConfigManager instance to access configuration  
        """  
        self.config_manager = config_manager  
        self.current_language = self.config_manager.get_value("ui.language", "zh_CN")  
        self.translations = {}  
        self.available_languages = self._get_available_languages()  
        self._load_translations()  
      
    def _get_available_languages(self):  
        """Get list of available languages from translation files"""  
        languages = []  
        translations_dir = os.path.join(  
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),  
            "resources", "translations"  
        )  
          
        if os.path.exists(translations_dir):  
            for filename in os.listdir(translations_dir):  
                if filename.endswith('.json') or filename.endswith('.yaml'):  
                    lang_code = os.path.splitext(filename)[0]  
                    languages.append(lang_code)  
          
        # Always ensure at least English and Chinese are available  
        if 'en_US' not in languages:  
            languages.append('en_US')  
        if 'zh_CN' not in languages:  
            languages.append('zh_CN')  
              
        return languages  
      
    def _load_translations(self):  
        """Load translations for the current language"""  
        translations_dir = os.path.join(  
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),  
            "resources", "translations"  
        )  
          
        # Try to load language file  
        lang_file = os.path.join(translations_dir, f"{self.current_language}.json")  
        if os.path.exists(lang_file):  
            try:  
                with open(lang_file, 'r', encoding='utf-8') as f:  
                    self.translations = json.load(f)  
                print(f"Loaded translations from {lang_file}")  
                return  
            except Exception as e:  
                print(f"Error loading translations from {lang_file}: {e}")  
          
        # Try YAML format as fallback  
        lang_file = os.path.join(translations_dir, f"{self.current_language}.yaml")  
        if os.path.exists(lang_file):  
            try:  
                with open(lang_file, 'r', encoding='utf-8') as f:  
                    self.translations = yaml.safe_load(f)  
                print(f"Loaded translations from {lang_file}")  
                return  
            except Exception as e:  
                print(f"Error loading translations from {lang_file}: {e}")  
          
        print(f"No translation file found for {self.current_language}, using keys as translations")  
      
    def get_text(self, key, default=None):  
        """  
        Get translated text for a key  
          
        Args:  
            key (str): Translation key  
            default: Default value if key is not found, if None, key is used as default  
              
        Returns:  
            str: Translated text  
        """  
        if default is None:  
            default = key  
              
        return self.translations.get(key, default)  
      
    def set_language(self, language_code):  
        """  
        Set the current language  
          
        Args:  
            language_code (str): Language code to set  
              
        Returns:  
            bool: True if language was set successfully, False otherwise  
        """  
        if language_code in self.available_languages:  
            self.current_language = language_code  
            self.config_manager.set_value("ui.language", language_code)  
            self._load_translations()  
            return True  
        return False  
      
    def get_language_name(self, language_code=None):  
        """  
        Get the display name of a language  
          
        Args:  
            language_code (str): Language code, or None for current language  
              
        Returns:  
            str: Language display name  
        """  
        if language_code is None:  
            language_code = self.current_language  
              
        language_names = {  
            'en_US': 'English',  
            'zh_CN': '中文(简体)',  
            'zh_TW': '中文(繁體)',  
            'ja_JP': '日本語',  
            'ko_KR': '한국어',  
            'fr_FR': 'Français',  
            'de_DE': 'Deutsch',  
            'es_ES': 'Español',  
            'ru_RU': 'Русский'  
        }  
          
        return language_names.get(language_code, language_code)