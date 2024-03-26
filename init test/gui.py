from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QApplication, QTextEdit, QMessageBox)
from PyQt5.QtCore import QProcess
import sys
from communication import SerialCommunication

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Egg Drawing CNC Controller")
        self.setGeometry(100, 100, 900, 600)  # Adjusted for additional space
        self.serial_comm = SerialCommunication()
        self.init_ui()
        self.serial_comm.request_state(self.update_status)

    def init_ui(self):
        mainLayout = QHBoxLayout()

        # Setup status and control panel
        self.setup_status_panel()

        # Setup preview panel
        self.previewPanel = QWidget()
        
        # Setup program setup and editing panel
        self.setup_program_panel()

        # Assemble main layout
        mainLayout.addWidget(self.statusPanel)
        mainLayout.addWidget(self.previewPanel)
        mainLayout.addWidget(self.setupPanel)

        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def setup_status_panel(self):
        self.statusPanel = QWidget()
        self.statusLayout = QVBoxLayout()
        self.statusLabel = QLabel("Status: Idle")
        self.calibrateButton = QPushButton("Calibrate")
        # Connect buttons to actions
        self.calibrateButton.clicked.connect(lambda: self.serial_comm.send_command("calibrate"))
        # Add widgets to layout
        self.statusLayout.addWidget(self.statusLabel)
        self.statusLayout.addWidget(self.calibrateButton)
        self.statusPanel.setLayout(self.statusLayout)

    def setup_program_panel(self):
        self.setupPanel = QWidget()
        self.setupLayout = QVBoxLayout()
        self.scriptEditor = QTextEdit()
        self.load_script()
        self.executeButton = QPushButton("Execute")
        # Connect execute button to the execute_script function
        self.executeButton.clicked.connect(self.execute_script)
        self.setupLayout.addWidget(self.scriptEditor)
        self.setupLayout.addWidget(self.executeButton)
        self.setupPanel.setLayout(self.setupLayout)

    def load_script(self):
        try:
            with open("execution.py", "r") as file:
                self.scriptEditor.setText(file.read())
        except FileNotFoundError:
            self.scriptEditor.setText("# Add your pattern functions here.")

    def execute_script(self):
        # Save the script before execution
        with open("execution.py", "w") as file:
            file.write(self.scriptEditor.toPlainText())
        # Execute the script
        process = QProcess(self)
        process.start("python", ["execution.py"])
        process.finished.connect(lambda: QMessageBox.information(self, "Execution Complete", "The pattern script has finished executing."))

    def update_status(self, status):
        self.statusLabel.setText(f"Status: {status}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
