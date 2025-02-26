from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTabWidget, QTextEdit, QGroupBox
from PyQt6.QtGui import QFont
from .widgets.sample_input_widget import SampleInputWidget
from .widgets.connection_settings_widget import ConnectionSettingsWidget
from .widgets.astm_template_widget import ASTMTemplateWidget
from .widgets.test_master_widget import TestMasterWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laboratory Analyzer Simulator")
        self.setMinimumSize(1000, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Top section
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        self.analyzer_label = QLabel("Analyzer:")
        self.analyzer_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.analyzer_combo = QComboBox()
        self.set_button = QPushButton("Set")
        self.connection_status = QLabel("LIS Connection Not Established")
        top_layout.addWidget(self.analyzer_label)
        top_layout.addWidget(self.analyzer_combo)
        top_layout.addWidget(self.set_button)
        top_layout.addStretch()
        top_layout.addWidget(self.connection_status)
        self.main_layout.addWidget(top_widget)

        # Tabs
        self.tab_widget = QTabWidget()
        self.lis_tab = QWidget()
        self.sample_tab = QWidget()
        self.result_tab = QWidget()
        self.tab_widget.addTab(self.lis_tab, "LIS")
        self.tab_widget.addTab(self.sample_tab, "Sample/Analyze")
        self.tab_widget.addTab(self.result_tab, "Results")
        self.main_layout.addWidget(self.tab_widget)

        # Setup tabs
        self.setup_lis_tab()
        self.setup_sample_tab()
        self.setup_result_tab()

        # Log section
        log_group = QGroupBox("Connection Logs")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        self.main_layout.addWidget(log_group)

    def setup_lis_tab(self):
        lis_layout = QVBoxLayout(self.lis_tab)
        self.connection_settings_widget = ConnectionSettingsWidget()
        self.astm_template_widget = ASTMTemplateWidget()
        self.test_master_widget = TestMasterWidget()
        lis_layout.addWidget(self.connection_settings_widget)
        lis_layout.addWidget(self.astm_template_widget)
        lis_layout.addWidget(self.test_master_widget)

    def setup_sample_tab(self):
        sample_layout = QVBoxLayout(self.sample_tab)
        self.sample_input_widget = SampleInputWidget()
        sample_layout.addWidget(self.sample_input_widget)

    def setup_result_tab(self):
        result_layout = QVBoxLayout(self.result_tab)
        # Add result tab widgets here (tables for samples and results)