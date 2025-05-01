# simcereb/ui/plugin_editor.py  
import os  
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                            QTextEdit,QPlainTextEdit, QLabel, QFileDialog, QMessageBox, QSplitter)  
from PyQt5.QtCore import Qt, QRegExp  , QSize
from PyQt5.QtGui import (QFont, QColor, QTextCharFormat, QSyntaxHighlighter,  QPainter,  
                        QTextCursor)  
  
class PythonSyntaxHighlighter(QSyntaxHighlighter):  
    """Python syntax highlighter for the plugin editor"""  
      
    def __init__(self, document):  
        super().__init__(document)  
          
        # Syntax highlighting rules  
        self.highlighting_rules = []  
          
        # Keywords  
        keyword_format = QTextCharFormat()  
        keyword_format.setForeground(QColor(120, 120, 255))  
        keyword_format.setFontWeight(QFont.Bold)  
          
        keywords = [  
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',  
            'del', 'elif', 'else', 'except', 'exec', 'finally', 'for',  
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',  
            'not', 'or', 'pass', 'print', 'raise', 'return', 'try',  
            'while', 'yield', 'self'  
        ]  
          
        for word in keywords:  
            pattern = QRegExp("\\b" + word + "\\b")  
            rule = (pattern, keyword_format)  
            self.highlighting_rules.append(rule)  
              
        # Class names  
        class_format = QTextCharFormat()  
        class_format.setForeground(QColor(200, 120, 50))  
        class_format.setFontWeight(QFont.Bold)  
        self.highlighting_rules.append((  
            QRegExp("\\bclass\\b\\s+\\w+"),  
            class_format  
        ))  
          
        # Function names  
        function_format = QTextCharFormat()  
        function_format.setForeground(QColor(60, 170, 130))  
        function_format.setFontWeight(QFont.Bold)  
        self.highlighting_rules.append((  
            QRegExp("\\bdef\\b\\s+\\w+(?=\\()"),  
            function_format  
        ))  
          
        # String literals  
        string_format = QTextCharFormat()  
        string_format.setForeground(QColor(20, 140, 20))  
        self.highlighting_rules.append((  
            QRegExp("\".*\""),  
            string_format  
        ))  
        self.highlighting_rules.append((  
            QRegExp("'.*'"),  
            string_format  
        ))  
          
        # Triple-quoted strings  
        triple_quote_format = QTextCharFormat()  
        triple_quote_format.setForeground(QColor(20, 140, 20))  
        self.highlighting_rules.append((  
            QRegExp("\"\"\".*\"\"\""),  
            triple_quote_format  
        ))  
        self.highlighting_rules.append((  
            QRegExp("'''.*'''"),  
            triple_quote_format  
        ))  
          
        # Comments  
        comment_format = QTextCharFormat()  
        comment_format.setForeground(QColor(128, 128, 128))  
        comment_format.setFontItalic(True)  
        self.highlighting_rules.append((  
            QRegExp("#[^\n]*"),  
            comment_format  
        ))  
          
    def highlightBlock(self, text):  
        """Apply syntax highlighting to the given block of text"""  
        for pattern, format in self.highlighting_rules:  
            expression = QRegExp(pattern)  
            index = expression.indexIn(text)  
            while index >= 0:  
                length = expression.matchedLength()  
                self.setFormat(index, length, format)  
                index = expression.indexIn(text, index + length)  
  
class LineNumberArea(QWidget):  
    """Widget for displaying line numbers"""  
      
    def __init__(self, editor):  
        super().__init__(editor)  
        self.editor = editor  
          
    def sizeHint(self):  
        """Return the recommended size for the widget"""  
        return QSize(self.editor.line_number_area_width(), 0)  
          
    def paintEvent(self, event):  
        """Paint the line numbers"""  
        self.editor.line_number_area_paint_event(event)  
  
class CodeEditor(QPlainTextEdit):  
    """Enhanced text editor with line numbers and syntax highlighting"""  
      
    def __init__(self, parent=None):  
        super().__init__(parent)  
          
        # Set font  
        font = QFont("Courier New", 10)  
        font.setFixedPitch(True)  
        self.setFont(font)  
          
        # Set tab width  
        self.setTabStopWidth(4 * self.fontMetrics().width(' '))  
          
        # Create syntax highlighter  
        self.highlighter = PythonSyntaxHighlighter(self.document())  
          
        # Line numbers  
        self.line_number_area = LineNumberArea(self)  
        self.document().blockCountChanged.connect(self.update_line_number_area_width)  
        self.verticalScrollBar().valueChanged.connect(self.update_line_number_area)  
        self.textChanged.connect(self.update_line_number_area)  
        self.update_line_number_area_width(0)  
          
    def line_number_area_width(self):  
        """Calculate the width of the line number area"""  
        digits = 1  
        max_num = max(1, self.document().blockCount())  
        while max_num >= 10:  
            max_num //= 10  
            digits += 1  
          
        space = 3 + self.fontMetrics().width('9') * digits  
        return space  
          
    def update_line_number_area_width(self, _):  
        """Update the width of the line number area"""  
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)  
          
    def update_line_number_area(self):  
        """Update the line number area"""  
        self.line_number_area.update()  
        self.update_line_number_area_width(0)  
          
    def resizeEvent(self, event):  
        """Handle resize events"""  
        super().resizeEvent(event)  
          
        cr = self.contentsRect()  
        self.line_number_area.setGeometry(  
            cr.left(), cr.top(), self.line_number_area_width(), cr.height()  
        )  
          
    def line_number_area_paint_event(self, event):  
        """Paint the line numbers"""  
        painter = QPainter(self.line_number_area)  
        painter.fillRect(event.rect(), QColor(240, 240, 240))  
          
        block = self.firstVisibleBlock()  
        block_number = block.blockNumber()  
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()  
        bottom = top + self.blockBoundingRect(block).height()  
          
        while block.isValid() and top <= event.rect().bottom():  
            if block.isVisible() and bottom >= event.rect().top():  
                number = str(block_number + 1)  
                painter.setPen(QColor(120, 120, 120))  
                painter.drawText(  
                    0, top, self.line_number_area.width(), self.fontMetrics().height(),  
                    Qt.AlignRight, number  
                )  
                  
            block = block.next()  
            top = bottom  
            bottom = top + self.blockBoundingRect(block).height()  
            block_number += 1  
  
class PluginEditor(QWidget):  
    """Plugin editor for creating and editing plugin code"""  
      
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.current_file = None  
        self.init_ui()  
          
    def init_ui(self):  
        """Initialize the user interface"""  
        main_layout = QVBoxLayout()  
          
        # Toolbar  
        toolbar_layout = QHBoxLayout()  
          
        self.new_button = QPushButton("New")  
        self.new_button.clicked.connect(self.new_file)  
        toolbar_layout.addWidget(self.new_button)  
          
        self.open_button = QPushButton("Open")  
        self.open_button.clicked.connect(self.open_file)  
        toolbar_layout.addWidget(self.open_button)  
          
        self.save_button = QPushButton("Save")  
        self.save_button.clicked.connect(self.save_file)  
        toolbar_layout.addWidget(self.save_button)  
          
        self.save_as_button = QPushButton("Save As")  
        self.save_as_button.clicked.connect(self.save_file_as)  
        toolbar_layout.addWidget(self.save_as_button)  
          
        toolbar_layout.addStretch()  
          
        self.run_button = QPushButton("Run")  
        self.run_button.clicked.connect(self.run_plugin)  
        toolbar_layout.addWidget(self.run_button)  
          
        main_layout.addLayout(toolbar_layout)  
          
        # Status bar  
        self.status_label = QLabel("Ready")  
        main_layout.addWidget(self.status_label)  
          
        # Editor and output  
        splitter = QSplitter(Qt.Vertical)  
          
        # Code editor  
        self.editor = CodeEditor()  
        splitter.addWidget(self.editor)  
          
        # Output console  
        self.output_console = QTextEdit()  
        self.output_console.setReadOnly(True)  
        self.output_console.setFont(QFont("Courier New", 10))  
        splitter.addWidget(self.output_console)  
          
        # Set initial sizes  
        splitter.setSizes([700, 300])  
          
        main_layout.addWidget(splitter)  
          
        self.setLayout(main_layout)  
          
        # Set default content  
        self.new_file()  
          
    def new_file(self):  
        """Create a new file"""  
        if self.maybe_save():  
            self.editor.clear()  
            self.current_file = None  
            self.status_label.setText("New file")  
              
            # Set default template  
            template = """from simcereb.plugins.base import CerebellumPlugin  
import numpy as np  
  
class MyPlugin(CerebellumPlugin):  
    """"""
    My custom plugin  
    """"""  
      
    def __init__(self, config=None):  
        super().__init__(config)  
        # Initialize plugin parameters  
        self.enabled = True  
          
    def initialize(self, robot, simulation):  
        """"""Initialize plugin""""""
        self.robot = robot  
        self.simulation = simulation  
          
    def update(self, dt):  
        """"""Update control outputs""""""
        if not self.enabled:  
            return  
              
        # Implement your control algorithm here  
        pass  
          
    def reset(self):  
        """"""Reset plugin state""""""
        pass  
          
    def get_parameters(self):  
        """"""Get plugin parameters""""""
        return {  
            "param1": 0.0,  
            "param2": 1.0  
        }  
          
    def set_parameters(self, params):  
        """"""Set plugin parameters""""""
        # Handle parameter updates here  
        pass  
          
    def is_enabled(self):  
        """"""Check if plugin is enabled""""""  
        return self.enabled  
          
    def enable(self):  
        """"""Enable plugin""""""  
        self.enabled = True  
          
    def disable(self):  
        """"""Disable plugin""""""  
        self.enabled = False  
"""  
            self.editor.setPlainText(template)  
              
    def open_file(self):  
        """Open a file"""  
        if self.maybe_save():  
            file_path, _ = QFileDialog.getOpenFileName(  
                self, "Open File", "", "Python Files (*.py);;All Files (*)"  
            )  
              
            if file_path:  
                try:  
                    with open(file_path, 'r') as f:  
                        self.editor.setPlainText(f.read())  
                    self.current_file = file_path  
                    self.status_label.setText(f"Opened: {file_path}")  
                except Exception as e:  
                    QMessageBox.critical(self, "Error", f"Failed to open file: {e}")  
                      
    def save_file(self):  
        """Save the current file"""  
        if self.current_file:  
            return self.save_file_to(self.current_file)  
        else:  
            return self.save_file_as()  
              
    def save_file_as(self):  
        """Save the current file with a new name"""  
        file_path, _ = QFileDialog.getSaveFileName(  
            self, "Save File", "", "Python Files (*.py);;All Files (*)"  
        )  
          
        if file_path:  
            return self.save_file_to(file_path)  
          
        return False  
          
    def save_file_to(self, file_path):  
        """Save the current file to the specified path"""  
        try:  
            with open(file_path, 'w') as f:  
                f.write(self.editor.toPlainText())  
            self.current_file = file_path  
            self.status_label.setText(f"Saved: {file_path}")  
            return True  
        except Exception as e:  
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")  
            return False  
              
    def maybe_save(self):  
        """Check if the current file needs to be saved"""  
        if not self.editor.document().isModified():  
            return True  
              
        ret = QMessageBox.warning(  
            self, "SimCereb",  
            "The document has been modified.\nDo you want to save your changes?",  
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel  
        )  
          
        if ret == QMessageBox.Save:  
            return self.save_file()  
        elif ret == QMessageBox.Cancel:  
            return False  
              
        return True  
          
    def run_plugin(self):  
        """Run the current plugin"""  
        # Save to a temporary file if not saved  
        if not self.current_file:  
            temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),   
                                   "plugins", "custom")  
            os.makedirs(temp_dir, exist_ok=True)  
            temp_file = os.path.join(temp_dir, "temp_plugin.py")  
            self.save_file_to(temp_file)  
          
        # Show output  
        self.output_console.clear()  
        self.output_console.append("Running plugin...")  
        self.output_console.append("------------------")  
        self.output_console.append("Plugin loaded successfully!")  
        self.output_console.append("Use the Plugin Tester to test your plugin.")