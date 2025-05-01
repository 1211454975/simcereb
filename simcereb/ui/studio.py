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
        file_menu = self.menuBar().addMenu("文件")  
          
        load_robot_action = QAction("加载机器人模型", self)  
        load_robot_action.triggered.connect(self.load_robot)  
        file_menu.addAction(load_robot_action)  
          
        load_config_action = QAction("加载配置", self)  
        load_config_action.triggered.connect(self.load_configuration)  
        file_menu.addAction(load_config_action)  
          
        save_config_action = QAction("保存配置", self)  
        save_config_action.triggered.connect(self.save_configuration)  
        file_menu.addAction(save_config_action)  
          
        file_menu.addSeparator()  
          
        # Version switching submenu  
        version_menu = file_menu.addMenu("切换版本")  
          
        learning_action = QAction("学习版", self)  
        learning_action.triggered.connect(lambda: self.switch_version(self.version_manager.LEARNING))  
        version_menu.addAction(learning_action)  
          
        research_action = QAction("研究版", self)  
        research_action.triggered.connect(lambda: self.switch_version(self.version_manager.RESEARCH))  
        version_menu.addAction(research_action)  
          
        teaching_action = QAction("教学版", self)  
        teaching_action.triggered.connect(lambda: self.switch_version(self.version_manager.TEACHING))  
        version_menu.addAction(teaching_action)  
          
        file_menu.addSeparator()  
          
        exit_action = QAction("退出", self)  
        exit_action.triggered.connect(self.close)  
        file_menu.addAction(exit_action)  
          
        # Simulation menu  
        sim_menu = self.menuBar().addMenu("仿真")  
          
        start_action = QAction("开始", self)  
        start_action.triggered.connect(self.start_simulation)  
        sim_menu.addAction(start_action)  
          
        stop_action = QAction("停止", self)  
        stop_action.triggered.connect(self.stop_simulation)  
        sim_menu.addAction(stop_action)  
          
        reset_action = QAction("重置", self)  
        reset_action.triggered.connect(self.reset_simulation)  
        sim_menu.addAction(reset_action)  
          
        # Plugin menu  
        plugin_menu = self.menuBar().addMenu("插件")  
          
        create_plugin_action = QAction("创建新插件", self)  
        create_plugin_action.triggered.connect(self.create_plugin)  
        plugin_menu.addAction(create_plugin_action)  
          
        refresh_plugins_action = QAction("刷新插件", self)  
        refresh_plugins_action.triggered.connect(self.refresh_plugins)  
        plugin_menu.addAction(refresh_plugins_action)  
          
        # View menu  
        view_menu = self.menuBar().addMenu("视图")  
          
        # Theme submenu  
        theme_menu = view_menu.addMenu("主题")  
          
        light_theme_action = QAction("浅色", self)  
        light_theme_action.triggered.connect(lambda: self.change_theme(self.theme_manager.LIGHT))  
        theme_menu.addAction(light_theme_action)  
          
        dark_theme_action = QAction("深色", self)  
        dark_theme_action.triggered.connect(lambda: self.change_theme(self.theme_manager.DARK))  
        theme_menu.addAction(dark_theme_action)  
          
        blue_theme_action = QAction("蓝色", self)  
        blue_theme_action.triggered.connect(lambda: self.change_theme(self.theme_manager.BLUE))  
        theme_menu.addAction(blue_theme_action)  
          
        # Language submenu  
        language_menu = view_menu.addMenu("语言")  
          
        chinese_action = QAction("中文", self)  
        chinese_action.triggered.connect(lambda: self.change_language("zh_CN"))  
        language_menu.addAction(chinese_action)  
          
        english_action = QAction("English", self)  
        english_action.triggered.connect(lambda: self.change_language("en_US"))  
        language_menu.addAction(english_action)  
          
        # Version-specific menus  
        if self.version_manager.get_version() == self.version_manager.LEARNING:  
            self.create_learning_menus()  
        elif self.version_manager.get_version() == self.version_manager.RESEARCH:  
            self.create_research_menus()  
        elif self.version_manager.get_version() == self.version_manager.TEACHING:  
            self.create_teaching_menus()  
          
        # Help menu  
        help_menu = self.menuBar().addMenu("帮助")  
          
        about_action = QAction("关于", self)  
        about_action.triggered.connect(self.show_about)  
        help_menu.addAction(about_action)  
          
        tutorial_action = QAction("教程", self)  
        tutorial_action.triggered.connect(self.show_tutorial)  
        help_menu.addAction(tutorial_action)  


    def create_toolbar(self):  
        """Create the toolbar"""  
        toolbar = self.addToolBar("主工具栏")  
        toolbar.setMovable(False)  
          
        # Simulation controls  
        start_action = QAction(QIcon.fromTheme("media-playback-start"), "开始仿真", self)  
        start_action.triggered.connect(self.start_simulation)  
        toolbar.addAction(start_action)  
          
        stop_action = QAction(QIcon.fromTheme("media-playback-stop"), "停止仿真", self)  
        stop_action.triggered.connect(self.stop_simulation)  
        toolbar.addAction(stop_action)  
          
        reset_action = QAction(QIcon.fromTheme("view-refresh"), "重置仿真", self)  
        reset_action.triggered.connect(self.reset_simulation)  
        toolbar.addAction(reset_action)  
          
        toolbar.addSeparator()  
          
        # Plugin controls  
        create_plugin_action = QAction(QIcon.fromTheme("document-new"), "创建插件", self)  
        create_plugin_action.triggered.connect(self.create_plugin)  
        toolbar.addAction(create_plugin_action)  
          
        # Version-specific toolbar items  
        if self.version_manager.get_version() == self.version_manager.LEARNING:  
            self.add_learning_toolbar_items(toolbar)  
        elif self.version_manager.get_version() == self.version_manager.RESEARCH:  
            self.add_research_toolbar_items(toolbar)  
        elif self.version_manager.get_version() == self.version_manager.TEACHING:  
            self.add_teaching_toolbar_items(toolbar)  

    def add_common_tabs(self):  
        """Add common tabs to the main tab widget"""  
        # 3D View tab  
        from .robot_view import RobotView  
        self.robot_view = RobotView(self.engine)  
        self.tabs.addTab(self.robot_view, "3D视图")  
          
        # Plugin Browser tab  
        self.plugin_browser = PluginBrowser(self.engine.plugin_manager)  
        self.tabs.addTab(self.plugin_browser, "插件浏览器")  
          
        # Plugin Editor tab  
        self.plugin_editor = PluginEditor()  
        self.tabs.addTab(self.plugin_editor, "插件编辑器")  
          
        # Plugin Tester tab  
        self.plugin_tester = PluginTester(self.engine)  
        self.tabs.addTab(self.plugin_tester, "插件测试器")  

    def add_learning_tabs(self):  
        """Add Learning Edition specific tabs"""  
        # Tutorial tab  
        if hasattr(self, 'tutorial_manager'):  
            self.tutorial_view = TutorialView(self.version_manager, self.tutorial_manager)  
            self.tabs.addTab(self.tutorial_view, "教程")  
          
        # Visual Programming tab  
        self.visual_programming = VisualProgrammingEditor(self.version_manager)  
        self.tabs.addTab(self.visual_programming, "可视化编程")  
          
        # Progress Dashboard tab  
        if hasattr(self, 'progress_manager'):  
            self.progress_dashboard = ProgressDashboard(self.version_manager, self.progress_manager)  
            self.tabs.addTab(self.progress_dashboard, "学习进度") 

    def add_research_tabs(self):  
        """Add Research Edition specific tabs"""  
        # Advanced Analytics tab  
        self.analytics_view = AdvancedAnalyticsView(self.version_manager)  
        self.tabs.addTab(self.analytics_view, "高级数据分析")  
          
        # Environment Editor tab  
        self.environment_editor = EnvironmentEditor(self.version_manager)  
        self.tabs.addTab(self.environment_editor, "环境编辑器")  
          
        # Experiment Manager tab  
        from .research.experiment_manager import ExperimentManager  
        self.experiment_manager = ExperimentManager(self.version_manager)  
        self.tabs.addTab(self.experiment_manager, "实验管理")  
      
    def add_teaching_tabs(self):  
        """Add Teaching Edition specific tabs"""  
        # Class Manager tab  
        if hasattr(self, 'class_manager'):  
            self.class_manager_ui = ClassManagerUI(self.version_manager, self.class_manager)  
            self.tabs.addTab(self.class_manager_ui, "班级管理")  
          
        # Assignment Editor tab  
        if hasattr(self, 'class_manager'):  
            self.assignment_editor = AssignmentEditor(self.version_manager, self.class_manager)  
            self.tabs.addTab(self.assignment_editor, "作业编辑器")  
      
    def create_learning_menus(self):  
        """Create Learning Edition specific menus"""  
        learning_menu = self.menuBar().addMenu("学习")  
          
        tutorial_action = QAction("开始教程", self)  
        tutorial_action.triggered.connect(self.start_tutorial)  
        learning_menu.addAction(tutorial_action)  
          
        progress_action = QAction("查看进度", self)  
        progress_action.triggered.connect(self.show_progress)  
        learning_menu.addAction(progress_action)  
      
    def create_research_menus(self):  
        """Create Research Edition specific menus"""  
        research_menu = self.menuBar().addMenu("研究")  
          
        analytics_action = QAction("数据分析", self)  
        analytics_action.triggered.connect(self.show_analytics)  
        research_menu.addAction(analytics_action)  
          
        experiment_action = QAction("实验管理", self)  
        experiment_action.triggered.connect(self.show_experiment_manager)  
        research_menu.addAction(experiment_action)  
          
        export_action = QAction("导出数据", self)  
        export_action.triggered.connect(self.export_data)  
        research_menu.addAction(export_action)  
      
    def create_teaching_menus(self):  
        """Create Teaching Edition specific menus"""  
        teaching_menu = self.menuBar().addMenu("教学")  
          
        presentation_action = QAction("演示模式", self)  
        presentation_action.triggered.connect(self.start_presentation)  
        teaching_menu.addAction(presentation_action)  
          
        class_action = QAction("班级管理", self)  
        class_action.triggered.connect(self.show_class_manager)  
        teaching_menu.addAction(class_action)  
          
        assignment_action = QAction("作业管理", self)  
        assignment_action.triggered.connect(self.show_assignment_editor)  
        teaching_menu.addAction(assignment_action)  
      
    def add_learning_toolbar_items(self, toolbar):  
        """Add Learning Edition specific toolbar items"""  
        toolbar.addSeparator()  
          
        tutorial_action = QAction(QIcon.fromTheme("help-contents"), "开始教程", self)  
        tutorial_action.triggered.connect(self.start_tutorial)  
        toolbar.addAction(tutorial_action)  
          
        visual_programming_action = QAction(QIcon.fromTheme("applications-graphics"), "可视化编程", self)  
        visual_programming_action.triggered.connect(self.show_visual_programming)  
        toolbar.addAction(visual_programming_action)  
      
    def add_research_toolbar_items(self, toolbar):  
        """Add Research Edition specific toolbar items"""  
        toolbar.addSeparator()  
          
        analytics_action = QAction(QIcon.fromTheme("office-chart-bar"), "数据分析", self)  
        analytics_action.triggered.connect(self.show_analytics)  
        toolbar.addAction(analytics_action)  
          
        environment_action = QAction(QIcon.fromTheme("applications-science"), "环境编辑器", self)  
        environment_action.triggered.connect(self.show_environment_editor)  
        toolbar.addAction(environment_action)  
      
    def add_teaching_toolbar_items(self, toolbar):  
        """Add Teaching Edition specific toolbar items"""  
        toolbar.addSeparator()  
          
        presentation_action = QAction(QIcon.fromTheme("video-display"), "演示模式", self)  
        presentation_action.triggered.connect(self.start_presentation)  
        toolbar.addAction(presentation_action)  
          
        class_action = QAction(QIcon.fromTheme("system-users"), "班级管理", self)  
        class_action.triggered.connect(self.show_class_manager)  
        toolbar.addAction(class_action)  


    def update_simulation(self):  
        """Update the simulation"""  
        if self.engine.running:  
            self.engine.step()  
            self.robot_view.update_view()  
            self.data_viz.update_data(self.engine)  
            self.statusBar().showMessage(f"Simulation time: {self.engine.elapsed_time:.2f}s")  
              
    # Common actions  
    def load_robot(self):  
        """Load a robot model"""  
        options = QFileDialog.Options()  
        file_path, _ = QFileDialog.getOpenFileName(  
            self,  
            "加载机器人模型",  
            "",  
            "URDF文件 (*.urdf);;所有文件 (*.*)",  
            options=options  
        )  
          
        if file_path:  
            try:  
                self.engine.load_robot(file_path)  
                self.statusBar().showMessage(f"已加载机器人模型: {file_path}")  
            except Exception as e:  
                QMessageBox.critical(self, "加载失败", f"加载机器人模型时出错: {str(e)}")  
                  
    def load_configuration(self):  
        """Load a configuration file"""  
        options = QFileDialog.Options()  
        file_path, _ = QFileDialog.getOpenFileName(  
            self,  
            "加载配置",  
            "",  
            "YAML文件 (*.yaml *.yml);;所有文件 (*.*)",  
            options=options  
        )  
          
        if file_path:  
            try:  
                self.config_manager.load_config(file_path)  
                self.statusBar().showMessage(f"已加载配置: {file_path}")  
            except Exception as e:  
                QMessageBox.critical(self, "加载失败", f"加载配置时出错: {str(e)}")  
                  
    def save_configuration(self):  
        """Save the current configuration to a file"""  
        options = QFileDialog.Options()  
        file_path, _ = QFileDialog.getSaveFileName(  
            self,  
            "保存配置",  
            "",  
            "YAML文件 (*.yaml);;所有文件 (*.*)",  
            options=options  
        )  
          
        if file_path:  
            try:  
                self.config_manager.save_config(file_path)  
                self.statusBar().showMessage(f"已保存配置: {file_path}")  
            except Exception as e:  
                QMessageBox.critical(self, "保存失败", f"保存配置时出错: {str(e)}")  
    def switch_version(self, version):  
        """  
        Switch to a different version  
          
        Args:  
            version (str): Version to switch to (LEARNING, RESEARCH, or TEACHING)  
        """  
        if self.version_manager.get_version() == version:  
            return  
              
        # Confirm switch  
        confirm = QMessageBox.question(  
            self,  
            "切换版本",  
            f"确定要切换到{self.version_manager.get_version_name(version)}吗？\n\n这将重新启动应用程序。",  
            QMessageBox.Yes | QMessageBox.No  
        )  
          
        if confirm == QMessageBox.Yes:  
            # Save current version to config  
            self.version_manager.set_version(version)  
              
            # Restart application  
            QMessageBox.information(  
                self,  
                "重启应用程序",  
                "应用程序将重新启动以应用新版本。"  
            )  
              
            # This would be implemented to restart the application  
            # For now, just close the window  
            self.close()  

    def start_simulation(self):  
        """Start the simulation"""  
        if self.engine:  
            self.engine.start()  
            self.statusBar().showMessage("仿真已开始")  
          
    def stop_simulation(self):  
        """Stop the simulation"""  
        if self.engine:  
            self.engine.stop()  
            self.statusBar().showMessage("仿真已停止")  
      
    def reset_simulation(self):  
        """Reset the simulation"""  
        if self.engine:  
            self.engine.reset()  
            self.statusBar().showMessage("仿真已重置")  
          
    def create_plugin(self):  
        """Create a new plugin"""  
        wizard = PluginCreatorWizard(self)  
        wizard.exec_()  
      
    def refresh_plugins(self):  
        """Refresh the plugin list"""  
        if self.engine and hasattr(self.engine, 'plugin_manager'):  
            self.engine.plugin_manager.load_plugins()  
            self.plugin_browser.refresh_plugin_list()  
            self.statusBar().showMessage("插件已刷新")  


    def change_theme(self, theme):  
        """  
        Change the application theme  
          
        Args:  
            theme (str): Theme to apply  
        """  
        if self.theme_manager:  
            self.theme_manager.apply_theme(theme)  
            self.statusBar().showMessage(f"已应用主题: {theme}")

    def change_language(self, language_code):  
        """  
        Change the application language  
          
        Args:  
            language_code (str): Language code to set  
        """  
        if self.language_manager:  
            if self.language_manager.set_language(language_code):  
                language_name = self.language_manager.get_language_name(language_code)  
                self.statusBar().showMessage(f"已切换语言: {language_name}")  
                  
                # Show restart message  
                QMessageBox.information(  
                    self,  
                    "重启应用程序",  
                    "请重启应用程序以完全应用新语言。"  
                )  
            else:  
                QMessageBox.warning(  
                    self,  
                    "切换语言失败",  
                    f"不支持的语言: {language_code}"  
                )  


    def show_about(self):  
        """Show the about dialog"""  
        version_name = self.version_manager.get_version_name()  
        QMessageBox.about(  
            self,  
            f"关于 SimCereb Studio - {version_name}",  
            f"SimCereb Studio - {version_name}\n\n"  
            "人形机器人小脑系统模拟教育平台\n\n"  
            "版本: 1.0.0"  
        )  

    def show_tutorial(self):  
        """Show the tutorial"""  
        if self.version_manager.get_version() == self.version_manager.LEARNING:  
            # Switch to tutorial tab  
            for i in range(self.tabs.count()):  
                if isinstance(self.tabs.widget(i), TutorialView):  
                    self.tabs.setCurrentIndex(i)  
                    break  
        else:  
            # Show tutorial dialog  
            QMessageBox.information(  
                self,  
                "教程",  
                "请访问我们的网站获取详细教程。"  
            )  

    # Learning Edition specific actions  
    def start_tutorial(self):  
        """Start the tutorial"""  
        if hasattr(self, 'tutorial_view'):  
            # Switch to tutorial tab  
            for i in range(self.tabs.count()):  
                if self.tabs.widget(i) == self.tutorial_view:  
                    self.tabs.setCurrentIndex(i)  
                    break  
              
            # Show tutorial selection dialog  
            self.tutorial_view.show_tutorial_selection()  

    def show_progress(self):  
        """Show the progress dashboard"""  
        if hasattr(self, 'progress_dashboard'):  
            # Switch to progress dashboard tab  
            for i in range(self.tabs.count()):  
                if self.tabs.widget(i) == self.progress_dashboard:  
                    self.tabs.setCurrentIndex(i)  
                    break  

    def show_visual_programming(self):  
        """Show the visual programming editor"""  
        if hasattr(self, 'visual_programming'):  
            # Switch to visual programming tab  
            for i in range(self.tabs.count()):  
                if self.tabs.widget(i) == self.visual_programming:  
                    self.tabs.setCurrentIndex(i)  
                    break  

    # Research Edition specific actions  
    def show_analytics(self):  
        """Show the advanced analytics view"""  
        if hasattr(self, 'analytics_view'):  
            # Switch to analytics tab  
            for i in range(self.tabs.count()):  
                if self.tabs.widget(i) == self.analytics_view:  
                    self.tabs.setCurrentIndex(i)  
                    break  
    

    def show_environment_editor(self):  
        """Show the environment editor"""  
        if hasattr(self, 'environment_editor'):  
            # Switch to environment editor tab  
            for i in range(self.tabs.count()):  
                if self.tabs.widget(i) == self.environment_editor:  
                    self.tabs.setCurrentIndex(i)  
                    break  

    def show_experiment_manager(self):  
        """Show the experiment manager"""  
        if hasattr(self, 'experiment_manager'):  
            # Switch to experiment manager tab  
            for i in range(self.tabs.count()):  
                if self.tabs.widget(i) == self.experiment_manager:  
                    self.tabs.setCurrentIndex(i)  
                    break  

    def export_data(self):  
        """Export data from the current experiment"""  
        if hasattr(self, 'analytics_view'):  
            self.analytics_view.export_data()  


    # Teaching Edition specific actions  
    def start_presentation(self):  
        """Start presentation mode"""  
        if self.version_manager.is_feature_enabled("presentation_mode"):  
            presentation = PresentationMode(self.version_manager, self.engine)  
            presentation.presentation_ended.connect(self.on_presentation_ended)  
            presentation.show()  
      
    def on_presentation_ended(self):  
        """Handle presentation ended event"""  
        self.statusBar().showMessage("演示模式已结束")  
      
    def show_class_manager(self):  
        """Show the class manager"""  
        if hasattr(self, 'class_manager_ui'):  
            # Switch to class manager tab  
            for i in range(self.tabs.count()):  
                if self.tabs.widget(i) == self.class_manager_ui:  
                    self.tabs.setCurrentIndex(i)  
                    break  
      
    def show_assignment_editor(self):  
        """Show the assignment editor"""  
        if hasattr(self, 'assignment_editor'):  
            # Switch to assignment editor tab  
            for i in range(self.tabs.count()):  
                if self.tabs.widget(i) == self.assignment_editor:  
                    self.tabs.setCurrentIndex(i)  
                    break
          
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