# simcereb/ui/studio.py  
import sys  
import os  
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QAction,   
                            QDockWidget, QFileDialog, QMessageBox)  
from PyQt5.QtCore import Qt, QTimer  
  
from ..core.engine import SimulationEngine  
from ..core.robot import HumanoidRobot  
from .plugin_browser import PluginBrowser  
from .plugin_creator import PluginCreatorWizard  
from .plugin_editor import PluginEditor  
from .plugin_tester import PluginTester  
from .robot_view import RobotView  
from .visualization import DataVisualization  
  
class SimCerebStudio(QMainWindow):  
    """Main window for the SimCereb Studio application"""  
      
    def __init__(self):  
        super().__init__()  
          
        # Initialize simulation engine  
        self.engine = SimulationEngine(use_gui=False)  # We'll handle visualization ourselves  
          
        # Initialize UI  
        self.init_ui()  
          
        # Start simulation timer  
        self.timer = QTimer(self)  
        self.timer.timeout.connect(self.update_simulation)  
        self.timer.start(int(self.engine.time_step * 1000))  # Convert to milliseconds  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        self.setWindowTitle("SimCereb Studio")  
        self.setGeometry(100, 100, 1200, 800)  
          
        # Create central widget with tabs  
        self.tabs = QTabWidget()  
        self.setCentralWidget(self.tabs)  
          
        # Create robot view  
        self.robot_view = RobotView(self.engine)  
        self.tabs.addTab(self.robot_view, "3D View")  
          
        # Create data visualization  
        self.data_viz = DataVisualization()  
        self.tabs.addTab(self.data_viz, "Data Visualization")  
          
        # Create plugin browser dock  
        self.plugin_browser = PluginBrowser(self.engine.plugin_manager)  
        plugin_browser_dock = QDockWidget("Plugin Browser", self)  
        plugin_browser_dock.setWidget(self.plugin_browser)  
        self.addDockWidget(Qt.LeftDockWidgetArea, plugin_browser_dock)  
          
        # Create plugin editor dock  
        self.plugin_editor = PluginEditor()  
        plugin_editor_dock = QDockWidget("Plugin Editor", self)  
        plugin_editor_dock.setWidget(self.plugin_editor)  
        self.addDockWidget(Qt.RightDockWidgetArea, plugin_editor_dock)  
          
        # Create plugin tester dock  
        self.plugin_tester = PluginTester(self.engine)  
        plugin_tester_dock = QDockWidget("Plugin Tester", self)  
        plugin_tester_dock.setWidget(self.plugin_tester)  
        self.addDockWidget(Qt.BottomDockWidgetArea, plugin_tester_dock)  
          
        # Create menu bar  
        self.create_menu_bar()  
          
        # Create status bar  
        self.statusBar().showMessage("Ready")  
          
    def create_menu_bar(self):  
        """Create the menu bar"""  
        # File menu  
        file_menu = self.menuBar().addMenu("File")  
          
        load_robot_action = QAction("Load Robot", self)  
        load_robot_action.triggered.connect(self.load_robot)  
        file_menu.addAction(load_robot_action)  
          
        load_config_action = QAction("Load Configuration", self)  
        load_config_action.triggered.connect(self.load_configuration)  
        file_menu.addAction(load_config_action)  
          
        save_config_action = QAction("Save Configuration", self)  
        save_config_action.triggered.connect(self.save_configuration)  
        file_menu.addAction(save_config_action)  
          
        file_menu.addSeparator()  
          
        exit_action = QAction("Exit", self)  
        exit_action.triggered.connect(self.close)  
        file_menu.addAction(exit_action)  
          
        # Simulation menu  
        sim_menu = self.menuBar().addMenu("Simulation")  
          
        start_action = QAction("Start", self)  
        start_action.triggered.connect(self.start_simulation)  
        sim_menu.addAction(start_action)  
          
        stop_action = QAction("Stop", self)  
        stop_action.triggered.connect(self.stop_simulation)  
        sim_menu.addAction(stop_action)  
          
        reset_action = QAction("Reset", self)  
        reset_action.triggered.connect(self.reset_simulation)  
        sim_menu.addAction(reset_action)  
          
        # Plugin menu  
        plugin_menu = self.menuBar().addMenu("Plugins")  
          
        create_plugin_action = QAction("Create New Plugin", self)  
        create_plugin_action.triggered.connect(self.create_plugin)  
        plugin_menu.addAction(create_plugin_action)  
          
        refresh_plugins_action = QAction("Refresh Plugins", self)  
        refresh_plugins_action.triggered.connect(self.refresh_plugins)  
        plugin_menu.addAction(refresh_plugins_action)  
          
        # Help menu  
        help_menu = self.menuBar().addMenu("Help")  
          
        about_action = QAction("About", self)  
        about_action.triggered.connect(self.show_about)  
        help_menu.addAction(about_action)  
          
    def update_simulation(self):  
        """Update the simulation"""  
        if self.engine.running:  
            self.engine.step()  
            self.robot_view.update_view()  
            self.data_viz.update_data(self.engine)  
            self.statusBar().showMessage(f"Simulation time: {self.engine.elapsed_time:.2f}s")  
              
    def load_robot(self):  
        """Load a robot model"""  
        file_path, _ = QFileDialog.getOpenFileName(  
            self, "Load Robot Model", "", "URDF Files (*.urdf);;All Files (*)"  
        )  
          
        if file_path:  
            try:  
                robot = HumanoidRobot(file_path)  
                self.engine.add_robot(robot)  
                self.statusBar().showMessage(f"Loaded robot from {file_path}")  
            except Exception as e:  
                QMessageBox.critical(self, "Error", f"Failed to load robot: {e}")  
                  
    def load_configuration(self):  
        """Load a configuration file"""  
        file_path, _ = QFileDialog.getOpenFileName(  
            self, "Load Configuration", "", "YAML Files (*.yaml);;All Files (*)"  
        )  
          
        if file_path:  
            try:  
                self.engine.config_manager.load_config(file_path)  
                self.engine.plugin_manager.load_plugins()  
                self.plugin_browser.refresh_plugin_list()  
                self.statusBar().showMessage(f"Loaded configuration from {file_path}")  
            except Exception as e:  
                QMessageBox.critical(self, "Error", f"Failed to load configuration: {e}")  
                  
    def save_configuration(self):  
        """Save the current configuration"""  
        file_path, _ = QFileDialog.getSaveFileName(  
            self, "Save Configuration", "", "YAML Files (*.yaml);;All Files (*)"  
        )  
          
        if file_path:  
            try:  
                self.engine.config_manager.save_config(file_path)  
                self.statusBar().showMessage(f"Saved configuration to {file_path}")  
            except Exception as e:  
                QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")  
                  
    def start_simulation(self):  
        """Start the simulation"""  
        self.engine.running = True  
        self.statusBar().showMessage("Simulation started")  
          
    def stop_simulation(self):  
        """Stop the simulation"""  
        self.engine.running = False  
        self.statusBar().showMessage("Simulation stopped")  
          
    def reset_simulation(self):  
        """Reset the simulation"""  
        self.engine.reset()  
        self.robot_view.update_view()  
        self.statusBar().showMessage("Simulation reset")  
          
    def create_plugin(self):  
        """Open the plugin creator wizard"""  
        wizard = PluginCreatorWizard(self)  
        if wizard.exec_():  
            self.plugin_browser.refresh_plugin_list()  
            self.statusBar().showMessage("Plugin created successfully")  
              
    def refresh_plugins(self):  
        """Refresh the plugin list"""  
        self.engine.plugin_manager.load_plugins()  
        self.plugin_browser.refresh_plugin_list()  
        self.statusBar().showMessage("Plugins refreshed")  
          
    def show_about(self):  
        """Show the about dialog"""  
        QMessageBox.about(  
            self,  
            "About SimCereb Studio",  
            "SimCereb Studio\n\n"  
            "An educational platform for humanoid robot cerebellum system simulation.\n\n"  
            "Version: 0.1.0"  
        )  
          
    def closeEvent(self, event):  
        """Handle window close event"""  
        self.engine.disconnect()  
        event.accept()  
  
def main():  
    """Main entry point for the application"""  
    app = QApplication(sys.argv)  
    studio = SimCerebStudio()  
    studio.show()  
    sys.exit(app.exec_())  
  
if __name__ == "__main__":  
    main()