from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer

class MainController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.setup_connections()
        self.load_analyzers()

    def setup_connections(self):
        self.view.set_button.clicked.connect(self.set_analyzer)
        self.view.connection_settings_widget.save_button.clicked.connect(self.save_connection_settings)
        self.view.test_master_widget.add_test_button.clicked.connect(self.add_test)
        self.view.sample_input_widget.add_sample_button.clicked.connect(self.view.sample_input_widget.add_sample_input)

    def load_analyzers(self):
        analyzers = self.model.get_analyzers()
        self.view.analyzer_combo.clear()
        for analyzer_id, name in analyzers:
            self.view.analyzer_combo.addItem(name, analyzer_id)

    def set_analyzer(self):
        analyzer_id = self.view.analyzer_combo.currentData()
        settings = self.model.get_connection_settings(analyzer_id)
        if settings:
            # Update connection settings widget
            pass
        tests = self.model.get_tests(analyzer_id)
        self.view.test_master_widget.test_table.setRowCount(len(tests))
        for i, test in enumerate(tests):
            for j, value in enumerate(test):
                self.view.test_master_widget.test_table.setItem(i, j, QTableWidgetItem(str(value)))

    def save_connection_settings(self):
        analyzer_id = self.view.analyzer_combo.currentData()
        if not analyzer_id:
            QMessageBox.warning(self.view, "Warning", "Please select an analyzer first")
            return
        # Collect settings from widget and save via model
        self.model.save_connection_settings(analyzer_id, settings)

    def add_test(self):
        row = self.view.test_master_widget.test_table.rowCount()
        self.view.test_master_widget.test_table.insertRow(row)
        self.view.test_master_widget.test_table.setItem(row, 0, QTableWidgetItem("New Test"))
        self.view.test_master_widget.test_table.setItem(row, 1, QTableWidgetItem("Unit"))
        self.view.test_master_widget.test_table.setItem(row, 2, QTableWidgetItem("0.0"))
        self.view.test_master_widget.test_table.setItem(row, 3, QTableWidgetItem("0.0"))