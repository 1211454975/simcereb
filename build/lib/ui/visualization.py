# simcereb/ui/visualization.py  
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget  
from PyQt5.QtCore import Qt  
import matplotlib.pyplot as plt  
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  
from matplotlib.figure import Figure  
  
class DataVisualization(QWidget):  
    """  
    Data visualization component for displaying robot and simulation data  
    """  
      
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        main_layout = QVBoxLayout()  
          
        # Create tabs for different visualizations  
        self.tabs = QTabWidget()  
          
        # Joint positions tab  
        self.joint_pos_tab = QWidget()  
        joint_pos_layout = QVBoxLayout(self.joint_pos_tab)  
          
        # Create matplotlib figure for joint positions  
        self.joint_pos_figure = Figure(figsize=(5, 4), dpi=100)  
        self.joint_pos_canvas = FigureCanvas(self.joint_pos_figure)  
        joint_pos_layout.addWidget(self.joint_pos_canvas)  
          
        # Center of mass tab  
        self.com_tab = QWidget()  
        com_layout = QVBoxLayout(self.com_tab)  
          
        # Create matplotlib figure for center of mass  
        self.com_figure = Figure(figsize=(5, 4), dpi=100)  
        self.com_canvas = FigureCanvas(self.com_figure)  
        com_layout.addWidget(self.com_canvas)  
          
        # ZMP tab  
        self.zmp_tab = QWidget()  
        zmp_layout = QVBoxLayout(self.zmp_tab)  
          
        # Create matplotlib figure for ZMP  
        self.zmp_figure = Figure(figsize=(5, 4), dpi=100)  
        self.zmp_canvas = FigureCanvas(self.zmp_figure)  
        zmp_layout.addWidget(self.zmp_canvas)  
          
        # Add tabs  
        self.tabs.addTab(self.joint_pos_tab, "Joint Positions")  
        self.tabs.addTab(self.com_tab, "Center of Mass")  
        self.tabs.addTab(self.zmp_tab, "Zero Moment Point")  
          
        main_layout.addWidget(self.tabs)  
          
        self.setLayout(main_layout)  
          
        # Initialize plots  
        self._init_plots()  
          
    def _init_plots(self):  
        """Initialize the plots"""  
        # Joint positions plot  
        self.joint_pos_ax = self.joint_pos_figure.add_subplot(111)  
        self.joint_pos_ax.set_title('Joint Positions')  
        self.joint_pos_ax.set_xlabel('Time (s)')  
        self.joint_pos_ax.set_ylabel('Position (rad)')  
        self.joint_pos_figure.tight_layout()  
          
        # Center of mass plot  
        self.com_ax = self.com_figure.add_subplot(111)  
        self.com_ax.set_title('Center of Mass')  
        self.com_ax.set_xlabel('X (m)')  
        self.com_ax.set_ylabel('Y (m)')  
        self.com_ax.grid(True)  
        self.com_figure.tight_layout()  
          
        # ZMP plot  
        self.zmp_ax = self.zmp_figure.add_subplot(111)  
        self.zmp_ax.set_title('Zero Moment Point')  
        self.zmp_ax.set_xlabel('X (m)')  
        self.zmp_ax.set_ylabel('Y (m)')  
        self.zmp_ax.grid(True)  
        self.zmp_figure.tight_layout()  
          
    def update_data(self, engine):  
        """  
        Update the visualization with new data  
          
        Args:  
            engine: Simulation engine instance  
        """  
        if not engine or not engine.robots:  
            return  
              
        robot = engine.robots[0]  
          
        # Update joint positions plot  
        self._update_joint_positions(robot, engine.elapsed_time)  
          
        # Update center of mass plot  
        self._update_com(robot)  
          
        # Update ZMP plot  
        self._update_zmp(robot)  
          
    def _update_joint_positions(self, robot, time):  
        """Update joint positions plot"""  
        # Clear the plot  
        self.joint_pos_ax.clear()  
          
        # Get joint positions  
        joint_positions = robot.get_joint_positions()  
          
        # Plot only a subset of joints for clarity  
        selected_joints = {}  
        for joint_id, pos in joint_positions.items():  
            joint_name = robot.joint_info.get(joint_id, {}).get('name', f"Joint {joint_id}")  
            if 'knee' in joint_name or 'hip' in joint_name or 'ankle' in joint_name:  
                selected_joints[joint_name] = pos  
          
        # Plot joint positions  
        if selected_joints:  
            names = list(selected_joints.keys())  
            positions = list(selected_joints.values())  
            self.joint_pos_ax.bar(names, positions)  
            self.joint_pos_ax.set_title(f'Joint Positions at t={time:.2f}s')  
            self.joint_pos_ax.set_ylabel('Position (rad)')  
            self.joint_pos_ax.tick_params(axis='x', rotation=45)  
              
        self.joint_pos_figure.tight_layout()  
        self.joint_pos_canvas.draw()  
          
    def _update_com(self, robot):  
        """Update center of mass plot"""  
        # Clear the plot  
        self.com_ax.clear()  
          
        # Get center of mass  
        com = robot.get_center_of_mass()  
          
        # Get support polygon  
        support_polygon = robot.get_support_polygon()  
          
        # Plot support polygon  
        if support_polygon:  
            # Close the polygon  
            polygon = support_polygon + [support_polygon[0]]  
            xs, ys = zip(*polygon)  
            self.com_ax.plot(xs, ys, 'b-', label='Support Polygon')  
              
        # Plot center of mass  
        self.com_ax.plot(com[0], com[1], 'ro', label='CoM')  
          
        self.com_ax.set_title('Center of Mass and Support Polygon')  
        self.com_ax.set_xlabel('X (m)')  
        self.com_ax.set_ylabel('Y (m)')  
        self.com_ax.grid(True)  
        self.com_ax.legend()  
        self.com_ax.axis('equal')  
        self.com_figure.tight_layout()  
        self.com_canvas.draw()  
          
    def _update_zmp(self, robot):  
        """Update ZMP plot"""  
        # Clear the plot  
        self.zmp_ax.clear()  
          
        # Get ZMP  
        zmp = robot.get_zero_moment_point()  
          
        # Get support polygon  
        support_polygon = robot.get_support_polygon()  
          
        # Plot support polygon  
        if support_polygon:  
            # Close the polygon  
            polygon = support_polygon + [support_polygon[0]]  
            xs, ys = zip(*polygon)  
            self.zmp_ax.plot(xs, ys, 'b-', label='Support Polygon')  
              
        # Plot ZMP  
        self.zmp_ax.plot(zmp[0], zmp[1], 'go', label='ZMP')  
          
        # Get center of mass  
        com = robot.get_center_of_mass()  
          
        # Plot center of mass  
        self.zmp_ax.plot(com[0], com[1], 'ro', label='CoM')  
          
        self.zmp_ax.set_title('Zero Moment Point and Support Polygon')  
        self.zmp_ax.set_xlabel('X (m)')  
        self.zmp_ax.set_ylabel('Y (m)')  
        self.zmp_ax.grid(True)  
        self.zmp_ax.legend()  
        self.zmp_ax.axis('equal')  
        self.zmp_figure.tight_layout()  
        self.zmp_canvas.draw()