# simcereb/ui/plugin_tester.py  
import os  
import sys  
import time  
import numpy as np  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                            QLabel, QComboBox, QTableWidget, QTableWidgetItem,  
                            QHeaderView, QSlider, QDoubleSpinBox, QGroupBox,  
                            QCheckBox, QProgressBar, QSplitter, QTextEdit)  
from PyQt5.QtCore import Qt, QTimer, pyqtSignal  
from PyQt5.QtGui import QColor  
  
class PluginTester(QWidget):  
    """插件测试工具，用于测试插件的功能和性能"""  
      
    # 定义信号  
    test_started = pyqtSignal(str)  # 测试开始信号，参数为插件名称  
    test_stopped = pyqtSignal(str)  # 测试结束信号，参数为插件名称  
      
    def __init__(self, engine, parent=None):  
        super().__init__(parent)  
        self.engine = engine  
        self.current_plugin = None  
        self.test_running = False  
        self.test_start_time = 0  
        self.test_metrics = {}  
        self.init_ui()  
          
        # 创建定时器用于更新数据  
        self.update_timer = QTimer(self)  
        self.update_timer.timeout.connect(self.update_data)  
        self.update_timer.start(100)  # 每100ms更新一次  
          
    def init_ui(self):  
        """初始化用户界面"""  
        main_layout = QVBoxLayout()  
          
        # 创建分割器，允许用户调整上下面板的大小  
        splitter = QSplitter(Qt.Vertical)  
          
        # 上部面板 - 插件选择和控制  
        top_panel = QWidget()  
        top_layout = QVBoxLayout(top_panel)  
          
        # 插件选择和测试控制  
        control_layout = QHBoxLayout()  
          
        # 插件选择  
        plugin_group = QGroupBox("插件选择")  
        plugin_layout = QVBoxLayout(plugin_group)  
          
        select_layout = QHBoxLayout()  
        select_layout.addWidget(QLabel("选择插件:"))  
        self.plugin_combo = QComboBox()  
        self.plugin_combo.currentIndexChanged.connect(self.on_plugin_selected)  
        select_layout.addWidget(self.plugin_combo)  
        plugin_layout.addLayout(select_layout)  
          
        # 插件描述  
        self.plugin_description = QLabel("请选择一个插件进行测试")  
        self.plugin_description.setWordWrap(True)  
        plugin_layout.addWidget(self.plugin_description)  
          
        control_layout.addWidget(plugin_group, 3)  
          
        # 测试控制  
        test_group = QGroupBox("测试控制")  
        test_layout = QVBoxLayout(test_group)  
          
        buttons_layout = QHBoxLayout()  
          
        self.test_button = QPushButton("开始测试")  
        self.test_button.clicked.connect(self.toggle_test)  
        buttons_layout.addWidget(self.test_button)  
          
        self.reset_button = QPushButton("重置")  
        self.reset_button.clicked.connect(self.reset_test)  
        buttons_layout.addWidget(self.reset_button)  
          
        test_layout.addLayout(buttons_layout)  
          
        # 测试进度  
        progress_layout = QHBoxLayout()  
        progress_layout.addWidget(QLabel("测试进度:"))  
        self.progress_bar = QProgressBar()  
        self.progress_bar.setRange(0, 100)  
        self.progress_bar.setValue(0)  
        progress_layout.addWidget(self.progress_bar)  
        test_layout.addLayout(progress_layout)  
          
        # 测试状态  
        self.status_label = QLabel("就绪")  
        test_layout.addWidget(self.status_label)  
          
        control_layout.addWidget(test_group, 2)  
          
        top_layout.addLayout(control_layout)  
          
        # 参数调整区域  
        params_group = QGroupBox("插件参数")  
        params_layout = QVBoxLayout(params_group)  
        self.params_table = QTableWidget(0, 3)  
        self.params_table.setHorizontalHeaderLabels(["参数名", "值", "调整"])  
        self.params_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        params_layout.addWidget(self.params_table)  
        top_layout.addWidget(params_group)  
          
        # 添加上部面板到分割器  
        splitter.addWidget(top_panel)  
          
        # 下部面板 - 测试结果  
        bottom_panel = QWidget()  
        bottom_layout = QVBoxLayout(bottom_panel)  
          
        # 测试结果区域  
        results_group = QGroupBox("测试结果")  
        results_layout = QVBoxLayout(results_group)  
          
        # 性能指标表格  
        self.results_table = QTableWidget(0, 2)  
        self.results_table.setHorizontalHeaderLabels(["指标", "值"])  
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        results_layout.addWidget(self.results_table)  
          
        # 测试日志  
        log_layout = QVBoxLayout()  
        log_layout.addWidget(QLabel("测试日志:"))  
        self.log_text = QTextEdit()  
        self.log_text.setReadOnly(True)  
        log_layout.addWidget(self.log_text)  
        results_layout.addLayout(log_layout)  
          
        bottom_layout.addWidget(results_group)  
          
        # 添加下部面板到分割器  
        splitter.addWidget(bottom_panel)  
          
        # 设置初始分割比例  
        splitter.setSizes([400, 300])  
          
        # 添加分割器到主布局  
        main_layout.addWidget(splitter)  
          
        self.setLayout(main_layout)  
          
        # 初始化插件列表  
        self.refresh_plugin_list()  
          
    def refresh_plugin_list(self):  
        """刷新插件列表"""  
        self.plugin_combo.clear()  
        for plugin_name in self.engine.plugin_manager.plugins.keys():  
            self.plugin_combo.addItem(plugin_name)  
              
    def on_plugin_selected(self, index):  
        """当选择插件时更新界面"""  
        if index < 0:  
            self.current_plugin = None  
            self.plugin_description.setText("请选择一个插件进行测试")  
            return  
              
        plugin_name = self.plugin_combo.currentText()  
        self.current_plugin = self.engine.plugin_manager.get_plugin(plugin_name)  
          
        if self.current_plugin:  
            # 更新插件描述  
            doc = self.current_plugin.__class__.__doc__  
            self.plugin_description.setText(doc.strip() if doc else "没有描述信息。")  
              
            # 更新参数表格  
            self.update_params_table()  
              
            # 更新状态  
            self.status_label.setText(f"已选择插件: {plugin_name}")  
              
            # 添加日志  
            self.log_text.append(f"已选择插件: {plugin_name}")  
              
    def update_params_table(self):  
        """更新参数表格"""  
        self.params_table.setRowCount(0)  
          
        if not self.current_plugin:  
            return  
              
        params = self.current_plugin.get_parameters()  
          
        for i, (param_name, param_value) in enumerate(params.items()):  
            self.params_table.insertRow(i)  
              
            # 参数名  
            name_item = QTableWidgetItem(param_name)  
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  
            self.params_table.setItem(i, 0, name_item)  
              
            # 参数值  
            value_item = QTableWidgetItem(str(param_value))  
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)  
            self.params_table.setItem(i, 1, value_item)  
              
            # 参数调整控件  
            param_widget = QWidget()  
            param_layout = QHBoxLayout(param_widget)  
            param_layout.setContentsMargins(0, 0, 0, 0)  
              
            if isinstance(param_value, (int, float)):  
                slider = QSlider(Qt.Horizontal)  
                slider.setMinimum(0)  
                slider.setMaximum(100)  
                slider.setValue(int(param_value * 10) if param_value <= 10 else 100)  
                  
                spinbox = QDoubleSpinBox()  
                spinbox.setMinimum(-1000)  
                spinbox.setMaximum(1000)  
                spinbox.setValue(param_value)  
                spinbox.setSingleStep(0.1)  
                  
                # 连接信号  
                slider.valueChanged.connect(  
                    lambda v, sb=spinbox: sb.setValue(v / 10)  
                )  
                spinbox.valueChanged.connect(  
                    lambda v, s=slider, pn=param_name: self.update_param_value(pn, v, s)  
                )  
                  
                param_layout.addWidget(slider)  
                param_layout.addWidget(spinbox)  
            elif isinstance(param_value, bool):  
                checkbox = QCheckBox()  
                checkbox.setChecked(param_value)  
                checkbox.stateChanged.connect(  
                    lambda state, pn=param_name: self.update_param_value(pn, state == Qt.Checked)  
                )  
                param_layout.addWidget(checkbox)  
            else:  
                # 对于非数值类型，显示一个标签  
                param_layout.addWidget(QLabel("不可调整"))  
                  
            self.params_table.setCellWidget(i, 2, param_widget)  
              
    def update_param_value(self, param_name, value, slider=None):  
        """更新参数值"""  
        if not self.current_plugin:  
            return  
              
        # 更新插件参数  
        params = {param_name: value}  
        self.current_plugin.set_parameters(params)  
          
        # 更新滑块位置（如果提供）  
        if slider and isinstance(value, (int, float)) and value <= 10:  
            slider.setValue(int(value * 10))  
              
        # 更新表格中的值  
        for i in range(self.params_table.rowCount()):  
            if self.params_table.item(i, 0).text() == param_name:  
                self.params_table.item(i, 1).setText(str(value))  
                break  
                  
        # 添加日志  
        self.log_text.append(f"参数 {param_name} 已更新为 {value}")  
          
    def toggle_test(self):  
        """开始或停止测试"""  
        if not self.test_running:  
            self.start_test()  
        else:  
            self.stop_test()  
              
    def start_test(self):  
        """开始测试"""  
        if not self.current_plugin:  
            self.status_label.setText("错误: 未选择插件")  
            return  
              
        self.test_running = True  
        self.test_button.setText("停止测试")  
        self.status_label.setText("测试运行中...")  
        self.test_start_time = time.time()  
          
        # 初始化进度条  
        self.progress_bar.setValue(0)  
          
        # 初始化结果表格  
        self.results_table.setRowCount(5)  
          
        # 添加基本指标  
        metrics = ["执行时间 (ms)", "CPU 使用率 (%)", "内存使用 (MB)", "稳定性 (%)", "性能评分"]  
        for i, metric in enumerate(metrics):  
            name_item = QTableWidgetItem(metric)  
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  
            self.results_table.setItem(i, 0, name_item)  
              
            value_item = QTableWidgetItem("0")  
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)  
            self.results_table.setItem(i, 1, value_item)  
              
        # 初始化测试指标  
        self.test_metrics = {  
            "execution_time": [],  
            "cpu_usage": [],  
            "memory_usage": [],  
            "stability": 100.0,  
            "score": 0.0  
        }  
          
        # 添加日志  
        self.log_text.append(f"开始测试插件: {self.plugin_combo.currentText()}")  
          
        # 发出测试开始信号  
        self.test_started.emit(self.plugin_combo.currentText())  
          
    def stop_test(self):  
        """停止测试"""  
        if not self.test_running:  
            return  
            
        self.test_running = False  
        self.test_button.setText("开始测试")  
        self.status_label.setText("测试已停止")  
        
        # 计算最终评分  
        if len(self.test_metrics["execution_time"]) > 0:  
            avg_time = sum(self.test_metrics["execution_time"]) / len(self.test_metrics["execution_time"])  
            avg_cpu = sum(self.test_metrics["cpu_usage"]) / len(self.test_metrics["cpu_usage"])  
            avg_memory = sum(self.test_metrics["memory_usage"]) / len(self.test_metrics["memory_usage"])  
            
            # 简单的评分算法，可以根据需要调整  
            score = 100.0 - (avg_time * 10) - (avg_cpu * 0.5) - (avg_memory * 0.1)  
            score = max(0, min(100, score))  
            self.test_metrics["score"] = score  
            
            # 更新结果表格  
            self.results_table.item(4, 1).setText(f"{score:.1f}")  
            
        # 添加日志  
        self.log_text.append(f"测试已停止，总时长: {time.time() - self.test_start_time:.2f}秒")  
        
        # 发出测试结束信号  
        self.test_stopped.emit(self.plugin_combo.currentText())  
    
    def reset_test(self):  
        """重置测试"""  
        # 停止测试（如果正在运行）  
        if self.test_running:  
            self.stop_test()  
        
        # 重置插件  
        if self.current_plugin:  
            self.current_plugin.reset()  
            
            # 更新参数表格  
            self.update_params_table()  
            
            # 清空结果表格  
            self.results_table.setRowCount(0)  
            
            # 重置进度条  
            self.progress_bar.setValue(0)  
            
            # 更新状态  
            self.status_label.setText("测试已重置")  
            
            # 添加日志  
            self.log_text.append(f"插件 {self.plugin_combo.currentText()} 已重置")  
            
    def update_data(self):  
        """更新测试数据"""  
        if self.test_running and self.current_plugin:  
            # 更新测试进度  
            elapsed_time = time.time() - self.test_start_time  
            progress = min(100, int(elapsed_time / 10 * 100))  # 假设测试持续10秒  
            self.progress_bar.setValue(progress)  
            
            # 在实际应用中，这里应该获取真实的性能数据  
            # 这里只是模拟一些随机数据  
            import random  
            
            # 模拟执行时间  
            execution_time = random.uniform(0.1, 5.0)  
            self.test_metrics["execution_time"].append(execution_time)  
            
            # 模拟CPU使用率  
            cpu_usage = random.uniform(1, 10)  
            self.test_metrics["cpu_usage"].append(cpu_usage)  
            
            # 模拟内存使用  
            memory_usage = random.uniform(10, 50)  
            self.test_metrics["memory_usage"].append(memory_usage)  
            
            # 模拟稳定性  
            stability = 100.0 - (len(self.test_metrics["execution_time"]) * 0.5)  
            stability = max(0, stability)  
            self.test_metrics["stability"] = stability  
            
            # 更新结果表格  
            if self.results_table.rowCount() >= 5:  
                self.results_table.item(0, 1).setText(f"{execution_time:.2f}")  
                self.results_table.item(1, 1).setText(f"{cpu_usage:.1f}")  
                self.results_table.item(2, 1).setText(f"{memory_usage:.1f}")  
                self.results_table.item(3, 1).setText(f"{stability:.1f}")  
                
                # 实时计算评分  
                if len(self.test_metrics["execution_time"]) > 0:  
                    avg_time = sum(self.test_metrics["execution_time"]) / len(self.test_metrics["execution_time"])  
                    avg_cpu = sum(self.test_metrics["cpu_usage"]) / len(self.test_metrics["cpu_usage"])  
                    avg_memory = sum(self.test_metrics["memory_usage"]) / len(self.test_metrics["memory_usage"])  
                    
                    score = 100.0 - (avg_time * 10) - (avg_cpu * 0.5) - (avg_memory * 0.1)  
                    score = max(0, min(100, score))  
                    self.test_metrics["score"] = score  
                    
                    self.results_table.item(4, 1).setText(f"{score:.1f}")  
            
            # 如果进度达到100%，自动停止测试  
            if progress >= 100:  
                self.stop_test()