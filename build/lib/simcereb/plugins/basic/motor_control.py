# simcereb/plugins/motor_control.py  
import numpy as np  
from ...core.plugin import CerebellumPlugin  
  
class PDControl(CerebellumPlugin):  
    """  
    PD控制插件，实现关节电机的PD控制  
      
    这个插件使用比例-微分(PD)控制算法来控制机器人关节。  
    PD控制是一种常用的控制方法，通过比例项和微分项的组合来控制系统。  
    """  
      
    def __init__(self, config=None):  
        super().__init__(config)  
        # 设置默认参数  
        default_params = {  
            "kp": 100.0,           # 比例增益  
            "kd": 2.0,             # 微分增益  
            "max_force": 100.0,    # 最大力矩  
            "control_mode": "position"  # 控制模式：position, velocity, torque  
        }  
          
        # 更新配置，使用默认值填充缺失的参数  
        for key, value in default_params.items():  
            if key not in self.config:  
                self.config[key] = value  
                  
    def initialize(self, robot, simulation):  
        """初始化插件"""  
        self.robot = robot  
        self.simulation = simulation  
        self.target_positions = {}  
          
        # 初始化目标位置为当前位置  
        joint_positions = self.robot.get_joint_positions()  
        for joint_id, position in joint_positions.items():  
            self.target_positions[joint_id] = position  
              
    def update(self, dt):  
        """更新控制输出"""  
        if not self.enabled:  
            return  
              
        # 获取当前关节状态  
        joint_positions = self.robot.get_joint_positions()  
        joint_velocities = self.robot.get_joint_velocities()  
          
        # 应用PD控制  
        if self.config["control_mode"] == "position":  
            self.robot.set_joint_pd_control(  
                self.target_positions,  
                kp=self.config["kp"],  
                kd=self.config["kd"]  
            )  
              
    def set_target_position(self, joint_id, position):  
        """  
        设置关节目标位置  
          
        Args:  
            joint_id: 关节ID或名称  
            position: 目标位置  
        """  
        if isinstance(joint_id, str):  
            # 如果提供的是关节名称，转换为ID  
            if joint_id in self.robot.joint_name_to_id:  
                joint_id = self.robot.joint_name_to_id[joint_id]  
            else:  
                return  
                  
        self.target_positions[joint_id] = position  
          
    def set_target_positions(self, positions):  
        """  
        设置多个关节的目标位置  
          
        Args:  
            positions (dict): 关节ID/名称到目标位置的映射  
        """  
        for joint_id, position in positions.items():  
            self.set_target_position(joint_id, position)  
              
    def reset(self):  
        """重置插件状态"""  
        # 重置目标位置为当前位置  
        joint_positions = self.robot.get_joint_positions()  
        for joint_id, position in joint_positions.items():  
            self.target_positions[joint_id] = position