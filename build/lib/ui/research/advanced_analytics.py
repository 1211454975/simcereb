# simcereb/ui/research/advanced_analytics.py  
"""  
Advanced analytics view for the Research Edition  
Provides detailed data analysis and visualization tools  
"""  
  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                            QLabel, QComboBox, QTabWidget, QSplitter, QTableWidget,  
                            QTableWidgetItem, QHeaderView, QFileDialog)  
from PyQt5.QtCore import Qt, pyqtSignal  
from PyQt5.QtGui import QFont  
  
import numpy as np  
import matplotlib.pyplot as plt  
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  
from matplotlib.figure import Figure  
  
from ..common.version_ui import VersionSpecificWidget  
  
class MatplotlibCanvas(FigureCanvas):  
    """Matplotlib canvas for embedding plots in PyQt"""  
      
    def __init__(self, parent=None, width=5, height=4, dpi=100):  
        self.fig = Figure(figsize=(width, height), dpi=dpi)  
        self.axes = self.fig.add_subplot(111)  
          
        super().__init__(self.fig)  
        self.setParent(parent)  
          
        # Make the canvas expandable  
        FigureCanvas.setSizePolicy(self,  
                                  QSizePolicy.Expanding,  
                                  QSizePolicy.Expanding)  
        FigureCanvas.updateGeometry(self)  
  
class AdvancedAnalyticsView(VersionSpecificWidget):  
    """  
    Advanced analytics view for the Research Edition  
    Provides detailed data analysis and visualization tools  
    """  
      
    # Signals  
    data_exported = pyqtSignal(str, str)  # Emitted when data is exported (format, path)  
      
    def __init__(self, version_manager, data_manager=None, parent=None):  
        """  
        Initialize the advanced analytics view  
          
        Args:  
            version_manager: VersionManager instance  
            data_manager: DataManager instance for accessing simulation data  
            parent: Parent widget  
        """  
        super().__init__(version_manager, parent)  
        self.data_manager = data_manager  
        self.current_dataset = None  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        # Main layout  
        main_layout = QVBoxLayout(self)  
          
        # Header  
        header_layout = QHBoxLayout()  
        title_label = QLabel("高级数据分析")  
        title_label.setFont(QFont("Arial", 18, QFont.Bold))  
        header_layout.addWidget(title_label)  
          
        # Dataset selector  
        self.dataset_selector = QComboBox()  
        self.dataset_selector.setMinimumWidth(200)  
        self.dataset_selector.currentIndexChanged.connect(self.load_dataset)  
        header_layout.addWidget(QLabel("数据集:"))  
        header_layout.addWidget(self.dataset_selector)  
          
        # Export button  
        export_button = QPushButton("导出数据")  
        export_button.clicked.connect(self.export_data)  
        header_layout.addWidget(export_button)  
          
        main_layout.addLayout(header_layout)  
          
        # Main content - tabs for different analysis views  
        self.tabs = QTabWidget()  
          
        # Time series tab  
        time_series_tab = QWidget()  
        time_series_layout = QVBoxLayout(time_series_tab)  
        self.time_series_canvas = MatplotlibCanvas(self)  
        time_series_layout.addWidget(self.time_series_canvas)  
          
        # Distribution tab  
        distribution_tab = QWidget()  
        distribution_layout = QVBoxLayout(distribution_tab)  
        self.distribution_canvas = MatplotlibCanvas(self)  
        distribution_layout.addWidget(self.distribution_canvas)  
          
        # Correlation tab  
        correlation_tab = QWidget()  
        correlation_layout = QVBoxLayout(correlation_tab)  
        self.correlation_canvas = MatplotlibCanvas(self)  
        correlation_layout.addWidget(self.correlation_canvas)  
          
        # Statistics tab  
        statistics_tab = QWidget()  
        statistics_layout = QVBoxLayout(statistics_tab)  
        self.statistics_table = QTableWidget()  
        self.statistics_table.setColumnCount(2)  
        self.statistics_table.setHorizontalHeaderLabels(["指标", "值"])  
        self.statistics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        statistics_layout.addWidget(self.statistics_table)  
          
        # Add tabs  
        self.tabs.addTab(time_series_tab, "时间序列")  
        self.tabs.addTab(distribution_tab, "分布")  
        self.tabs.addTab(correlation_tab, "相关性")  
        self.tabs.addTab(statistics_tab, "统计")  
          
        main_layout.addWidget(self.tabs)  
          
        # Populate dataset selector  
        self.populate_dataset_selector()  
      
    def populate_dataset_selector(self):  
        """Populate the dataset selector with available datasets"""  
        self.dataset_selector.clear()  
          
        if self.data_manager:  
            datasets = self.data_manager.get_available_datasets()  
            for dataset in datasets:  
                self.dataset_selector.addItem(dataset)  
        else:  
            # Add sample datasets for demonstration  
            self.dataset_selector.addItem("平衡控制实验")  
            self.dataset_selector.addItem("步态生成实验")  
            self.dataset_selector.addItem("传感器融合实验")  
      
    def load_dataset(self, index):  
        """  
        Load a dataset for analysis  
          
        Args:  
            index (int): Index of the selected dataset  
        """  
        if index < 0:  
            return  
              
        dataset_name = self.dataset_selector.itemText(index)  
          
        if self.data_manager:  
            # Load real data from data manager  
            self.current_dataset = self.data_manager.load_dataset(dataset_name)  
        else:  
            # Generate sample data for demonstration  
            self.current_dataset = self._generate_sample_data(dataset_name)  
          
        # Update all views  
        self.update_time_series_view()  
        self.update_distribution_view()  
        self.update_correlation_view()  
        self.update_statistics_view()  
      
    def update_time_series_view(self):  
        """Update the time series view with current dataset"""  
        if not self.current_dataset:  
            return  
              
        # Clear previous plot  
        self.time_series_canvas.axes.clear()  
          
        # Plot time series data  
        for key, values in self.current_dataset.items():  
            if key != 'time' and isinstance(values, list) and len(values) > 0:  
                self.time_series_canvas.axes.plot(  
                    self.current_dataset.get('time', range(len(values))),  
                    values,  
                    label=key  
                )  
          
        self.time_series_canvas.axes.set_xlabel('时间 (秒)')  
        self.time_series_canvas.axes.set_ylabel('值')  
        self.time_series_canvas.axes.set_title('时间序列数据')  
        self.time_series_canvas.axes.legend()  
        self.time_series_canvas.axes.grid(True)  
          
        # Refresh canvas  
        self.time_series_canvas.draw()  
      
    def update_distribution_view(self):  
        """Update the distribution view with current dataset"""  
        if not self.current_dataset:  
            return  
              
        # Clear previous plot  
        self.distribution_canvas.axes.clear()  
          
        # Plot distribution data  
        for key, values in self.current_dataset.items():  
            if key != 'time' and isinstance(values, list) and len(values) > 0:  
                self.distribution_canvas.axes.hist(  
                    values,  
                    bins=20,  
                    alpha=0.5,  
                    label=key  
                )  
          
        self.distribution_canvas.axes.set_xlabel('值')  
        self.distribution_canvas.axes.set_ylabel('频率')  
        self.distribution_canvas.axes.set_title('数据分布')  
        self.distribution_canvas.axes.legend()  
        self.distribution_canvas.axes.grid(True)  
          
        # Refresh canvas  
        self.distribution_canvas.draw()  
      
    def update_correlation_view(self):  
        """Update the correlation view with current dataset"""  
        if not self.current_dataset:  
            return  
              
        # Clear previous plot  
        self.correlation_canvas.axes.clear()  
          
        # Prepare data for correlation matrix  
        data_keys = [k for k in self.current_dataset.keys() if k != 'time']  
        if len(data_keys) < 2:  
            return  
              
        data_values = [self.current_dataset[k] for k in data_keys]  
        data_array = np.array(data_values).T  
          
        # Calculate correlation matrix  
        corr_matrix = np.corrcoef(data_array.T)  
          
        # Plot correlation matrix  
        im = self.correlation_canvas.axes.imshow(corr_matrix, cmap='coolwarm')  
        self.correlation_canvas.fig.colorbar(im)  
          
        # Set labels  
        self.correlation_canvas.axes.set_xticks(range(len(data_keys)))  
        self.correlation_canvas.axes.set_yticks(range(len(data_keys)))  
        self.correlation_canvas.axes.set_xticklabels(data_keys, rotation=45)  
        self.correlation_canvas.axes.set_yticklabels(data_keys)  
          
        # Add correlation values  
        for i in range(len(data_keys)):  
            for j in range(len(data_keys)):  
                self.correlation_canvas.axes.text(  
                    j, i, f"{corr_matrix[i, j]:.2f}",  
                    ha="center", va="center", color="black"  
                )  
          
        self.correlation_canvas.axes.set_title('相关性矩阵')  
          
        # Refresh canvas  
        self.correlation_canvas.draw()  
      
    def update_statistics_view(self):  
        """Update the statistics view with current dataset"""  
        if not self.current_dataset:  
            return  
              
        # Clear previous data  
        self.statistics_table.setRowCount(0)  
          
        # Calculate statistics for each data series  
        for key, values in self.current_dataset.items():  
            if key != 'time' and isinstance(values, list) and len(values) > 0:  
                # Convert to numpy array for calculations  
                data = np.array(values)  
                  
                # Add statistics rows  
                self._add_statistic_row(f"{key} - 平均值", f"{np.mean(data):.4f}")  
                self._add_statistic_row(f"{key} - 中位数", f"{np.median(data):.4f}")  
                self._add_statistic_row(f"{key} - 标准差", f"{np.std(data):.4f}")  
                self._add_statistic_row(f"{key} - 最小值", f"{np.min(data):.4f}")  
                self._add_statistic_row(f"{key} - 最大值", f"{np.max(data):.4f}")  
                self._add_statistic_row(f"{key} - 数据点数", f"{len(data)}")  
                self._add_statistic_row("", "")  # Empty row for spacing  
      
    def _add_statistic_row(self, name, value):  
        """Add a row to the statistics table"""  
        row = self.statistics_table.rowCount()  
        self.statistics_table.insertRow(row)  
        self.statistics_table.setItem(row, 0, QTableWidgetItem(name))  
        self.statistics_table.setItem(row, 1, QTableWidgetItem(value))  
      
    def export_data(self):  
        """Export the current dataset to a file"""  
        if not self.current_dataset:  
            return  
              
        # Show file dialog  
        options = QFileDialog.Options()  
        file_path, file_filter = QFileDialog.getSaveFileName(  
            self,  
            "导出数据",  
            "",  
            "CSV文件 (*.csv);;JSON文件 (*.json);;HDF5文件 (*.h5)",  
            options=options  
        )  
          
        if not file_path:  
            return  
              
        # Determine format from filter  
        if file_filter == "CSV文件 (*.csv)":  
            format = "csv"  
        elif file_filter == "JSON文件 (*.json)":  
            format = "json"  
        elif file_filter == "HDF5文件 (*.h5)":  
            format = "h5"  
        else:  
            format = "csv"  # Default  
          
        # Export data  
        if self.data_manager:  
            success = self.data_manager.export_dataset(self.current_dataset, file_path, format)  
        else:  
            # Simulate export  
            success = True  
              
        if success:  
            self.data_exported.emit(format, file_path)  
      
    def _generate_sample_data(self, dataset_name):  
        """  
        Generate sample data for demonstration  
          
        Args:  
            dataset_name (str): Name of the dataset to generate  
              
        Returns:  
            dict: Sample dataset  
        """  
        np.random.seed(42)  # For reproducible results  
          
        # Generate time array  
        time = np.linspace(0, 10, 100)  
          
        if dataset_name == "平衡控制实验":  
            # Generate balance control data  
            com_x = 0.05 * np.sin(time) + 0.01 * np.random.randn(len(time))  
            com_y = 0.03 * np.cos(time) + 0.01 * np.random.randn(len(time))  
            zmp_x = 0.04 * np.sin(time + 0.2) + 0.015 * np.random.randn(len(time))  
            zmp_y = 0.025 * np.cos(time + 0.2) + 0.015 * np.random.randn(len(time))  
              
            return {  
                "time": time.tolist(),  
                "COM_X": com_x.tolist(),  
                "COM_Y": com_y.tolist(),  
                "ZMP_X": zmp_x.tolist(),  
                "ZMP_Y": zmp_y.tolist()  
            }  
              
        elif dataset_name == "步态生成实验":  
            # Generate gait data  
            right_hip = 0.3 * np.sin(time) + 0.05 * np.random.randn(len(time))  
            left_hip = 0.3 * np.sin(time + np.pi) + 0.05 * np.random.randn(len(time))  
            right_knee = 0.5 * np.maximum(0, np.sin(time)) + 0.05 * np.random.randn(len(time))  
            left_knee = 0.5 * np.maximum(0, np.sin(time + np.pi)) + 0.05 * np.random.randn(len(time))  
              
            return {  
                "time": time.tolist(),  
                "右髋关节": right_hip.tolist(),  
                "左髋关节": left_hip.tolist(),  
                "右膝关节": right_knee.tolist(),  
                "左膝关节": left_knee.tolist()  
            }  
              
        elif dataset_name == "传感器融合实验":  
            # Generate sensor fusion data  
            gyro_x = 0.1 * np.sin(2 * time) + 0.05 * np.random.randn(len(time))  
            gyro_y = 0.1 * np.cos(2 * time) + 0.05 * np.random.randn(len(time))  
            accel_x = 0.2 * np.sin(time) + 0.1 * np.random.randn(len(time))  
            accel_y = 0.2 * np.cos(time) + 0.1 * np.random.randn(len(time))  
            fused_x = 0.15 * np.sin(time) + 0.02 * np.random.randn(len(time))  
            fused_y = 0.15 * np.cos(time) + 0.02 * np.random.randn(len(time))  
              
            return {  
                "time": time.tolist(),  
                "陀螺仪_X": gyro_x.tolist(),  
                "陀螺仪_Y": gyro_y.tolist(),  
                "加速度计_X": accel_x.tolist(),  
                "加速度计_Y": accel_y.tolist(),  
                "融合结果_X": fused_x.tolist(),  
                "融合结果_Y": fused_y.tolist()  
            }  
              
        else:  
            # Default dataset  
            data1 = np.sin(time) + 0.1 * np.random.randn(len(time))  
            data2 = np.cos(time) + 0.1 * np.random.randn(len(time))  
              
            return {  
                "time": time.tolist(),  
                "数据1": data1.tolist(),  
                "数据2": data2.tolist()  
            }