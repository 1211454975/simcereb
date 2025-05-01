# simcereb/ui/learning/visual_programming.py  
"""  
Visual programming interface for the Learning Edition  
Provides a block-based programming environment for beginners  
"""  
  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                            QLabel, QSplitter, QToolBar, QAction, QMenu,  
                            QGraphicsView, QGraphicsScene, QDockWidget, QListWidget)  
from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QRectF  
from PyQt5.QtGui import QIcon, QColor, QPen, QBrush, QFont  
  
from ..common.version_ui import VersionSpecificWidget  
  
class BlockItem:  
    """Represents a programming block in the visual programming interface"""  
      
    def __init__(self, block_type, name, color="#4A90E2", inputs=None, outputs=None):  
        self.block_type = block_type  
        self.name = name  
        self.color = color  
        self.inputs = inputs or []  
        self.outputs = outputs or []  
        self.position = QPointF(0, 0)  
        self.width = 150  
        self.height = 40 + (max(len(self.inputs), len(self.outputs)) * 20)  
        self.connections = []  
          
    def to_code(self):  
        """Convert block to Python code"""  
        # This would be implemented based on block type  
        return f"# {self.name} block\n"  
  
class BlockGraphicsItem(QGraphicsRectItem):  
    """Graphics item for a programming block"""  
      
    def __init__(self, block, parent=None):  
        super().__init__(0, 0, block.width, block.height, parent)  
        self.block = block  
        self.setPos(block.position)  
        self.setBrush(QBrush(QColor(block.color)))  
        self.setPen(QPen(Qt.black, 1))  
        self.setFlag(QGraphicsItem.ItemIsMovable)  
        self.setFlag(QGraphicsItem.ItemIsSelectable)  
          
        # Add text label  
        self.label = QGraphicsTextItem(block.name, self)  
        self.label.setPos(10, 10)  
        self.label.setDefaultTextColor(Qt.white)  
        font = QFont()  
        font.setBold(True)  
        self.label.setFont(font)  
          
        # Add input/output connectors  
        self._add_connectors()  
      
    def _add_connectors(self):  
        """Add input and output connectors to the block"""  
        # Add input connectors on the left  
        for i, input_name in enumerate(self.block.inputs):  
            y = 40 + i * 20  
            connector = QGraphicsEllipseItem(-5, y-5, 10, 10, self)  
            connector.setBrush(QBrush(Qt.red))  
            connector.setPen(QPen(Qt.black, 1))  
              
            label = QGraphicsTextItem(input_name, self)  
            label.setPos(10, y-10)  
            label.setDefaultTextColor(Qt.white)  
          
        # Add output connectors on the right  
        for i, output_name in enumerate(self.block.outputs):  
            y = 40 + i * 20  
            connector = QGraphicsEllipseItem(self.block.width-5, y-5, 10, 10, self)  
            connector.setBrush(QBrush(Qt.green))  
            connector.setPen(QPen(Qt.black, 1))  
              
            label = QGraphicsTextItem(output_name, self)  
            label.setPos(self.block.width-60, y-10)  
            label.setDefaultTextColor(Qt.white)  
  
class VisualProgrammingEditor(VersionSpecificWidget):  
    """  
    Visual programming editor for the Learning Edition  
    Provides a block-based programming environment  
    """  
      
    # Signals  
    code_generated = pyqtSignal(str)  # Emitted when code is generated from blocks  
      
    def __init__(self, version_manager, parent=None):  
        """  
        Initialize the visual programming editor  
          
        Args:  
            version_manager: VersionManager instance  
            parent: Parent widget  
        """  
        super().__init__(version_manager, parent)  
        self.blocks = []  
        self.connections = []  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        # Main layout  
        main_layout = QVBoxLayout(self)  
          
        # Toolbar  
        toolbar = QToolBar("Visual Programming Toolbar")  
          
        # Add actions  
        new_action = QAction(QIcon.fromTheme("document-new"), "新建", self)  
        new_action.triggered.connect(self.new_program)  
        toolbar.addAction(new_action)  
          
        save_action = QAction(QIcon.fromTheme("document-save"), "保存", self)  
        save_action.triggered.connect(self.save_program)  
        toolbar.addAction(save_action)  
          
        load_action = QAction(QIcon.fromTheme("document-open"), "加载", self)  
        load_action.triggered.connect(self.load_program)  
        toolbar.addAction(load_action)  
          
        toolbar.addSeparator()  
          
        generate_action = QAction(QIcon.fromTheme("system-run"), "生成代码", self)  
        generate_action.triggered.connect(self.generate_code)  
        toolbar.addAction(generate_action)  
          
        switch_action = QAction(QIcon.fromTheme("view-refresh"), "切换到代码视图", self)  
        switch_action.triggered.connect(self.switch_to_code_view)  
        toolbar.addAction(switch_action)  
          
        main_layout.addWidget(toolbar)  
          
        # Main content  
        content_splitter = QSplitter(Qt.Horizontal)  
          
        # Block palette  
        self.block_palette = QListWidget()  
        self.block_palette.setDragEnabled(True)  
        self.populate_block_palette()  
          
        # Create a dock widget for the palette  
        palette_dock = QDockWidget("积木块", self)  
        palette_dock.setWidget(self.block_palette)  
        palette_dock.setFeatures(QDockWidget.DockWidgetMovable)  
          
        # Graphics view for the blocks  
        self.scene = QGraphicsScene(self)  
        self.scene.setSceneRect(0, 0, 2000, 2000)  
          
        self.view = QGraphicsView(self.scene)  
        self.view.setRenderHint(QPainter.Antialiasing)  
        self.view.setDragMode(QGraphicsView.RubberBandDrag)  
          
        content_splitter.addWidget(palette_dock)  
        content_splitter.addWidget(self.view)  
        content_splitter.setSizes([200, 800])  
          
        main_layout.addWidget(content_splitter)  
          
        # Status bar  
        status_layout = QHBoxLayout()  
        self.status_label = QLabel("就绪")  
        status_layout.addWidget(self.status_label)  
          
        main_layout.addLayout(status_layout)  
      
    def populate_block_palette(self):  
        """Populate the block palette with available blocks"""  
        # Motor control blocks  
        self.block_palette.addItem("电机控制 - 设置位置")  
        self.block_palette.addItem("电机控制 - 设置速度")  
          
        # Sensor blocks  
        self.block_palette.addItem("传感器 - 读取IMU")  
        self.block_palette.addItem("传感器 - 读取足部力")  
          
        # Logic blocks  
        self.block_palette.addItem("逻辑 - 如果条件")  
        self.block_palette.addItem("逻辑 - 循环")  
          
        # Math blocks  
        self.block_palette.addItem("数学 - 加法")  
        self.block_palette.addItem("数学 - 乘法")  
        self.block_palette.addItem("数学 - PID控制器")  
      
    def new_program(self):  
        """Create a new program"""  
        self.blocks = []  
        self.connections = []  
        self.scene.clear()  
        self.status_label.setText("已创建新程序")  
      
    def save_program(self):  
        """Save the current program"""  
        # This would be implemented to save the block configuration  
        self.status_label.setText("程序已保存")  
      
    def load_program(self):  
        """Load a program"""  
        # This would be implemented to load a saved block configuration  
        self.status_label.setText("程序已加载")  
      
    def generate_code(self):  
        """Generate Python code from the blocks"""  
        code = "# 由SimCereb学习版可视化编程生成的代码\n\n"  
          
        # This would be implemented to convert blocks to code  
        for block in self.blocks:  
            code += block.to_code() + "\n"  
          
        self.code_generated.emit(code)  
        self.status_label.setText("代码已生成")  
          
        return code  
      
    def switch_to_code_view(self):  
        """Switch to code view"""  
        code = self.generate_code()  
        # This would emit a signal to the main application to switch views  
        self.status_label.setText("已切换到代码视图")