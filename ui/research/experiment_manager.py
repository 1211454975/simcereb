# simcereb/ui/research/experiment_manager.py  
"""  
Experiment manager for the Research Edition  
Provides tools for managing and running batch experiments  
"""  
  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                            QLabel, QTableWidget, QTableWidgetItem, QHeaderView,  
                            QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,  
                            QGroupBox, QFormLayout, QProgressBar, QMessageBox)  
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QMutex  
from PyQt5.QtGui import QFont, QIcon  
  
from ..common.version_ui import VersionSpecificWidget  
  
class ExperimentWorker(QThread):  
    """Worker thread for running experiments"""  
      
    # Signals  
    progress_updated = pyqtSignal(int, int)  # (experiment_index, progress)  
    experiment_completed = pyqtSignal(int, dict)  # (experiment_index, results)  
    all_completed = pyqtSignal()  
      
    def __init__(self, experiments, simulation_engine):  
        """  
        Initialize the experiment worker  
          
        Args:  
            experiments (list): List of experiment configurations  
            simulation_engine: SimulationEngine instance  
        """  
        super().__init__()  
        self.experiments = experiments  
        self.simulation_engine = simulation_engine  
        self.mutex = QMutex()  
        self.abort = False  
      
    def run(self):  
        """Run the experiments"""  
        for i, experiment in enumerate(self.experiments):  
            # Check if abort requested  
            self.mutex.lock()  
            if self.abort:  
                self.mutex.unlock()  
                break  
            self.mutex.unlock()  
              
            # Run experiment  
            results = self._run_experiment(experiment)  
              
            # Emit progress  
            self.progress_updated.emit(i, 100)  
              
            # Emit results  
            self.experiment_completed.emit(i, results)  
          
        # Emit all completed signal  
        self.all_completed.emit()  
      
    def stop(self):  
        """Stop the experiments"""  
        self.mutex.lock()  
        self.abort = True  
        self.mutex.unlock()  
      
    def _run_experiment(self, experiment):  
        """  
        Run a single experiment  
          
        Args:  
            experiment (dict): Experiment configuration  
              
        Returns:  
            dict: Experiment results  
        """  
        # This would be implemented to run the experiment using the simulation engine  
        # For now, just return some sample results  
        import time  
        import random  
          
        # Simulate experiment running  
        total_steps = 100  
        for step in range(total_steps):  
            # Check if abort requested  
            self.mutex.lock()  
            if self.abort:  
                self.mutex.unlock()  
                return {"status": "aborted"}  
            self.mutex.unlock()  
              
            # Simulate work  
            time.sleep(0.05)  
              
            # Update progress  
            progress = int((step + 1) / total_steps * 100)  
            self.progress_updated.emit(self.experiments.index(experiment), progress)  
          
        # Generate sample results  
        return {  
            "status": "completed",  
            "metrics": {  
                "balance_time": random.uniform(5.0, 30.0),  
                "energy_consumption": random.uniform(50.0, 200.0),  
                "stability_score": random.uniform(0.5, 1.0)  
            }  
        }  
  
class ExperimentManager(VersionSpecificWidget):  
    """  
    Experiment manager for batch experiments  
    """  
      
    def __init__(self, version_manager, simulation_engine=None, parent=None):  
        """  
        Initialize the experiment manager  
          
        Args:  
            version_manager: VersionManager instance  
            simulation_engine: SimulationEngine instance  
            parent: Parent widget  
        """  
        super().__init__(version_manager, parent)  
        self.simulation_engine = simulation_engine  
        self.experiments = []  
        self.experiment_worker = None  
        self.init_ui()  
      
    def init_ui(self):  
        """Initialize the user interface"""  
        # Main layout  
        main_layout = QVBoxLayout(self)  
          
        # Header  
        header_layout = QHBoxLayout()  
        title_label = QLabel("实验管理器")  
        title_label.setFont(QFont("Arial", 18, QFont.Bold))  
        header_layout.addWidget(title_label)  
        header_layout.addStretch()  
          
        # Experiment controls  
        add_button = QPushButton("添加实验")  
        add_button.clicked.connect(self.add_experiment)  
        header_layout.addWidget(add_button)  
          
        remove_button = QPushButton("删除实验")  
        remove_button.clicked.connect(self.remove_experiment)  
        header_layout.addWidget(remove_button)  
          
        run_button = QPushButton("运行实验")  
        run_button.clicked.connect(self.run_experiments)  
        header_layout.addWidget(run_button)  
          
        stop_button = QPushButton("停止实验")  
        stop_button.clicked.connect(self.stop_experiments)  
        header_layout.addWidget(stop_button)  
          
        main_layout.addLayout(header_layout)  
          
        # Experiment table  
        self.experiment_table = QTableWidget()  
        self.experiment_table.setColumnCount(5)  
        self.experiment_table.setHorizontalHeaderLabels(["名称", "插件", "参数", "进度", "状态"])  
        self.experiment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        self.experiment_table.setSelectionBehavior(QTableWidget.SelectRows)  
        main_layout.addWidget(self.experiment_table)  
          
        # Parameter configuration  
        param_group = QGroupBox("参数配置")  
        param_layout = QFormLayout(param_group)  
          
        # Plugin selection  
        self.plugin_combo = QComboBox()  
        self.populate_plugin_combo()  
        param_layout.addRow("插件:", self.plugin_combo)  

        # Parameter grid  
        self.param_table = QTableWidget()  
        self.param_table.setColumnCount(4)  
        self.param_table.setHorizontalHeaderLabels(["参数名", "起始值", "结束值", "步长"])  
        self.param_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        param_layout.addRow("参数扫描:", self.param_table)  
          
        # Add parameter button  
        add_param_button = QPushButton("添加参数")  
        add_param_button.clicked.connect(self.add_parameter)  
        param_layout.addRow("", add_param_button)  
          
        # Experiment name  
        self.experiment_name_edit = QLineEdit()  
        self.experiment_name_edit.setText("实验_" + datetime.now().strftime("%Y%m%d_%H%M%S"))  
        param_layout.addRow("实验名称:", self.experiment_name_edit)  
          
        # Repetitions  
        self.repetitions_spin = QSpinBox()  
        self.repetitions_spin.setRange(1, 100)  
        self.repetitions_spin.setValue(3)  
        param_layout.addRow("重复次数:", self.repetitions_spin)  
          
        # Add experiment button  
        add_experiment_button = QPushButton("添加到实验列表")  
        add_experiment_button.clicked.connect(self.add_experiment_from_params)  
        param_layout.addRow("", add_experiment_button)  
          
        main_layout.addWidget(param_group)  
          
        # Results group  
        results_group = QGroupBox("实验结果")  
        results_layout = QVBoxLayout(results_group)  
          
        # Results table  
        self.results_table = QTableWidget()  
        self.results_table.setColumnCount(5)  
        self.results_table.setHorizontalHeaderLabels(["实验", "平衡时间", "能量消耗", "稳定性得分", "状态"])  
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        results_layout.addWidget(self.results_table)  
          
        # Export results button  
        export_button = QPushButton("导出结果")  
        export_button.clicked.connect(self.export_results)  
        results_layout.addWidget(export_button)  
          
        main_layout.addWidget(results_group)  


    def populate_plugin_combo(self):  
        """Populate the plugin combo box with available plugins"""  
        self.plugin_combo.clear()  
          
        if self.simulation_engine and hasattr(self.simulation_engine, 'plugin_manager'):  
            plugins = self.simulation_engine.plugin_manager.get_plugins()  
            for plugin_name in plugins:  
                self.plugin_combo.addItem(plugin_name)  
        else:  
            # Add sample plugins for demonstration  
            self.plugin_combo.addItem("平衡控制插件")  
            self.plugin_combo.addItem("步态生成插件")  
            self.plugin_combo.addItem("传感器融合插件")  

    def add_parameter(self):  
        """Add a parameter to the parameter table"""  
        row = self.param_table.rowCount()  
        self.param_table.insertRow(row)  
          
        # Parameter name  
        name_item = QTableWidgetItem("参数_" + str(row + 1))  
        self.param_table.setItem(row, 0, name_item)  
          
        # Start value  
        start_item = QTableWidgetItem("0.0")  
        self.param_table.setItem(row, 1, start_item)  
          
        # End value  
        end_item = QTableWidgetItem("1.0")  
        self.param_table.setItem(row, 2, end_item)  
          
        # Step  
        step_item = QTableWidgetItem("0.1")  
        self.param_table.setItem(row, 3, step_item)  

    def add_experiment_from_params(self):  
        """Add an experiment based on current parameter settings"""  
        # Get plugin  
        plugin_name = self.plugin_combo.currentText()  
        if not plugin_name:  
            QMessageBox.warning(self, "添加实验", "请选择插件")  
            return  
          
        # Get parameters  
        parameters = []  
        for row in range(self.param_table.rowCount()):  
            param_name = self.param_table.item(row, 0).text()  
            start_value = float(self.param_table.item(row, 1).text())  
            end_value = float(self.param_table.item(row, 2).text())  
            step = float(self.param_table.item(row, 3).text())  
              
            parameters.append({  
                "name": param_name,  
                "start": start_value,  
                "end": end_value,  
                "step": step  
            })  
          
        # Generate experiment configurations  
        experiment_configs = self._generate_experiment_configs(  
            self.experiment_name_edit.text(),  
            plugin_name,  
            parameters,  
            self.repetitions_spin.value()  
        )  
          
        # Add to experiment list  
        for config in experiment_configs:  
            self.add_experiment_to_table(config)  

    def _generate_experiment_configs(self, base_name, plugin_name, parameters, repetitions):  
        """  
        Generate experiment configurations based on parameter ranges  
          
        Args:  
            base_name (str): Base name for the experiments  
            plugin_name (str): Name of the plugin to use  
            parameters (list): List of parameter configurations  
            repetitions (int): Number of repetitions for each configuration  
              
        Returns:  
            list: List of experiment configurations  
        """  
        # This is a simplified implementation that generates all combinations of parameters  
        # In a real implementation, this would be more sophisticated  
          
        configs = []  
          
        # If no parameters, just create a single experiment  
        if not parameters:  
            for i in range(repetitions):  
                configs.append({  
                    "name": f"{base_name}_{i+1}",  
                    "plugin": plugin_name,  
                    "parameters": {},  
                    "repetition": i+1  
                })  
            return configs  
          
        # Generate parameter combinations  
        param_values = []  
        for param in parameters:  
            values = []  
            current = param["start"]  
            while current <= param["end"] + 1e-10:  # Add small epsilon to handle floating point comparison  
                values.append(current)  
                current += param["step"]  
            param_values.append((param["name"], values))  
          
        # Generate all combinations  
        import itertools  
        combinations = list(itertools.product(*[values for _, values in param_values]))  
          
        # Create experiment configs  
        for i, combination in enumerate(combinations):  
            for rep in range(repetitions):  
                params = {param_values[j][0]: combination[j] for j in range(len(param_values))}  
                configs.append({  
                    "name": f"{base_name}_config{i+1}_rep{rep+1}",  
                    "plugin": plugin_name,  
                    "parameters": params,  
                    "repetition": rep+1,  
                    "config_index": i+1  
                })  
          
        return configs  
    
    def add_experiment_to_table(self, config):  
        """  
        Add an experiment configuration to the table  
          
        Args:  
            config (dict): Experiment configuration  
        """  
        row = self.experiment_table.rowCount()  
        self.experiment_table.insertRow(row)  
          
        # Name  
        name_item = QTableWidgetItem(config["name"])  
        self.experiment_table.setItem(row, 0, name_item)  
          
        # Plugin  
        plugin_item = QTableWidgetItem(config["plugin"])  
        self.experiment_table.setItem(row, 1, plugin_item)  
          
        # Parameters  
        params_str = ", ".join([f"{k}={v}" for k, v in config["parameters"].items()])  
        params_item = QTableWidgetItem(params_str)  
        self.experiment_table.setItem(row, 2, params_item)  
          
        # Progress  
        progress_item = QTableWidgetItem("0%")  
        self.experiment_table.setItem(row, 3, progress_item)  
          
        # Status  
        status_item = QTableWidgetItem("等待中")  
        self.experiment_table.setItem(row, 4, status_item)  
          
        # Add to experiments list  
        self.experiments.append(config) 

    def add_experiment(self):  
        """Add a new experiment manually"""  
        # This would open a dialog to configure the experiment  
        # For now, just add a sample experiment  
        config = {  
            "name": f"实验_{len(self.experiments)+1}",  
            "plugin": "平衡控制插件",  
            "parameters": {"kp": 10.0, "kd": 1.0},  
            "repetition": 1  
        }  
        self.add_experiment_to_table(config)  

    def remove_experiment(self):  
        """Remove the selected experiment"""  
        selected_rows = self.experiment_table.selectionModel().selectedRows()  
        if not selected_rows:  
            return  
              
        # Remove in reverse order to avoid index issues  
        rows = sorted([index.row() for index in selected_rows], reverse=True)  
          
        for row in rows:  
            self.experiment_table.removeRow(row)  
            if row < len(self.experiments):  
                self.experiments.pop(row)  

    def run_experiments(self):  
        """Run all experiments"""  
        if not self.experiments:  
            QMessageBox.warning(self, "运行实验", "没有可运行的实验")  
            return  
              
        # Check if already running  
        if self.experiment_worker and self.experiment_worker.isRunning():  
            QMessageBox.warning(self, "运行实验", "实验已在运行中")  
            return  
              
        # Clear results table  
        self.results_table.setRowCount(0)  
          
        # Reset experiment status  
        for row in range(self.experiment_table.rowCount()):  
            self.experiment_table.setItem(row, 3, QTableWidgetItem("0%"))  
            self.experiment_table.setItem(row, 4, QTableWidgetItem("等待中"))  
          
        # Create and start worker thread  
        self.experiment_worker = ExperimentWorker(self.experiments, self.simulation_engine)  
        self.experiment_worker.progress_updated.connect(self.update_experiment_progress)  
        self.experiment_worker.experiment_completed.connect(self.on_experiment_completed)  
        self.experiment_worker.all_completed.connect(self.on_all_experiments_completed)  
        self.experiment_worker.start()  

    def stop_experiments(self):  
        """Stop running experiments"""  
        if self.experiment_worker and self.experiment_worker.isRunning():  
            self.experiment_worker.stop()  
            QMessageBox.information(self, "停止实验", "正在停止实验，请等待当前实验完成...")  
      
    def update_experiment_progress(self, experiment_index, progress):  
        """  
        Update the progress of an experiment  
          
        Args:  
            experiment_index (int): Index of the experiment  
            progress (int): Progress percentage (0-100)  
        """  
        if 0 <= experiment_index < self.experiment_table.rowCount():  
            self.experiment_table.setItem(  
                experiment_index,   
                3,   
                QTableWidgetItem(f"{progress}%")  
            )  
              
            # Update status if needed  
            if progress > 0 and progress < 100:  
                self.experiment_table.setItem(  
                    experiment_index,  
                    4,  
                    QTableWidgetItem("运行中")  
                )  

    def on_experiment_completed(self, experiment_index, results):  
        """  
        Handle experiment completion  
          
        Args:  
            experiment_index (int): Index of the completed experiment  
            results (dict): Experiment results  
        """  
        if 0 <= experiment_index < self.experiment_table.rowCount():  
            # Update experiment status  
            self.experiment_table.setItem(  
                experiment_index,  
                4,  
                QTableWidgetItem("已完成")  
            )  
              
            # Add to results table  
            row = self.results_table.rowCount()  
            self.results_table.insertRow(row)  
              
            # Experiment name  
            self.results_table.setItem(  
                row,  
                0,  
                QTableWidgetItem(self.experiments[experiment_index]["name"])  
            )  
              
            # Metrics  
            metrics = results.get("metrics", {})  
              
            self.results_table.setItem(  
                row,  
                1,  
                QTableWidgetItem(f"{metrics.get('balance_time', 0):.2f}")  
            )  
              
            self.results_table.setItem(  
                row,  
                2,  
                QTableWidgetItem(f"{metrics.get('energy_consumption', 0):.2f}")  
            )  
              
            self.results_table.setItem(  
                row,  
                3,  
                QTableWidgetItem(f"{metrics.get('stability_score', 0):.2f}")  
            )  
              
            # Status  
            self.results_table.setItem(  
                row,  
                4,  
                QTableWidgetItem(results.get("status", "未知"))  
            )  
      
    def on_all_experiments_completed(self):  
        """Handle completion of all experiments"""  
        QMessageBox.information(self, "实验完成", "所有实验已完成")  


    def export_results(self):  
        """Export experiment results to a file"""  
        if self.results_table.rowCount() == 0:  
            QMessageBox.warning(self, "导出结果", "没有可导出的结果")  
            return  
              
        # Show file dialog  
        options = QFileDialog.Options()  
        file_path, _ = QFileDialog.getSaveFileName(  
            self,  
            "导出结果",  
            "",  
            "CSV文件 (*.csv);;JSON文件 (*.json)",  
            options=options  
        )  
          
        if not file_path:  
            return  
              
        try:  
            # Collect results data  
            results_data = []  
            for row in range(self.results_table.rowCount()):  
                result = {  
                    "experiment": self.results_table.item(row, 0).text(),  
                    "balance_time": float(self.results_table.item(row, 1).text()),  
                    "energy_consumption": float(self.results_table.item(row, 2).text()),  
                    "stability_score": float(self.results_table.item(row, 3).text()),  
                    "status": self.results_table.item(row, 4).text()  
                }  
                results_data.append(result)  
              
            # Export based on file extension  
            if file_path.endswith(".csv"):  
                self._export_csv(file_path, results_data)  
            elif file_path.endswith(".json"):  
                self._export_json(file_path, results_data)  
            else:  
                # Default to CSV if no extension  
                if not "." in os.path.basename(file_path):  
                    file_path += ".csv"  
                    self._export_csv(file_path, results_data)  
                else:  
                    raise ValueError("不支持的文件格式")  
                      
            QMessageBox.information(self, "导出成功", f"结果已导出到: {file_path}")  
        except Exception as e:  
            QMessageBox.critical(self, "导出失败", f"导出结果时出错: {str(e)}")  
    def _export_csv(self, file_path, results_data):  
        """  
        Export results to CSV file  
          
        Args:  
            file_path (str): Path to save the CSV file  
            results_data (list): List of result dictionaries  
        """  
        import csv  
          
        with open(file_path, 'w', newline='', encoding='utf-8') as f:  
            # Get all field names from the results  
            fieldnames = set()  
            for result in results_data:  
                fieldnames.update(result.keys())  
              
            fieldnames = sorted(list(fieldnames))  
              
            # Write CSV  
            writer = csv.DictWriter(f, fieldnames=fieldnames)  
            writer.writeheader()  
            writer.writerows(results_data)  


    def _export_json(self, file_path, results_data):  
        """  
        Export results to JSON file  
          
        Args:  
            file_path (str): Path to save the JSON file  
            results_data (list): List of result dictionaries  
        """  
        import json  
          
        with open(file_path, 'w', encoding='utf-8') as f:  
            json.dump(results_data, f, indent=2, ensure_ascii=False)