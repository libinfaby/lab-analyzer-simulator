import sys
import random
import time
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QComboBox, QPushButton, QTabWidget, QRadioButton,
                            QLineEdit, QCheckBox, QTextEdit, QProgressBar, QGroupBox,
                            QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
                            QSplitter, QMessageBox, QScrollArea, QSpacerItem, QSizePolicy,
                            QStackedWidget, QFrame, QListWidget, QListWidgetItem, QToolButton)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QDateTime, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette

class LabSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laboratory Analyzer Simulator")
        self.setMinimumSize(1000, 700)
        
        # Setup the database
        self.create_database()
        
        # Setup the UI
        self.setup_ui()
        
        # Load analyzer list
        self.load_analyzers()
        
    def create_database(self):
        conn = sqlite3.connect('analyzersim.db')
        cursor = conn.cursor()
        
        # Create analyzer table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyzers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        ''')
        
        # Create connection settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS connection_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analyzer_id INTEGER,
            connection_type TEXT,
            socket_type TEXT,
            analyzer_address TEXT,
            analyzer_port TEXT,
            lis_address TEXT,
            lis_port TEXT,
            serial_port TEXT,
            baud_rate TEXT,
            data_bits TEXT,
            stop_bits TEXT,
            parity TEXT,
            auto_result_sending INTEGER,
            request_sample_info INTEGER,
            sample_id_delay INTEGER,
            result_sending_delay INTEGER,
            FOREIGN KEY (analyzer_id) REFERENCES analyzers(id)
        )
        ''')
        
        # Create ASTM message templates table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS astm_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analyzer_id INTEGER,
            template_type TEXT,
            template_content TEXT,
            FOREIGN KEY (analyzer_id) REFERENCES analyzers(id)
        )
        ''')
        
        # Create tests table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analyzer_id INTEGER,
            test_code TEXT,
            unit TEXT,
            lower_range REAL,
            upper_range REAL,
            FOREIGN KEY (analyzer_id) REFERENCES analyzers(id)
        )
        ''')
        
        # Create samples table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_number TEXT,
            patient_id TEXT,
            patient_name TEXT,
            date_time TEXT
        )
        ''')
        
        # Create results table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id INTEGER,
            test_id INTEGER,
            result_value REAL,
            sent INTEGER DEFAULT 0,
            FOREIGN KEY (sample_id) REFERENCES samples(id),
            FOREIGN KEY (test_id) REFERENCES tests(id)
        )
        ''')
        
        # Insert some initial data if needed
        cursor.execute("SELECT COUNT(*) FROM analyzers")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("INSERT INTO analyzers (name) VALUES ('Analyzer 1')")
            cursor.execute("INSERT INTO analyzers (name) VALUES ('Analyzer 2')")
            
            # Insert some test examples
            analyzer_id = 1
            tests = [
                ('Test_1', 'mmol/l', 0.5, 5.0),
                ('Photo_reflex_test', 'mmol/l', 1.0, 5.5),
                ('Photometric_test', 'mmol/l', 0.05, 1.2)
            ]
            for test in tests:
                cursor.execute('''
                INSERT INTO tests (analyzer_id, test_code, unit, lower_range, upper_range)
                VALUES (?, ?, ?, ?, ?)
                ''', (analyzer_id, test[0], test[1], test[2], test[3]))
        
        conn.commit()
        conn.close()
    
    def setup_ui(self):
        # Set up main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Set dark mode stylesheet
        self.setStyleSheet('''
            QMainWindow {
                background-color: #2b2b2b;
            }
           (QWidget, QGroupBox) {
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #1e88e5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                border-radius: 4px;
                background-color: #333333;
            }
            QTabBar::tab {
                background-color: #404040;
                border: 1px solid #404040;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 12px;
                margin-right: 2px;
                color: #ffffff;
            }
            QTabBar::tab:selected {
                background-color: #333333;
                border-bottom: 1px solid #333333;
            }
            QLineEdit, QComboBox, QTableWidget, QTextEdit {
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 3px;
                background-color: #404040;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down-arrow.png);  /* You might need to provide a white arrow icon */
            }
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 4px;
                text-align: center;
                background-color: #333333;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #1e88e5;
                width: 10px;
                margin: 0.5px;
            }
            QHeaderView::section {
                background-color: #404040;
                padding: 4px;
                border: 1px solid #555555;
                color: #ffffff;
            }
            QTableWidget {
                gridline-color: #555555;
            }
            QRadioButton {
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
            }
        ''')
        
        # Top section - Analyzer selector
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(10, 10, 10, 5)
        
        analyzer_label = QLabel("Analyzer:")
        analyzer_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.analyzer_combo = QComboBox()
        self.analyzer_combo.setFixedWidth(200)
        self.analyzer_combo.setFont(QFont("Arial", 10))
        
        set_button = QPushButton("Set")
        set_button.setFixedWidth(80)
        set_button.clicked.connect(self.set_analyzer)
        
        connection_status = QLabel("LIS Connection Not Established")
        connection_status.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        connection_status.setStyleSheet("color: #ff4444;")
        
        top_layout.addWidget(analyzer_label)
        top_layout.addWidget(self.analyzer_combo)
        top_layout.addWidget(set_button)
        top_layout.addStretch()
        top_layout.addWidget(connection_status)
        
        self.main_layout.addWidget(top_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create the three tabs
        self.lis_tab = QWidget()
        self.sample_tab = QWidget()
        self.result_tab = QWidget()
        
        self.tab_widget.addTab(self.lis_tab, "LIS")
        self.tab_widget.addTab(self.sample_tab, "Sample/Analyze")
        self.tab_widget.addTab(self.result_tab, "Results")
        
        # Setup LIS Tab
        self.setup_lis_tab()
        
        # Setup Sample/Analyze Tab
        self.setup_sample_tab()
        
        # Setup Results Tab
        self.setup_result_tab()
        
        # Add status bar for logs
        self.statusBar().showMessage("Ready")
        
        # Add a log viewer at the bottom
        log_group = QGroupBox("Connection Logs")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        self.main_layout.addWidget(log_group)
        
    def setup_lis_tab(self):
        lis_layout = QHBoxLayout(self.lis_tab)
        
        # Create left and right splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        lis_layout.addWidget(splitter)
        
        # Left side - Connection settings
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Connection type selection
        conn_type_group = QGroupBox("Connection Type")
        conn_type_layout = QHBoxLayout(conn_type_group)
        
        self.tcp_radio = QRadioButton("TCP/IP")
        self.serial_radio = QRadioButton("Serial")
        self.tcp_radio.setChecked(True)
        
        conn_type_layout.addWidget(self.tcp_radio)
        conn_type_layout.addWidget(self.serial_radio)
        
        left_layout.addWidget(conn_type_group)
        
        # TCP/IP settings
        self.tcp_widget = QWidget()
        tcp_layout = QFormLayout(self.tcp_widget)
        
        # Socket type
        socket_layout = QHBoxLayout()
        self.server_radio = QRadioButton("Server")
        self.client_radio = QRadioButton("Client")
        self.server_radio.setChecked(True)
        socket_layout.addWidget(self.server_radio)
        socket_layout.addWidget(self.client_radio)
        tcp_layout.addRow("Socket Type:", socket_layout)
        
        # Analyzer address and port
        self.analyzer_address = QLineEdit("127.0.0.1")
        tcp_layout.addRow("Analyzer Address:", self.analyzer_address)
        
        self.analyzer_port = QLineEdit("12000")
        tcp_layout.addRow("Analyzer Port:", self.analyzer_port)
        
        # LIS address and port
        self.lis_address = QLineEdit("127.0.0.1")
        tcp_layout.addRow("LIS Address:", self.lis_address)
        
        self.lis_port = QLineEdit("13000")
        tcp_layout.addRow("LIS Port:", self.lis_port)
        
        left_layout.addWidget(self.tcp_widget)
        
        # Serial settings
        self.serial_widget = QWidget()
        self.serial_widget.setVisible(False)  # Hide initially
        serial_layout = QFormLayout(self.serial_widget)
        
        # Serial port
        self.serial_port = QComboBox()
        self.serial_port.addItems(["COM1", "COM2", "COM3"])
        serial_layout.addRow("Serial Port:", self.serial_port)
        
        # Baud rate
        self.baud_rate = QLineEdit("9600")
        self.baud_rate.setPlaceholderText("2400, 4800, 9600, 19200")
        serial_layout.addRow("Baud Rate:", self.baud_rate)
        
        # Data bits
        self.data_bits = QLineEdit("8")
        serial_layout.addRow("Data Bits:", self.data_bits)
        
        # Stop bits
        self.stop_bits = QLineEdit("1")
        self.stop_bits.setPlaceholderText("1 or 2")
        serial_layout.addRow("Stop Bits:", self.stop_bits)
        
        # Parity
        self.parity = QComboBox()
        self.parity.addItems(["Even", "Odd", "No", "Space", "Mark"])
        self.parity.setCurrentText("No")
        serial_layout.addRow("Parity:", self.parity)
        
        left_layout.addWidget(self.serial_widget)
        
        # Common settings
        common_group = QGroupBox("Common Settings")
        common_layout = QVBoxLayout(common_group)
        
        self.auto_result = QCheckBox("Automatic Result Sending")
        self.request_sample = QCheckBox("Request Sample Info")
        common_layout.addWidget(self.auto_result)
        common_layout.addWidget(self.request_sample)
        
        sample_delay_layout = QHBoxLayout()
        sample_delay_layout.addWidget(QLabel("Sample ID Sending Delay (ms):"))
        self.sample_delay = QLineEdit("0")
        sample_delay_layout.addWidget(self.sample_delay)
        common_layout.addLayout(sample_delay_layout)
        
        result_delay_layout = QHBoxLayout()
        result_delay_layout.addWidget(QLabel("Result Sending Delay (ms):"))
        self.result_delay = QLineEdit("0")
        result_delay_layout.addWidget(self.result_delay)
        common_layout.addLayout(result_delay_layout)
        
        left_layout.addWidget(common_group)
        
        # Save connection settings button
        save_button = QPushButton("Save Connection Settings")
        save_button.clicked.connect(self.save_connection_settings)
        left_layout.addWidget(save_button)
        
        # Connect button
        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.connect_to_lis)
        left_layout.addWidget(connect_button)
        
        left_layout.addStretch()
        
        # Right side - ASTM Message Templates
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Create tab widget for ASTM templates
        astm_tabs = QTabWidget()
        
        # Sample Info Request Template Tab
        sample_info_tab = QWidget()
        sample_info_layout = QVBoxLayout(sample_info_tab)
        
        sample_info_text = QTextEdit()
        sample_info_text.setPlaceholderText("Enter ASTM message template for sample info request...")
        sample_info_text.setText("Send: <ENQ>\nRead: <ACK>\n\nSend: <STX>1H|\\^&|||1^Analyzer_1^|||||||||P||20101118101825<CR><ETX>A1\nRead: <ACK>\n\nSend: <STX>2Q|1|^SampleID_03^^||^^^ALL^||||||O<CR><ETX>FF\n\nRead: <ACK>\n\nSend: <STX>3L|1|N<CR><ETX>06\n\nRead: <ACK>\n\nSend: < EOT >")
        
        # Field selector UI for sample info
        field_group = QGroupBox("Add Field")
        field_layout = QHBoxLayout(field_group)
        
        field_selector = QComboBox()
        field_selector.addItems(["ENQ", "ACK", "STX", "ETX", "H", "P", "O", "Q", "R"])
        field_layout.addWidget(field_selector)
        
        field_text = QLineEdit()
        field_layout.addWidget(field_text)
        
        field_direction = QComboBox()
        field_direction.addItems(["Send", "Read"])
        field_layout.addWidget(field_direction)
        
        add_field_button = QPushButton("Add")
        field_layout.addWidget(add_field_button)
        
        sample_info_layout.addWidget(sample_info_text)
        sample_info_layout.addWidget(field_group)
        
        # Result Sending Template Tab
        result_send_tab = QWidget()
        result_send_layout = QVBoxLayout(result_send_tab)
        
        result_send_text = QTextEdit()
        result_send_text.setPlaceholderText("Enter ASTM message template for result sending...")
        result_send_text.setText("send: <ENQ>\nread: <ACK>\nsend: <STX>1H]\\Aé|[]1 Analyzer 1^7.0]||||||||P|]20190801124640<CR><EXT>E4\nread: <ACK>\n\nsend: <STX>2P|1|PatientID_07|||Patient Name_7|||U|||||||||||||||||||<CR><EXT>67\nread: <ACK>\n\nsend: <STX>3O|1|SampleID_07^0.0^5^1|||^^^Test_1^0.0|R||||||X|||3|||||||1|F<CR><EXT>2C\nread: <ACK>\n\nsend: <STX>4R|1|^^^Test_1^0.0|2.4|mmol/l||N||F||<root user>||20190801124608|Analyzer 1<CR><EXT>3F\nread: <ACK>\n\nsend: <STX>5O|2|SampleID_07^0.0^5^1|||^^^Photo_reflex_test^0.0|R||||||X|||3|||||||1|F<CR><EXT>0D\nread: <ACK>\n\nsend: <STX>6R|1|^^^Photo_reflex_test^0.0|3.205|mmol/l||N||F||<root user>||20190801124606|Analyzer 1<CR><EXT>81\nread: <ACK>\n\nsend: <STX>7O|3|SampleID_07^0.0^5^1|||^^^Photometric_test^0.0|R||||||X|||3|||||||1|F<CR><EXT>AF\nread: <ACK>\n\nsend: <STX>0R|1|^^^Photometric_test^0.0|0.06|mmol/l||N||F||<root user>||20190801124607|Analyzer 1<CR><EXT>E7\nread: <ACK>\n\nsend: <STX>1L|1|N<CR><EXT>04\nread")
        
        # Field selector UI for result sending
        result_field_group = QGroupBox("Add Field")
        result_field_layout = QHBoxLayout(result_field_group)
        
        result_field_selector = QComboBox()
        result_field_selector.addItems(["ENQ", "ACK", "STX", "ETX", "H", "P", "O", "Q", "R"])
        result_field_layout.addWidget(result_field_selector)
        
        result_field_text = QLineEdit()
        result_field_layout.addWidget(result_field_text)
        
        result_field_direction = QComboBox()
        result_field_direction.addItems(["Send", "Read"])
        result_field_layout.addWidget(result_field_direction)
        
        result_add_field_button = QPushButton("Add")
        result_field_layout.addWidget(result_add_field_button)
        
        result_send_layout.addWidget(result_send_text)
        result_send_layout.addWidget(result_field_group)
        
        # Add tabs to the ASTM templates tab widget
        astm_tabs.addTab(sample_info_tab, "Sample Info Request Template")
        astm_tabs.addTab(result_send_tab, "Result Sending Template")
        
        right_layout.addWidget(astm_tabs)
        
        # Test Master table
        test_group = QGroupBox("Test Master")
        test_layout = QVBoxLayout(test_group)
        
        self.test_table = QTableWidget()
        self.test_table.setColumnCount(4)
        self.test_table.setHorizontalHeaderLabels(["Test Code", "Unit", "Lower Range", "Upper Range"])
        self.test_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        test_button_layout = QHBoxLayout()
        add_test_button = QPushButton("Add Test")
        add_test_button.clicked.connect(self.add_test)
        edit_test_button = QPushButton("Edit Test")
        edit_test_button.clicked.connect(self.edit_test)
        delete_test_button = QPushButton("Delete Test")
        delete_test_button.clicked.connect(self.delete_test)
        
        test_button_layout.addWidget(add_test_button)
        test_button_layout.addWidget(edit_test_button)
        test_button_layout.addWidget(delete_test_button)
        
        test_layout.addWidget(self.test_table)
        test_layout.addLayout(test_button_layout)
        
        right_layout.addWidget(test_group)
        
        # Save templates button
        save_templates_button = QPushButton("Save Templates and Test Data")
        save_templates_button.clicked.connect(self.save_templates)
        right_layout.addWidget(save_templates_button)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])  # Initial sizes
        
        # Connect connection type radio buttons
        self.tcp_radio.toggled.connect(self.toggle_connection_type)
        self.serial_radio.toggled.connect(self.toggle_connection_type)
        
        # Connect socket type radio buttons
        self.server_radio.toggled.connect(self.toggle_socket_type)
        self.client_radio.toggled.connect(self.toggle_socket_type)
        
        # Connect field selector buttons
        add_field_button.clicked.connect(lambda: self.add_field(field_selector, field_text, field_direction, sample_info_text))
        result_add_field_button.clicked.connect(lambda: self.add_field(result_field_selector, result_field_text, result_field_direction, result_send_text))
        
        LabSimulator.toggle_socket_type(self)
        
    def setup_sample_tab(self):
        sample_layout = QVBoxLayout(self.sample_tab)
        
        # Sample number input area
        sample_group = QGroupBox("Sample Input")
        sample_input_layout = QVBoxLayout(sample_group)
        
        # Sample number widget that can dynamically add more
        self.sample_widget = QWidget()
        self.sample_layout = QVBoxLayout(self.sample_widget)
        self.sample_layout.setContentsMargins(0, 0, 0, 0)
        
        # Initial sample input
        self.add_sample_input()
        
        # sample_input_layout.addWidget(self.sample_widget)
        # Create a scroll area and add the sample widget to it
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Important - this allows the widget to resize
        scroll_area.setWidget(self.sample_widget)

        # Add the scroll area to the sample input layout
        sample_input_layout.addWidget(scroll_area)
        
        # Add more samples button
        add_sample_button = QPushButton("Add More Samples")
        add_sample_button.clicked.connect(self.add_sample_input)
        sample_input_layout.addWidget(add_sample_button)

        # Now set the layout on the group box
        sample_group.setLayout(sample_input_layout)

        sample_layout.addWidget(sample_group)
        
        # Start analysis button
        start_button = QPushButton()
        start_button.setIcon(QIcon.fromTheme("media-playback-start"))
        start_button.setText("Start Analysis")
        start_button.setIconSize(QSize(24, 24))
        start_button.setStyleSheet("font-size: 16px; padding: 10px;")
        start_button.clicked.connect(self.start_analysis)
        sample_layout.addWidget(start_button)
        
        # Progress section
        progress_group = QGroupBox("Analysis Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        current_sample_layout = QHBoxLayout()
        current_sample_layout.addWidget(QLabel("Current Sample:"))
        self.current_sample_label = QLabel("None")
        current_sample_layout.addWidget(self.current_sample_label)
        current_sample_layout.addStretch()
        progress_layout.addLayout(current_sample_layout)
        
        sample_layout.addWidget(progress_group)
        
        # Patient info section
        patient_group = QGroupBox("Patient Information")
        patient_layout = QFormLayout(patient_group)
        
        self.patient_id_label = QLabel("Not Available")
        self.patient_name_label = QLabel("Not Available")
        
        patient_layout.addRow("Patient ID:", self.patient_id_label)
        patient_layout.addRow("Patient Name:", self.patient_name_label)
        
        # Test details
        test_details_group = QGroupBox("Test Details")
        test_details_layout = QVBoxLayout(test_details_group)
        
        self.test_list = QListWidget()
        test_details_layout.addWidget(self.test_list)
        
        patient_layout.addRow("Tests:", test_details_group)
        
        sample_layout.addWidget(patient_group)
        
        # Add a spacer at the bottom
        sample_layout.addStretch()
        
    def setup_result_tab(self):
        result_layout = QVBoxLayout(self.result_tab)
        
        # Split view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        result_layout.addWidget(splitter)
        
        # Left side - Sample list
        sample_list_group = QGroupBox("Samples")
        sample_list_layout = QVBoxLayout(sample_list_group)
        
        self.sample_list = QTableWidget()
        self.sample_list.setColumnCount(3)
        self.sample_list.setHorizontalHeaderLabels(["Sample No.", "Patient ID", "Patient Name"])
        self.sample_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sample_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sample_list.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.sample_list.selectionModel().selectionChanged.connect(self.load_sample_results)
        
        sample_list_layout.addWidget(self.sample_list)
        
        # Right side - Result details
        result_details_group = QGroupBox("Results")
        result_details_layout = QVBoxLayout(result_details_group)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["Test Code", "Result", "Unit", "Normal Range", "Sent"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        result_details_layout.addWidget(self.result_table)
        
        # Buttons for sending results
        button_layout = QHBoxLayout()
        
        send_selected_button = QPushButton("Send Selected Results")
        send_selected_button.clicked.connect(self.send_selected_results)
        
        send_all_button = QPushButton("Send All Results")
        send_all_button.clicked.connect(self.send_all_results)
        
        button_layout.addWidget(send_selected_button)
        button_layout.addWidget(send_all_button)
        
        result_details_layout.addLayout(button_layout)
        
        # Add widgets to splitter
        splitter.addWidget(sample_list_group)
        splitter.addWidget(result_details_group)
        splitter.setSizes([300, 700])  # Initial sizes
        
    def load_analyzers(self):
        try:
            conn = sqlite3.connect('analyzersim.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM analyzers")
            analyzers = cursor.fetchall()
            conn.close()
            
            self.analyzer_combo.clear()
            for analyzer in analyzers:
                self.analyzer_combo.addItem(analyzer[1], analyzer[0])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load analyzers: {str(e)}")
    
    def set_analyzer(self):
        analyzer_id = self.analyzer_combo.currentData()
        analyzer_name = self.analyzer_combo.currentText()
        try:
            conn = sqlite3.connect('analyzersim.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT connection_type, socket_type, analyzer_address, analyzer_port, 
                       lis_address, lis_port, serial_port, baud_rate, data_bits, 
                       stop_bits, parity, auto_result_sending, request_sample_info,
                       sample_id_delay, result_sending_delay 
                FROM connection_settings 
                WHERE analyzer_id = ?
            """, (analyzer_id,))
            
            settings = cursor.fetchone()
            if settings:
                if settings[0] == "TCP/IP":
                    self.tcp_radio.setChecked(True)
                    if settings[1] == "Server":
                        self.server_radio.setChecked(True)
                    else:
                        self.client_radio.setChecked(True)
                    self.analyzer_address.setText(settings[2] or "")
                    self.analyzer_port.setText(settings[3] or "")
                    self.lis_address.setText(settings[4] or "")
                    self.lis_port.setText(settings[5] or "")
                else:
                    self.serial_radio.setChecked(True)
                    self.serial_port.setCurrentText(settings[6] or "COM1")
                    self.baud_rate.setText(settings[7] or "9600")
                    self.data_bits.setText(settings[8] or "8")
                    self.stop_bits.setText(settings[9] or "1")
                    self.parity.setCurrentText(settings[10] or "No")
                
                self.auto_result.setChecked(bool(settings[11]))
                self.request_sample.setChecked(bool(settings[12]))
                self.sample_delay.setText(str(settings[13] or "0"))
                self.result_delay.setText(str(settings[14] or "0"))
            
            cursor.execute("""
                SELECT template_type, template_content 
                FROM astm_templates 
                WHERE analyzer_id = ?
            """, (analyzer_id,))
            
            templates = cursor.fetchall()
            for template in templates:
                if template[0] == "sample_info":
                    pass
                elif template[0] == "result_send":
                    pass
            
            cursor.execute("""
                SELECT test_code, unit, lower_range, upper_range 
                FROM tests 
                WHERE analyzer_id = ?
            """, (analyzer_id,))
            
            tests = cursor.fetchall()
            self.test_table.setRowCount(len(tests))
            for i, test in enumerate(tests):
                self.test_table.setItem(i, 0, QTableWidgetItem(test[0]))
                self.test_table.setItem(i, 1, QTableWidgetItem(test[1]))
                self.test_table.setItem(i, 2, QTableWidgetItem(str(test[2])))
                self.test_table.setItem(i, 3, QTableWidgetItem(str(test[3])))
            
            conn.close()
            
            QMessageBox.information(self, "Success", f"Analyzer '{analyzer_name}' selected successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load analyzer settings: {str(e)}")
    
    def toggle_connection_type(self):
        if self.tcp_radio.isChecked():
            self.tcp_widget.setVisible(True)
            self.serial_widget.setVisible(False)
        else:
            self.tcp_widget.setVisible(False)
            self.serial_widget.setVisible(True)
    
    def toggle_socket_type(self):
        server_mode = self.server_radio.isChecked()
        self.analyzer_address.setEnabled(True)
        self.analyzer_port.setEnabled(server_mode)
        self.lis_address.setEnabled(True)
        self.lis_port.setEnabled(not server_mode)
    
    def add_field(self, selector, text, direction, target):
        field = selector.currentText()
        content = text.text()
        dir_text = direction.currentText()
        
        if field in ["ENQ", "ACK", "STX", "ETX", "EOT"]:
            target.append(f"{dir_text}: <{field}>")
        else:
            target.append(f"{dir_text}: {field} {content}")
    
    def save_connection_settings(self):
        analyzer_id = self.analyzer_combo.currentData()
        if not analyzer_id:
            QMessageBox.warning(self, "Warning", "Please select an analyzer first")
            return
        
        try:
            conn = sqlite3.connect('analyzersim.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM connection_settings WHERE analyzer_id = ?", (analyzer_id,))
            existing = cursor.fetchone()
            
            connection_type = "TCP/IP" if self.tcp_radio.isChecked() else "Serial"
            socket_type = "Server" if self.server_radio.isChecked() else "Client"
            analyzer_address = self.analyzer_address.text()
            analyzer_port = self.analyzer_port.text()
            lis_address = self.lis_address.text()
            lis_port = self.lis_port.text()
            serial_port = self.serial_port.currentText()
            baud_rate = self.baud_rate.text()
            data_bits = self.data_bits.text()
            stop_bits = self.stop_bits.text()
            parity = self.parity.currentText()
            auto_result = 1 if self.auto_result.isChecked() else 0
            request_sample = 1 if self.request_sample.isChecked() else 0
            sample_delay = self.sample_delay.text()
            result_delay = self.result_delay.text()
            
            if existing:
                cursor.execute("""
                    UPDATE connection_settings 
                    SET connection_type = ?, socket_type = ?, analyzer_address = ?,
                        analyzer_port = ?, lis_address = ?, lis_port = ?,
                        serial_port = ?, baud_rate = ?, data_bits = ?,
                        stop_bits = ?, parity = ?, auto_result_sending = ?,
                        request_sample_info = ?, sample_id_delay = ?,
                        result_sending_delay = ?
                    WHERE analyzer_id = ?
                """, (connection_type, socket_type, analyzer_address, analyzer_port,
                     lis_address, lis_port, serial_port, baud_rate, data_bits,
                     stop_bits, parity, auto_result, request_sample,
                     sample_delay, result_delay, analyzer_id))
            else:
                cursor.execute("""
                    INSERT INTO connection_settings 
                    (analyzer_id, connection_type, socket_type, analyzer_address,
                     analyzer_port, lis_address, lis_port, serial_port, baud_rate,
                     data_bits, stop_bits, parity, auto_result_sending,
                     request_sample_info, sample_id_delay, result_sending_delay)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (analyzer_id, connection_type, socket_type, analyzer_address,
                     analyzer_port, lis_address, lis_port, serial_port, baud_rate,
                     data_bits, stop_bits, parity, auto_result, request_sample,
                     sample_delay, result_delay))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Connection settings saved successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save connection settings: {str(e)}")
    
    def save_templates(self):
        analyzer_id = self.analyzer_combo.currentData()
        if not analyzer_id:
            QMessageBox.warning(self, "Warning", "Please select an analyzer first")
            return
        
        try:
            conn = sqlite3.connect('analyzersim.db')
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM tests WHERE analyzer_id = ?", (analyzer_id,))
            
            for row in range(self.test_table.rowCount()):
                test_code = self.test_table.item(row, 0).text()
                unit = self.test_table.item(row, 1).text()
                lower_range = float(self.test_table.item(row, 2).text())
                upper_range = float(self.test_table.item(row, 3).text())
                
                cursor.execute("""
                    INSERT INTO tests (analyzer_id, test_code, unit, lower_range, upper_range)
                    VALUES (?, ?, ?, ?, ?)
                """, (analyzer_id, test_code, unit, lower_range, upper_range))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Templates and test data saved successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save templates and test data: {str(e)}")
    
    def add_test(self):
        row = self.test_table.rowCount()
        self.test_table.insertRow(row)
        self.test_table.setItem(row, 0, QTableWidgetItem("New Test"))
        self.test_table.setItem(row, 1, QTableWidgetItem("Unit"))
        self.test_table.setItem(row, 2, QTableWidgetItem("0.0"))
        self.test_table.setItem(row, 3, QTableWidgetItem("0.0"))
    
    def edit_test(self):
        selected = self.test_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a test to edit")
            return
        
        QMessageBox.information(self, "Info", "Test editing not implemented yet")
    
    def delete_test(self):
        selected = self.test_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a test to delete")
            return
        
        row = selected[0].row()
        test_code = self.test_table.item(row, 0).text()
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                    f"Are you sure you want to delete test '{test_code}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                    QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.test_table.removeRow(row)
    
    def add_sample_input(self):
        sample_row = QWidget()
        sample_row_layout = QHBoxLayout(sample_row)
        sample_row_layout.setContentsMargins(0, 0, 0, 0)
        
        sample_label = QLabel("Sample Number:")
        sample_input = QLineEdit()
        sample_input.setPlaceholderText("Enter sample ID")
        
        patient_label = QLabel("Patient ID:")
        patient_input = QLineEdit()
        patient_input.setPlaceholderText("Enter patient ID")
        
        patient_name_label = QLabel("Patient Name:")
        patient_name_input = QLineEdit()
        patient_name_input.setPlaceholderText("Enter patient name")
        
        sample_row_layout.addWidget(sample_label)
        sample_row_layout.addWidget(sample_input)
        sample_row_layout.addWidget(patient_label)
        sample_row_layout.addWidget(patient_input)
        sample_row_layout.addWidget(patient_name_label)
        sample_row_layout.addWidget(patient_name_input)
        
        remove_button = QToolButton()
        remove_button.setText("X")
        remove_button.clicked.connect(lambda: self.remove_sample_input(sample_row))
        sample_row_layout.addWidget(remove_button)
        
        self.sample_layout.addWidget(sample_row)
    
    def remove_sample_input(self, sample_row):
        sample_row.deleteLater()
    
    def connect_to_lis(self):
        analyzer_id = self.analyzer_combo.currentData()
        if not analyzer_id:
            QMessageBox.warning(self, "Warning", "Please select an analyzer first")
            return
        
        self.log_text.append("Connecting to LIS...")
        QTimer.singleShot(1000, lambda: self.log_text.append("Connected successfully"))
        self.statusBar().showMessage("Connected")
    
    def start_analysis(self):
        sample_ids = []
        patient_ids = []
        patient_names = []
        
        for i in range(self.sample_layout.count()):
            widget = self.sample_layout.itemAt(i).widget()
            if widget:
                layout = widget.layout()
                sample_input = layout.itemAt(1).widget()
                patient_input = layout.itemAt(3).widget()
                patient_name_input = layout.itemAt(5).widget()
                
                if sample_input.text():
                    sample_ids.append(sample_input.text())
                    patient_ids.append(patient_input.text())
                    patient_names.append(patient_name_input.text())
        
        if not sample_ids:
            QMessageBox.warning(self, "Warning", "Please enter at least one sample ID")
            return
        
        self.store_samples(sample_ids, patient_ids, patient_names)
        self.generate_results(sample_ids)
        self.load_sample_list()
        
        self.progress_bar.setMaximum(len(sample_ids))
        self.progress_bar.setValue(0)
        
        self.current_sample_index = 0
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(lambda: self.update_progress(sample_ids))
        self.progress_timer.start(1000)
        
        QMessageBox.information(self, "Started", "Analysis started for {} samples".format(len(sample_ids)))
    
    def update_progress(self, sample_ids):
        if self.current_sample_index < len(sample_ids):
            self.progress_bar.setValue(self.current_sample_index + 1)
            self.current_sample_label.setText(sample_ids[self.current_sample_index])
            self.current_sample_index += 1
        else:
            self.progress_timer.stop()
            self.current_sample_label.setText("Completed")
            QMessageBox.information(self, "Completed", "Analysis completed for all samples")
    
    def store_samples(self, sample_ids, patient_ids, patient_names):
        try:
            conn = sqlite3.connect('analyzersim.db')
            cursor = conn.cursor()
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for i, sample_id in enumerate(sample_ids):
                cursor.execute("SELECT id FROM samples WHERE sample_number = ?", (sample_id,))
                existing = cursor.fetchone()
                
                patient_id = patient_ids[i] if i < len(patient_ids) else ""
                patient_name = patient_names[i] if i < len(patient_names) else ""
                
                if existing:
                    cursor.execute("""
                        UPDATE samples SET
                        patient_id = ?,
                        patient_name = ?,
                        date_time = ?
                        WHERE sample_number = ?
                    """, (patient_id, patient_name, now, sample_id))
                else:
                    cursor.execute("""
                        INSERT INTO samples
                        (sample_number, patient_id, patient_name, date_time)
                        VALUES (?, ?, ?, ?)
                    """, (sample_id, patient_id, patient_name, now))
            
            conn.commit()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to store samples: {str(e)}")
    
    def generate_results(self, sample_ids):
        try:
            analyzer_id = self.analyzer_combo.currentData()
            if not analyzer_id:
                return
            
            conn = sqlite3.connect('analyzersim.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, test_code, lower_range, upper_range
                FROM tests
                WHERE analyzer_id = ?
            """, (analyzer_id,))
            
            tests = cursor.fetchall()
            if not tests:
                conn.close()
                return
            
            for sample_id in sample_ids:
                cursor.execute("SELECT id FROM samples WHERE sample_number = ?", (sample_id,))
                sample_db_id = cursor.fetchone()[0]
                
                for test in tests:
                    test_id, test_code, lower_range, upper_range = test
                    
                    result_value = round(random.uniform(lower_range, upper_range), 3)
                    
                    cursor.execute("""
                        SELECT id FROM results
                        WHERE sample_id = ? AND test_id = ?
                    """, (sample_db_id, test_id))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        cursor.execute("""
                            UPDATE results SET
                            result_value = ?,
                            sent = 0
                            WHERE sample_id = ? AND test_id = ?
                        """, (result_value, sample_db_id, test_id))
                    else:
                        cursor.execute("""
                            INSERT INTO results
                            (sample_id, test_id, result_value, sent)
                            VALUES (?, ?, ?, 0)
                        """, (sample_db_id, test_id, result_value))
            
            conn.commit()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate results: {str(e)}")
    
    def load_sample_list(self):
        try:
            conn = sqlite3.connect('analyzersim.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, sample_number, patient_id, patient_name
                FROM samples
                ORDER BY date_time DESC
            """)
            
            samples = cursor.fetchall()
            
            self.sample_list.setRowCount(len(samples))
            for i, sample in enumerate(samples):
                sample_id, sample_number, patient_id, patient_name = sample
                
                self.sample_list.setItem(i, 0, QTableWidgetItem(sample_number))
                self.sample_list.setItem(i, 1, QTableWidgetItem(patient_id))
                self.sample_list.setItem(i, 2, QTableWidgetItem(patient_name))
                self.sample_list.item(i, 0).setData(Qt.ItemDataRole.UserRole, sample_id)
            
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sample list: {str(e)}")
    
    def load_sample_results(self):
        selected = self.sample_list.selectedItems()
        if not selected:
            return
        
        sample_db_id = self.sample_list.item(selected[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            conn = sqlite3.connect('analyzersim.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT patient_id, patient_name
                FROM samples
                WHERE id = ?
            """, (sample_db_id,))
            
            patient = cursor.fetchone()
            self.patient_id_label.setText(patient[0])
            self.patient_name_label.setText(patient[1])
            
            cursor.execute("""
                SELECT r.id, t.test_code, r.result_value, t.unit, t.lower_range, t.upper_range, r.sent
                FROM results r
                JOIN tests t ON r.test_id = t.id
                WHERE r.sample_id = ?
            """, (sample_db_id,))
            
            results = cursor.fetchall()
            
            self.result_table.setRowCount(len(results))
            for i, result in enumerate(results):
                result_id, test_code, result_value, unit, lower_range, upper_range, sent = result
                
                normal_range = f"{lower_range} - {upper_range}"
                sent_text = "Yes" if sent else "No"
                
                self.result_table.setItem(i, 0, QTableWidgetItem(test_code))
                self.result_table.setItem(i, 1, QTableWidgetItem(str(result_value)))
                self.result_table.setItem(i, 2, QTableWidgetItem(unit))
                self.result_table.setItem(i, 3, QTableWidgetItem(normal_range))
                self.result_table.setItem(i, 4, QTableWidgetItem(sent_text))
                
                self.result_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, result_id)
                
                if result_value < lower_range or result_value > upper_range:
                    for col in range(5):
                        item = self.result_table.item(i, col)
                        item.setBackground(QColor(80, 0, 0))
            
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sample results: {str(e)}")
            
    def send_selected_results(self):
        selected = self.result_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select results to send")
            return
        
        rows = set()
        for item in selected:
            rows.add(item.row())
        
        result_ids = []
        for row in rows:
            result_id = self.result_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            result_ids.append(result_id)
        
        self.send_results(result_ids)
    
    def send_all_results(self):
        result_ids = []
        for row in range(self.result_table.rowCount()):
            result_id = self.result_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            result_ids.append(result_id)
        
        self.send_results(result_ids)
    
    def send_results(self, result_ids):
        if not result_ids:
            return
        
        try:
            conn = sqlite3.connect('analyzersim.db')
            cursor = conn.cursor()
            
            for result_id in result_ids:
                cursor.execute("UPDATE results SET sent = 1 WHERE id = ?", (result_id,))
            
            conn.commit()
            conn.close()
            
            self.load_sample_results()
            
            self.log_text.append(f"Sent {len(result_ids)} results to LIS")
            QMessageBox.information(self, "Success", f"{len(result_ids)} results sent successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send results: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabSimulator()
    window.show()
    sys.exit(app.exec())