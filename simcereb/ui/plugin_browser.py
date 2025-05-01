# simcereb/ui/plugin_browser.py  
import os  
import sys  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,   
                            QPushButton, QLabel, QGroupBox, QCheckBox,   
                            QTextEdit, QSplitter, QFileDialog, QMessageBox)  
from PyQt5.QtCore import Qt  
  
class PluginBrowser(QWidget):  
    """插件浏览器，用于管理已安装的插件"""  
      
    def __init__(self, plugin_manager, parent=None):  
        super().__init__(parent)  
        self.plugin_manager = plugin_manager  
        self.init_ui()  
          
    def init_ui(self):  
        """初始化用户界面"""  
        main_layout = QHBoxLayout()  
          
        # 创建分割器，允许用户调整左右面板的大小  
        splitter = QSplitter(Qt.Horizontal)  
          
        # 左侧插件列表面板  
        left_panel = QWidget()  
        left_layout = QVBoxLayout(left_panel)  
          
        # 插件列表标题  
        list_label = QLabel("已安装插件")  
        list_label.setStyleSheet("font-weight: bold;")  
        left_layout.addWidget(list_label)  
          
        # 插件列表  
        self.plugin_list = QListWidget()  
        self.plugin_list.currentItemChanged.connect(self.on_plugin_selected)  
        left_layout.addWidget(self.plugin_list)  
          
        # 插件操作按钮  
        buttons_layout = QHBoxLayout()  
          
        self.refresh_button = QPushButton("刷新")  
        self.refresh_button.clicked.connect(self.refresh_plugin_list)  
        buttons_layout.addWidget(self.refresh_button)  
          
        self.import_button = QPushButton("导入")  
        self.import_button.clicked.connect(self.import_plugin)  
        buttons_layout.addWidget(self.import_button)  
          
        left_layout.addLayout(buttons_layout)  
          
        # 右侧插件详情面板  
        right_panel = QWidget()  
        right_layout = QVBoxLayout(right_panel)  
          
        # 插件详情标题  
        self.plugin_name_label = QLabel("选择一个插件查看详情")  
        self.plugin_name_label.setStyleSheet("font-size: 14px; font-weight: bold;")  
        right_layout.addWidget(self.plugin_name_label)  
          
        # 插件描述  
        description_group = QGroupBox("描述")  
        description_layout = QVBoxLayout(description_group)  
        self.description_text = QTextEdit()  
        self.description_text.setReadOnly(True)  
        description_layout.addWidget(self.description_text)  
        right_layout.addWidget(description_group)  
          
        # 插件状态控制  
        status_group = QGroupBox("状态")  
        status_layout = QVBoxLayout(status_group)  
        self.enabled_checkbox = QCheckBox("启用")  
        self.enabled_checkbox.toggled.connect(self.on_plugin_toggled)  
        status_layout.addWidget(self.enabled_checkbox)  
        right_layout.addWidget(status_group)  
          
        # 插件操作按钮  
        detail_buttons_layout = QHBoxLayout()  
          
        self.configure_button = QPushButton("配置")  
        self.configure_button.clicked.connect(self.on_configure_clicked)  
        detail_buttons_layout.addWidget(self.configure_button)  
          
        self.edit_button = QPushButton("编辑")  
        self.edit_button.clicked.connect(self.on_edit_clicked)  
        detail_buttons_layout.addWidget(self.edit_button)  
          
        self.test_button = QPushButton("测试")  
        self.test_button.clicked.connect(self.on_test_clicked)  
        detail_buttons_layout.addWidget(self.test_button)  
          
        self.delete_button = QPushButton("删除")  
        self.delete_button.clicked.connect(self.on_delete_clicked)  
        self.delete_button.setStyleSheet("color: red;")  
        detail_buttons_layout.addWidget(self.delete_button)  
          
        right_layout.addLayout(detail_buttons_layout)  
          
        # 添加面板到分割器  
        splitter.addWidget(left_panel)  
        splitter.addWidget(right_panel)  
          
        # 设置初始分割比例  
        splitter.setSizes([200, 400])  
          
        # 添加分割器到主布局  
        main_layout.addWidget(splitter)  
          
        self.setLayout(main_layout)  
          
        # 初始化插件列表  
        self.refresh_plugin_list()  
          
        # 初始化按钮状态  
        self.update_button_states(False)  
          
    def refresh_plugin_list(self):  
        """刷新插件列表"""  
        self.plugin_list.clear()  
          
        # 添加内置插件  
        built_in_plugins = self.get_built_in_plugins()  
        for plugin_name in built_in_plugins:  
            self.plugin_list.addItem(f"[内置] {plugin_name}")  
              
        # 添加自定义插件  
        custom_plugins = self.get_custom_plugins()  
        for plugin_name in custom_plugins:  
            self.plugin_list.addItem(f"[自定义] {plugin_name}")  
              
        # 添加当前加载的插件  
        for plugin_name in self.plugin_manager.plugins.keys():  
            # 检查是否已经在列表中  
            found = False  
            for i in range(self.plugin_list.count()):  
                item_text = self.plugin_list.item(i).text()  
                if plugin_name in item_text:  
                    found = True  
                    break  
                      
            if not found:  
                self.plugin_list.addItem(plugin_name)  
                  
    def get_built_in_plugins(self):  
        """获取内置插件列表"""  
        # 获取插件目录  
        plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins")  
          
        # 排除这些文件和目录  
        exclude = ["__init__.py", "__pycache__", "base.py", "custom"]  
          
        # 查找所有插件文件  
        plugins = []  
        for file in os.listdir(plugin_dir):  
            if file.endswith(".py") and file not in exclude:  
                plugins.append(file[:-3])  # 移除 .py 后缀  
                  
        return plugins  
          
    def get_custom_plugins(self):  
        """获取自定义插件列表"""  
        # 获取自定义插件目录  
        custom_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),   
                                 "plugins", "custom")  
          
        # 检查目录是否存在  
        if not os.path.exists(custom_dir):  
            return []  
              
        # 排除这些文件和目录  
        exclude = ["__init__.py", "__pycache__"]  
          
        # 查找所有插件文件  
        plugins = []  
        for file in os.listdir(custom_dir):  
            if file.endswith(".py") and file not in exclude:  
                plugins.append(file[:-3])  # 移除 .py 后缀  
                  
        return plugins  
          
    def on_plugin_selected(self, current, previous):  
        """当选择插件时更新详情面板"""  
        if current is None:  
            self.update_button_states(False)  
            return  
              
        # 解析插件名称  
        item_text = current.text()  
        if "[内置]" in item_text:  
            plugin_name = item_text.replace("[内置] ", "")  
            is_built_in = True  
        elif "[自定义]" in item_text:  
            plugin_name = item_text.replace("[自定义] ", "")  
            is_built_in = False  
        else:  
            plugin_name = item_text  
            is_built_in = False  
              
        # 获取插件实例  
        plugin = self.plugin_manager.get_plugin(plugin_name)  
          
        # 更新详情面板  
        self.plugin_name_label.setText(f"插件: {plugin_name}")  
          
        if plugin:  
            # 插件已加载  
            self.description_text.setPlainText(self.get_plugin_description(plugin))  
            self.enabled_checkbox.setChecked(plugin.is_enabled())  
            self.enabled_checkbox.setEnabled(True)  
        else:  
            # 插件未加载  
            self.description_text.setPlainText("此插件尚未加载。\n\n点击\"配置\"按钮将其添加到配置文件中。")  
            self.enabled_checkbox.setChecked(False)  
            self.enabled_checkbox.setEnabled(False)  
              
        # 更新按钮状态  
        self.update_button_states(True, is_built_in)  
          
    def get_plugin_description(self, plugin):  
        """获取插件描述"""  
        doc = plugin.__class__.__doc__  
        if doc:  
            return doc.strip()  
        else:  
            return "没有描述信息。"  
              
    def update_button_states(self, selected, is_built_in=False):  
        """更新按钮状态"""  
        self.configure_button.setEnabled(selected)  
        self.test_button.setEnabled(selected)  
          
        # 内置插件不能编辑或删除  
        self.edit_button.setEnabled(selected and not is_built_in)  
        self.delete_button.setEnabled(selected and not is_built_in)  
          
    def on_plugin_toggled(self, checked):  
        """启用或禁用插件"""  
        current_item = self.plugin_list.currentItem()  
        if current_item:  
            # 解析插件名称  
            item_text = current_item.text()  
            if "[内置]" in item_text:  
                plugin_name = item_text.replace("[内置] ", "")  
            elif "[自定义]" in item_text:  
                plugin_name = item_text.replace("[自定义] ", "")  
            else:  
                plugin_name = item_text  
                  
            # 获取插件实例  
            plugin = self.plugin_manager.get_plugin(plugin_name)  
            if plugin:  
                if checked:  
                    plugin.enable()  
                else:  
                    plugin.disable()  
                      
    def on_configure_clicked(self):  
        """打开插件配置对话框"""  
        current_item = self.plugin_list.currentItem()  
        if current_item:  
            # 解析插件名称  
            item_text = current_item.text()  
            if "[内置]" in item_text:  
                plugin_name = item_text.replace("[内置] ", "")  
            elif "[自定义]" in item_text:  
                plugin_name = item_text.replace("[自定义] ", "")  
            else:  
                plugin_name = item_text  
                  
            # 这里应该打开配置对话框  
            # 在实际实现中，可能需要创建一个配置对话框类  
            QMessageBox.information(self, "配置插件",   
                                   f"将打开 {plugin_name} 的配置对话框。\n\n"  
                                   "此功能尚未实现。")  
              
    def on_edit_clicked(self):  
        """打开插件编辑器"""  
        current_item = self.plugin_list.currentItem()  
        if current_item:  
            # 解析插件名称  
            item_text = current_item.text()  
            if "[自定义]" in item_text:  
                plugin_name = item_text.replace("[自定义] ", "")  
                  
                # 获取插件文件路径  
                plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),   
                                         "plugins", "custom")  
                plugin_file = os.path.join(plugin_dir, f"{plugin_name}.py")  
                  
                # 检查文件是否存在  
                if os.path.exists(plugin_file):  
                    # 这里应该打开编辑器  
                    # 在实际实现中，可能需要创建一个编辑器窗口或使用外部编辑器  
                    QMessageBox.information(self, "编辑插件",   
                                           f"将打开 {plugin_file} 进行编辑。\n\n"  
                                           "此功能尚未实现。")  
                else:  
                    QMessageBox.warning(self, "文件不存在",   
                                       f"插件文件 {plugin_file} 不存在。")  
              
    def on_test_clicked(self):  
        """打开插件测试工具"""  
        current_item = self.plugin_list.currentItem()  
        if current_item:  
            # 解析插件名称  
            item_text = current_item.text()  
            if "[内置]" in item_text:  
                plugin_name = item_text.replace("[内置] ", "")  
            elif "[自定义]" in item_text:  
                plugin_name = item_text.replace("[自定义] ", "")  
            else:  
                plugin_name = item_text  
                  
            # 这里应该打开测试工具  
            # 在实际实现中，可能需要创建一个测试工具窗口  
            QMessageBox.information(self, "测试插件",   
                                   f"将打开 {plugin_name} 的测试工具。\n\n"  
                                   "此功能尚未实现。")  
              
    def on_delete_clicked(self):  
        """删除插件"""  
        current_item = self.plugin_list.currentItem()  
        if current_item:  
            # 解析插件名称  
            item_text = current_item.text()  
            if "[自定义]" in item_text:  
                plugin_name = item_text.replace("[自定义] ", "")  
                
                # 确认删除  
                reply = QMessageBox.question(self, "确认删除",   
                                            f"确定要删除插件 {plugin_name} 吗？\n\n"  
                                            "此操作不可撤销。",  
                                            QMessageBox.Yes | QMessageBox.No,   
                                            QMessageBox.No)  
                
                if reply == QMessageBox.Yes:  
                    # 获取插件文件路径  
                    plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),   
                                            "plugins", "custom")  
                    plugin_file = os.path.join(plugin_dir, f"{plugin_name}.py")  
                    
                    # 尝试删除文件  
                    try:  
                        # 如果插件已加载，先卸载它  
                        if plugin_name in self.plugin_manager.plugins:  
                            del self.plugin_manager.plugins[plugin_name]  
                            
                        # 删除文件  
                        if os.path.exists(plugin_file):  
                            os.remove(plugin_file)  
                            
                        # 删除配置示例文件（如果存在）  
                        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),   
                                                "configs", "examples")  
                        config_file = os.path.join(config_dir, f"{plugin_name.lower().replace(' ', '_')}_config.yaml")  
                        if os.path.exists(config_file):  
                            os.remove(config_file)  
                            
                        # 刷新插件列表  
                        self.refresh_plugin_list()  
                        
                        # 清空详情面板  
                        self.plugin_name_label.setText("选择一个插件查看详情")  
                        self.description_text.clear()  
                        self.enabled_checkbox.setChecked(False)  
                        self.enabled_checkbox.setEnabled(False)  
                        self.update_button_states(False)  
                        
                        QMessageBox.information(self, "删除成功", f"插件 {plugin_name} 已成功删除。")  
                    except Exception as e:  
                        QMessageBox.critical(self, "删除失败", f"无法删除插件: {e}")  
  
    def import_plugin(self):  
        """导入外部插件"""  
        file_path, _ = QFileDialog.getOpenFileName(  
            self, "导入插件文件", "", "Python Files (*.py);;All Files (*)"  
        )  
        
        if file_path:  
            try:  
                # 获取目标目录  
                plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),   
                                        "plugins", "custom")  
                os.makedirs(plugin_dir, exist_ok=True)  
                
                # 获取文件名  
                file_name = os.path.basename(file_path)  
                
                # 目标路径  
                target_path = os.path.join(plugin_dir, file_name)  
                
                # 检查文件是否已存在  
                if os.path.exists(target_path):  
                    reply = QMessageBox.question(self, "文件已存在",   
                                                f"文件 {file_name} 已存在，是否覆盖？",  
                                                QMessageBox.Yes | QMessageBox.No,   
                                                QMessageBox.No)  
                    if reply == QMessageBox.No:  
                        return  
                
                # 复制文件  
                import shutil  
                shutil.copy2(file_path, target_path)  
                
                # 刷新插件列表  
                self.refresh_plugin_list()  
                
                QMessageBox.information(self, "导入成功", f"插件 {file_name} 已成功导入。")  
            except Exception as e:  
                QMessageBox.critical(self, "导入失败", f"无法导入插件: {e}")