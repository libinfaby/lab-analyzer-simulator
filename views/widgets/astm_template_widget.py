from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTextEdit, QGroupBox, QHBoxLayout, QComboBox, QLineEdit, QPushButton

class ASTMTemplateWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        astm_tabs = QTabWidget()
        
        # Sample Info Tab
        sample_info_tab = QWidget()
        sample_info_layout = QVBoxLayout(sample_info_tab)
        self.sample_info_text = QTextEdit()
        sample_info_layout.addWidget(self.sample_info_text)
        
        # Result Send Tab
        result_send_tab = QWidget()
        result_send_layout = QVBoxLayout(result_send_tab)
        self.result_send_text = QTextEdit()
        result_send_layout.addWidget(self.result_send_text)
        
        astm_tabs.addTab(sample_info_tab, "Sample Info Request Template")
        astm_tabs.addTab(result_send_tab, "Result Sending Template")
        
        layout.addWidget(astm_tabs)
        
        self.save_templates_button = QPushButton("Save Templates and Test Data")
        layout.addWidget(self.save_templates_button)