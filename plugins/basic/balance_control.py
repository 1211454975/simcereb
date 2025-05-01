# simcereb/plugins/balance_control.py  
import numpy as np  
from ..base import CerebellumPlugin  
  
class ZMPControl(CerebellumPlugin):  
    """  
    零力矩点(ZMP)平衡控制插件  
      
    这个插件使用零力矩点(ZMP)方法来控制人形机器人的平衡。  
    ZMP是机器人动力学中的一个重要概念，表示所有地面反作用力的合力矩为零的点。  
    通过控制ZMP保持在支撑多边形内，可以保持机器人的平衡。  
    """  
      
    def __init__(self, config=None):  
        super().__init__(config)  
        # 设置默认参数  
        default_params = {  
            "com_height": 0.5,     # 质心高度  
            "stability_margin": 0.05,  # 稳定裕度  
            "kp": 10.0,            # 比例增益  
            "kd": 1.0,             # 微分增益  
            "ki": 0.1              # 积分增益  
        }  
          
        # 更新配置，使用默认值填充缺失的参数  
        for key, value in default_params.items():  
            if key not in self.config:  
                self.config[key] = value  
                  
        # 初始化积分误差  
        self.integral_error_x = 0.0  
        self.integral_error_y = 0.0  
        self.previous_error_x = 0.0  
        self.previous_error_y = 0.0  
                  
    def initialize(self, robot, simulation):  
        """初始化插件"""  
        self.robot = robot  
        self.simulation = simulation  
          
    def update(self, dt):  
        """更新控制输出"""  
        if not self.enabled:  
            return  
              
        # 获取当前ZMP和支撑多边形  
        zmp = self.robot.get_zero_moment_point()  
        support_polygon = self.robot.get_support_polygon()  
          
        if not support_polygon:  
            # 没有支撑多边形，无法控制平衡  
            return  
              
        # 计算支撑多边形的中心  
        center_x = sum(p[0] for p in support_polygon) / len(support_polygon)  
        center_y = sum(p[1] for p in support_polygon) / len(support_polygon)  
          
        # 计算ZMP误差  
        error_x = center_x - zmp[0]  
        error_y = center_y - zmp[1]  
          
        # 更新积分误差  
        self.integral_error_x += error_x * dt  
        self.integral_error_y += error_y * dt  
          
        # 计算微分误差  
        derivative_error_x = (error_x - self.previous_error_x) / dt  
        derivative_error_y = (error_y - self.previous_error_y) / dt  
          
        # 保存当前误差用于下一次计算  
        self.previous_error_x = error_x  
        self.previous_error_y = error_y  
          
        # 计算控制输出（PID控制）  
        control_x = (self.config["kp"] * error_x +   
                    self.config["ki"] * self.integral_error_x +   
                    self.config["kd"] * derivative_error_x)  
        control_y = (self.config["kp"] * error_y +   
                    self.config["ki"] * self.integral_error_y +   
                    self.config["kd"] * derivative_error_y)  
          
        # 应用控制输出（这里简化为对躯干施加力）  
        if abs(control_x) > 0.01 or abs(control_y) > 0.01:  
            self.robot.apply_external_force(  
                "torso",   
                [control_x, control_y, 0.0]  
            )  
              
    def reset(self):  
        """重置插件状态"""  
        self.integral_error_x = 0.0  
        self.integral_error_y = 0.0  
        self.previous_error_x = 0.0  
        self.previous_error_y = 0.0