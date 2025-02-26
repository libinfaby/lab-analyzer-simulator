from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QToolButton, QPushButton, QScrollArea

class SampleInputWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.sample_container = QWidget()
        self.sample_layout = QVBoxLayout(self.sample_container)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.sample_container)
        layout.addWidget(scroll_area)
        
        self.add_sample_button = QPushButton("Add More Samples")
        layout.addWidget(self.add_sample_button)
        
        self.add_sample_input()

    def add_sample_input(self):
        sample_row = QWidget()
        sample_row_layout = QHBoxLayout(sample_row)
        
        sample_label = QLabel("Sample Number:")
        sample_input = QLineEdit()
        patient_label = QLabel("Patient ID:")
        patient_input = QLineEdit()
        patient_name_label = QLabel("Patient Name:")
        patient_name_input = QLineEdit()
        
        sample_row_layout.addWidget(sample_label)
        sample_row_layout.addWidget(sample_input)
        sample_row_layout.addWidget(patient_label)
        sample_row_layout.addWidget(patient_input)
        sample_row_layout.addWidget(patient_name_label)
        sample_row_layout.addWidget(patient_name_input)
        
        remove_button = QToolButton()
        remove_button.setText("X")
        remove_button.clicked.connect(lambda: sample_row.deleteLater())
        sample_row_layout.addWidget(remove_button)
        
        self.sample_layout.addWidget(sample_row)