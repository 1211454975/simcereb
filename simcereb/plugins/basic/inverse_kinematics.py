# simcereb/plugins/inverse_kinematics.py  
import numpy as np  
from ...core.plugin import CerebellumPlugin  
  
class AnalyticalIK(CerebellumPlugin):  
    """  
    解析逆运动学插件  
      
    这个插件实现了解析法求解人形机器人的逆运动学问题。  
    解析法通过几何关系直接计算关节角度，适用于结构简单的机器人链。  
    对于人形机器人，主要用于手臂和腿部的末端位置控制。  
    """  
      
    def __init__(self, config=None):  
        super().__init__(config)  
        # 设置默认参数  
        default_params = {  
            "max_iterations": 100,  # 最大迭代次数（用于数值方法）  
            "tolerance": 0.001,     # 收敛容差  
            "damping": 0.1,         # 阻尼因子（用于数值方法）  
            "method": "analytical"  # 求解方法：analytical, jacobian, ccd  
        }  
          
        # 更新配置，使用默认值填充缺失的参数  
        for key, value in default_params.items():  
            if key not in self.config:  
                self.config[key] = value  
                  
        # 初始化目标位置  
        self.targets = {}  
          
    def initialize(self, robot, simulation):  
        """初始化插件"""  
        self.robot = robot  
        self.simulation = simulation  
          
        # 初始化机器人链信息  
        self.chains = self._identify_kinematic_chains()  
          
    def _identify_kinematic_chains(self):  
        """识别机器人的运动学链"""  
        chains = {  
            "left_arm": [],  
            "right_arm": [],  
            "left_leg": [],  
            "right_leg": []  
        }  
          
        # 遍历所有关节，根据名称归类到不同的运动学链  
        for joint_id, info in self.robot.joint_info.items():  
            joint_name = info['name']  
              
            if 'left' in joint_name and ('shoulder' in joint_name or 'elbow' in joint_name or 'wrist' in joint_name):  
                chains["left_arm"].append(joint_id)  
            elif 'right' in joint_name and ('shoulder' in joint_name or 'elbow' in joint_name or 'wrist' in joint_name):  
                chains["right_arm"].append(joint_id)  
            elif 'left' in joint_name and ('hip' in joint_name or 'knee' in joint_name or 'ankle' in joint_name):  
                chains["left_leg"].append(joint_id)  
            elif 'right' in joint_name and ('hip' in joint_name or 'knee' in joint_name or 'ankle' in joint_name):  
                chains["right_leg"].append(joint_id)  
                  
        return chains  
          
    def update(self, dt):  
        """更新控制输出"""  
        if not self.enabled or not self.targets:  
            return  
              
        # 处理每个目标位置  
        for end_effector, target in self.targets.items():  
            if end_effector in self.chains:  
                # 获取运动学链  
                chain = self.chains[end_effector]  
                  
                # 根据选择的方法求解逆运动学  
                if self.config["method"] == "analytical":  
                    joint_angles = self._solve_analytical(end_effector, chain, target)  
                elif self.config["method"] == "jacobian":  
                    joint_angles = self._solve_jacobian(end_effector, chain, target)  
                elif self.config["method"] == "ccd":  
                    joint_angles = self._solve_ccd(end_effector, chain, target)  
                else:  
                    # 默认使用解析法  
                    joint_angles = self._solve_analytical(end_effector, chain, target)  
                      
                # 应用关节角度  
                if joint_angles:  
                    self.robot.set_joint_positions(joint_angles)  
                      
    def _solve_analytical(self, end_effector, chain, target):  
        """  
        使用解析法求解逆运动学  
          
        Args:  
            end_effector (str): 末端执行器名称  
            chain (list): 运动学链中的关节ID列表  
            target (list): 目标位置 [x, y, z]  
              
        Returns:  
            dict: 关节ID到关节角度的映射  
        """  
        # 这里实现解析法求解逆运动学  
        # 对于简单的2-3自由度链，可以使用几何方法直接求解  
          
        # 简化实现：仅处理手臂的2自由度逆运动学（肩部和肘部）  
        if 'arm' in end_effector and len(chain) >= 2:  
            # 获取肩部和肘部关节  
            shoulder_joint = None  
            elbow_joint = None  
              
            for joint_id in chain:  
                joint_name = self.robot.joint_info[joint_id]['name']  
                if 'shoulder' in joint_name:  
                    shoulder_joint = joint_id  
                elif 'elbow' in joint_name:  
                    elbow_joint = joint_id  
                      
            if shoulder_joint is not None and elbow_joint is not None:  
                # 获取肩部位置  
                shoulder_pos = None  
                if 'torso' in self.robot.link_name_to_id:  
                    torso_state = self.robot.get_link_state('torso')  
                    if torso_state:  
                        # 简化：假设肩部位于躯干侧面  
                        torso_pos = np.array(torso_state['position'])  
                        if 'left' in end_effector:  
                            shoulder_pos = torso_pos + np.array([-0.2, 0, 0.1])  
                        else:  
                            shoulder_pos = torso_pos + np.array([0.2, 0, 0.1])  
                  
                if shoulder_pos is not None:  
                    # 计算目标相对于肩部的位置  
                    target_rel = np.array(target) - shoulder_pos  
                      
                    # 计算到目标的距离  
                    distance = np.linalg.norm(target_rel)  
                      
                    # 假设上臂和前臂长度  
                    upper_arm_length = 0.3  
                    forearm_length = 0.25  
                      
                    # 使用余弦定理计算肘部角度  
                    cos_elbow = (upper_arm_length**2 + forearm_length**2 - distance**2) / (2 * upper_arm_length * forearm_length)  
                    cos_elbow = np.clip(cos_elbow, -1.0, 1.0)  # 确保在有效范围内  
                    elbow_angle = np.arccos(cos_elbow)  
                      
                    # 计算肩部角度  
                    # 简化：仅考虑XZ平面内的角度  
                    shoulder_angle = np.arctan2(target_rel[2], target_rel[0])  
                      
                    # 返回关节角度  
                    return {  
                        shoulder_joint: shoulder_angle,  
                        elbow_joint: elbow_angle  
                    }  
                      
        # 对于其他情况，返回空字典  
        return {}  
          
    def _solve_jacobian(self, end_effector, chain, target):  
        """  
        使用雅可比矩阵法求解逆运动学  
          
        Args:  
            end_effector (str): 末端执行器名称  
            chain (list): 运动学链中的关节ID列表  
            target (list): 目标位置 [x, y, z]  
              
        Returns:  
            dict: 关节ID到关节角度的映射  
        """  
        # 这里实现雅可比矩阵法求解逆运动学  
        # 雅可比矩阵法是一种数值方法，适用于任意自由度的机器人  
          
        # 获取当前关节角度  
        current_angles = {}  
        for joint_id in chain:  
            current_angles[joint_id] = self.robot.joint_states[joint_id]['position']  
              
        # 获取末端执行器当前位置  
        end_effector_link = None  
        if 'arm' in end_effector:  
            if 'left' in end_effector and 'left_hand' in self.robot.link_name_to_id:  
                end_effector_link = 'left_hand'  
            elif 'right' in end_effector and 'right_hand' in self.robot.link_name_to_id:  
                end_effector_link = 'right_hand'  
        elif 'leg' in end_effector:  
            if 'left' in end_effector and 'left_foot' in self.robot.link_name_to_id:  
                end_effector_link = 'left_foot'  
            elif 'right' in end_effector and 'right_foot' in self.robot.link_name_to_id:  
                end_effector_link = 'right_foot'  
                  
        if end_effector_link is None:  
            return {}  
              
        end_effector_state = self.robot.get_link_state(end_effector_link)  
        if not end_effector_state:  
            return {}  
              
        current_pos = np.array(end_effector_state['position'])  
          
        # 计算位置误差  
        error = np.array(target) - current_pos  
        error_norm = np.linalg.norm(error)  
          
        # 如果误差小于容差，则不需要调整  
        if error_norm < self.config["tolerance"]:  
            return {}  
              
        # 迭代求解  
        iterations = 0  
        while error_norm > self.config["tolerance"] and iterations < self.config["max_iterations"]:  
            # 计算雅可比矩阵  
            jacobian = self._calculate_jacobian(chain, end_effector_link)  
              
            # 使用阻尼最小二乘法求解关节角度增量  
            damping = self.config["damping"]  
            j_transpose = jacobian.T  
            j_pseudo_inv = j_transpose.dot(np.linalg.inv(jacobian.dot(j_transpose) + damping**2 * np.eye(3)))  
            delta_theta = j_pseudo_inv.dot(error)  
              
            # 更新关节角度  
            for i, joint_id in enumerate(chain):  
                if i < len(delta_theta):  
                    current_angles[joint_id] += delta_theta[i]  
                      
            # 应用新的关节角度并获取新的末端执行器位置  
            self.robot.set_joint_positions(current_angles)  
            end_effector_state = self.robot.get_link_state(end_effector_link)  
            if not end_effector_state:  
                break  
                  
            current_pos = np.array(end_effector_state['position'])  
            error = np.array(target) - current_pos  
            error_norm = np.linalg.norm(error)  
              
            iterations += 1  
              
        return current_angles  
          
    def _calculate_jacobian(self, chain, end_effector_link):  
        """  
        计算雅可比矩阵  
          
        Args:  
            chain (list): 运动学链中的关节ID列表  
            end_effector_link (str): 末端执行器链接名称  
              
        Returns:  
            numpy.ndarray: 雅可比矩阵  
        """  
        # 这里实现雅可比矩阵的计算  
        # 雅可比矩阵表示关节角度变化对末端执行器位置的影响  
          
        # 简化实现：使用数值微分计算雅可比矩阵  
        jacobian = np.zeros((3, len(chain)))  
          
        # 获取末端执行器当前位置  
        end_effector_state = self.robot.get_link_state(end_effector_link)  
        if not end_effector_state:  
            return jacobian  
              
        current_pos = np.array(end_effector_state['position'])  
          
        # 获取当前关节角度  
        current_angles = {}  
        for joint_id in chain:  
            current_angles[joint_id] = self.robot.joint_states[joint_id]['position']  
              
        # 对每个关节计算雅可比列  
        for i, joint_id in enumerate(chain):  
            # 保存当前角度  
            original_angle = current_angles[joint_id]  
              
            # 微小扰动  
            delta = 0.01  
            current_angles[joint_id] = original_angle + delta  
              
            # 应用新角度  
            self.robot.set_joint_positions({joint_id: current_angles[joint_id]})  
              
            # 获取新的末端执行器位置  
            new_state = self.robot.get_link_state(end_effector_link)  
            if new_state:  
                new_pos = np.array(new_state['position'])  
                  
                # 计算雅可比列  
                jacobian[:, i] = (new_pos - current_pos) / delta  
                  
            # 恢复原始角度  
            current_angles[joint_id] = original_angle  
            self.robot.set_joint_positions({joint_id: original_angle})  
              
        return jacobian  
          
    def _solve_ccd(self, end_effector, chain, target):  
        """  
        使用循环坐标下降法(CCD)求解逆运动学  
        
        Args:  
            end_effector (str): 末端执行器名称  
            chain (list): 运动学链中的关节ID列表  
            target (list): 目标位置 [x, y, z]  
            
        Returns:  
            dict: 关节ID到关节角度的映射  
        """  
        # 这里实现CCD算法求解逆运动学  
        # CCD是一种迭代算法，从末端关节开始，逐个调整关节角度  
        
        # 获取末端执行器链接  
        end_effector_link = None  
        if 'arm' in end_effector:  
            if 'left' in end_effector and 'left_hand' in self.robot.link_name_to_id:  
                end_effector_link = 'left_hand'  
            elif 'right' in end_effector and 'right_hand' in self.robot.link_name_to_id:  
                end_effector_link = 'right_hand'  
        elif 'leg' in end_effector:  
            if 'left' in end_effector and 'left_foot' in self.robot.link_name_to_id:  
                end_effector_link = 'left_foot'  
            elif 'right' in end_effector and 'right_foot' in self.robot.link_name_to_id:  
                end_effector_link = 'right_foot'  
                
        if end_effector_link is None:  
            return {}  
            
        # 获取当前关节角度  
        current_angles = {}  
        for joint_id in chain:  
            current_angles[joint_id] = self.robot.joint_states[joint_id]['position']  
        
        # 获取末端执行器当前位置  
        end_effector_state = self.robot.get_link_state(end_effector_link)  
        if not end_effector_state:  
            return {}  
            
        # 迭代求解  
        target_pos = np.array(target)  
        iterations = 0  
        error = np.linalg.norm(np.array(end_effector_state['position']) - target_pos)  
        
        while error > self.config["tolerance"] and iterations < self.config["max_iterations"]:  
            # 从末端关节向基座关节遍历  
            for joint_id in reversed(chain):  
                # 获取关节位置  
                joint_link = self.robot.joint_info[joint_id]['link_name']  
                joint_state = self.robot.get_link_state(joint_link)  
                if not joint_state:  
                    continue  
                    
                joint_pos = np.array(joint_state['position'])  
                
                # 获取末端执行器当前位置  
                end_effector_state = self.robot.get_link_state(end_effector_link)  
                if not end_effector_state:  
                    break  
                    
                end_effector_pos = np.array(end_effector_state['position'])  
                
                # 计算向量  
                current_to_target = target_pos - joint_pos  
                current_to_end = end_effector_pos - joint_pos  
                
                # 归一化向量  
                current_to_target = current_to_target / np.linalg.norm(current_to_target)  
                current_to_end = current_to_end / np.linalg.norm(current_to_end)  
                
                # 计算旋转轴和角度  
                rotation_axis = np.cross(current_to_end, current_to_target)  
                rotation_axis_norm = np.linalg.norm(rotation_axis)  
                
                if rotation_axis_norm > 1e-6:  # 避免除以零  
                    rotation_axis = rotation_axis / rotation_axis_norm  
                    cos_angle = np.clip(np.dot(current_to_end, current_to_target), -1.0, 1.0)  
                    angle = np.arccos(cos_angle)  
                    
                    # 限制角度变化，避免过大的调整  
                    angle = np.clip(angle, -0.5, 0.5)  
                    
                    # 确定旋转方向  
                    if np.dot(np.cross(current_to_end, current_to_target), rotation_axis) < 0:  
                        angle = -angle  
                    
                    # 更新关节角度  
                    current_angles[joint_id] += angle  
                    
                    # 应用新的关节角度  
                    self.robot.set_joint_positions({joint_id: current_angles[joint_id]})  
            
            # 获取新的末端执行器位置，计算误差  
            end_effector_state = self.robot.get_link_state(end_effector_link)  
            if end_effector_state:  
                error = np.linalg.norm(np.array(end_effector_state['position']) - target_pos)  
            
            iterations += 1  
        
        return current_angles  
    
    def set_target(self, end_effector, target_position):  
        """  
        设置末端执行器的目标位置  
        
        Args:  
            end_effector (str): 末端执行器名称 ("left_arm", "right_arm", "left_leg", "right_leg")  
            target_position (list): 目标位置 [x, y, z]  
        """  
        if end_effector in self.chains:  
            self.targets[end_effector] = target_position  
        else:  
            print(f"警告: 未知的末端执行器 '{end_effector}'")  
            
    def clear_targets(self):  
        """清除所有目标位置"""  
        self.targets.clear()  
        
    def get_end_effector_position(self, end_effector):  
        """  
        获取末端执行器的当前位置  
        
        Args:  
            end_effector (str): 末端执行器名称  
            
        Returns:  
            list: 末端执行器位置 [x, y, z] 或 None  
        """  
        end_effector_link = None  
        
        if 'arm' in end_effector:  
            if 'left' in end_effector and 'left_hand' in self.robot.link_name_to_id:  
                end_effector_link = 'left_hand'  
            elif 'right' in end_effector and 'right_hand' in self.robot.link_name_to_id:  
                end_effector_link = 'right_hand'  
        elif 'leg' in end_effector:  
            if 'left' in end_effector and 'left_foot' in self.robot.link_name_to_id:  
                end_effector_link = 'left_foot'  
            elif 'right' in end_effector and 'right_foot' in self.robot.link_name_to_id:  
                end_effector_link = 'right_foot'  
                
        if end_effector_link is None:  
            return None  
            
        end_effector_state = self.robot.get_link_state(end_effector_link)  
        if end_effector_state:  
            return end_effector_state['position']  
        
        return None  
        
    def reset(self):  
        """重置插件状态"""  
        self.targets.clear()