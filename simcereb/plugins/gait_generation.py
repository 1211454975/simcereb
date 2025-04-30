# simcereb/plugins/gait_generation.py  
import numpy as np  
from .base import CerebellumPlugin  
  
class CPGGait(CerebellumPlugin):  
    """  
    中枢模式发生器(CPG)步态生成插件  
      
    这个插件使用中枢模式发生器(CPG)来生成人形机器人的行走步态。  
    CPG是一种生物启发的方法，模拟生物体内的神经振荡器网络来生成周期性运动模式。  
    """  
      
    def __init__(self, config=None):  
        super().__init__(config)  
        # 设置默认参数  
        default_params = {  
            "step_height": 0.05,   # 步高  
            "step_length": 0.1,    # 步长  
            "cycle_time": 1.0,     # 步态周期时间  
            "phase_offset": 0.5    # 左右腿之间的相位差  
        }  
          
        # 更新配置，使用默认值填充缺失的参数  
        for key, value in default_params.items():  
            if key not in self.config:  
                self.config[key] = value  
                  
        # 初始化CPG状态  
        self.phase = 0.0  
        self.walking = False  
          
    def initialize(self, robot, simulation):  
        """初始化插件"""  
        self.robot = robot  
        self.simulation = simulation  
          
        # 获取腿部关节ID  
        self.leg_joints = {}  
        for joint_id, info in self.robot.joint_info.items():  
            joint_name = info['name']  
            if ('hip' in joint_name or 'knee' in joint_name or 'ankle' in joint_name) and 'side' not in joint_name:  
                self.leg_joints[joint_id] = joint_name  
                  
    def update(self, dt):  
        """更新控制输出"""  
        if not self.enabled or not self.walking:  
            return  
              
        # 更新相位  
        self.phase += dt / self.config["cycle_time"]  
        if self.phase >= 1.0:  
            self.phase -= 1.0  
              
        # 计算左右腿的相位  
        right_phase = self.phase  
        left_phase = (self.phase + self.config["phase_offset"]) % 1.0  
          
        # 计算关节角度  
        joint_targets = {}  
          
        # 右腿关节  
        for joint_id, joint_name in self.leg_joints.items():  
            if 'right' in joint_name:  
                if 'hip' in joint_name:  
                    # 髋关节前后摆动  
                    joint_targets[joint_id] = self._calculate_hip_angle(right_phase)  
                elif 'knee' in joint_name:  
                    # 膝关节弯曲  
                    joint_targets[joint_id] = self._calculate_knee_angle(right_phase)  
                elif 'ankle' in joint_name:  
                    # 踝关节调整  
                    joint_targets[joint_id] = self._calculate_ankle_angle(right_phase)  
                      
        # 左腿关节  
        for joint_id, joint_name in self.leg_joints.items():  
            if 'left' in joint_name:  
                if 'hip' in joint_name:  
                    # 髋关节前后摆动  
                    joint_targets[joint_id] = self._calculate_hip_angle(left_phase)  
                elif 'knee' in joint_name:  
                    # 膝关节弯曲  
                    joint_targets[joint_id] = self._calculate_knee_angle(left_phase)  
                elif 'ankle' in joint_name:  
                    # 踝关节调整  
                    joint_targets[joint_id] = self._calculate_ankle_angle(left_phase)  
                      
        # 应用关节角度  
        if hasattr(self.robot, 'set_joint_pd_control'):  
            self.robot.set_joint_pd_control(joint_targets)  
        else:  
            self.robot.set_joint_positions(joint_targets)  
              
    def _calculate_hip_angle(self, phase):  
        """计算髋关节角度"""  
        # 简单的正弦函数模拟摆动  
        return self.config["step_length"] * np.sin(2 * np.pi * phase)  
          
    def _calculate_knee_angle(self, phase):  
        """计算膝关节角度"""  
        # 在摆动相位抬高膝盖，在支撑相位伸直  
        if phase < 0.5:  
            # 摆动相位  
            return max(0, self.config["step_height"] * np.sin(2 * np.pi * phase))  
        else:  
            # 支撑相位  
            return 0.1  # 略微弯曲以保持稳定  
              
    def _calculate_ankle_angle(self, phase):  
        """计算踝关节角度"""  
        # 踝关节角度需要与髋关节和膝关节协调，以保持足底平行于地面  
        # 在摆动相位，踝关节需要抬起脚尖；在支撑相位，踝关节需要提供稳定支撑  
        if phase < 0.5:  
            # 摆动相位 - 抬起脚尖以避免拖地  
            return -0.5 * self.config["step_length"] * np.sin(2 * np.pi * phase)  
        else:  
            # 支撑相位 - 提供稳定支撑  
            return -0.3 * self.config["step_length"] * np.sin(2 * np.pi * phase)  
            
    def start_walking(self):  
        """开始行走"""  
        self.walking = True  
        self.phase = 0.0  
        
    def stop_walking(self):  
        """停止行走"""  
        self.walking = False  
        
        # 逐渐回到站立姿势  
        joint_targets = {}  
        for joint_id in self.leg_joints.keys():  
            joint_targets[joint_id] = 0.0  
            
        # 膝盖略微弯曲以保持稳定  
        for joint_id, joint_name in self.leg_joints.items():  
            if 'knee' in joint_name:  
                joint_targets[joint_id] = 0.1  
                
        # 应用关节角度  
        if hasattr(self.robot, 'set_joint_pd_control'):  
            self.robot.set_joint_pd_control(joint_targets)  
        else:  
            self.robot.set_joint_positions(joint_targets)  
            
    def set_walking_parameters(self, step_height=None, step_length=None, cycle_time=None, phase_offset=None):  
        """  
        设置行走参数  
        
        Args:  
            step_height (float, optional): 步高  
            step_length (float, optional): 步长  
            cycle_time (float, optional): 步态周期时间  
            phase_offset (float, optional): 左右腿之间的相位差  
        """  
        if step_height is not None:  
            self.config["step_height"] = step_height  
        if step_length is not None:  
            self.config["step_length"] = step_length  
        if cycle_time is not None:  
            self.config["cycle_time"] = cycle_time  
        if phase_offset is not None:  
            self.config["phase_offset"] = phase_offset  
            
    def reset(self):  
        """重置插件状态"""  
        self.phase = 0.0  
        self.walking = False