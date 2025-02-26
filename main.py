import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
from controllers.main_controller import MainController
from models.data_model import DataModel

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load stylesheet
    with open("resources/styles/dark_theme.qss", "r") as f:
        app.setStyleSheet(f.read())
    
    model = DataModel()
    view = MainWindow()
    controller = MainController(model, view)
    
    view.show()
    sys.exit(app.exec())