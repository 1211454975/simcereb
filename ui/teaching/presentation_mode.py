# simcereb/ui/teaching/presentation_mode.py  
"""  
Presentation mode for the Teaching Edition  
Provides tools for classroom demonstrations and presentations  
"""  
  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                            QLabel, QToolBar, QAction, QSplitter, QComboBox,  
                            QCheckBox, QSlider, QGroupBox, QSpacerItem, QSizePolicy)  
from PyQt5.QtCore import Qt, pyqtSignal, QTimer  
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette  
  
from ..common.version_ui import VersionSpecificWidget  
  
class PresentationMode(VersionSpecificWidget):  
    """  
    Presentation mode for classroom demonstrations  
    """  
      
    # Signals  
    presentation_ended = pyqtSignal()  # Emitted when presentation is ended  
      
    def __init__(self, version_manager, simulation_engine=None, parent=None):  
        """  
        Initialize the presentation mode  
          
        Args:  
            version_manager: VersionManager instance  
            simulation_engine: SimulationEngine instance for controlling the simulation  
            parent: Parent widget  
        """  
        super().__init__(version_manager, parent)  
        self.simulation_engine = simulation_engine  
        self.is_recording = False  
        self.is_paused = False  
        self.annotations = []  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        # Set window to fullscreen or maximized  
        self.showMaximized()  
          
        # Use a dark palette for presentation mode  
        palette = QPalette()  
        palette.setColor(QPalette.Window, QColor(30, 30, 30))  
        palette.setColor(QPalette.WindowText, Qt.white)  
        palette.setColor(QPalette.Base, QColor(40, 40, 40))  
        palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))  
        palette.setColor(QPalette.Text, Qt.white)  
        palette.setColor(QPalette.Button, QColor(60, 60, 60))  
        palette.setColor(QPalette.ButtonText, Qt.white)  
        self.setPalette(palette)  
          
        # Main layout  
        main_layout = QVBoxLayout(self)  
        main_layout.setContentsMargins(0, 0, 0, 0)  
          
        # Toolbar  
        toolbar = QToolBar("Presentation Toolbar")  
        toolbar.setIconSize(QSize(32, 32))  
        toolbar.setMovable(False)  
          
        # Exit presentation mode  
        exit_action = QAction(QIcon.fromTheme("window-close"), "退出演示模式", self)  
        exit_action.triggered.connect(self.exit_presentation)  
        toolbar.addAction(exit_action)  
          
        toolbar.addSeparator()  
          
        # Playback controls  
        play_pause_action = QAction(QIcon.fromTheme("media-playback-pause"), "暂停", self)  
        play_pause_action.triggered.connect(self.toggle_play_pause)  
        toolbar.addAction(play_pause_action)  
          
        step_action = QAction(QIcon.fromTheme("media-skip-forward"), "单步执行", self)  
        step_action.triggered.connect(self.step_simulation)  
        toolbar.addAction(step_action)  
          
        reset_action = QAction(QIcon.fromTheme("media-playback-stop"), "重置", self)  
        reset_action.triggered.connect(self.reset_simulation)  
        toolbar.addAction(reset_action)  
          
        toolbar.addSeparator()  
          
        # Recording controls  
        self.record_action = QAction(QIcon.fromTheme("media-record"), "开始录制", self)  
        self.record_action.triggered.connect(self.toggle_recording)  
        toolbar.addAction(self.record_action)  
          
        toolbar.addSeparator()  
          
        # Annotation tools  
        annotation_label = QLabel("注释工具:")  
        toolbar.addWidget(annotation_label)  
          
        self.annotation_type_combo = QComboBox()  
        self.annotation_type_combo.addItems(["箭头", "文本", "圆形", "矩形", "自由绘制"])  
        toolbar.addWidget(self.annotation_type_combo)  
          
        add_annotation_action = QAction(QIcon.fromTheme("list-add"), "添加注释", self)  
        add_annotation_action.triggered.connect(self.add_annotation)  
        toolbar.addAction(add_annotation_action)  
          
        clear_annotations_action = QAction(QIcon.fromTheme("edit-clear"), "清除注释", self)  
        clear_annotations_action.triggered.connect(self.clear_annotations)  
        toolbar.addAction(clear_annotations_action)  
          
        # Add toolbar to layout  
        main_layout.addWidget(toolbar)  
          
        # Main content  
        content_splitter = QSplitter(Qt.Horizontal)  
          
        # Simulation view (main view)  
        self.simulation_view = QWidget()  
        simulation_layout = QVBoxLayout(self.simulation_view)  
        simulation_layout.setContentsMargins(0, 0, 0, 0)  
          
        # Placeholder for simulation view  
        self.simulation_placeholder = QLabel("模拟视图")  
        self.simulation_placeholder.setAlignment(Qt.AlignCenter)  
        self.simulation_placeholder.setStyleSheet("font-size: 24pt; color: white;")  
        self.simulation_placeholder.setMinimumSize(800, 600)  
        simulation_layout.addWidget(self.simulation_placeholder)  
          
        content_splitter.addWidget(self.simulation_view)  
          
        # Controls panel (right side)  
        controls_panel = QWidget()  
        controls_layout = QVBoxLayout(controls_panel)  
          
        # Simulation parameters  
        params_group = QGroupBox("模拟参数")  
        params_layout = QVBoxLayout(params_group)  
          
        # Speed control  
        speed_layout = QHBoxLayout()  
        speed_layout.addWidget(QLabel("速度:"))  
          
        self.speed_slider = QSlider(Qt.Horizontal)  
        self.speed_slider.setRange(10, 200)  
        self.speed_slider.setValue(100)  
        self.speed_slider.setTickPosition(QSlider.TicksBelow)  
        self.speed_slider.setTickInterval(10)  
        self.speed_slider.valueChanged.connect(self.set_simulation_speed)  
        speed_layout.addWidget(self.speed_slider)  
          
        self.speed_label = QLabel("100%")  
        speed_layout.addWidget(self.speed_label)  
          
        params_layout.addLayout(speed_layout)  
          
        # Visibility options  
        self.show_forces_check = QCheckBox("显示力")  
        self.show_forces_check.toggled.connect(self.toggle_forces_visibility)  
        params_layout.addWidget(self.show_forces_check)  
          
        # self.show


        self.show_trajectories_check = QCheckBox("显示轨迹")  
        self.show_trajectories_check.toggled.connect(self.toggle_trajectories_visibility)  
        params_layout.addWidget(self.show_trajectories_check)  
          
        self.show_sensors_check = QCheckBox("显示传感器数据")  
        self.show_sensors_check.toggled.connect(self.toggle_sensors_visibility)  
        params_layout.addWidget(self.show_sensors_check)  
          
        controls_layout.addWidget(params_group)  
          
        # Notes section  
        notes_group = QGroupBox("教学笔记")  
        notes_layout = QVBoxLayout(notes_group)  
          
        self.notes_edit = QTextEdit()  
        self.notes_edit.setPlaceholderText("在此处添加教学笔记...")  
        notes_layout.addWidget(self.notes_edit)  
          
        controls_layout.addWidget(notes_group)  
          
        content_splitter.addWidget(controls_panel)  
          
        # Set initial sizes for the splitter  
        content_splitter.setSizes([700, 300])  
          
        main_layout.addWidget(content_splitter)  
          
        # Status bar  
        status_layout = QHBoxLayout()  
        self.status_label = QLabel("就绪")  
        status_layout.addWidget(self.status_label)  
          
        # Timer display  
        self.timer_label = QLabel("00:00")  
        self.timer_label.setAlignment(Qt.AlignRight)  
        status_layout.addWidget(self.timer_label)  
          
        main_layout.addLayout(status_layout)  
          
        # Initialize timer  
        self.timer = QTimer(self)  
        self.timer.timeout.connect(self.update_timer)  
        self.elapsed_time = 0  
          
        # Start in paused state  
        self.is_paused = True  
      
    def exit_presentation(self):  
        """Exit presentation mode"""  
        # Stop timer and recording if active  
        self.timer.stop()  
        if self.is_recording:  
            self.toggle_recording()  
          
        # Emit signal to notify parent  
        self.presentation_ended.emit()  
          
        # Close the window  
        self.close()  
      
    def toggle_play_pause(self):  
        """Toggle between play and pause states"""  
        if self.is_paused:  
            # Resume simulation  
            if self.simulation_engine:  
                self.simulation_engine.resume()  
              
            # Start timer  
            self.timer.start(1000)  # Update every second  
              
            # Update UI  
            self.is_paused = False  
            self.status_label.setText("运行中")  
              
            # Update button text  
            sender = self.sender()  
            if isinstance(sender, QAction):  
                sender.setText("暂停")  
                sender.setIcon(QIcon.fromTheme("media-playback-pause"))  
        else:  
            # Pause simulation  
            if self.simulation_engine:  
                self.simulation_engine.pause()  
              
            # Stop timer  
            self.timer.stop()  
              
            # Update UI  
            self.is_paused = True  
            self.status_label.setText("已暂停")  
              
            # Update button text  
            sender = self.sender()  
            if isinstance(sender, QAction):  
                sender.setText("继续")  
                sender.setIcon(QIcon.fromTheme("media-playback-start"))  
      
    def step_simulation(self):  
        """Execute a single step in the simulation"""  
        if self.simulation_engine:  
            # Ensure simulation is paused  
            if not self.is_paused:  
                self.toggle_play_pause()  
              
            # Execute a single step  
            self.simulation_engine.step()  
              
            # Update status  
            self.status_label.setText("执行单步")  
      
    def reset_simulation(self):  
        """Reset the simulation to initial state"""  
        if self.simulation_engine:  
            # Reset simulation  
            self.simulation_engine.reset()  
              
            # Reset timer  
            self.elapsed_time = 0  
            self.timer_label.setText("00:00")  
              
            # Ensure simulation is paused  
            if not self.is_paused:  
                self.toggle_play_pause()  
              
            # Update status  
            self.status_label.setText("已重置")  
              
            # Clear annotations  
            self.clear_annotations()  
      
    def toggle_recording(self):  
        """Toggle recording state"""  
        if not self.is_recording:  
            # Start recording  
            if self.simulation_engine:  
                self.simulation_engine.start_recording()  
              
            # Update UI  
            self.is_recording = True  
            self.status_label.setText("录制中...")  
              
            # Update button text  
            sender = self.sender()  
            if isinstance(sender, QAction):  
                sender.setText("停止录制")  
                sender.setIcon(QIcon.fromTheme("media-playback-stop"))  
        else:  
            # Stop recording  
            if self.simulation_engine:  
                recording_path = self.simulation_engine.stop_recording()  
                  
                # Show save dialog  
                if recording_path:  
                    QMessageBox.information(  
                        self,  
                        "录制完成",  
                        f"录制已保存到: {recording_path}"  
                    )  
              
            # Update UI  
            self.is_recording = False  
            self.status_label.setText("录制已停止")  
              
            # Update button text  
            sender = self.sender()  
            if isinstance(sender, QAction):  
                sender.setText("开始录制")  
                sender.setIcon(QIcon.fromTheme("media-record"))  
      
    def add_annotation(self):  
        """Add an annotation to the simulation view"""  
        annotation_type = self.annotation_type_combo.currentText()  
          
        if annotation_type == "文本":  
            # Show dialog to get text  
            text, ok = QInputDialog.getText(self, "添加文本注释", "文本内容:")  
            if ok and text:  
                # This would create a text annotation in the simulation view  
                self.annotations.append({  
                    "type": "text",  
                    "text": text,  
                    "position": [0.5, 0.5],  # Center of the view  
                    "color": "#FFFFFF"  
                })  
                self.status_label.setText(f"已添加文本注释: {text}")  
        else:  
            # For other annotation types, enable drawing mode  
            self.status_label.setText(f"请在模拟视图中绘制 {annotation_type}")  
            # This would enable drawing mode in the simulation view  
      
    def clear_annotations(self):  
        """Clear all annotations"""  
        self.annotations = []  
        # This would clear annotations from the simulation view  
        self.status_label.setText("已清除所有注释")  
      
    def set_simulation_speed(self, value):  
        """  
        Set the simulation speed  
          
        Args:  
            value (int): Speed value (percentage)  
        """  
        if self.simulation_engine:  
            # Convert percentage to factor (100% = 1.0)  
            speed_factor = value / 100.0  
            self.simulation_engine.set_speed(speed_factor)  
          
        # Update label  
        self.speed_label.setText(f"{value}%")  
          
        # Update status  
        self.status_label.setText(f"速度已设置为 {value}%")  
      
    def toggle_forces_visibility(self, checked):  
        """  
        Toggle visibility of forces in the simulation  
          
        Args:  
            checked (bool): Whether forces should be visible  
        """  
        if self.simulation_engine:  
            self.simulation_engine.set_forces_visible(checked)  
          
        # Update status  
        status = "显示" if checked else "隐藏"  
        self.status_label.setText(f"力向量已{status}")  
      
    def toggle_trajectories_visibility(self, checked):  
        """  
        Toggle visibility of trajectories in the simulation  
          
        Args:  
            checked (bool): Whether trajectories should be visible  
        """  
        if self.simulation_engine:  
            self.simulation_engine.set_trajectories_visible(checked)  
          
        # Update status  
        status = "显示" if checked else "隐藏"  
        self.status_label.setText(f"轨迹已{status}")  
      
    def toggle_sensors_visibility(self, checked):  
        """  
        Toggle visibility of sensor data in the simulation  
          
        Args:  
            checked (bool): Whether sensor data should be visible  
        """  
        if self.simulation_engine:  
            self.simulation_engine.set_sensors_visible(checked)  
          
        # Update status  
        status = "显示" if checked else "隐藏"  
        self.status_label.setText(f"传感器数据已{status}")  
      
    def update_timer(self):  
        """Update the timer display"""  
        self.elapsed_time += 1  
        minutes = self.elapsed_time // 60  
        seconds = self.elapsed_time % 60  
        self.timer_label.setText(f"{minutes:02d}