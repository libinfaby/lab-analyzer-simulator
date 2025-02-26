from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QLineEdit, QComboBox, QPushButton, QCheckBox, QLabel, QGroupBox, QFormLayout

class ConnectionSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Connection type
        conn_type_group = QGroupBox("Connection Type")
        conn_type_layout = QHBoxLayout(conn_type_group)
        self.tcp_radio = QRadioButton("TCP/IP")
        self.serial_radio = QRadioButton("Serial")
        self.tcp_radio.setChecked(True)
        conn_type_layout.addWidget(self.tcp_radio)
        conn_type_layout.addWidget(self.serial_radio)
        layout.addWidget(conn_type_group)
        
        # TCP settings
        self.tcp_widget = QWidget()
        tcp_layout = QFormLayout(self.tcp_widget)
        self.server_radio = QRadioButton("Server")
        self.client_radio = QRadioButton("Client")
        self.server_radio.setChecked(True)
        socket_layout = QHBoxLayout()
        socket_layout.addWidget(self.server_radio)
        socket_layout.addWidget(self.client_radio)
        tcp_layout.addRow("Socket Type:", socket_layout)
        self.analyzer_address = QLineEdit("127.0.0.1")
        tcp_layout.addRow("Analyzer Address:", self.analyzer_address)
        # Add other TCP fields...
        layout.addWidget(self.tcp_widget)
        
        # Serial settings (hidden initially)
        self.serial_widget = QWidget()
        self.serial_widget.setVisible(False)
        # Add serial fields...
        
        # Common settings
        common_group = QGroupBox("Common Settings")
        common_layout = QVBoxLayout(common_group)
        self.auto_result = QCheckBox("Automatic Result Sending")
        self.request_sample = QCheckBox("Request Sample Info")
        common_layout.addWidget(self.auto_result)
        common_layout.addWidget(self.request_sample)
        layout.addWidget(common_group)
        
        self.save_button = QPushButton("Save Connection Settings")
        layout.addWidget(self.save_button)