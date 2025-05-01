# simcereb/ui/research/environment_editor.py  
"""  
Environment editor for the Research Edition  
Provides tools for creating and editing simulation environments  
"""  
  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                            QLabel, QComboBox, QDoubleSpinBox, QListWidget,  
                            QGroupBox, QFormLayout, QTabWidget, QColorDialog,  
                            QListWidgetItem, QMenu, QAction, QMessageBox)  
from PyQt5.QtCore import Qt, pyqtSignal, QPoint  
from PyQt5.QtGui import QIcon, QColor, QPainter, QPixmap  
  
from ..common.version_ui import VersionSpecificWidget  
  
class EnvironmentEditor(VersionSpecificWidget):  
    """  
    Environment editor for creating and editing simulation environments  
    """  
      
    # Signals  
    environment_created = pyqtSignal(dict)  # Emitted when a new environment is created  
    environment_updated = pyqtSignal(dict)  # Emitted when an environment is updated  
      
    def __init__(self, version_manager, parent=None):  
        """  
        Initialize the environment editor  
          
        Args:  
            version_manager: VersionManager instance  
            parent: Parent widget  
        """  
        super().__init__(version_manager, parent)  
        self.current_environment = None  
        self.obstacles = []  
        self.sensors = []  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        # Main layout  
        main_layout = QVBoxLayout(self)  
          
        # Header  
        header_layout = QHBoxLayout()  
        title_label = QLabel("环境编辑器")  
        title_label.setFont(QFont("Arial", 18, QFont.Bold))  
        header_layout.addWidget(title_label)  
        header_layout.addStretch()  
          
        # Environment controls  
        new_button = QPushButton("新建环境")  
        new_button.clicked.connect(self.create_new_environment)  
        header_layout.addWidget(new_button)  
          
        save_button = QPushButton("保存环境")  
        save_button.clicked.connect(self.save_environment)  
        header_layout.addWidget(save_button)  
          
        load_button = QPushButton("加载环境")  
        load_button.clicked.connect(self.load_environment)  
        header_layout.addWidget(load_button)  
          
        main_layout.addLayout(header_layout)  
          
        # Main content - tabs for different aspects of the environment  
        self.tabs = QTabWidget()  
          
        # Terrain tab  
        terrain_tab = QWidget()  
        terrain_layout = QVBoxLayout(terrain_tab)  
          
        # Terrain type  
        terrain_group = QGroupBox("地形类型")  
        terrain_form = QFormLayout(terrain_group)  
          
        self.terrain_type_combo = QComboBox()  
        self.terrain_type_combo.addItems(["平地", "斜坡", "台阶", "不平整地面"])  
        self.terrain_type_combo.currentIndexChanged.connect(self.on_terrain_type_changed)  
        terrain_form.addRow("类型:", self.terrain_type_combo)  
          
        # Terrain parameters (will be updated based on selected type)  
        self.terrain_params_widget = QWidget()  
        self.terrain_params_layout = QFormLayout(self.terrain_params_widget)  
          
        terrain_layout.addWidget(terrain_group)  
        terrain_layout.addWidget(self.terrain_params_widget)  
        terrain_layout.addStretch()  
          
        # Obstacles tab  
        obstacles_tab = QWidget()  
        obstacles_layout = QVBoxLayout(obstacles_tab)  
          
        # Obstacle controls  
        obstacle_controls = QHBoxLayout()  
          
        self.obstacle_type_combo = QComboBox()  
        self.obstacle_type_combo.addItems(["盒子", "球体", "圆柱体", "自定义"])  
        obstacle_controls.addWidget(QLabel("类型:"))  
        obstacle_controls.addWidget(self.obstacle_type_combo)  
          
        add_obstacle_button = QPushButton("添加障碍物")  
        add_obstacle_button.clicked.connect(self.add_obstacle)  
        obstacle_controls.addWidget(add_obstacle_button)  
          
        obstacles_layout.addLayout(obstacle_controls)  
          
        # Obstacle list  
        self.obstacle_list = QListWidget()  
        self.obstacle_list.setContextMenuPolicy(Qt.CustomContextMenu)  
        self.obstacle_list.customContextMenuRequested.connect(self.show_obstacle_context_menu)  
        obstacles_layout.addWidget(self.obstacle_list)  
          
        # Sensors tab  
        sensors_tab = QWidget()  
        sensors_layout = QVBoxLayout(sensors_tab)  
          
        # Sensor controls  
        sensor_controls = QHBoxLayout()  
          
        self.sensor_type_combo = QComboBox()  
        self.sensor_type_combo.addItems(["相机", "激光雷达", "力传感器", "接触传感器"])  
        sensor_controls.addWidget(QLabel("类型:"))  
        sensor_controls.addWidget(self.sensor_type_combo)  
          
        add_sensor_button = QPushButton("添加传感器")  
        add_sensor_button.clicked.connect(self.add_sensor)  
        sensor_controls.addWidget(add_sensor_button)  
          
        sensors_layout.addLayout(sensor_controls)  
          
        # Sensor list  
        self.sensor_list = QListWidget()  
        self.sensor_list.setContextMenuPolicy(Qt.CustomContextMenu)  
        self.sensor_list.customContextMenuRequested.connect(self.show_sensor_context_menu)  
        sensors_layout.addWidget(self.sensor_list)  
          
        # Add tabs  
        self.tabs.addTab(terrain_tab, "地形")  
        self.tabs.addTab(obstacles_tab, "障碍物")  
        self.tabs.addTab(sensors_tab, "传感器")  
          
        main_layout.addWidget(self.tabs)  
          
        # Preview (placeholder for now)  
        preview_group = QGroupBox("预览")  
        preview_layout = QVBoxLayout(preview_group)  
        self.preview_label = QLabel("环境预览将在这里显示")  
        self.preview_label.setAlignment(Qt.AlignCenter)  
        self.preview_label.setMinimumHeight(200)  
        self.preview_label.setStyleSheet("background-color: #f0f0f0;")  
        preview_layout.addWidget(self.preview_label)  
          
        main_layout.addWidget(preview_group)  
          
        # Initialize terrain parameters for default terrain type  
        self.on_terrain_type_changed(0)  
      
    def on_terrain_type_changed(self, index):  
        """  
        Update terrain parameters based on selected terrain type  
          
        Args:  
            index (int): Index of the selected terrain type  
        """  
        # Clear existing parameters  
        while self.terrain_params_layout.count():  
            item = self.terrain_params_layout.takeAt(0)  
            if item.widget():  
                item.widget().deleteLater()  
          
        # Add parameters based on terrain type  
        if index == 0:  # 平地  
            # Flat terrain has minimal parameters  
            friction_spin = QDoubleSpinBox()  
            friction_spin.setRange(0.0, 1.0)  
            friction_spin.setValue(0.5)  
            friction_spin.setSingleStep(0.1)  
            self.terrain_params_layout.addRow("摩擦系数:", friction_spin)  
              
        elif index == 1:  # 斜坡  
            # Slope parameters  
            angle_spin = QDoubleSpinBox()  
            angle_spin.setRange(0.0, 45.0)  
            angle_spin.setValue(15.0)  
            angle_spin.setSingleStep(1.0)  
            self.terrain_params_layout.addRow("角度 (度):", angle_spin)  
              
            length_spin = QDoubleSpinBox()  
            length_spin.setRange(1.0, 20.0)  
            length_spin.setValue(5.0)  
            length_spin.setSingleStep(0.5)  
            self.terrain_params_layout.addRow("长度 (米):", length_spin)  
              
            friction_spin = QDoubleSpinBox()  
            friction_spin.setRange(0.0, 1.0)  
            friction_spin.setValue(0.5)  
            friction_spin.setSingleStep(0.1)  
            self.terrain_params_layout.addRow("摩擦系数:", friction_spin)  
              
        elif index == 2:  # 台阶  
            # Stairs parameters  
            step_height_spin = QDoubleSpinBox()  
            step_height_spin.setRange(0.01, 0.5)  
            step_height_spin.setValue(0.1)  
            step_height_spin.setSingleStep(0.01)  
            self.terrain_params_layout.addRow("台阶高度 (米):", step_height_spin)  
              
            step_width_spin = QDoubleSpinBox()  
            step_width_spin.setRange(0.1, 1.0)  
            step_width_spin.setValue(0.3)  
            step_width_spin.setSingleStep(0.05)  
            self.terrain_params_layout.addRow("台阶宽度 (米):", step_width_spin)  
              
            steps_spin = QDoubleSpinBox()  
            steps_spin.setRange(1, 20)  
            steps_spin.setValue(5)  
            steps_spin.setSingleStep(1)  
            steps_spin.setDecimals(0)  
            self.terrain_params_layout.addRow("台阶数量:", steps_spin)  
              
            friction_spin = QDoubleSpinBox()  
            friction_spin.setRange(0.0, 1.0)  
            friction_spin.setValue(0.5)  
            friction_spin.setSingleStep(0.1)  
            self.terrain_params_layout.addRow("摩擦系数:", friction_spin)  
              
        elif index == 3:  # 不平整地面  
            # Rough terrain parameters  
            roughness_spin = QDoubleSpinBox()  
            roughness_spin.setRange(0.01, 0.5)  
            roughness_spin.setValue(0.1)  
            roughness_spin.setSingleStep(0.01)  
            self.terrain_params_layout.addRow("粗糙度 (米):", roughness_spin)  
              
            seed_spin = QDoubleSpinBox()  
            seed_spin.setRange(0, 1000)  
            seed_spin.setValue(42)  
            seed_spin.setDecimals(0)  
            self.terrain_params_layout.addRow("随机种子:", seed_spin)  
              
            size_spin = QDoubleSpinBox()  
            size_spin.setRange(5.0, 50.0)  
            size_spin.setValue(10.0)  
            size_spin.setSingleStep(1.0)  
            self.terrain_params_layout.addRow("地形大小 (米):", size_spin)  
              
            friction_spin = QDoubleSpinBox()  
            friction_spin.setRange(0.0, 1.0)  
            friction_spin.setValue(0.5)  
            friction_spin.setSingleStep(0.1)  
            self.terrain_params_layout.addRow("摩擦系数:", friction_spin)  
      
    def create_new_environment(self):  
        """Create a new environment"""  
        # Reset current environment  
        self.current_environment = {  
            "name": "新环境",  
            "terrain": {  
                "type": "flat",  
                "parameters": {  
                    "friction": 0.5  
                }  
            },  
            "obstacles": [],  
            "sensors": []  
        }  
          
        # Reset UI  
        self.terrain_type_combo.setCurrentIndex(0)  
        self.obstacle_list.clear()  
        self.sensor_list.clear()  
        self.obstacles = []  
        self.sensors = []  
          
        # Update preview  
        self.update_preview()  
          
        # Emit signal  
        self.environment_created.emit(self.current_environment)  
      
    def save_environment(self):  
        """Save the current environment"""  
        if not self.current_environment:  
            QMessageBox.warning(self, "保存失败", "没有可保存的环境")  
            return  
              
        # Update environment data from UI  
        self._update_environment_from_ui()  
          
        # Show file dialog  
        options = QFileDialog.Options()  
        file_path, _ = QFileDialog.getSaveFileName(  
            self,  
            "保存环境",  
            "",  
            "环境文件 (*.env.json)",  
            options=options  
        )  
          
        if not file_path:  
            return  
              
        # Add extension if not present  
        if not file_path.endswith('.env.json'):  
            file_path += '.env.json'  
              
        # Save to file  
        try:  
            with open(file_path, 'w', encoding='utf-8') as f:  
                json.dump(self.current_environment, f, indent=2, ensure_ascii=False)  
            QMessageBox.information(self, "保存成功", f"环境已保存到: {file_path}")  
        except Exception as e:  
            QMessageBox.critical(self, "保存失败", f"保存环境时出错: {str(e)}")  
      
    def load_environment(self):  
        """Load an environment from file"""  
        # Show file dialog  
        options = QFileDialog.Options()  
        file_path, _ = QFileDialog.getOpenFileName(  
            self,  
            "加载环境",  
            "",  
            "环境文件 (*.env.json)",  
            options=options  
        )  
          
        if not file_path:  
            return  
              
        # Load from file  
        try:  
            with open(file_path, 'r', encoding='utf-8') as f:  
                environment = json.load(f)  
                  
            # Validate environment data  
            if not isinstance(environment, dict) or 'terrain' not in environment:  
                raise ValueError("无效的环境文件格式")  
                  
            # Set as current environment  
            self.current_environment = environment  
              
            # Update UI  
            self._update_ui_from_environment()  
              
            # Update preview  
            self.update_preview()  
              
            # Emit signal  
            self.environment_updated.emit(self.current_environment)  
              
            QMessageBox.information(self, "加载成功", f"环境已加载: {environment.get('name', '未命名')}")  
        except Exception as e:  
            QMessageBox.critical(self, "加载失败", f"加载环境时出错: {str(e)}")  
      
    def add_obstacle(self):  
        """Add a new obstacle to the environment"""  
        obstacle_type = self.obstacle_type_combo.currentText()  
          
        # Create obstacle data  
        obstacle = {  
            "type": obstacle_type,  
            "position": [0.0, 0.0, 0.0],  
            "size": [1.0, 1.0, 1.0],  
            "color": "#808080",  
            "rotation": [0.0, 0.0, 0.0]  
        }  
          
        # Add to list  
        self.obstacles.append(obstacle)  
          
        # Add to UI  
        item = QListWidgetItem(f"{obstacle_type} ({len(self.obstacles)})")  
        self.obstacle_list.addItem(item)  
          
        # Update preview  
        self.update_preview()  
      
    def add_sensor(self):  
        """Add a new sensor to the environment"""  
        sensor_type = self.sensor_type_combo.currentText()  
          
        # Create sensor data  
        sensor = {  
            "type": sensor_type,  
            "position": [0.0, 0.0, 0.0],  
            "rotation": [0.0, 0.0, 0.0]  
        }  
          
        # Add type-specific parameters  
        if sensor_type == "相机":  
            sensor["parameters"] = {  
                "resolution": [640, 480],  
                "field_of_view": 60.0,  
                "near_plane": 0.1,  
                "far_plane": 100.0  
            }  
        elif sensor_type == "激光雷达":  
            sensor["parameters"] = {  
                "range": 10.0,  
                "resolution": 1.0,  
                "scan_angle": 270.0,  
                "scan_rate": 10.0  
            }  
        elif sensor_type == "力传感器":  
            sensor["parameters"] = {  
                "max_force": 100.0,  
                "noise": 0.01  
            }  
        elif sensor_type == "接触传感器":  
            sensor["parameters"] = {  
                "threshold": 0.01,  
                "size": [0.1, 0.1, 0.01]  
            }  
          
        # Add to list  
        self.sensors.append(sensor)  
          
        # Add to UI  
        item = QListWidgetItem(f"{sensor_type} ({len(self.sensors)})")  
        self.sensor_list.addItem(item)  
          
        # Update preview  
        self.update_preview()  
      
    def show_obstacle_context_menu(self, position):  
        """Show context menu for obstacles"""  
        if self.obstacle_list.count() == 0:  
            return  
              
        # Get selected item  
        item = self.obstacle_list.itemAt(position)  
        if not item:  
            return  
              
        # Create menu  
        menu = QMenu()  
        edit_action = QAction("编辑", self)  
        delete_action = QAction("删除", self)  
          
        menu.addAction(edit_action)  
        menu.addAction(delete_action)  
          
        # Show menu and get selected action  
        action = menu.exec_(self.obstacle_list.mapToGlobal(position))  
          
        # Handle action  
        if action == edit_action:  
            self._edit_obstacle(self.obstacle_list.row(item))  
        elif action == delete_action:  
            self._delete_obstacle(self.obstacle_list.row(item))  
      
    def show_sensor_context_menu(self, position):  
        """Show context menu for sensors"""  
        if self.sensor_list.count() == 0:  
            return  
              
        # Get selected item  
        item = self.sensor_list.itemAt(position)  
        if not item:  
            return  
              
        # Create menu  
        menu = QMenu()  
        edit_action = QAction("编辑", self)  
        delete_action = QAction("删除", self)  
          
        menu.addAction(edit_action)  
        menu.addAction(delete_action)  
          
        # Show menu and get selected action  
        action = menu.exec_(self.sensor_list.mapToGlobal(position))  
          
        # Handle action  
        if action == edit_action:  
            self._edit_sensor(self.sensor_list.row(item))  
        elif action == delete_action:  
            self._delete_sensor(self.sensor_list.row(item))  
      
    def _edit_obstacle(self, index):  
        """  
        Edit an obstacle  
          
        Args:  
            index (int): Index of the obstacle to edit  
        """  
        # This would open a dialog to edit obstacle properties  
        # For now, just print a message  
        print(f"Editing obstacle {index}")  
      
    def _delete_obstacle(self, index):  
        """  
        Delete an obstacle  
          
        Args:  
            index (int): Index of the obstacle to delete  
        """  
        if 0 <= index < len(self.obstacles):  
            # Remove from list  
            self.obstacles.pop(index)  
              
            # Remove from UI  
            self.obstacle_list.takeItem(index)  
              
            # Update preview  
            self.update_preview()  
      
    def _edit_sensor(self, index):  
        """  
        Edit a sensor  
          
        Args:  
            index (int): Index of the sensor to edit  
        """  
        # This would open a dialog to edit sensor properties  
        # For now, just print a message  
        print(f"Editing sensor {index}")  
      
    def _delete_sensor(self, index):  
        """  
        Delete a sensor  
          
        Args:  
            index (int): Index of the sensor to delete  
        """  
        if 0 <= index < len(self.sensors):  
            # Remove from list  
            self.sensors.pop(index)  
              
            # Remove from UI  
            self.sensor_list.takeItem(index)  
              
            # Update preview  
            self.update_preview()  
      
    def _update_environment_from_ui(self):  
        """Update environment data from UI state"""  
        if not self.current_environment:  
            return  
              
        # Update terrain  
        terrain_type = self.terrain_type_combo.currentText()  
        terrain_params = {}  
          
        # Get terrain parameters from UI  
        for i in range(self.terrain_params_layout.rowCount()):  
            label_item = self.terrain_params_layout.itemAt(i, QFormLayout.LabelRole)  
            field_item = self.terrain_params_layout.itemAt(i, QFormLayout.FieldRole)  
              
            if label_item and field_item:  
                label = label_item.widget().text().rstrip(':')  
                field = field_item.widget()  
                  
                if isinstance(field, QDoubleSpinBox):  
                    # Convert label to parameter name  
                    param_name = label.lower().replace(' ', '_').replace('(米)', '').replace('(度)', '')  
                    terrain_params[param_name] = field.value()  
          
        # Update environment  
        self.current_environment["terrain"] = {  
            "type": terrain_type,  
            "parameters": terrain_params  
        }  
          
        # Update obstacles and sensors  
        self.current_environment["obstacles"] = self.obstacles  
        self.current_environment["sensors"] = self.sensors  
      
    def _update_ui_from_environment(self):  
        """Update UI state from environment data"""  
        if not self.current_environment:  
            return  
              
        # Update terrain UI  
        terrain = self.current_environment.get("terrain", {})  
        terrain_type = terrain.get("type", "flat")  
          
        # Find index of terrain type in combo box  
        for i in range(self.terrain_type_combo.count()):  
            if self.terrain_type_combo.itemText(i) == terrain_type:  
                self.terrain_type_combo.setCurrentIndex(i)  
                break  
          
        # Update terrain parameters  
        # This would need to be implemented based on the specific parameters for each terrain type  
          
        # Update obstacles  
        self.obstacles = self.current_environment.get("obstacles", [])  
        self.obstacle_list.clear()  
          
        for i, obstacle in enumerate(self.obstacles):  
            item = QListWidgetItem(f"{obstacle.get('type', 'Unknown')} ({i+1})")  
            self.obstacle_list.addItem(item)  
          
        # Update sensors  
        self.sensors = self.current_environment.get("sensors", [])  
        self.sensor_list.clear()  
          
        for i, sensor in enumerate(self.sensors):  
            item = QListWidgetItem(f"{sensor.get('type', 'Unknown')} ({i+1})")  
            self.sensor_list.addItem(item)  
      
    def update_preview(self):  
        """Update the environment preview"""  
        # This would generate a preview image of the environment  
        # For now, just update the label text  
        if self.current_environment:  
            terrain_type = self.current_environment.get("terrain", {}).get("type", "unknown")  
            num_obstacles = len(self.obstacles)  
            num_sensors = len(self.sensors)  
              
            self.preview_label.setText(  
                f"环境预览: {terrain_type} 地形, {num_obstacles} 个障碍物, {num_sensors} 个传感器"  
            )  
        else:  
            self.preview_label.setText("环境预览将在这里显示")