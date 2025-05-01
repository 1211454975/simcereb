# simcereb/ui/robot_view.py  
import os  
import numpy as np  
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QGroupBox  
from PyQt5.QtCore import Qt, QTimer  
from PyQt5.QtGui import QImage, QPixmap  
  
try:  
    import pybullet as p  
    from pybullet_utils import bullet_client  
except ImportError:  
    print("Warning: pybullet not found. Robot view will not work properly.")  
  
class RobotView(QWidget):  
    """  
    3D visualization of the robot using PyBullet's rendering capabilities  
    """  
      
    def __init__(self, engine, parent=None):  
        """  
        Initialize the robot view  
          
        Args:  
            engine: Simulation engine instance  
            parent: Parent widget  
        """  
        super().__init__(parent)  
        self.engine = engine  
        self.width = 640  
        self.height = 480  
        self.view_matrix = None  
        self.proj_matrix = None  
        self.camera_distance = 1.5  
        self.camera_yaw = 45  
        self.camera_pitch = -30  
        self.camera_target = [0, 0, 0]  
        self.init_ui()  
          
        # Create timer for updating the view  
        self.update_timer = QTimer(self)  
        self.update_timer.timeout.connect(self.update_view)  
        self.update_timer.start(50)  # 20 FPS  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        main_layout = QVBoxLayout()  
          
        # Image display  
        self.image_label = QLabel()  
        self.image_label.setMinimumSize(self.width, self.height)  
        self.image_label.setAlignment(Qt.AlignCenter)  
        main_layout.addWidget(self.image_label)  
          
        # Camera controls  
        camera_group = QGroupBox("Camera Controls")  
        camera_layout = QVBoxLayout(camera_group)  
          
        # Distance control  
        distance_layout = QHBoxLayout()  
        distance_layout.addWidget(QLabel("Distance:"))  
        self.distance_slider = QSlider(Qt.Horizontal)  
        self.distance_slider.setMinimum(10)  
        self.distance_slider.setMaximum(50)  
        self.distance_slider.setValue(int(self.camera_distance * 10))  
        self.distance_slider.valueChanged.connect(self.on_distance_changed)  
        distance_layout.addWidget(self.distance_slider)  
        camera_layout.addLayout(distance_layout)  
          
        # Yaw control  
        yaw_layout = QHBoxLayout()  
        yaw_layout.addWidget(QLabel("Yaw:"))  
        self.yaw_slider = QSlider(Qt.Horizontal)  
        self.yaw_slider.setMinimum(0)  
        self.yaw_slider.setMaximum(360)  
        self.yaw_slider.setValue(self.camera_yaw)  
        self.yaw_slider.valueChanged.connect(self.on_yaw_changed)  
        yaw_layout.addWidget(self.yaw_slider)  
        camera_layout.addLayout(yaw_layout)  
          
        # Pitch control  
        pitch_layout = QHBoxLayout()  
        pitch_layout.addWidget(QLabel("Pitch:"))  
        self.pitch_slider = QSlider(Qt.Horizontal)  
        self.pitch_slider.setMinimum(-89)  
        self.pitch_slider.setMaximum(89)  
        self.pitch_slider.setValue(self.camera_pitch)  
        self.pitch_slider.valueChanged.connect(self.on_pitch_changed)  
        pitch_layout.addWidget(self.pitch_slider)  
        camera_layout.addLayout(pitch_layout)  
          
        # Reset camera button  
        self.reset_button = QPushButton("Reset Camera")  
        self.reset_button.clicked.connect(self.reset_camera)  
        camera_layout.addWidget(self.reset_button)  
          
        main_layout.addWidget(camera_group)  
          
        self.setLayout(main_layout)  
          
    def on_distance_changed(self, value):  
        """Handle camera distance change"""  
        self.camera_distance = value / 10.0  
        self.update_view()  
          
    def on_yaw_changed(self, value):  
        """Handle camera yaw change"""  
        self.camera_yaw = value  
        self.update_view()  
          
    def on_pitch_changed(self, value):  
        """Handle camera pitch change"""  
        self.camera_pitch = value  
        self.update_view()  
          
    def reset_camera(self):  
        """Reset camera to default position"""  
        self.camera_distance = 1.5  
        self.camera_yaw = 45  
        self.camera_pitch = -30  
        self.camera_target = [0, 0, 0]  
          
        # Update sliders  
        self.distance_slider.setValue(int(self.camera_distance * 10))  
        self.yaw_slider.setValue(self.camera_yaw)  
        self.pitch_slider.setValue(self.camera_pitch)  
          
        self.update_view()  
          
    def update_camera_target(self):  
        """Update camera target to focus on the robot"""  
        if self.engine and self.engine.robots:  
            # Get the position of the first robot  
            robot = self.engine.robots[0]  
            base_pos, _ = robot.get_base_position_and_orientation()  
            self.camera_target = base_pos  
        else:  
            # Default target if no robot is loaded  
            self.camera_target = [0, 0, 0]  
              
    def update_view(self):  
        """Update the 3D view"""  
        if not self.engine or not hasattr(self.engine, 'physics_client'):  
            return  
              
        # Update camera target  
        self.update_camera_target()  
          
        # Compute view matrix  
        self.view_matrix = p.computeViewMatrixFromYawPitchRoll(  
            cameraTargetPosition=self.camera_target,  
            distance=self.camera_distance,  
            yaw=self.camera_yaw,  
            pitch=self.camera_pitch,  
            roll=0,  
            upAxisIndex=2  
        )  
          
        # Compute projection matrix  
        aspect = float(self.width) / float(self.height)  
        self.proj_matrix = p.computeProjectionMatrixFOV(  
            fov=60,  
            aspect=aspect,  
            nearVal=0.1,  
            farVal=100.0  
        )  
          
        # Get the rendered image  
        img_arr = p.getCameraImage(  
            width=self.width,  
            height=self.height,  
            viewMatrix=self.view_matrix,  
            projectionMatrix=self.proj_matrix,  
            renderer=p.ER_BULLET_HARDWARE_OPENGL  
        )  
          
        # Convert the image to QImage  
        w = img_arr[0]  # width  
        h = img_arr[1]  # height  
        rgb = img_arr[2]  # RGB data  
          
        # Convert RGB to QImage  
        qimg = QImage(rgb, w, h, QImage.Format_RGB888)  
          
        # Display the image  
        pixmap = QPixmap.fromImage(qimg)  
        self.image_label.setPixmap(pixmap)  
          
    def resizeEvent(self, event):  
        """Handle resize events"""  
        super().resizeEvent(event)  
          
        # Update image size  
        self.width = self.image_label.width()  
        self.height = self.image_label.height()  
          
        # Update view  
        self.update_view()