# SimCereb  
  
SimCereb是一个基于PyBullet的人形机器人小脑系统模拟教育平台。它提供了插件架构，允许学生实验不同的控制算法，用于人形机器人的平衡和运动控制。  
  
## 版本  
  
SimCereb提供三个版本，针对不同的用户群体：  
  
- **学习版**：面向初学者和学生，提供简化界面和引导式学习  
- **研究版**：面向研究人员和高级用户，提供高级分析和实验工具  
- **教学版**：面向教育工作者，提供班级管理和教学演示功能  
  
## 特性  
  
- 插件架构，便于扩展  
- 关键控制算法的默认实现  
- 用户友好的Studio界面，用于可视化和参数调整  
- 基于配置的插件管理  
- 实时数据可视化和分析工具  
- 版本特定功能：  
  - 学习版：交互式教程、可视化编程、学习进度跟踪  
  - 研究版：高级数据分析、环境编辑器、批量实验  
  - 教学版：班级管理、作业系统、演示模式  
  
## 安装  
  
```bash  
pip install -r requirements.txt  
python setup.py install
```



## 快速开始
```python
from simcereb.core.engine import SimulationEngine  
from simcereb.core.robot import HumanoidRobot  
  
# 创建仿真引擎  [header-1](#header-1)
engine = SimulationEngine()  
  
# 加载机器人  [header-2](#header-2)
robot = HumanoidRobot("models/humanoid.urdf")  
engine.add_robot(robot)  
  
# 运行仿真  [header-3](#header-3)
engine.run()
```

## 使用Studio界面

```python
# 启动默认版本（学习版）  [header-4](#header-4)
python -m simcereb  
  
# 指定版本  [header-5](#header-5)
python -m simcereb --version learning  # 学习版  
python -m simcereb --version research  # 研究版  
python -m simcereb --version teaching  # 教学版  
  
# 指定配置文件  [header-6](#header-6)
python -m simcereb --config path/to/config.yaml

```


## 创建自定义插件

```python
from simcereb.core.plugin.base_plugin import CerebellumPlugin  
  
class MyCustomPlugin(CerebellumPlugin):  
    def __init__(self, config=None):  
        super().__init__(config)  
          
    def initialize(self, robot, simulation):  
        # 初始化插件  
        pass  
          
    def update(self, dt):  
        # 更新控制输出  
        pass
```
然后更新一下配置文件
```yaml
plugins:  
  balance_control:  
    type: "MyCustomPlugin"  
    path: "path/to/my_plugin.py"  
    parameters:  
      custom_param1: 1.0
```
# 版本切换
您可以在Studio界面中通过"文件 > 切换版本"菜单切换不同版本，或者使用命令行参数指定版本。

# 文档
详细文档请参阅docs/目录。

# MIT
This completes the implementation of the key components for the SimCereb project with its three-version structure (Learning, Research, and Teaching editions). The project now has a well-organized structure with version-specific features and a unified core architecture.



Scanned README.md
