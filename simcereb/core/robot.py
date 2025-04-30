"""  
Robot abstraction for humanoid robots in the SimCereb system  
"""  
  
import os  
import numpy as np  
import pybullet as p  
  
class HumanoidRobot:  
    """  
    Humanoid robot class that provides a high-level interface for controlling  
    a humanoid robot in the PyBullet simulation  
    """  
      
    def __init__(self, urdf_path, initial_pose="stand"):  
        """  
        Initialize the humanoid robot  
          
        Args:  
            urdf_path (str): Path to the URDF file  
            initial_pose (str): Initial pose of the robot (stand, sit, etc.)  
        """  
        self.urdf_path = urdf_path  
        self.initial_pose = initial_pose  
        self.robot_id = None  
        self.num_joints = 0  
        self.joint_info = {}  
        self.joint_name_to_id = {}  
        self.link_name_to_id = {}  
        self.joint_states = {}  
        self.physics_client = None  
          
    def load(self, physics_client):  
        """  
        Load the robot into the simulation  
          
        Args:  
            physics_client: PyBullet physics client  
        """  
        self.physics_client = physics_client  
          
        # Check if URDF file exists  
        if not os.path.exists(self.urdf_path):  
            # Try to find it relative to the current file  
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
            alt_path = os.path.join(base_path, "models", os.path.basename(self.urdf_path))  
            if os.path.exists(alt_path):  
                self.urdf_path = alt_path  
            else:  
                raise FileNotFoundError(f"URDF file not found: {self.urdf_path}")  
          
        # Load the robot  
        self.robot_id = p.loadURDF(  
            self.urdf_path,  
            basePosition=[0, 0, 1],  # Start 1m above ground  
            baseOrientation=p.getQuaternionFromEuler([0, 0, 0]),  
            useFixedBase=False,  
            flags=p.URDF_USE_SELF_COLLISION  
        )  
          
        # Get joint information  
        self.num_joints = p.getNumJoints(self.robot_id)  
        for i in range(self.num_joints):  
            joint_info = p.getJointInfo(self.robot_id, i)  
            joint_name = joint_info[1].decode('utf-8')  
            link_name = joint_info[12].decode('utf-8')  
              
            self.joint_info[i] = {  
                'name': joint_name,  
                'type': joint_info[2],  
                'lower_limit': joint_info[8],  
                'upper_limit': joint_info[9],  
                'max_force': joint_info[10],  
                'max_velocity': joint_info[11],  
                'link_name': link_name  
            }  
              
            self.joint_name_to_id[joint_name] = i  
            self.link_name_to_id[link_name] = i  
              
        # Set initial pose  
        self.set_pose(self.initial_pose)  
          
        # Update joint states  
        self.update_joint_states()  
          
    def update_joint_states(self):  
        """Update the joint states dictionary with current joint positions and velocities"""  
        for i in range(self.num_joints):  
            joint_state = p.getJointState(self.robot_id, i)  
            self.joint_states[i] = {  
                'position': joint_state[0],  
                'velocity': joint_state[1],  
                'reaction_forces': joint_state[2],  
                'applied_torque': joint_state[3]  
            }  
              
    def set_pose(self, pose_name):  
        """  
        Set the robot to a predefined pose  
          
        Args:  
            pose_name (str): Name of the pose (stand, sit, etc.)  
        """  
        if pose_name == "stand":  
            # Define a standing pose  
            # This is a simple example, you might want to define more complex poses  
            for i in range(self.num_joints):  
                if self.joint_info[i]['type'] == p.JOINT_REVOLUTE:  
                    # Set all joints to zero position  
                    p.resetJointState(self.robot_id, i, 0)  
                      
            # Adjust specific joints for standing pose  
            if "left_knee" in self.joint_name_to_id:  
                p.resetJointState(self.robot_id, self.joint_name_to_id["left_knee"], 0.1)  
            if "right_knee" in self.joint_name_to_id:  
                p.resetJointState(self.robot_id, self.joint_name_to_id["right_knee"], 0.1)  
                  
        elif pose_name == "sit":  
            # Define a sitting pose  
            for i in range(self.num_joints):  
                if self.joint_info[i]['type'] == p.JOINT_REVOLUTE:  
                    # Set all joints to zero position  
                    p.resetJointState(self.robot_id, i, 0)  
                      
            # Adjust specific joints for sitting pose  
            if "left_knee" in self.joint_name_to_id:  
                p.resetJointState(self.robot_id, self.joint_name_to_id["left_knee"], 1.5)  
            if "right_knee" in self.joint_name_to_id:  
                p.resetJointState(self.robot_id, self.joint_name_to_id["right_knee"], 1.5)  
            if "left_hip" in self.joint_name_to_id:  
                p.resetJointState(self.robot_id, self.joint_name_to_id["left_hip"], -0.5)  
            if "right_hip" in self.joint_name_to_id:  
                p.resetJointState(self.robot_id, self.joint_name_to_id["right_hip"], -0.5)  
          
        # Update joint states after changing pose  
        self.update_joint_states()  
          
    def set_joint_positions(self, joint_positions):  
        """  
        Set joint positions  
          
        Args:  
            joint_positions (dict): Dictionary mapping joint names or IDs to target positions  
        """  
        for joint, position in joint_positions.items():  
            joint_id = joint if isinstance(joint, int) else self.joint_name_to_id.get(joint)  
            if joint_id is not None:  
                p.setJointMotorControl2(  
                    self.robot_id,  
                    joint_id,  
                    p.POSITION_CONTROL,  
                    targetPosition=position,  
                    force=self.joint_info[joint_id]['max_force'],  
                    maxVelocity=self.joint_info[joint_id]['max_velocity']  
                )  
                  
    def set_joint_velocities(self, joint_velocities):  
        """  
        Set joint velocities  
          
        Args:  
            joint_velocities (dict): Dictionary mapping joint names or IDs to target velocities  
        """  
        for joint, velocity in joint_velocities.items():  
            joint_id = joint if isinstance(joint, int) else self.joint_name_to_id.get(joint)  
            if joint_id is not None:  
                p.setJointMotorControl2(  
                    self.robot_id,  
                    joint_id,  
                    p.VELOCITY_CONTROL,  
                    targetVelocity=velocity,  
                    force=self.joint_info[joint_id]['max_force']  
                )  
                  
    def set_joint_torques(self, joint_torques):  
        """  
        Set joint torques  
          
        Args:  
            joint_torques (dict): Dictionary mapping joint names or IDs to target torques  
        """  
        for joint, torque in joint_torques.items():  
            joint_id = joint if isinstance(joint, int) else self.joint_name_to_id.get(joint)  
            if joint_id is not None:  
                p.setJointMotorControl2(  
                    self.robot_id,  
                    joint_id,  
                    p.TORQUE_CONTROL,  
                    force=torque  
                )  
                  
    def set_joint_pd_control(self, joint_targets, kp=None, kd=None):  
        """  
        Set joint PD control  
          
        Args:  
            joint_targets (dict): Dictionary mapping joint names or IDs to target positions  
            kp (float or dict): Proportional gain (global or per-joint)  
            kd (float or dict): Derivative gain (global or per-joint)  
        """  
        for joint, target in joint_targets.items():  
            joint_id = joint if isinstance(joint, int) else self.joint_name_to_id.get(joint)  
            if joint_id is not None:  
                # Determine kp and kd for this joint  
                joint_kp = kp[joint] if isinstance(kp, dict) else kp  
                joint_kd = kd[joint] if isinstance(kd, dict) else kd  
                  
                p.setJointMotorControl2(  
                    self.robot_id,  
                    joint_id,  
                    p.POSITION_CONTROL,  
                    targetPosition=target,  
                    positionGain=joint_kp if joint_kp is not None else 0.3,  
                    velocityGain=joint_kd if joint_kd is not None else 1.0,  
                    force=self.joint_info[joint_id]['max_force']  
                )  
                  
    def get_joint_states(self):  
        """  
        Get current joint states  
          
        Returns:  
            dict: Dictionary of joint states  
        """  
        self.update_joint_states()  
        return self.joint_states  
          
    def get_joint_positions(self):  
        """  
        Get current joint positions  
          
        Returns:  
            dict: Dictionary mapping joint IDs to positions  
        """  
        self.update_joint_states()  
        return {i: state['position'] for i, state in self.joint_states.items()}  
          
    def get_joint_velocities(self):  
        """  
        Get current joint velocities  
          
        Returns:  
            dict: Dictionary mapping joint IDs to velocities  
        """  
        self.update_joint_states()  
        return {i: state['velocity'] for i, state in self.joint_states.items()}  
          
    def get_base_position_and_orientation(self):  
        """  
        Get the base position and orientation  
          
        Returns:  
            tuple: (position, orientation) as (list, list)  
        """  
        return p.getBasePositionAndOrientation(self.robot_id)  
          
    def get_base_velocity(self):  
        """  
        Get the base linear and angular velocity  
          
        Returns:  
            tuple: (linear_velocity, angular_velocity) as (list, list)  
        """  
        return p.getBaseVelocity(self.robot_id)  
          
    def get_link_state(self, link_name):  
        """  
        Get the state of a specific link  
          
        Args:  
            link_name (str): Name of the link  
              
        Returns:  
            dict: Link state information  
        """  
        link_id = self.link_name_to_id.get(link_name)  
        if link_id is not None:  
            state = p.getLinkState(self.robot_id, link_id, computeLinkVelocity=1)  
            return {  
                'position': state[0],  
                'orientation': state[1],  
                'local_position': state[2],  
                'local_orientation': state[3],  
                'world_linear_velocity': state[4],  
                'world_angular_velocity': state[5]  
            }  
        return None  
          
    def get_center_of_mass(self):  
        """  
        Calculate the center of mass of the robot  
          
        Returns:  
            list: [x, y, z] position of the center of mass  
        """  
        total_mass = 0  
        weighted_pos = np.zeros(3)  
          
        # Add base contribution  
        base_mass = 1.0  # Assuming base mass is 1.0 if not specified  
        base_pos, _ = self.get_base_position_and_orientation()  
        weighted_pos += np.array(base_pos) * base_mass  
        total_mass += base_mass  
          
        # Add link contributions  
        for i in range(self.num_joints):  
            link_state = p.getLinkState(self.robot_id, i)  
            link_mass = 0.1  # Assuming link mass is 0.1 if not specified  
            weighted_pos += np.array(link_state[0]) * link_mass  
            total_mass += link_mass  
              
        # Calculate COM  
        if total_mass > 0:  
            com = weighted_pos / total_mass  
            return com.tolist()  
        else:  
            return [0, 0, 0]  
              
    def get_support_polygon(self):  
        """
        Calculate the support polygon based on foot contacts  
        
        Returns:  
            list: List of [x, y] coordinates representing the support polygon vertices  
        """  
        # This is a simplified implementation  
        # In a real implementation, you would check for foot contacts and calculate the convex hull  
        
        # Get foot positions  
        left_foot_pos = None  
        right_foot_pos = None  
      
        if "left_foot" in self.link_name_to_id:  
            left_foot_state = self.get_link_state("left_foot")  
            if left_foot_state:  
                left_foot_pos = left_foot_state['position']  
                
        if "right_foot" in self.link_name_to_id:  
            right_foot_state = self.get_link_state("right_foot")  
            if right_foot_state:  
                right_foot_pos = right_foot_state['position']  
              
        # Create support polygon  
        if left_foot_pos and right_foot_pos:  
            # Simple rectangle approximation  
            length = 0.1  # Foot length  
            width = 0.06  # Foot width  
            
            # Left foot corners  
            lf_corners = [  
                [left_foot_pos[0] + length/2, left_foot_pos[1] + width/2],  
                [left_foot_pos[0] + length/2, left_foot_pos[1] - width/2],  
                [left_foot_pos[0] - length/2, left_foot_pos[1] - width/2],  
                [left_foot_pos[0] - length/2, left_foot_pos[1] + width/2]  
            ]  
            
            # Right foot corners  
            rf_corners = [  
                [right_foot_pos[0] + length/2, right_foot_pos[1] + width/2],  
                [right_foot_pos[0] + length/2, right_foot_pos[1] - width/2],  
                [right_foot_pos[0] - length/2, right_foot_pos[1] - width/2],  
                [right_foot_pos[0] - length/2, right_foot_pos[1] + width/2]  
            ]  
            
            # Combine all corners to form the support polygon  
            return lf_corners + rf_corners  
        elif left_foot_pos:  
            # Only left foot in contact  
            length = 0.1  
            width = 0.06  
            return [  
                [left_foot_pos[0] + length/2, left_foot_pos[1] + width/2],  
                [left_foot_pos[0] + length/2, left_foot_pos[1] - width/2],  
                [left_foot_pos[0] - length/2, left_foot_pos[1] - width/2],  
                [left_foot_pos[0] - length/2, left_foot_pos[1] + width/2]  
            ]  
        elif right_foot_pos:  
            # Only right foot in contact  
            length = 0.1  
            width = 0.06  
            return [  
                [right_foot_pos[0] + length/2, right_foot_pos[1] + width/2],  
                [right_foot_pos[0] + length/2, right_foot_pos[1] - width/2],  
                [right_foot_pos[0] - length/2, right_foot_pos[1] - width/2],  
                [right_foot_pos[0] - length/2, right_foot_pos[1] + width/2]  
            ]  
        else:  
            # No feet in contact  
            return []  
  
    def get_zero_moment_point(self):  
        """  
        Calculate the Zero Moment Point (ZMP) of the robot  
        
        Returns:  
            list: [x, y, z] position of the ZMP  
        """  
        # This is a simplified implementation  
        # In a real implementation, you would use force sensors and calculate the ZMP  
        
        # Get center of mass  
        com = self.get_center_of_mass()  
        
        # Get base velocity  
        linear_vel, _ = self.get_base_velocity()  
        
        # Simple ZMP calculation (assuming flat ground at z=0)  
        # ZMP = COM - (h/g) * COM_acceleration  
        # For simplicity, we use velocity as a proxy for acceleration  
        g = 9.81  # Gravity  
        h = com[2]  # Height of COM  
        
        if h > 0:  
            zmp_x = com[0] - (h/g) * linear_vel[0]  
            zmp_y = com[1] - (h/g) * linear_vel[1]  
            return [zmp_x, zmp_y, 0.0]  
        else:  
            return [com[0], com[1], 0.0]  
            
    def is_stable(self):  
        """  
        Check if the robot is stable (ZMP is inside the support polygon)  
        
        Returns:  
            bool: True if stable, False otherwise  
        """  
        # Get ZMP  
        zmp = self.get_zero_moment_point()  
        
        # Get support polygon  
        support_polygon = self.get_support_polygon()  
        
        # If no support polygon, robot is not stable  
        if not support_polygon:  
            return False  
            
        # Check if ZMP is inside the support polygon  
        # This is a simplified implementation using ray casting algorithm  
        x, y = zmp[0], zmp[1]  
        inside = False  
        
        j = len(support_polygon) - 1  
        for i in range(len(support_polygon)):  
            if ((support_polygon[i][1] > y) != (support_polygon[j][1] > y)) and (x < support_polygon[i][0] + (support_polygon[j][0] - support_polygon[i][0]) *   
                (y - support_polygon[i][1]) / (support_polygon[j][1] - support_polygon[i][1])):  
                inside = not inside  
            j = i  
            
        return inside  
        
    def get_joint_limits(self):  
        """  
        Get joint limits for all joints  
        
        Returns:  
            dict: Dictionary mapping joint IDs to (lower_limit, upper_limit) tuples  
        """  
        limits = {}  
        for joint_id, info in self.joint_info.items():  
            limits[joint_id] = (info['lower_limit'], info['upper_limit'])  
        return limits  
        
    def apply_external_force(self, link_name, force, position=None, frame=p.WORLD_FRAME):  
        """  
        Apply external force to a link  
        
        Args:  
            link_name (str): Name of the link  
            force (list): Force vector [x, y, z]  
            position (list, optional): Position to apply force. Defaults to link COM.  
            frame (int, optional): Coordinate frame. Defaults to WORLD_FRAME.  
        """  
        link_id = self.link_name_to_id.get(link_name)  
        if link_id is not None:  
            if position is None:  
                # Apply at center of mass  
                p.applyExternalForce(  
                    self.robot_id,  
                    link_id,  
                    force,  
                    [0, 0, 0],  # Apply at COM  
                    p.LINK_FRAME if frame == p.LINK_FRAME else p.WORLD_FRAME  
                )  
            else:  
                # Apply at specified position  
                p.applyExternalForce(  
                    self.robot_id,  
                    link_id,  
                    force,  
                    position,  
                    frame  
                )