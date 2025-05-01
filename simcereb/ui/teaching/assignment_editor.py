# simcereb/ui/teaching/assignment_editor.py  
"""  
Assignment editor for the Teaching Edition  
Provides tools for creating and editing assignments  
"""  
  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                            QLabel, QLineEdit, QTextEdit, QDateEdit, QComboBox,  
                            QListWidget, QListWidgetItem, QGroupBox, QFormLayout,  
                            QSpinBox, QCheckBox, QTabWidget, QFileDialog, QMessageBox)  
from PyQt5.QtCore import Qt, pyqtSignal, QDate  
from PyQt5.QtGui import QFont, QIcon  
  
from ..common.version_ui import VersionSpecificWidget  
  
class AssignmentEditor(VersionSpecificWidget):  
    """  
    Assignment editor for creating and editing assignments  
    """  
      
    # Signals  
    assignment_created = pyqtSignal(dict)  # Emitted when a new assignment is created  
    assignment_updated = pyqtSignal(dict)  # Emitted when an assignment is updated  
      
    def __init__(self, version_manager, class_manager=None, parent=None):  
        """  
        Initialize the assignment editor  
          
        Args:  
            version_manager: VersionManager instance  
            class_manager: ClassManager instance for managing assignments  
            parent: Parent widget  
        """  
        super().__init__(version_manager, parent)  
        self.class_manager = class_manager  
        self.current_assignment = None  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        # Main layout  
        main_layout = QVBoxLayout(self)  
          
        # Header  
        header_layout = QHBoxLayout()  
        title_label = QLabel("作业编辑器")  
        title_label.setFont(QFont("Arial", 18, QFont.Bold))  
        header_layout.addWidget(title_label)  
        header_layout.addStretch()  
          
        # Assignment controls  
        new_button = QPushButton("新建作业")  
        new_button.clicked.connect(self.create_new_assignment)  
        header_layout.addWidget(new_button)  
          
        save_button = QPushButton("保存作业")  
        save_button.clicked.connect(self.save_assignment)  
        header_layout.addWidget(save_button)  
          
        main_layout.addLayout(header_layout)  
          
        # Main content - tabs for different aspects of the assignment  
        self.tabs = QTabWidget()  
          
        # Basic info tab  
        basic_tab = QWidget()  
        basic_layout = QFormLayout(basic_tab)  
          
        # Title  
        self.title_edit = QLineEdit()  
        basic_layout.addRow("标题:", self.title_edit)  
          
        # Description  
        self.description_edit = QTextEdit()  
        self.description_edit.setMaximumHeight(100)  
        basic_layout.addRow("描述:", self.description_edit)  
          
        # Due date  
        self.due_date_edit = QDateEdit()  
        self.due_date_edit.setCalendarPopup(True)  
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))  # Default to one week from now  
        basic_layout.addRow("截止日期:", self.due_date_edit)  
          
        # Class selection  
        self.class_combo = QComboBox()  
        self.populate_class_combo()  
        basic_layout.addRow("班级:", self.class_combo)  
          
        # Difficulty  
        self.difficulty_combo = QComboBox()  
        self.difficulty_combo.addItems(["简单", "中等", "困难"])  
        basic_layout.addRow("难度:", self.difficulty_combo)  
          
        # Points  
        self.points_spin = QSpinBox()  
        self.points_spin.setRange(1, 100)  
        self.points_spin.setValue(10)  
        basic_layout.addRow("分值:", self.points_spin)  
          
        # Tasks tab  
        tasks_tab = QWidget()  
        tasks_layout = QVBoxLayout(tasks_tab)  
          
        # Task controls  
        task_controls = QHBoxLayout()  
        add_task_button = QPushButton("添加任务")  
        add_task_button.clicked.connect(self.add_task)  
        task_controls.addWidget(add_task_button)  
          
        remove_task_button = QPushButton("删除任务")  
        remove_task_button.clicked.connect(self.remove_task)  
        task_controls.addWidget(remove_task_button)  
          
        task_controls.addStretch()  
          
        tasks_layout.addLayout(task_controls)  
          
        # Task list  
        self.task_list = QListWidget()  
        self.task_list.setSelectionMode(QListWidget.SingleSelection)  
        tasks_layout.addWidget(self.task_list)  
          
        # Task details  
        task_details_group = QGroupBox("任务详情")  
        task_details_layout = QFormLayout(task_details_group)  
          
        self.task_title_edit = QLineEdit()  
        task_details_layout.addRow("标题:", self.task_title_edit)  
          
        self.task_description_edit = QTextEdit()  
        task_details_layout.addRow("描述:", self.task_description_edit)  
          
        self.task_points_spin = QSpinBox()  
        self.task_points_spin.setRange(1, 100)  
        self.task_points_spin.setValue(5)  
        task_details_layout.addRow("分值:", self.task_points_spin)  
          
        self.task_auto_grade_check = QCheckBox("自动评分")  
        task_details_layout.addRow("", self.task_auto_grade_check)  
          
        update_task_button = QPushButton("更新任务")  
        update_task_button.clicked.connect(self.update_task)  
        task_details_layout.addRow("", update_task_button)  
          
        tasks_layout.addWidget(task_details_group)  

        #

    def load_assignment(self, assignment_id):  
        """  
        Load an existing assignment for editing  
          
        Args:  
            assignment_id (str): ID of the assignment to load  
        """  
        if self.class_manager:  
            assignment = self.class_manager.get_assignment(assignment_id)  
            if assignment:  
                self.current_assignment = assignment  
                self._update_ui_from_assignment()  
                return True  
        return False  
      
    def _update_ui_from_assignment(self):  
        """Update UI elements from the current assignment data"""  
        if not self.current_assignment:  
            return  
              
        # Update basic info  
        self.title_edit.setText(self.current_assignment.get("title", ""))  
        self.description_edit.setText(self.current_assignment.get("description", ""))  
          
        # Set due date  
        due_date_str = self.current_assignment.get("due_date", "")  
        if due_date_str:  
            try:  
                date_parts = due_date_str.split("-")  
                if len(date_parts) == 3:  
                    year, month, day = map(int, date_parts)  
                    self.due_date_edit.setDate(QDate(year, month, day))  
            except Exception as e:  
                print(f"Error parsing due date: {e}")  
          
        # Set class  
        class_id = self.current_assignment.get("class_id", "")  
        if class_id:  
            for i in range(self.class_combo.count()):  
                if self.class_combo.itemData(i) == class_id:  
                    self.class_combo.setCurrentIndex(i)  
                    break  
          
        # Set difficulty  
        difficulty = self.current_assignment.get("difficulty", "中等")  
        index = self.difficulty_combo.findText(difficulty)  
        if index >= 0:  
            self.difficulty_combo.setCurrentIndex(index)  
          
        # Set points  
        self.points_spin.setValue(self.current_assignment.get("points", 10))  
          
        # Load tasks  
        self.tasks = self.current_assignment.get("tasks", [])  
        self.task_list.clear()  
        for task in self.tasks:  
            self.task_list.addItem(task.get("title", "未命名任务"))  
          
        # Load resources  
        self.resources = self.current_assignment.get("resources", [])  
        self.resource_list.clear()  
        for resource in self.resources:  
            self.resource_list.addItem(resource.get("name", "未命名资源"))  
      
    def on_task_selected(self, current, previous):  
        """  
        Handle task selection change  
          
        Args:  
            current: Current selected item  
            previous: Previously selected item  
        """  
        if not current:  
            # Clear task details  
            self.task_title_edit.clear()  
            self.task_description_edit.clear()  
            self.task_points_spin.setValue(5)  
            self.task_auto_grade_check.setChecked(False)  
            return  
              
        # Get selected task  
        row = self.task_list.row(current)  
        if 0 <= row < len(self.tasks):  
            task = self.tasks[row]  
              
            # Update task details  
            self.task_title_edit.setText(task.get("title", ""))  
            self.task_description_edit.setText(task.get("description", ""))  
            self.task_points_spin.setValue(task.get("points", 5))  
            self.task_auto_grade_check.setChecked(task.get("auto_grade", False))  
      
    def export_assignment(self):  
        """Export the current assignment to a file"""  
        if not self.current_assignment:  
            QMessageBox.warning(self, "导出失败", "没有可导出的作业")  
            return  
              
        # Update assignment data from UI  
        self._update_assignment_from_ui()  
          
        # Show file dialog  
        options = QFileDialog.Options()  
        file_path, _ = QFileDialog.getSaveFileName(  
            self,  
            "导出作业",  
            "",  
            "JSON文件 (*.json)",  
            options=options  
        )  
          
        if not file_path:  
            return  
              
        # Add extension if not present  
        if not file_path.endswith('.json'):  
            file_path += '.json'  
              
        # Save to file  
        try:  
            with open(file_path, 'w', encoding='utf-8') as f:  
                json.dump(self.current_assignment, f, indent=2, ensure_ascii=False)  
            QMessageBox.information(self, "导出成功", f"作业已导出到: {file_path}")  
        except Exception as e:  
            QMessageBox.critical(self, "导出失败", f"导出作业时出错: {str(e)}")  
      
    def import_assignment(self):  
        """Import an assignment from a file"""  
        # Show file dialog  
        options = QFileDialog.Options()  
        file_path, _ = QFileDialog.getOpenFileName(  
            self,  
            "导入作业",  
            "",  
            "JSON文件 (*.json)",  
            options=options  
        )  
          
        if not file_path:  
            return  
              
        # Load from file  
        try:  
            with open(file_path, 'r', encoding='utf-8') as f:  
                assignment = json.load(f)  
                  
            # Validate assignment data  
            if not isinstance(assignment, dict) or 'title' not in assignment:  
                raise ValueError("无效的作业文件格式")  
                  
            # Set as current assignment  
            self.current_assignment = assignment  
              
            # Update UI  
            self._update_ui_from_assignment()  
              
            QMessageBox.information(self, "导入成功", f"作业已导入: {assignment.get('title', '未命名')}")  
        except Exception as e:  
            QMessageBox.critical(self, "导入失败", f"导入作业时出错: {str(e)}")  
      
    def preview_assignment(self):  
        """Preview the assignment as students would see it"""  
        if not self.current_assignment:  
            QMessageBox.warning(self, "预览失败", "没有可预览的作业")  
            return  
              
        # Update assignment data from UI  
        self._update_assignment_from_ui()  
          
        # Create and show preview dialog  
        preview_dialog = AssignmentPreviewDialog(self.current_assignment, self)  
        preview_dialog.exec_()  
      
    def duplicate_assignment(self):  
        """Create a duplicate of the current assignment"""  
        if not self.current_assignment:  
            QMessageBox.warning(self, "复制失败", "没有可复制的作业")  
            return  
              
        # Update assignment data from UI  
        self._update_assignment_from_ui()  
          
        # Create a copy  
        import copy  
        new_assignment = copy.deepcopy(self.current_assignment)  
          
        # Modify title to indicate it's a copy  
        new_assignment["title"] = f"{new_assignment.get('title', '')} (副本)"  
          
        # Set as current assignment  
        self.current_assignment = new_assignment  
          
        # Update UI  
        self._update_ui_from_assignment()  
          
        QMessageBox.information(self, "复制成功", "已创建作业副本")


class AssignmentPreviewDialog(QDialog):  
    """Dialog for previewing an assignment as students would see it"""  
      
    def __init__(self, assignment, parent=None):  
        super().__init__(parent)  
        self.assignment = assignment  
        self.setWindowTitle("作业预览")  
        self.setMinimumSize(600, 400)  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        layout = QVBoxLayout(self)  
          
        # Header  
        header_layout = QHBoxLayout()  
        title_label = QLabel(self.assignment.get("title", "未命名作业"))  
        title_label.setFont(QFont("Arial", 16, QFont.Bold))  
        header_layout.addWidget(title_label)  
          
        # Due date  
        due_date = self.assignment.get("due_date", "")  
        if due_date:  
            due_label = QLabel(f"截止日期: {due_date}")  
            due_label.setAlignment(Qt.AlignRight)  
            header_layout.addWidget(due_label)  
          
        layout.addLayout(header_layout)  
          
        # Description  
        description = self.assignment.get("description", "")  
        if description:  
            desc_group = QGroupBox("描述")  
            desc_layout = QVBoxLayout(desc_group)  
            desc_label = QLabel(description)  
            desc_label.setWordWrap(True)  
            desc_layout.addWidget(desc_label)  
            layout.addWidget(desc_group)  
          
        # Tasks  
        tasks = self.assignment.get("tasks", [])  
        if tasks:  
            tasks_group = QGroupBox(f"任务 (总分: {self.assignment.get('points', 0)}分)")  
            tasks_layout = QVBoxLayout(tasks_group)  
              
            for i, task in enumerate(tasks):  
                task_widget = QWidget()  
                task_layout = QVBoxLayout(task_widget)  
                  
                # Task header  
                task_header = QHBoxLayout()  
                task_title = QLabel(f"{i+1}. {task.get('title', '未命名任务')}")  
                task_title.setFont(QFont("Arial", 12, QFont.Bold))  
                task_header.addWidget(task_title)  
                  
                # Task points  
                points = task.get("points", 0)  
                points_label = QLabel(f"{points}分")  
                points_label.setAlignment(Qt.AlignRight)  
                task_header.addWidget(points_label)  
                  
                task_layout.addLayout(task_header)  
                  
                # Task description  
                task_desc = QLabel(task.get("description", ""))  
                task_desc.setWordWrap(True)  
                task_layout.addWidget(task_desc)  
                  
                tasks_layout.addWidget(task_widget)  
                  
                # Add separator if not the last task  
                if i < len(tasks) - 1:  
                    line = QFrame()  
                    line.setFrameShape(QFrame.HLine)  
                    line.setFrameShadow(QFrame.Sunken)  
                    tasks_layout.addWidget(line)  
              
            layout.addWidget(tasks_group)  
          
        # Resources  
        resources = self.assignment.get("resources", [])  
        if resources:  
            resources_group = QGroupBox("资源")  
            resources_layout = QVBoxLayout(resources_group)  
              
            for resource in resources:  
                resource_layout = QHBoxLayout()  
                  
                # Resource icon based on type  
                icon_label = QLabel()  
                resource_type = resource.get("type", "other")  
                if resource_type == "document":  
                    icon_label.setText("📄")  
                elif resource_type == "image":  
                    icon_label.setText("🖼️")  
                elif resource_type == "video":  
                    icon_label.setText("🎬")  
                elif resource_type == "code":  
                    icon_label.setText("💻")  
                else:  
                    icon_label.setText("📎")  
                  
                resource_layout.addWidget(icon_label)  
                  
                # Resource name  
                name_label = QLabel(resource.get("name", "未命名资源"))  
                resource_layout.addWidget(name_label)  
                resource_layout.addStretch()  
                  
                resources_layout.addLayout(resource_layout)  
              
            layout.addWidget(resources_group)  
          
        # Buttons  
        button_layout = QHBoxLayout()  
        button_layout.addStretch()  
          
        close_button = QPushButton("关闭")  
        close_button.clicked.connect(self.accept)  
        button_layout.addWidget(close_button)  
          
        layout.addLayout(button_layout)