# simcereb/ui/teaching/class_manager_ui.py  
"""  
Class manager UI for the Teaching Edition  
Provides tools for managing classes and students  
"""  
  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                            QLabel, QTableWidget, QTableWidgetItem, QHeaderView,  
                            QDialog, QLineEdit, QFormLayout, QDialogButtonBox,  
                            QTabWidget, QMessageBox, QComboBox, QDateEdit)  
from PyQt5.QtCore import Qt, pyqtSignal, QDate  
from PyQt5.QtGui import QFont, QIcon  
  
from ..common.version_ui import VersionSpecificWidget  
  
class AddStudentDialog(QDialog):  
    """Dialog for adding a new student"""  
      
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.setWindowTitle("添加学生")  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        layout = QFormLayout(self)  
          
        # Student name  
        self.name_edit = QLineEdit()  
        layout.addRow("姓名:", self.name_edit)  
          
        # Student ID  
        self.id_edit = QLineEdit()  
        layout.addRow("学号:", self.id_edit)  
          
        # Email  
        self.email_edit = QLineEdit()  
        layout.addRow("邮箱:", self.email_edit)  
          
        # Buttons  
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  
        button_box.accepted.connect(self.accept)  
        button_box.rejected.connect(self.reject)  
        layout.addRow(button_box)  
      
    def get_student_data(self):  
        """Get the entered student data"""  
        return {  
            "name": self.name_edit.text(),  
            "id": self.id_edit.text(),  
            "email": self.email_edit.text()  
        }
    

class AddAssignmentDialog(QDialog):  
    """Dialog for adding a new assignment"""  
      
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.setWindowTitle("添加作业")  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        layout = QFormLayout(self)  
          
        # Assignment title  
        self.title_edit = QLineEdit()  
        layout.addRow("标题:", self.title_edit)  
          
        # Description  
        self.description_edit = QLineEdit()  
        layout.addRow("描述:", self.description_edit)  
          
        # Due date  
        self.due_date_edit = QDateEdit()  
        self.due_date_edit.setCalendarPopup(True)  
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))  # Default to one week from now  
        layout.addRow("截止日期:", self.due_date_edit)  
          
        # Buttons  
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  
        button_box.accepted.connect(self.accept)  
        button_box.rejected.connect(self.reject)  
        layout.addRow(button_box)  
      
    def get_assignment_data(self):  
        """Get the entered assignment data"""  
        return {  
            "title": self.title_edit.text(),  
            "description": self.description_edit.text(),  
            "due_date": self.due_date_edit.date().toString("yyyy-MM-dd")  
        }



class ClassManagerUI(VersionSpecificWidget):  
    """  
    Class manager UI for the Teaching Edition  
    Provides tools for managing classes and students  
    """  
      
    def __init__(self, version_manager, class_manager=None, parent=None):  
        """  
        Initialize the class manager UI  
          
        Args:  
            version_manager: VersionManager instance  
            class_manager: ClassManager instance for managing classes and students  
            parent: Parent widget  
        """  
        super().__init__(version_manager, parent)  
        self.class_manager = class_manager  
        self.current_class_id = None  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        # Main layout  
        main_layout = QVBoxLayout(self)  
          
        # Header  
        header_layout = QHBoxLayout()  
        title_label = QLabel("班级管理")  
        title_label.setFont(QFont("Arial", 18, QFont.Bold))  
        header_layout.addWidget(title_label)  
        header_layout.addStretch()  
          
        # Class controls  
        self.class_selector = QComboBox()  
        self.class_selector.setMinimumWidth(200)  
        self.class_selector.currentIndexChanged.connect(self.on_class_selected)  
        header_layout.addWidget(QLabel("班级:"))  
        header_layout.addWidget(self.class_selector)  
          
        add_class_button = QPushButton("新建班级")  
        add_class_button.clicked.connect(self.add_class)  
        header_layout.addWidget(add_class_button)  
          
        main_layout.addLayout(header_layout)  
          
        # Tabs for different aspects of class management  
        self.tabs = QTabWidget()  
          
        # Students tab  
        students_tab = QWidget()  
        students_layout = QVBoxLayout(students_tab)  
          
        # Student controls  
        student_controls = QHBoxLayout()  
        add_student_button = QPushButton("添加学生")  
        add_student_button.clicked.connect(self.add_student)  
        student_controls.addWidget(add_student_button)  
          
        remove_student_button = QPushButton("移除学生")  
        remove_student_button.clicked.connect(self.remove_student)  
        student_controls.addWidget(remove_student_button)  
          
        student_controls.addStretch()  
          
        students_layout.addLayout(student_controls)  
          
        # Student table  
        self.student_table = QTableWidget()  
        self.student_table.setColumnCount(4)  
        self.student_table.setHorizontalHeaderLabels(["姓名", "学号", "邮箱", "进度"])  
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        self.student_table.setSelectionBehavior(QTableWidget.SelectRows)  
        students_layout.addWidget(self.student_table)  
          
        # Assignments tab  
        assignments_tab = QWidget()  
        assignments_layout = QVBoxLayout(assignments_tab)  
          
        # Assignment controls  
        assignment_controls = QHBoxLayout()  
        add_assignment_button = QPushButton("添加作业")  
        add_assignment_button.clicked.connect(self.add_assignment)  
        assignment_controls.addWidget(add_assignment_button)  
          
        remove_assignment_button = QPushButton("删除作业")  
        remove_assignment_button.clicked.connect(self.remove_assignment)  
        assignment_controls.addWidget(remove_assignment_button)  
          
        assignment_controls.addStretch()  
          
        assignments_layout.addLayout(assignment_controls)  
          
        # Assignment table  
        self.assignment_table = QTableWidget()  
        self.assignment_table.setColumnCount(4)  
        self.assignment_table.setHorizontalHeaderLabels(["标题", "描述", "截止日期", "完成率"])  
        self.assignment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        self.assignment_table.setSelectionBehavior(QTableWidget.SelectRows)  
        assignments_layout.addWidget(self.assignment_table)  
          
        # Progress tab  
        progress_tab = QWidget()  
        progress_layout = QVBoxLayout(progress_tab)  
          
        # Progress overview  
        progress_overview = QGroupBox("班级进度概览")  
        progress_overview_layout = QVBoxLayout(progress_overview)  
          
        self.overall_progress_bar = QProgressBar()  
        self.overall_progress_bar.setRange(0, 100)  
        self.overall_progress_bar.setValue(0)  
        progress_overview_layout.addWidget(self.overall_progress_bar)  
          
        self.progress_label = QLabel("班级平均进度: 0%")  
        progress_overview_layout.addWidget(self.progress_label)  
          
        progress_layout.addWidget(progress_overview)  
          
        # Progress details table  
        self.progress_table = QTableWidget()  
        self.progress_table.setColumnCount(5)  
        self.progress_table.setHorizontalHeaderLabels(["学生", "已完成教程", "已完成作业", "技能等级", "总进度"])  
        self.progress_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        progress_layout.addWidget(self.progress_table)  
          
        # Add tabs  
        self.tabs.addTab(students_tab, "学生")  
        self.tabs.addTab(assignments_tab, "作业")  
        self.tabs.addTab(progress_tab, "进度")  
          
        main_layout.addWidget(self.tabs)  
          
        # Populate class selector  
        self.refresh_class_list()  
      
    def refresh_class_list(self):  
        """Refresh the class list"""  
        self.class_selector.clear()  
          
        if self.class_manager:  
            classes = self.class_manager.get_classes()  
            for class_id, class_info in classes.items():  
                self.class_selector.addItem(class_info.get("name", "未命名班级"), class_id)  
        else:  
            # Add sample classes for demonstration  
            self.class_selector.addItem("示例班级 1", "sample1")  
            self.class_selector.addItem("示例班级 2", "sample2")  
      
    def on_class_selected(self, index):  
        """  
        Handle class selection  
          
        Args:  
            index (int): Index of the selected class  
        """  
        if index < 0:  
            self.current_class_id = None  
            return  
              
        self.current_class_id = self.class_selector.itemData(index)  
        self.refresh_class_data()  
      
    def refresh_class_data(self):  
        """Refresh all data for the current class"""  
        if not self.current_class_id:  
            # Clear all tables  
            self.student_table.setRowCount(0)  
            self.assignment_table.setRowCount(0)  
            self.progress_table.setRowCount(0)  
            self.overall_progress_bar.setValue(0)  
            self.progress_label.setText("班级平均进度: 0%")  
            return  
              
        # Refresh student table  
        self.refresh_student_table()  
          
        # Refresh assignment table  
        self.refresh_assignment_table()  
          
        # Refresh progress table  
        self.refresh_progress_table()  
      
    def refresh_student_table(self):  
        """Refresh the student table for the current class"""  
        self.student_table.setRowCount(0)  
          
        if self.class_manager:  
            students = self.class_manager.get_students_in_class(self.current_class_id)  
            for i, (student_id, student_info) in enumerate(students.items()):  
                self.student_table.insertRow(i)  
                self.student_table.setItem(i, 0, QTableWidgetItem(student_info.get("name", "")))  
                self.student_table.setItem(i, 1, QTableWidgetItem(student_info.get("id", "")))  
                self.student_table.setItem(i, 2, QTableWidgetItem(student_info.get("email", "")))  
                  
                # Calculate progress  
                progress = student_info.get("progress", {}).get("overall", 0)  
                progress_item = QTableWidgetItem(f"{int(progress * 100)}%")  
                self.student_table.setItem(i, 3, progress_item)  
        else:  
            # Add sample data for demonstration  
            sample_students = [  
                {"name": "张三", "id": "2023001", "email": "zhang@example.com", "progress": 0.8},  
                {"name": "李四", "id": "2023002", "email": "li@example.com", "progress": 0.6},  
                {"name": "王五", "id": "2023003", "email": "wang@example.com", "progress": 0.4},  
                {"name": "赵六", "id": "2023004", "email": "zhao@example.com", "progress": 0.2}  
            ]  
              
            for i, student in enumerate(sample_students):  
                self.student_table.insertRow(i)  
                self.student_table.setItem(i, 0, QTableWidgetItem(student["name"]))  
                self.student_table.setItem(i, 1, QTableWidgetItem(student["id"]))  
                self.student_table.setItem(i, 2, QTableWidgetItem(student["email"]))  
                  
                progress_item = QTableWidgetItem(f"{int(student['progress'] * 100)}%")  
                self.student_table.setItem(i, 3, progress_item)  
      
    def refresh_assignment_table(self):  
        """Refresh the assignment table for the current class"""  
        self.assignment_table.setRowCount(0)  
          
        if self.class_manager:  
            assignments = self.class_manager.get_assignments_for_class(self.current_class_id)  
            for i, (assignment_id, assignment_info) in enumerate(assignments.items()):  
                self.assignment_table.insertRow(i)  
                self.assignment_table.setItem(i, 0, QTableWidgetItem(assignment_info.get("title", "")))  
                self.assignment_table.setItem(i, 1, QTableWidgetItem(assignment_info.get("description", "")))  
                self.assignment_table.setItem(i, 2, QTableWidgetItem(assignment_info.get("due_date", "")))  
                  
                # Calculate completion rate  
                completion_rate = assignment_info.get("completion_rate", 0)  
                completion_item = QTableWidgetItem(f"{int(completion_rate * 100)}%")  
                self.assignment_table.setItem(i, 3, completion_item)  
        else:  
            # Add sample data for demonstration  
            sample_assignments = [  
                {"title": "平衡控制实验", "description": "实现基本的平衡控制算法", "due_date": "2025-05-15", "completion_rate": 0.75},  
                {"title": "步态生成实验", "description": "实现基本的步态生成算法", "due_date": "2025-05-30", "completion_rate": 0.5},  
                {"title": "传感器融合实验", "description": "实现基本的传感器融合算法", "due_date": "2025-06-15", "completion_rate": 0.25}  
            ]  
              
            for i, assignment in enumerate(sample_assignments):  
                self.assignment_table.insertRow(i)  
                self.assignment_table.setItem(i, 0, QTableWidgetItem(assignment["title"]))  
                self.assignment_table.setItem(i, 1, QTableWidgetItem(assignment["description"]))  
                self.assignment_table.setItem(i, 2, QTableWidgetItem(assignment["due_date"]))  
                  
                completion_item = QTableWidgetItem(f"{int(assignment['completion_rate'] * 100)}%")  
                self.assignment_table.setItem(i, 3, completion_item)  
      
    def refresh_progress_table(self):  
        """Refresh the progress table for the current class"""  
        self.progress_table.setRowCount(0)  
          
        if self.class_manager:  
            students = self.class_manager.get_students_in_class(self.current_class_id)  
            total_progress = 0  
              
            for i, (student_id, student_info) in enumerate(students.items()):  
                self.progress_table.insertRow(i)  
                self.progress_table.setItem(i, 0, QTableWidgetItem(student_info.get("name", "")))  
                  
                # Calculate progress details  
                progress = student_info.get("progress", {})  
                tutorials_progress = progress.get("tutorials", 0)  
                assignments_progress = progress.get("assignments", 0)  
                skills_level = progress.get("skills", 0)  
                overall_progress = progress.get("overall", 0)  
                  
                # Add to table  
                self.progress_table.setItem(i, 1, QTableWidgetItem(f"{int(tutorials_progress * 100)}%"))  
                self.progress_table.setItem(i, 2, QTableWidgetItem(f"{int(assignments_progress * 100)}%"))  
                self.progress_table.setItem(i, 3, QTableWidgetItem(f"{skills_level}/5"))  
                self.progress_table.setItem(i, 4, QTableWidgetItem(f"{int(overall_progress * 100)}%"))  
                  
                total_progress += overall_progress  
              
            # Update overall progress  
            if len(students) > 0:  
                avg_progress = total_progress / len(students)  
                self.overall_progress_bar.setValue(int(avg_progress * 100))  
                self.progress_label.setText(f"班级平均进度: {int(avg_progress * 100)}%")  
        else:  
            # Add sample data for demonstration  
            sample_progress = [  
                {"name": "张三", "tutorials": 0.9, "assignments": 0.8, "skills": 4, "overall": 0.85},  
                {"name": "李四", "tutorials": 0.7, "assignments": 0.6, "skills": 3, "overall": 0.65},  
                {"name": "王五", "tutorials": 0.5, "assignments": 0.4, "skills": 2, "overall": 0.45},  
                {"name": "赵六", "tutorials": 0.3, "assignments": 0.2, "skills": 1, "overall": 0.25}  
            ]  
              
            total_progress = 0  
            for i, progress in enumerate(sample_progress):  
                self.progress_table.insertRow(i)  
                self.progress_table.setItem(i, 0, QTableWidgetItem(progress["name"]))  
                self.progress_table.setItem(i, 1, QTableWidgetItem(f"{int(progress['tutorials'] * 100)}%"))  
                self.progress_table.setItem(i, 2, QTableWidgetItem(f"{int(progress['assignments'] * 100)}%"))  
                self.progress_table.setItem(i, 3, QTableWidgetItem(f"{progress['skills']}/5"))  
                self.progress_table.setItem(i, 4, QTableWidgetItem(f"{int(progress['overall'] * 100)}%"))  
                  
                total_progress += progress["overall"]  
              
            # Update overall progress  
            avg_progress = total_progress / len(sample_progress)  
            self.overall_progress_bar.setValue(int(avg_progress * 100))  
            self.progress_label.setText(f"班级平均进度: {int(avg_progress * 100)}%")  
      
    def add_class(self):  
        """Add a new class"""  
        # Show dialog to get class name  
        class_name, ok = QInputDialog.getText(self, "新建班级", "班级名称:")  
          
        if ok and class_name:  
            if self.class_manager:  
                # Create class using class manager  
                class_id = self.class_manager.create_class(class_name)  
                  
                # Refresh class list  
                self.refresh_class_list()  
                  
                # Select the new class  
                for i in range(self.class_selector.count()):  
                    if self.class_selector.itemData(i) == class_id:  
                        self.class_selector.setCurrentIndex(i)  
                        break  
            else:  
                # Just add to combo box for demonstration  
                self.class_selector.addItem(class_name, f"sample{self.class_selector.count()+1}")  
                self.class_selector.setCurrentIndex(self.class_selector.count()-1)  
      
    def add_student(self):  
        """Add a new student to the current class"""  
        if not self.current_class_id:  
            QMessageBox.warning(self, "添加学生", "请先选择或创建一个班级")  
            return  
              
        # Show dialog to get student info  
        dialog = AddStudentDialog(self)  
        if dialog.exec_() == QDialog.Accepted:  
            student_data = dialog.get_student_data()  
              
            if self.class_manager:  
                # Add student using class manager  
                self.class_manager.add_student(  
                    self.current_class_id,  
                    student_data["name"],  
                    student_data["email"],  
                    student_id=student_data["id"]  
                )  
              
            # Refresh student table  
            self.refresh_student_table()  
      
    def remove_student(self):  
        """Remove a student from the current class"""  
        if not self.current_class_id:  
            return  
              
        # Get selected student  
        selected_rows = self.student_table.selectionModel().selectedRows()  
        if not selected_rows:  
            QMessageBox.warning(self, "移除学生", "请先选择要移除的学生")  
            return  
              
        # Confirm removal  
        confirm = QMessageBox.question(  
            self,  
            "移除学生",  
            "确定要移除所选学生吗？",  
            QMessageBox.Yes | QMessageBox.No  
        )  
          
        if confirm == QMessageBox.Yes:  
            # Get student ID  
            row = selected_rows[0].row()  
            student_name = self.student_table.item(row, 0).text()  
            student_id = self.student_table.item(row, 1).text()  
              
            if self.class_manager:  
                # Remove student using class manager  
                self.class_manager.remove_student_from_class(self.current_class_id, student_id)  
              
            # Refresh student table  
            self.refresh_student_table()  
              
            # Refresh progress table  
            self.refresh_progress_table()  
      
    def add_assignment(self):  
        """Add a new assignment to the current class"""  
        if not self.current_class_id:  
            QMessageBox.warning(self, "添加作业", "请先选择或创建一个班级")  
            return  
              
        # Show dialog to get assignment info  
        dialog = AddAssignmentDialog(self)  
        if dialog.exec_() == QDialog.Accepted:  
            assignment_data = dialog.get_assignment_data()  
              
            if self.class_manager:  
                # Add assignment using class manager  
                self.class_manager.create_assignment(  
                    self.current_class_id,  
                    assignment_data["title"],  
                    assignment_data["description"],  
                    assignment_data["due_date"],  
                    []  # Empty tasks list for now  
                )  
              
            # Refresh assignment table  
            self.refresh_assignment_table()  
      
    def remove_assignment(self):  
        """Remove an assignment from the current class"""  
        if not self.current_class_id:  
            return  
              
        # Get selected assignment  
        selected_rows = self.assignment_table.selectionModel().selectedRows()  
        if not selected_rows:  
            QMessageBox.warning(self, "删除作业", "请先选择要删除的作业")  
            return  
              
        # Confirm removal  
        confirm = QMessageBox.question(  
            self,  
            "删除作业",  
            "确定要删除所选作业吗？",  
            QMessageBox.Yes | QMessageBox.No  
        )  
          
        if confirm == QMessageBox.Yes:  
            # Get assignment title  
            row = selected_rows[0].row()  
            assignment_title = self.assignment_table.item(row, 0).text()  
              
            if self.class_manager:  
                # Remove assignment using class manager  
                self.class_manager.remove_assignment(self.current_class_id, assignment_title)  
              
            # Refresh assignment table  
            self.refresh_assignment_table()