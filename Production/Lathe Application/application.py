from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QLabel, QApplication,
                             QVBoxLayout, QHBoxLayout, QWidget,QGridLayout)
from PyQt5.QtGui import QPainter, QImage, QIcon, QPixmap, QFont
from io import BytesIO
import pygame
import serial
import time
from structure import *
from commands import *
import sys

class MainWindow(QMainWindow):
    def __init__(self, queue):
        super().__init__()
        self.setWindowTitle("Egg Lathe")
        self.setGeometry(100, 100, 800, 600)
        self.queue = queue
        self.progress = None
        self.serial = None
        # Main widget and layout
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QHBoxLayout(self.centralWidget)

        # Left layout for preview and console text
        self.leftLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.leftLayout)

        # Preview image label
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setFixedSize(400, 400)  # Adjust as necessary
        self.leftLayout.addWidget(self.imageLabel)

        # Console text label
        self.consoleTextLabel = QLabel()
        self.consoleTextLabel.setFont(QFont(None, 25))
        self.consoleTextLabel.setAlignment(Qt.AlignCenter)
        self.leftLayout.addWidget(self.consoleTextLabel)
        
        # ETA text label
        self.etaText = QLabel("ETA")
        self.etaText.setFont(QFont(None, 25))
        self.etaText.setAlignment(Qt.AlignCenter)
        self.leftLayout.addWidget(self.consoleTextLabel)

        # Right layout for the movement control panel and execute button
        self.rightLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.rightLayout)

        # Add MovementControlPanel
        self.movementPanel = self.MovementControlPanel(self)
        self.rightLayout.addWidget(self.movementPanel)

        # Execute button
        self.executeButton = QPushButton("Connect")
        self.executeButton.clicked.connect(self.connectSerial)
        self.rightLayout.addWidget(self.executeButton)
        
        # Simulate button
        self.simulateButton = QPushButton("Simulate")
        self.simulateButton.clicked.connect(self.startSimulation)
        self.rightLayout.addWidget(self.simulateButton)
        
        # Spacer to push everything to the top
        self.rightLayout.addStretch()

        # Initialize other components
        self.consoleText = ""
        self.commandtime = COMMAND_TIME
    
        self.progress = 0
        
        self.simulationTimer = QTimer(self)
        self.simulationTimer.timeout.connect(self.simulate)
        self.commandtime = COMMAND_TIME  # Example value, adjust as necessary

        
        # Set up a QTimer to update the preview image
        self.previewTimer = QTimer(self)
        self.previewTimer.timeout.connect(self.updatePreview)
        self.oldProgress = 0
        self.previewTimer.start(100)  # update every 100 milliseconds

    def updatePreview(self):
        if self.progress != self.oldProgress:
            self.previewPaths(progress=self.progress)
            self.oldProgress = self.progress
    def startSimulation(self):
        self.simulationTimer.start(10)
        self.simulateButton.setText("Stop Simulation")
        # Disconnect all connections to avoid multiple connections to slots
        self.simulateButton.clicked.disconnect()
        # Connect the new slot
        self.simulateButton.clicked.connect(self.stopSimulation)
    def stopSimulation(self):
        self.simulationTimer.stop()
        self.progress = 0
        self.simulateButton.setText("Simulate")
        # Disconnect all connections to avoid multiple connections to slots
        self.simulateButton.clicked.disconnect()
        # Connect the new slot
        self.simulateButton.clicked.connect(self.startSimulation)
    def simulate(self):
        if self.queue and self.progress < self.queue.length:
            print("looping")
            command = self.queue.queue[self.progress]
            start_time = time.time_ns()
            self.progress += 1
            #self.previewPaths(self.progress)
            self.consoleTextLabel.setText(f"Executing {command.type} {command.movement}")  # Assuming command is a string, update this if it's not
            self.commandtime = self.commandtime + (time.time_ns() - start_time)
            print(f"loop complete, progress is {self.progress}")
            # Calculate average command time if needed
            # self.commandtime = self.commandtime / self.commands_executed
            
        else:
            print("Simulation complete")
            self.simulationTimer.stop()  # Stop the timer if there are no more commands

        
    def updateAll(self):
        self.updateExecuteButton()
        self.updateConsoleText()
        self.previewPaths(progress=self.progress)
        QApplication.processEvents()
    def previewPaths(self,progress = None):
        self.displayPygameSurface(self.queue.previewPygame((False,True), surface = False, executionIndex = progress))
    
    def updateExecuteButton(self):
        if self.serial != None: 
            # Update the button's text
            self.executeButton.setText("Execute")
            # Disconnect all connections to avoid multiple connections to slots
            self.executeButton.clicked.disconnect()
            # Connect the new slot
            self.executeButton.clicked.connect(self.executeButtonClicked)
        else:
            # Update the button's text
            self.executeButton.setText("Connect")
            # Disconnect all connections to avoid multiple connections to slots
            self.executeButton.clicked.disconnect()
            # Connect the new slot
            self.executeButton.clicked.connect(self.connectSerial)
            
    def connectSerial(self, port = '/dev/cu.usbmodem101'):
        print(f"Attempting to connect to port {'/dev/cu.usbmodem101'}")
        try:
            ser = serial.Serial(str('/dev/cu.usbmodem101'), 9600, timeout=1)
        except serial.SerialException:
            print("The port is not available")
            self.consoleText = f"Cannot connect to port {'/dev/cu.usbmodem101'}"
            self.serial = None
            self.updateExecuteButton()
            self.updateConsoleText()
            return True
        else:
            self.serial = ser
            self.consoleText = f"Connecting to {'/dev/cu.usbmodem101'}"
            print("Connecting...")
            time.sleep(0.1)  # Allow time for the connection to establish
            self.consoleText = "Connected!"
            self.updateExecuteButton()
            self.updateConsoleText()
            return False
    
    def executeButtonClicked(self):
        if self.serial != None:
            self.consoleText = "Executing..."
            self.updateConsoleText()
            self.queue.execute(self.serial, window=self)
            return True
        else:
            self.consoleText = "Cannot execute; no device connected"
            self.updateConsoleText()
            return False

    def updateConsoleText(self):
        self.consoleTextLabel.setText(self.consoleText)
        self.etaText.setText(str(((len(self.queue.queue)-self.progress)*self.commandtime)/1000000000))
        
    def pygameSurfaceToQPixmap(self, pygameSurface):
        """Converts a Pygame surface to a QPixmap using a BytesIO object."""
        image_data = BytesIO()
        pygame.image.save(pygameSurface, image_data, 'PNG')
        image_data.seek(0)

        qimage = QImage()
        qimage.loadFromData(image_data.getvalue())

        return QPixmap.fromImage(qimage)

    def displayPygameSurface(self, pygameSurface):
        """Updates the QLabel with the new Pygame surface."""
        pixmap = self.pygameSurfaceToQPixmap(pygameSurface)
        self.imageLabel.setPixmap(pixmap)
    
    class MovementControlPanel(QWidget):
        def __init__(self, window):
            super().__init__()
            self.initUI()
            self.distance = 10
            self.window = window

        def initUI(self):
            # Define a fixed size for the buttons
            button_size = QSize(50, 50)

            # Create a grid layout
            grid = QGridLayout()
            grid.setSpacing(10)  # Add some spacing between buttons

            # Initialize buttons with a fixed square size
            self.upButton = QPushButton()
            self.upButton.setFixedSize(button_size)
            self.upButton.setIcon(QIcon('Images/arrowiconup.png'))  # Replace with your actual icon path
            self.upButton.setIconSize(QSize(50, 50))  # Set a suitable icon size
            self.upButton.clicked.connect(self.moveUp)

            self.downButton = QPushButton()
            self.downButton.setFixedSize(button_size)
            self.downButton.setIcon(QIcon('Images/arrowicondown.png'))  # Replace with your actual icon path
            self.downButton.setIconSize(QSize(50, 50))
            self.downButton.clicked.connect(self.moveDown)

            self.leftButton = QPushButton()
            self.leftButton.setFixedSize(button_size)
            self.leftButton.setIcon(QIcon('Images/arrowiconleft.png'))  # Replace with your actual icon path
            self.leftButton.setIconSize(QSize(50, 50))
            self.leftButton.clicked.connect(self.moveLeft)

            self.rightButton = QPushButton()
            self.rightButton.setFixedSize(button_size)
            self.rightButton.setIcon(QIcon('Images/arrowiconright.png'))  # Replace with your actual icon path
            self.rightButton.setIconSize(QSize(50, 50))
            self.rightButton.clicked.connect(self.moveRight)

            self.homeButton = QPushButton()
            self.homeButton.setFixedSize(button_size)
            self.homeButton.setIcon(QIcon('path/to/your/home-icon.png'))  # Replace with your actual icon path
            self.homeButton.setIconSize(QSize(50, 50))
            self.homeButton.clicked.connect(self.moveHome)

            # Adding buttons to specific positions in the grid
            grid.addWidget(self.upButton, 0, 1)
            grid.addWidget(self.leftButton, 1, 0)
            grid.addWidget(self.homeButton, 1, 1)
            grid.addWidget(self.rightButton, 1, 2)
            grid.addWidget(self.downButton, 2, 1)

            # Set equal row and column sizes
            for i in range(3):
                grid.setColumnMinimumWidth(i, button_size.width())
                grid.setRowMinimumHeight(i, button_size.height())

            # Set the layout of the widget
            self.setLayout(grid)
            
            # Calculate and set a fixed size for the widget based on the button sizes and spacing
            grid_width = button_size.width() * 3 + grid.spacing() * 2
            grid_height = button_size.height() * 3 + grid.spacing() * 2
            self.setFixedSize(grid_width, grid_height)
        
        # Movement functions
        def moveUp(self):
            print("Move Up")
            self.movementSend(Command("move",(0,self.distance)))
            # Your code to send the move up command to the machine

        def moveDown(self):
            print("Move Down")
            self.movementSend(Command("move",(0,-self.distance)))
            # Your code to send the move down command to the machine

        def moveLeft(self):
            print("Move Left")
            self.movementSend(Command("move",(-self.distance,0)))
            # Your code to send the move left command to the machine

        def moveRight(self):
            print("Move Right")
            self.movementSend(Command("move",(self.distance,0)))
            # Your code to send the move right command to the machine

        def moveHome(self):
            print("Move Home")
            self.movementSend(Command("calibrate"))
            # Your code to send the machine to its home position
        
        def movementSend(self,command):
            if self.window.serial != None:
                command.execute(self.window.serial)
                self.window.consoleText = f"Executing command {command.type}"
            else:
                self.window.consoleText = f"Couldn't execute command {command.type}; Serial closed"
            self.window.updateConsoleText()


def run(queue):
    app = QApplication(sys.argv)
    window = MainWindow(queue)
    window.show()
    sys.exit(app.exec_())

# Running the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(Queue())
    window.show()
    sys.exit(app.exec_())