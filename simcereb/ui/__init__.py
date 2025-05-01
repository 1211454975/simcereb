"""  
用户界面模块，包含学习版、研究版和教学版的界面组件  
"""  
  
# 导入通用UI组件  
from simcereb.ui.common.language_manager import LanguageManager  
  
# 导入版本特定组件  
try:  
    from simcereb.ui.research.environment_editor import EnvironmentEditor  
    from simcereb.ui.research.experiment_manager import ExperimentManager  
    from simcereb.ui.plugin_browser import PluginBrowser  
      
    __all__ = ['LanguageManager', 'EnvironmentEditor', 'ExperimentManager', 'PluginBrowser']  
except ImportError:  
    __all__ = ['LanguageManager']  
  
# 支持的UI语言  
SUPPORTED_LANGUAGES = ['en_US', 'zh_CN', 'zh_TW', 'ja_JP', 'ko_KR', 'fr_FR', 'de_DE', 'es_ES', 'ru_RU']