# simcereb/ui/learning/tutorial_view.py  
"""  
Tutorial view for the Learning Edition  
Provides interactive tutorials and guided learning  
"""  
  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                            QLabel, QTextBrowser, QProgressBar, QSplitter)  
from PyQt5.QtCore import Qt, pyqtSignal  
from PyQt5.QtGui import QIcon, QPixmap  
  
from ..common.version_ui import VersionSpecificWidget  
  
class TutorialView(VersionSpecificWidget):  
    """  
    Interactive tutorial view for guided learning  
    """  
      
    # Signals  
    tutorial_completed = pyqtSignal(str)  # Emitted when a tutorial is completed  
      
    def __init__(self, version_manager, tutorial_manager, parent=None):  
        """  
        Initialize the tutorial view  
          
        Args:  
            version_manager: VersionManager instance  
            tutorial_manager: TutorialManager instance  
            parent: Parent widget  
        """  
        super().__init__(version_manager, parent)  
        self.tutorial_manager = tutorial_manager  
        self.current_tutorial = None  
        self.current_step = None  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        # Main layout  
        main_layout = QVBoxLayout(self)  
          
        # Header  
        header_layout = QHBoxLayout()  
        self.title_label = QLabel("教程")  
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")  
        header_layout.addWidget(self.title_label)  
        header_layout.addStretch()  
          
        # Tutorial selection button  
        self.select_tutorial_button = QPushButton("选择教程")  
        self.select_tutorial_button.clicked.connect(self.show_tutorial_selection)  
        header_layout.addWidget(self.select_tutorial_button)  
          
        main_layout.addLayout(header_layout)  
          
        # Progress bar  
        self.progress_layout = QHBoxLayout()  
        self.progress_label = QLabel("进度:")  
        self.progress_bar = QProgressBar()  
        self.progress_bar.setRange(0, 100)  
        self.progress_bar.setValue(0)  
        self.progress_layout.addWidget(self.progress_label)  
        self.progress_layout.addWidget(self.progress_bar)  
          
        main_layout.addLayout(self.progress_layout)  
          
        # Main content splitter  
        self.content_splitter = QSplitter(Qt.Horizontal)  
          
        # Tutorial content  
        self.content_browser = QTextBrowser()  
        self.content_browser.setOpenExternalLinks(True)  
        self.content_splitter.addWidget(self.content_browser)  
          
        # Simulation view placeholder  
        self.simulation_view = QWidget()  
        self.simulation_view.setStyleSheet("background-color: #f0f0f0;")  
        self.simulation_layout = QVBoxLayout(self.simulation_view)  
        self.simulation_label = QLabel("模拟视图")  
        self.simulation_label.setAlignment(Qt.AlignCenter)  
        self.simulation_layout.addWidget(self.simulation_label)  
        self.content_splitter.addWidget(self.simulation_view)  
          
        # Set initial sizes  
        self.content_splitter.setSizes([400, 600])  
        main_layout.addWidget(self.content_splitter, 1)  
          
        # Navigation buttons  
        nav_layout = QHBoxLayout()  
          
        self.prev_button = QPushButton("上一步")  
        self.prev_button.clicked.connect(self.go_to_previous_step)  
        self.prev_button.setEnabled(False)  
          
        self.next_button = QPushButton("下一步")  
        self.next_button.clicked.connect(self.go_to_next_step)  
        self.next_button.setEnabled(False)  
          
        nav_layout.addStretch()  
        nav_layout.addWidget(self.prev_button)  
        nav_layout.addWidget(self.next_button)  
          
        main_layout.addLayout(nav_layout)  
          
        # Set initial state  
        self.update_ui()  
      
    def show_tutorial_selection(self):  
        """Show the tutorial selection dialog"""  
        # This would be implemented with a custom dialog  
        # For now, we'll just load a sample tutorial  
        tutorials = self.tutorial_manager.get_available_tutorials()  
        if tutorials:  
            self.load_tutorial(tutorials[0])  
      
    def load_tutorial(self, tutorial_id):  
        """  
        Load a specific tutorial  
          
        Args:  
            tutorial_id (str): ID of the tutorial to load  
        """  
        self.current_tutorial = tutorial_id  
        first_step = self.tutorial_manager.start_tutorial(tutorial_id)  
        if first_step:  
            self.current_step = first_step  
            self.update_ui()  
            self.next_button.setEnabled(True)  
      
    def go_to_next_step(self):  
        """Go to the next step in the current tutorial"""  
        next_step = self.tutorial_manager.next_step()  
        if next_step:  
            self.current_step = next_step  
            self.update_ui()  
            self.prev_button.setEnabled(True)  
        else:  
            # Tutorial completed  
            self.complete_tutorial()  
      
    def go_to_previous_step(self):  
        """Go to the previous step in the current tutorial"""  
        prev_step = self.tutorial_manager.previous_step()  
        if prev_step:  
            self.current_step = prev_step  
            self.update_ui()  
            if self.tutorial_manager.is_first_step():  
                self.prev_button.setEnabled(False)  
        else:  
            self.prev_button.setEnabled(False)  
      
    def complete_tutorial(self):  
        """Mark the current tutorial as completed"""  
        if self.current_tutorial:  
            self.tutorial_completed.emit(self.current_tutorial)  
            self.next_button.setText("完成")  
            self.next_button.clicked.disconnect()  
            self.next_button.clicked.connect(self.reset_tutorial)  
      
    def reset_tutorial(self):  
        """Reset the tutorial view to initial state"""  
        self.current_tutorial = None  
        self.current_step = None  
        self.next_button.setText("下一步")  
        self.next_button.clicked.disconnect()  
        self.next_button.clicked.connect(self.go_to_next_step)  
        self.next_button.setEnabled(False)  
        self.prev_button.setEnabled(False)  
        self.update_ui()  
      
    def update_ui(self):  
        """Update the UI based on current tutorial and step"""  
        if self.current_tutorial and self.current_step:  
            # Update title  
            tutorial_info = self.tutorial_manager.get_tutorial_info(self.current_tutorial)  
            self.title_label.setText(tutorial_info.get("title", "教程"))  
              
            # Update progress  
            progress = self.tutorial_manager.get_progress()  
            self.progress_bar.setValue(int(progress * 100))  
              
            # Update content  
            self.content_browser.setHtml(self.current_step.get("content", ""))  
              
            # Update simulation view if needed  
            simulation_config = self.current_step.get("simulation", None)  
            if simulation_config:  
                self.update_simulation(simulation_config)  
        else:  
            # No tutorial loaded  
            self.title_label.setText("教程")  
            self.progress_bar.setValue(0)  
            self.content_browser.setHtml(  
                "<h1>欢迎使用SimCereb学习版</h1>"  
                "<p>请选择一个教程开始学习人形机器人小脑控制系统。</p>"  
                "<p>点击右上角的\"选择教程\"按钮开始。</p>"  
            )  
      
    def update_simulation(self, simulation_config):  
        """  
        Update the simulation view based on configuration  
          
        Args:  
            simulation_config (dict): Simulation configuration  
        """  
        # This would be implemented to connect with the simulation engine  
        # For now, we'll just update the placeholder  
        self.simulation_label.setText(f"模拟: {simulation_config.get('name', '基础模拟')}")  
      
    def resizeEvent(self, event):  
        """Handle resize events"""  
        super().resizeEvent(event)  
        # Adjust splitter sizes on resize if needed  
        width = self.width()  
        self.content_splitter.setSizes([int(width * 0.4), int(width * 0.6)])