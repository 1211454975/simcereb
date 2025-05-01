# simcereb/ui/learning/progress_dashboard.py  
"""  
Progress dashboard for the Learning Edition  
Displays student progress and achievements  
"""  
  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                            QLabel, QProgressBar, QScrollArea, QFrame,  
                            QGridLayout, QGroupBox)  
from PyQt5.QtCore import Qt, pyqtSignal  
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor  
  
from ..common.version_ui import VersionSpecificWidget  
  
class AchievementWidget(QFrame):  
    """Widget to display a single achievement"""  
      
    def __init__(self, title, description, icon_path=None, completed=False, parent=None):  
        super().__init__(parent)  
        self.title = title  
        self.description = description  
        self.icon_path = icon_path  
        self.completed = completed  
          
        self.setFrameShape(QFrame.StyledPanel)  
        self.setFrameShadow(QFrame.Raised)  
        self.setStyleSheet(  
            "background-color: #f0f0f0; border-radius: 5px; padding: 5px;"  
        )  
          
        self.init_ui()  
      
    def init_ui(self):  
        """Initialize the user interface"""  
        layout = QVBoxLayout(self)  
          
        # Icon  
        icon_label = QLabel()  
        if self.icon_path:  
            pixmap = QPixmap(self.icon_path)  
            icon_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))  
        else:  
            # Default icon  
            icon_label.setText("🏆")  
            icon_label.setFont(QFont("Arial", 24))  
          
        icon_label.setAlignment(Qt.AlignCenter)  
        layout.addWidget(icon_label)  
          
        # Title  
        title_label = QLabel(self.title)  
        title_label.setFont(QFont("Arial", 10, QFont.Bold))  
        title_label.setAlignment(Qt.AlignCenter)  
        layout.addWidget(title_label)  
          
        # Description  
        desc_label = QLabel(self.description)  
        desc_label.setWordWrap(True)  
        desc_label.setAlignment(Qt.AlignCenter)  
        layout.addWidget(desc_label)  
          
        # Status  
        status_label = QLabel("已完成" if self.completed else "未完成")  
        status_label.setStyleSheet(  
            f"color: {'green' if self.completed else 'gray'}; font-weight: bold;"  
        )  
        status_label.setAlignment(Qt.AlignCenter)  
        layout.addWidget(status_label)  
          
        # Apply grayscale effect if not completed  
        if not self.completed:  
            self.setStyleSheet(  
                "background-color: #f0f0f0; border-radius: 5px; padding: 5px; color: #888;"  
            )  
  
class ProgressDashboard(VersionSpecificWidget):  
    """  
    Progress dashboard for the Learning Edition  
    Displays student progress and achievements  
    """  
      
    def __init__(self, version_manager, progress_manager=None, parent=None):  
        """  
        Initialize the progress dashboard  
          
        Args:  
            version_manager: VersionManager instance  
            progress_manager: ProgressManager instance to track user progress  
            parent: Parent widget  
        """  
        super().__init__(version_manager, parent)  
        self.progress_manager = progress_manager  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        # Main layout  
        main_layout = QVBoxLayout(self)  
          
        # Header  
        header_layout = QHBoxLayout()  
        title_label = QLabel("学习进度")  
        title_label.setFont(QFont("Arial", 18, QFont.Bold))  
        header_layout.addWidget(title_label)  
        header_layout.addStretch()  
          
        refresh_button = QPushButton("刷新")  
        refresh_button.clicked.connect(self.refresh_data)  
        header_layout.addWidget(refresh_button)  
          
        main_layout.addLayout(header_layout)  
          
        # Overall progress  
        progress_group = QGroupBox("总体进度")  
        progress_layout = QVBoxLayout(progress_group)  
          
        self.overall_progress_bar = QProgressBar()  
        self.overall_progress_bar.setRange(0, 100)  
        self.overall_progress_bar.setValue(0)  
        progress_layout.addWidget(self.overall_progress_bar)  
          
        self.progress_label = QLabel("已完成: 0%")  
        progress_layout.addWidget(self.progress_label)  
          
        main_layout.addWidget(progress_group)  
          
        # Create a scroll area for the content  
        scroll_area = QScrollArea()  
        scroll_area.setWidgetResizable(True)  
        scroll_content = QWidget()  
        scroll_layout = QVBoxLayout(scroll_content)  
          
        # Tutorial progress  
        tutorial_group = QGroupBox("教程进度")  
        tutorial_layout = QVBoxLayout(tutorial_group)  
          
        self.tutorial_grid = QGridLayout()  
        tutorial_layout.addLayout(self.tutorial_grid)  
          
        scroll_layout.addWidget(tutorial_group)  
          
        # Achievements  
        achievement_group = QGroupBox("成就")  
        achievement_layout = QVBoxLayout(achievement_group)  
          
        self.achievement_grid = QGridLayout()  
        achievement_layout.addLayout(self.achievement_grid)  

        scroll_layout.addWidget(achievement_group)  
          
        # Skills progress  
        skills_group = QGroupBox("技能掌握")  
        skills_layout = QVBoxLayout(skills_group)  
          
        self.skills_grid = QGridLayout()  
        skills_layout.addLayout(self.skills_grid)  
          
        scroll_layout.addWidget(skills_group)  
          
        # Set the scroll content  
        scroll_area.setWidget(scroll_content)  
        main_layout.addWidget(scroll_area, 1)  # 1 = stretch factor  
          
        # Load initial data  
        self.refresh_data()  
    def refresh_data(self):  
        """Refresh all progress data"""  
        if self.progress_manager:  
            # Update overall progress  
            overall_progress = self.progress_manager.get_overall_progress()  
            self.overall_progress_bar.setValue(int(overall_progress * 100))  
            self.progress_label.setText(f"已完成: {int(overall_progress * 100)}%")  
              
            # Update tutorial progress  
            self._update_tutorial_progress()  
              
            # Update achievements  
            self._update_achievements()  
              
            # Update skills  
            self._update_skills_progress()  
        else:  
            # Use sample data if no progress manager is available  
            self._load_sample_data()  
      
    def _update_tutorial_progress(self):  
        """Update the tutorial progress grid"""  
        # Clear existing items  
        self._clear_layout(self.tutorial_grid)  
          
        # Get tutorial progress from progress manager  
        tutorials = self.progress_manager.get_tutorials()  
          
        # Add tutorial progress bars  
        row = 0  
        for tutorial_id, tutorial_info in tutorials.items():  
            # Tutorial name  
            name_label = QLabel(tutorial_info.get("title", tutorial_id))  
            self.tutorial_grid.addWidget(name_label, row, 0)  
              
            # Progress bar  
            progress = tutorial_info.get("progress", 0)  
            progress_bar = QProgressBar()  
            progress_bar.setRange(0, 100)  
            progress_bar.setValue(int(progress * 100))  
            self.tutorial_grid.addWidget(progress_bar, row, 1)  
              
            # Status  
            status = "已完成" if progress >= 1.0 else f"{int(progress * 100)}%"  
            status_label = QLabel(status)  
            self.tutorial_grid.addWidget(status_label, row, 2)  
              
            row += 1  
      
    def _update_achievements(self):  
        """Update the achievements grid"""  
        # Clear existing items  
        self._clear_layout(self.achievement_grid)  
          
        # Get achievements from progress manager  
        achievements = self.progress_manager.get_achievements()  
          
        # Add achievement widgets  
        col, row = 0, 0  
        max_cols = 3  # Display 3 achievements per row  
          
        for achievement_id, achievement_info in achievements.items():  
            widget = AchievementWidget(  
                title=achievement_info.get("title", achievement_id),  
                description=achievement_info.get("description", ""),  
                icon_path=achievement_info.get("icon"),  
                completed=achievement_info.get("completed", False)  
            )  
              
            self.achievement_grid.addWidget(widget, row, col)  
              
            col += 1  
            if col >= max_cols:  
                col = 0  
                row += 1  
      
    def _update_skills_progress(self):  
        """Update the skills progress grid"""  
        # Clear existing items  
        self._clear_layout(self.skills_grid)  
          
        # Get skills from progress manager  
        skills = self.progress_manager.get_skills()  
          
        # Add skill progress bars  
        row = 0  
        for skill_id, skill_info in skills.items():  
            # Skill name  
            name_label = QLabel(skill_info.get("name", skill_id))  
            self.skills_grid.addWidget(name_label, row, 0)  
              
            # Progress bar  
            level = skill_info.get("level", 0)  
            max_level = skill_info.get("max_level", 5)  
            progress_bar = QProgressBar()  
            progress_bar.setRange(0, max_level)  
            progress_bar.setValue(level)  
            self.skills_grid.addWidget(progress_bar, row, 1)  
              
            # Level  
            level_label = QLabel(f"等级 {level}/{max_level}")  
            self.skills_grid.addWidget(level_label, row, 2)  
              
            row += 1  
      
    def _clear_layout(self, layout):  
        """Clear all widgets from a layout"""  
        if layout is not None:  
            while layout.count():  
                item = layout.takeAt(0)  
                widget = item.widget()  
                if widget is not None:  
                    widget.deleteLater()  
                else:  
                    self._clear_layout(item.layout())  
      
    def _load_sample_data(self):  
        """Load sample data for demonstration"""  
        # Set overall progress  
        self.overall_progress_bar.setValue(35)  
        self.progress_label.setText("已完成: 35%")  
          
        # Sample tutorials  
        self._clear_layout(self.tutorial_grid)  
        sample_tutorials = [  
            {"title": "平衡控制基础", "progress": 1.0},  
            {"title": "步态生成入门", "progress": 0.6},  
            {"title": "传感器数据处理", "progress": 0.3},  
            {"title": "机器人动力学", "progress": 0.0}  
        ]  
          
        for i, tutorial in enumerate(sample_tutorials):  
            name_label = QLabel(tutorial["title"])  
            self.tutorial_grid.addWidget(name_label, i, 0)  
              
            progress_bar = QProgressBar()  
            progress_bar.setRange(0, 100)  
            progress_bar.setValue(int(tutorial["progress"] * 100))  
            self.tutorial_grid.addWidget(progress_bar, i, 1)  
              
            status = "已完成" if tutorial["progress"] >= 1.0 else f"{int(tutorial['progress'] * 100)}%"  
            status_label = QLabel(status)  
            self.tutorial_grid.addWidget(status_label, i, 2)  
          
        # Sample achievements  
        self._clear_layout(self.achievement_grid)  
        sample_achievements = [  
            {"title": "第一步", "description": "完成第一个教程", "completed": True},  
            {"title": "平衡大师", "description": "让机器人保持平衡超过1分钟", "completed": True},  
            {"title": "行走者", "description": "实现稳定的行走控制", "completed": False},  
            {"title": "跑步者", "description": "实现稳定的跑步控制", "completed": False},  
            {"title": "跳跃者", "description": "实现稳定的跳跃控制", "completed": False},  
            {"title": "创新者", "description": "创建自己的控制算法", "completed": False}  
        ]  
          
        col, row = 0, 0  
        max_cols = 3  
          
        for achievement in sample_achievements:  
            widget = AchievementWidget(  
                title=achievement["title"],  
                description=achievement["description"],  
                completed=achievement["completed"]  
            )  
              
            self.achievement_grid.addWidget(widget, row, col)  
              
            col += 1  
            if col >= max_cols:  
                col = 0  
                row += 1  
          
        # Sample skills  
        self._clear_layout(self.skills_grid)  
        sample_skills = [  
            {"name": "平衡控制", "level": 3, "max_level": 5},  
            {"name": "步态生成", "level": 2, "max_level": 5},  
            {"name": "传感器处理", "level": 1, "max_level": 5},  
            {"name": "动力学分析", "level": 0, "max_level": 5},  
            {"name": "算法设计", "level": 2, "max_level": 5}  
        ]  
          
        for i, skill in enumerate(sample_skills):  
            name_label = QLabel(skill["name"])  
            self.skills_grid.addWidget(name_label, i, 0)  
              
            progress_bar = QProgressBar()  
            progress_bar.setRange(0, skill["max_level"])  
            progress_bar.setValue(skill["level"])  
            self.skills_grid.addWidget(progress_bar, i, 1)  
              
            level_label = QLabel(f"等级 {skill['level']}/{skill['max_level']}")  
            self.skills_grid.addWidget(level_label, i, 2)


# simcereb/tools/learning/progress_manager.py  
"""  
Progress manager for tracking student learning progress  
"""  
  
import os  
import json  
import time  
from datetime import datetime  
  
class ProgressManager:  
    """  
    Manages and tracks student learning progress  
    """  
      
    def __init__(self, config_manager, user_id=None):  
        """  
        Initialize the progress manager  
          
        Args:  
            config_manager: ConfigManager instance  
            user_id: User ID to track progress for, or None for current user  
        """  
        self.config_manager = config_manager  
        self.user_id = user_id or "default_user"  
        self.data_dir = os.path.join(  
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),  
            "data", "progress"  
        )  
          
        # Ensure data directory exists  
        os.makedirs(self.data_dir, exist_ok=True)  
          
        # Load progress data  
        self.progress_data = self._load_progress_data()  
      
    def _load_progress_data(self):  
        """Load progress data from file"""  
        progress_file = os.path.join(self.data_dir, f"{self.user_id}.json")  
          
        if os.path.exists(progress_file):  
            try:  
                with open(progress_file, 'r', encoding='utf-8') as f:  
                    return json.load(f)  
            except Exception as e:  
                print(f"Error loading progress data: {e}")  
                return self._create_default_progress_data()  
        else:  
            return self._create_default_progress_data()  
      
    def _create_default_progress_data(self):  
        """Create default progress data structure"""  
        return {  
            "user_id": self.user_id,  
            "created_at": datetime.now().isoformat(),  
            "last_updated": datetime.now().isoformat(),  
            "tutorials": {},  
            "achievements": {},  
            "skills": {},  
            "completed_tasks": [],  
            "statistics": {  
                "total_time": 0,  
                "sessions": 0,  
                "last_session": None  
            }  
        }  
      
    def _save_progress_data(self):  
        """Save progress data to file"""  
        progress_file = os.path.join(self.data_dir, f"{self.user_id}.json")  
          
        # Update last updated timestamp  
        self.progress_data["last_updated"] = datetime.now().isoformat()  
          
        try:  
            with open(progress_file, 'w', encoding='utf-8') as f:  
                json.dump(self.progress_data, f, indent=2)  
        except Exception as e:  
            print(f"Error saving progress data: {e}")  
      
    def get_overall_progress(self):  
        """  
        Calculate overall progress as a value between 0 and 1  
          
        Returns:  
            float: Overall progress (0-1)  
        """  
        # Calculate tutorial progress  
        tutorials = self.progress_data.get("tutorials", {})  
        tutorial_progress = 0  
        if tutorials:  
            tutorial_progress = sum(t.get("progress", 0) for t in tutorials.values()) / len(tutorials)  
          
        # Calculate achievement progress  
        achievements = self.progress_data.get("achievements", {})  
        achievement_progress = 0  
        if achievements:  
            achievement_progress = sum(1 for a in achievements.values() if a.get("completed", False)) / len(achievements)  
          
        # Calculate skill progress  
        skills = self.progress_data.get("skills", {})  
        skill_progress = 0  
        if skills:  
            skill_progress = sum(s.get("level", 0) / s.get("max_level", 1) for s in skills.values()) / len(skills)  
          
        # Weight the different components  
        overall_progress = (tutorial_progress * 0.5) + (achievement_progress * 0.3) + (skill_progress * 0.2)  
          
        return overall_progress  
      
    def get_tutorials(self):  
        """Get all tutorials and their progress"""  
        return self.progress_data.get("tutorials", {})  
      
    def get_achievements(self):  
        """Get all achievements and their status"""  
        return self.progress_data.get("achievements", {})  
      
    def get_skills(self):  
        """Get all skills and their levels"""  
        return self.progress_data.get("skills", {})  
      
    def update_tutorial_progress(self, tutorial_id, progress):  
        """  
        Update progress for a specific tutorial  
          
        Args:  
            tutorial_id (str): ID of the tutorial  
            progress (float): Progress value between 0 and 1  
        """  
        tutorials = self.progress_data.setdefault("tutorials", {})  
          
        if tutorial_id not in tutorials:  
            # Get tutorial info from config  
            tutorial_info = self.config_manager.get_value(f"tutorials.{tutorial_id}", {})  
              
            tutorials[tutorial_id] = {  
                "title": tutorial_info.get("title", tutorial_id),  
                "progress": 0,  
                "started_at": datetime.now().isoformat(),  
                "completed_at": None  
            }  
          
        # Update progress  
        tutorials[tutorial_id]["progress"] = max(0, min(1, progress))  
          
        # If completed, set completed timestamp  
        if progress >= 1.0 and not tutorials[tutorial_id].get("completed_at"):  
            tutorials[tutorial_id]["completed_at"] = datetime.now().isoformat()  
              
            # Check for achievements  
            self._check_tutorial_achievements(tutorial_id)  
          
        self._save_progress_data()  
      
    def unlock_achievement(self, achievement_id):  
        """  
        Unlock an achievement  
          
        Args:  
            achievement_id (str): ID of the achievement  
        """  
        achievements = self.progress_data.setdefault("achievements", {})  
          
        if achievement_id not in achievements:  
            # Get achievement info from config  
            achievement_info = self.config_manager.get_value(f"achievements.{achievement_id}", {})  
              
            achievements[achievement_id] = {  
                "title": achievement_info.get("title", achievement_id),  
                "description": achievement_info.get("description", ""),  
                "icon": achievement_info.get("icon"),  
                "completed": False,  
                "unlocked_at": None  
            }  
          
        # Mark as completed if not already  
        if not achievements[achievement_id].get("completed", False):  
            achievements[achievement_id]["completed"] = True  
            achievements[achievement_id]["unlocked_at"] = datetime.now().isoformat()  
              
            # Check for skill improvements  
            self._check_skill_improvements(achievement_id)  
          
        self._save_progress_data()
    def update_skill_level(self, skill_id, level):  
        """  
        Update level for a specific skill  
          
        Args:  
            skill_id (str): ID of the skill  
            level (int): New skill level  
        """  
        skills = self.progress_data.setdefault("skills", {})  
          
        if skill_id not in skills:  
            # Get skill info from config  
            skill_info = self.config_manager.get_value(f"skills.{skill_id}", {})  
              
            skills[skill_id] = {  
                "name": skill_info.get("name", skill_id),  
                "level": 0,  
                "max_level": skill_info.get("max_level", 5),  
                "updated_at": datetime.now().isoformat()  
            }  
          
        # Update level  
        max_level = skills[skill_id].get("max_level", 5)  
        skills[skill_id]["level"] = max(0, min(max_level, level))  
        skills[skill_id]["updated_at"] = datetime.now().isoformat()  
          
        # Check for achievements  
        self._check_skill_achievements(skill_id)  
          
        self._save_progress_data()  
      
    def complete_task(self, task_id, metadata=None):  
        """  
        Mark a task as completed  
          
        Args:  
            task_id (str): ID of the task  
            metadata (dict): Additional metadata about the task completion  
        """  
        completed_tasks = self.progress_data.setdefault("completed_tasks", [])  
          
        # Check if task is already completed  
        for task in completed_tasks:  
            if task.get("id") == task_id:  
                return  
          
        # Add task to completed tasks  
        task_data = {  
            "id": task_id,  
            "completed_at": datetime.now().isoformat()  
        }  
          
        if metadata:  
            task_data["metadata"] = metadata  
          
        completed_tasks.append(task_data)  
          
        # Check for achievements and tutorial progress  
        self._check_task_achievements(task_id)  
          
        self._save_progress_data()  
      
    def start_session(self):  
        """Start a new learning session"""  
        statistics = self.progress_data.setdefault("statistics", {})  
        statistics["sessions"] = statistics.get("sessions", 0) + 1  
        statistics["last_session"] = datetime.now().isoformat()  
        statistics["current_session_start"] = datetime.now().isoformat()  
          
        self._save_progress_data()  
      
    def end_session(self):  
        """End the current learning session"""  
        statistics = self.progress_data.setdefault("statistics", {})  
          
        if "current_session_start" in statistics:  
            start_time = datetime.fromisoformat(statistics["current_session_start"])  
            end_time = datetime.now()  
            session_duration = (end_time - start_time).total_seconds()  
              
            statistics["total_time"] = statistics.get("total_time", 0) + session_duration  
            statistics.pop("current_session_start", None)  
              
            self._save_progress_data()  
      
    def get_available_tutorials(self):  
        """Get list of available tutorial IDs"""  
        tutorials_config = self.config_manager.get_value("tutorials", {})  
        return list(tutorials_config.keys())  
      
    def get_tutorial_info(self, tutorial_id):  
        """Get information about a specific tutorial"""  
        return self.config_manager.get_value(f"tutorials.{tutorial_id}", {})  
      
    def get_progress(self):  
        """Get current progress in the active tutorial"""  
        if not hasattr(self, 'current_tutorial') or not self.current_tutorial:  
            return 0  
              
        tutorials = self.progress_data.get("tutorials", {})  
        tutorial = tutorials.get(self.current_tutorial, {})  
          
        return tutorial.get("progress", 0)  
      
    def _check_tutorial_achievements(self, tutorial_id):  
        """Check for achievements related to tutorial completion"""  
        # This would check for achievements like "complete first tutorial"  
        # or "complete all basic tutorials" etc.  
          
        # Example implementation:  
        tutorials = self.progress_data.get("tutorials", {})  
        completed_tutorials = [t for t in tutorials.values() if t.get("completed_at")]  
          
        # Unlock "first tutorial" achievement  
        if len(completed_tutorials) == 1:  
            self.unlock_achievement("first_tutorial")  
          
        # Unlock "all basic tutorials" achievement  
        basic_tutorials = self.config_manager.get_value("tutorial_categories.basic", [])  
        if all(t in [tutorial.get("id") for tutorial in completed_tutorials] for t in basic_tutorials):  
            self.unlock_achievement("all_basic_tutorials")  
      
    def _check_skill_achievements(self, skill_id):  
        """Check for achievements related to skill levels"""  
        # This would check for achievements like "reach level 5 in balance control"  
          
        # Example implementation:  
        skills = self.progress_data.get("skills", {})  
        skill = skills.get(skill_id, {})  
          
        if skill.get("level", 0) >= 5:  
            self.unlock_achievement(f"master_{skill_id}")  
      
    def _check_skill_improvements(self, achievement_id):  
        """Check if an achievement should improve skills"""  
        # This would update skills based on achievements  
          
        # Example implementation:  
        achievement_skill_map = {  
            "balance_master": {"balance_control": 1},  
            "walking_expert": {"gait_generation": 1},  
            "sensor_guru": {"sensor_processing": 1}  
        }  
          
        if achievement_id in achievement_skill_map:  
            for skill_id, level_increase in achievement_skill_map[achievement_id].items():  
                skills = self.progress_data.get("skills", {})  
                current_level = skills.get(skill_id, {}).get("level", 0)  
                self.update_skill_level(skill_id, current_level + level_increase)  
      
    def _check_task_achievements(self, task_id):  
        """Check for achievements related to task completion"""  
        # This would check for achievements like "complete 10 tasks"  
          
        # Example implementation:  
        completed_tasks = self.progress_data.get("completed_tasks", [])  
          
        if len(completed_tasks) >= 10:  
            self.unlock_achievement("task_master")  
          
        # Check for specific task achievements  
        task_achievement_map = {  
            "balance_robot_30s": "balance_achievement",  
            "walk_5_meters": "walking_achievement",  
            "jump_obstacle": "jumping_achievement"  
        }  
          
        if task_id in task_achievement_map:  
            self.unlock_achievement(task_achievement_map[task_id])
          