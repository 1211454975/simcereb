"""  
Core simulation engine that integrates with PyBullet  
"""  
  
import pybullet as p  
import pybullet_data  
import time  
import numpy as np  
from .plugin.plugin_manager import PluginManager  
from ..core.config_manager import ConfigManager  
  
class SimulationEngine:  
    """  
    Main simulation engine that manages the PyBullet physics simulation  
    """  
      
    def __init__(self, config_file=None, use_gui=True):  
        """  
        Initialize the simulation engine  
          
        Args:  
            config_file (str): Path to configuration file  
            use_gui (bool): Whether to use GUI or direct mode  
        """  
        self.use_gui = use_gui  
        self.physics_client = None  
        self.robots = []  
        self.running = False  
        self.time_step = 1.0/240.0  
        self.elapsed_time = 0.0  
          
        # Load configuration  
        self.config_manager = ConfigManager(config_file)  
          
        # Initialize plugin manager  
        self.plugin_manager = PluginManager(self.config_manager)  
          
        # Connect to physics server  
        self._connect_physics_server()  
          
    def _connect_physics_server(self):  
        """Connect to PyBullet physics server"""  
        if self.use_gui:  
            self.physics_client = p.connect(p.GUI)  
        else:  
            self.physics_client = p.connect(p.DIRECT)  
              
        # Set additional path for loading models  
        p.setAdditionalSearchPath(pybullet_data.getDataPath())  
          
        # Set gravity  
        gravity = self.config_manager.get_value("simulation.gravity", [0, 0, -9.81])  
        p.setGravity(gravity[0], gravity[1], gravity[2])  
          
        # Load ground plane  
        p.loadURDF("plane.urdf")  
          
    def add_robot(self, robot):  
        """  
        Add a robot to the simulation  
          
        Args:  
            robot: Robot instance to add  
        """  
        robot.load(self.physics_client)  
        self.robots.append(robot)  
          
        # Initialize plugins with this robot  
        self.plugin_manager.initialize_plugins(robot, self)  
          
    def step(self):  
        """Perform a single simulation step"""  
        # Update plugins  
        self.plugin_manager.update_plugins(self.time_step)  
          
        # Step simulation  
        p.stepSimulation()  
          
        # Update elapsed time  
        self.elapsed_time += self.time_step  
          
    def run(self, duration=None):  
        """  
        Run the simulation for a specified duration  
          
        Args:  
            duration (float): Duration in seconds, or None for indefinite  
        """  
        self.running = True  
        start_time = time.time()  
          
        while self.running:  
            self.step()  
              
            # Check if duration has elapsed  
            if duration is not None and self.elapsed_time >= duration:  
                self.running = False  
                  
            # Sleep to maintain real-time simulation if using GUI  
            if self.use_gui:  
                time_to_sleep = self.time_step - (time.time() - start_time)  
                if time_to_sleep > 0:  
                    time.sleep(time_to_sleep)  
                start_time = time.time()  
                  
    def stop(self):  
        """Stop the simulation"""  
        self.running = False  
          
    def reset(self):  
        """Reset the simulation"""  
        p.resetSimulation()  
        self.elapsed_time = 0.0  
          
        # Reload robots  
        for robot in self.robots:  
            robot.load(self.physics_client)  
              
        # Reset plugins  
        self.plugin_manager.reset_plugins()  
          
    def disconnect(self):  
        """Disconnect from the physics server"""  
        if self.physics_client is not None:  
            p.disconnect(self.physics_client)  
            self.physics_client = None