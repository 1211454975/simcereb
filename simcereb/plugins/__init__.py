"""  
插件模块，包含各种控制算法和功能扩展  
"""  
  
try:  
    from simcereb.plugins.base import CerebellumPlugin  
    __all__ = ['CerebellumPlugin']  
      
    # 尝试导入内置插件  
    try:  
        from simcereb.plugins.inverse_kinematics import AnalyticalIK  
        __all__.append('AnalyticalIK')  
    except ImportError:  
        pass  
      
    try:  
        from simcereb.plugins.gait_generation import CPGGait  
        __all__.append('CPGGait')  
    except ImportError:  
        pass  
          
except ImportError:  
    __all__ = []  
  
# 插件版本支持信息  
PLUGIN_VERSIONS = {  
    'PDControl': ['learning', 'research', 'teaching'],  
    'ZMPControl': ['learning', 'research', 'teaching'],  
    'CPGGait': ['learning', 'research', 'teaching'],  
    'AnalyticalIK': ['research', 'teaching']  
}