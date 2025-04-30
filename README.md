# SimCereb  
  
SimCereb is an educational platform for humanoid robot cerebellum system simulation based on PyBullet. It provides a plugin-based architecture that allows students to experiment with different control algorithms for humanoid robots.  
  
## Features  
  
- Plugin-based architecture for easy extension  
- Default implementations of key control algorithms  
- User-friendly studio interface for visualization and parameter tuning  
- Configuration-based plugin management  
- Real-time data visualization and analysis tools  
  
## Installation  
  
```bash  
pip install -r requirements.txt  
python setup.py install
```

## Quick start
```python
from simcereb.core.engine import SimulationEngine  
from simcereb.core.robot import HumanoidRobot  
  
# Create simulation engine  [header-3](#header-3)
engine = SimulationEngine()  
  
# Load robot  [header-4](#header-4)
robot = HumanoidRobot("models/humanoid.urdf")  
engine.add_robot(robot)  
  
# Run simulation  [header-5](#header-5)
engine.run()
```

## Using the Studio
```python
python -m simcereb.ui.studio
```
## Creating Custom Plugins

```python
from simcereb.plugins.base import CerebellumPlugin  
  
class MyCustomPlugin(CerebellumPlugin):  
    def __init__(self, config=None):  
        super().__init__(config)  
          
    def initialize(self, robot, simulation):  
        # Initialize your plugin  
        pass  
          
    def update(self, dt):  
        # Update control outputs  
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
