# simcereb/ui/plugin_creator.py  
import os  
import sys  
from PyQt5.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QLabel,  QHBoxLayout, 
                            QLineEdit, QComboBox, QTextEdit, QPushButton,  
                            QFileDialog, QMessageBox)  
from PyQt5.QtCore import Qt, QRegExp  
from PyQt5.QtGui import QFont  
  
class PluginCreatorWizard(QWizard):  
    """插件创建向导，引导学生创建新的插件"""  
      
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.setWindowTitle("创建新插件")  
        self.setWizardStyle(QWizard.ModernStyle)  
          
        # 添加向导页面  
        self.addPage(IntroPage())  
        self.addPage(BasicInfoPage())  
        self.addPage(PluginTypePage())  
        self.addPage(ImplementationPage())  
        self.addPage(ConclusionPage())  
          
        self.setMinimumSize(700, 500)  
          
    def accept(self):  
        """完成向导时创建插件"""  
        # 获取向导中的信息  
        plugin_name = self.field("plugin_name")  
        plugin_type = self.field("plugin_type")  
        plugin_code = self.field("plugin_code")  
          
        # 创建插件文件  
        success = self.create_plugin_file(plugin_name, plugin_type, plugin_code)  
        if success:  
            super().accept()  
          
    def create_plugin_file(self, plugin_name, plugin_type, plugin_code):  
        """创建插件文件"""  
        try:  
            # 确定插件文件路径  
            plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),   
                                    "plugins", "custom")  
              
            # 确保目录存在  
            os.makedirs(plugin_dir, exist_ok=True)  
              
            # 创建文件名  
            file_name = f"{plugin_name.lower().replace(' ', '_')}.py"  
            file_path = os.path.join(plugin_dir, file_name)  
              
            # 检查文件是否已存在  
            if os.path.exists(file_path):  
                reply = QMessageBox.question(self, "文件已存在",   
                                            f"文件 {file_name} 已存在，是否覆盖？",  
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  
                if reply == QMessageBox.No:  
                    return False  
              
            # 写入文件  
            with open(file_path, 'w', encoding='utf-8') as f:  
                f.write(plugin_code)  
                  
            # 创建配置示例  
            self.create_config_example(plugin_name, plugin_type, file_path)  
              
            QMessageBox.information(self, "插件创建成功",   
                                   f"插件已创建: {file_path}\n\n"  
                                   f"您可以在插件浏览器中找到并测试您的插件。")  
            return True  
              
        except Exception as e:  
            QMessageBox.critical(self, "创建插件失败", str(e))  
            return False  
              
    def create_config_example(self, plugin_name, plugin_type, file_path):  
        """创建配置文件示例"""  
        try:  
            # 生成类名  
            class_name = "".join(word.capitalize() for word in plugin_name.split())  
              
            # 创建配置示例文件  
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),   
                                     "configs", "examples")  
            os.makedirs(config_dir, exist_ok=True)  
              
            config_file = os.path.join(config_dir, f"{plugin_name.lower().replace(' ', '_')}_config.yaml")  
              
            with open(config_file, 'w', encoding='utf-8') as f:  
                f.write(f"""# {plugin_name} 插件配置示例  
plugins:  
  {plugin_name.lower().replace(' ', '_')}:  
    type: "{class_name}"  
    path: "{os.path.relpath(file_path, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}"  
    parameters:  
      param1: 0.0  
      param2: 1.0  
""")  
        except Exception as e:  
            print(f"创建配置示例失败: {e}")  
  
class IntroPage(QWizardPage):  
    """向导介绍页面"""  
      
    def __init__(self):  
        super().__init__()  
        self.setTitle("创建新插件")  
        self.setSubTitle("欢迎使用SimCereb插件创建向导")  
          
        layout = QVBoxLayout()  
        label = QLabel(  
            "这个向导将引导您创建一个新的SimCereb插件。\n\n"  
            "插件可以实现各种功能，如电机控制、平衡控制、步态生成等。\n\n"  
            "通过创建自定义插件，您可以实现自己的控制算法，并在SimCereb平台上进行测试和验证。\n\n"  
            "点击\"下一步\"开始创建您的插件。"  
        )  
        label.setWordWrap(True)  
        layout.addWidget(label)  
          
        self.setLayout(layout)  
  
class BasicInfoPage(QWizardPage):  
    """基本信息页面"""  
      
    def __init__(self):  
        super().__init__()  
        self.setTitle("插件基本信息")  
        self.setSubTitle("请输入插件的基本信息")  
          
        layout = QVBoxLayout()  
          
        # 插件名称  
        layout.addWidget(QLabel("插件名称:"))  
        name_edit = QLineEdit()  
        name_edit.setPlaceholderText("例如: My Balance Controller")  
        layout.addWidget(name_edit)  
        self.registerField("plugin_name*", name_edit)  
          
        # 插件描述  
        layout.addWidget(QLabel("插件描述:"))  
        desc_edit = QTextEdit()  
        desc_edit.setPlaceholderText("请描述您的插件功能和用途...")  
        layout.addWidget(desc_edit)  
        self.registerField("plugin_description", desc_edit, "plainText")  
          
        # 作者信息  
        layout.addWidget(QLabel("作者:"))  
        author_edit = QLineEdit()  
        layout.addWidget(author_edit)  
        self.registerField("plugin_author", author_edit)  
          
        self.setLayout(layout)  
  
class PluginTypePage(QWizardPage):  
    """插件类型页面"""  
      
    def __init__(self):  
        super().__init__()  
        self.setTitle("插件类型")  
        self.setSubTitle("请选择插件类型")  
          
        layout = QVBoxLayout()  
          
        # 插件类型  
        layout.addWidget(QLabel("插件类型:"))  
        type_combo = QComboBox()  
        type_combo.addItems([  
            "电机控制插件 (Motor Control)",   
            "平衡控制插件 (Balance Control)",   
            "步态生成插件 (Gait Generation)",   
            "传感器处理插件 (Sensor Processing)",   
            "逆运动学插件 (Inverse Kinematics)",  
            "自定义插件 (Custom)"  
        ])  
        layout.addWidget(type_combo)  
        self.registerField("plugin_type", type_combo, "currentText")  
          
        # 插件功能说明  
        self.type_description = QLabel()  
        self.type_description.setWordWrap(True)  
        layout.addWidget(self.type_description)  
          
        # 连接信号  
        type_combo.currentIndexChanged.connect(self.update_description)  
          
        self.setLayout(layout)  
          
        # 初始化描述  
        self.update_description(0)  
          
    def update_description(self, index):  
        """更新插件类型描述"""  
        descriptions = [  
            "电机控制插件用于实现关节电机的控制算法，如PD控制、力矩控制等。",  
            "平衡控制插件用于实现人形机器人的平衡控制算法，如ZMP控制、COM控制等。",  
            "步态生成插件用于生成人形机器人的行走步态，如CPG、ZMP轨迹规划等。",  
            "传感器处理插件用于处理各类传感器数据，如IMU、力传感器等。",  
            "逆运动学插件用于实现机器人的逆运动学计算，解决末端执行器位置到关节角度的映射。",  
            "自定义插件可以实现任何您想要的功能，完全由您自定义。"  
        ]  
        self.type_description.setText(descriptions[index])  
  
class ImplementationPage(QWizardPage):  
    """实现代码页面"""  
      
    def __init__(self):  
        super().__init__()  
        self.setTitle("插件实现")  
        self.setSubTitle("请编写插件代码或使用模板")  
          
        layout = QVBoxLayout()  
          
        # 代码编辑器  
        layout.addWidget(QLabel("插件代码:"))  
        code_edit = QTextEdit()  
        code_edit.setFont(QFont("Courier New", 10))  
        layout.addWidget(code_edit)  
          
        # 按钮布局  
        buttons_layout = QHBoxLayout()  
          
        # 添加模板按钮  
        template_button = QPushButton("使用模板")  
        template_button.clicked.connect(lambda: self.use_template(code_edit))  
        buttons_layout.addWidget(template_button)  
          
        # 导入现有文件按钮  
        import_button = QPushButton("导入文件")  
        import_button.clicked.connect(lambda: self.import_file(code_edit))  
        buttons_layout.addWidget(import_button)  
          
        layout.addLayout(buttons_layout)  
          
        self.registerField("plugin_code", code_edit, "plainText")  
        self.setLayout(layout)  
          
    def initializePage(self):  
        """页面初始化时自动使用模板"""  
        self.use_template(self.findChild(QTextEdit))  
          
    def use_template(self, code_edit):  
        """使用模板代码"""  
        template = """from simcereb.plugins.base import CerebellumPlugin  
import numpy as np  
  
class {class_name}(CerebellumPlugin):  
    \"\"\"  
    {description}  
      
    Author: {author}  
    \"\"\"  
      
    def __init__(self, config=None):  
        super().__init__(config)  
        # 初始化插件参数  
        self.enabled = True  
        # TODO: 在这里初始化您的插件参数  
          
    def initialize(self, robot, simulation):  
        \"\"\"初始化插件\"\"\"  
        self.robot = robot  
        self.simulation = simulation  
        # TODO: 在这里进行插件初始化  
          
    def update(self, dt):  
        \"\"\"更新控制输出\"\"\"  
        if not self.enabled:  
            return  
              
        # TODO: 在这里实现您的控制算法  
        # 示例: 获取机器人状态  
        # joint_states = self.robot.get_joint_states()  
        #   
        # 示例: 设置关节控制  
        # self.robot.set_joint_control(joint_id, target_position, target_velocity)  
          
    def reset(self):  
        \"\"\"重置插件状态\"\"\"  
        # TODO: 在这里重置插件状态  
        pass  
          
    def get_parameters(self):  
        \"\"\"获取插件参数\"\"\"  
        return {{  
            "param1": 0.0,  
            "param2": 1.0  
            # TODO: 添加您的参数  
        }}  
          
    def set_parameters(self, params):  
        \"\"\"设置插件参数\"\"\"  
        # TODO: 在这里处理参数更新  
        if "param1" in params:  
            self.config["param1"] = params["param1"]  
        if "param2" in params:  
            self.config["param2"] = params["param2"]  
          
    def is_enabled(self):  
        \"\"\"检查插件是否启用\"\"\"  
        return self.enabled  
          
    def enable(self):  
        \"\"\"启用插件\"\"\"  
        self.enabled = True  
          
    def disable(self):  
        \"\"\"禁用插件\"\"\"  
        self.enabled = False  
"""  
        # 获取插件名称和描述  
        plugin_name = self.wizard().field("plugin_name")  
        plugin_description = self.wizard().field("plugin_description")  
        plugin_author = self.wizard().field("plugin_author")  
          
        # 生成类名  
        class_name = "".join(word.capitalize() for word in plugin_name.split())  
          
        # 填充模板  
        filled_template = template.format(  
            class_name=class_name,  
            description=plugin_description,  
            author=plugin_author  
        )  
          
        # 设置到编辑器  
        code_edit.setPlainText(filled_template)  
          
    def import_file(self, code_edit):  
        """从文件导入代码"""  
        file_path, _ = QFileDialog.getOpenFileName(  
            self, "导入Python文件", "", "Python Files (*.py);;All Files (*)"  
        )  
          
        if file_path:  
            try:  
                with open(file_path, 'r', encoding='utf-8') as f:  
                    code_edit.setPlainText(f.read())  
            except Exception as e:  
                QMessageBox.critical(self, "导入失败", f"无法导入文件: {e}")  
  
class ConclusionPage(QWizardPage):  
    """结束页面"""  
      
    def __init__(self):  
        super().__init__()  
        self.setTitle("完成")  
        self.setSubTitle("插件创建即将完成")  
          
        layout = QVBoxLayout()  
        label = QLabel(  
            "您已经完成了插件的创建。\n\n"  
            "点击\"完成\"按钮创建插件。\n\n"  
            "创建后，您可以在插件浏览器中找到并测试您的插件，或者通过配置文件将其添加到您的仿真中。"  
        )  
        label.setWordWrap(True)  
        layout.addWidget(label)  
          
        # 配置信息  
        config_label = QLabel(  
            "系统将自动为您创建一个配置示例文件，您可以在configs/examples目录中找到它。\n"  
            "要使用您的插件，请将配置示例中的内容添加到您的配置文件中。"  
        )  
        config_label.setWordWrap(True)  
        layout.addWidget(config_label)  
          
        self.setLayout(layout)