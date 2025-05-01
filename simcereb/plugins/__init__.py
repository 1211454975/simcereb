"""  
插件模块，包含各种控制算法和功能扩展  
"""  
  
from simcereb.plugins.base import CerebellumPlugin  
  
# 导入所有内置插件  
try:  
    from simcereb.plugins.inverse_kinematics import AnalyticalIK  
    __all__ = ['CerebellumPlugin', 'AnalyticalIK']  
except ImportError:  
    __all__ = ['CerebellumPlugin']  
  
# 插件版本支持信息  
PLUGIN_VERSIONS = {  
    'PDControl': ['learning', 'research', 'teaching'],  
    'ZMPControl': ['learning', 'research', 'teaching'],  
    'CPGGait': ['learning', 'research', 'teaching'],  
}