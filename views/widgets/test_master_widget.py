from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QHBoxLayout, QPushButton, QTableWidgetItem, QHeaderView

class TestMasterWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.test_table = QTableWidget()
        self.test_table.setColumnCount(4)
        self.test_table.setHorizontalHeaderLabels(["Test Code", "Unit", "Lower Range", "Upper Range"])
        self.test_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.test_table)
        
        button_layout = QHBoxLayout()
        self.add_test_button = QPushButton("Add Test")
        self.edit_test_button = QPushButton("Edit Test")
        self.delete_test_button = QPushButton("Delete Test")
        button_layout.addWidget(self.add_test_button)
        button_layout.addWidget(self.edit_test_button)
        button_layout.addWidget(self.delete_test_button)
        layout.addLayout(button_layout)