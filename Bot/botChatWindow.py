from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
import os, sys
# Required for config management
from collections import deque
# Required for chat message history management



class botChatWindow(QMainWindow):
    """The window class"""

    def __init__(self):
    # setup
        super().__init__()

        self.thisExeDir = os.path.dirname(sys.executable)
        # the directory this exe is located in
        self.mainIcon = os.path.join(sys._MEIPASS, "SBO.png")
        # the directory containing the program icon png (built-in)

        self.mainFolder = os.path.abspath(os.path.join(self.thisExeDir, "..", "..", ".."))
        # stores the "main" folder (SBO, which is 3 folders up)

        self.setMinimumSize(400, 600)
        # sets the window size 
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setWindowTitle("SBOT Command Log Window")
        # sets title name

        self.stdinThread = QThread()
        # the thread for the STDIN reader to sit in
        self.stdinWorker = StdinWorker()
        # reference to the actual worker class

    ### Main Layout ###

        self.mainLayout = QGridLayout()
        # sets the main layout to use
        self.mainLayout.setObjectName("mainLayout")
        # sets name
        self.mainLayout.setContentsMargins(15, 20, 15, 20)
        # sets margins of 25px 
        self.mainLayout.setVerticalSpacing(25)
        # sets vertical spacing

        self.centerWidget = QWidget()
        # creates a widget to sit in the middle of the screen
        self.centerWidget.setLayout(self.mainLayout)
        # sets the main layout

        self.setCentralWidget(self.centerWidget)
        # sets the centerWidget to the central widget

    ### Console ###

        self.consoleScroll = QScrollArea()
        # a console-like scrollable area
        self.consoleScroll.setWidgetResizable(True)
        # allows the widget to be resized
        self.consoleScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # disables the scroll bar
        self.consoleScroll.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        # allows the scroll area to resize on window expand
        self.consoleScroll.setMinimumSize(300, 525)
        # sets a minimum height
        self.consoleScroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                padding-top: 15px;
                padding-bottom: 15px;
            }
        """)
        # sets a custom style to add some space between the edges and the text
        self.mainLayout.addWidget(self.consoleScroll, 1, 1, 3, 3)
        # adds the label to the main layout (top middle)

        self.mainLabel = QLabel()
        # a label to hold the main information about current process
        self.mainLabel.setText("Twitch Command Chat\nWaiting for commands...")
        # initial text
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        # left-aligns the label to the bottom
        self.mainLabel.setWordWrap(True)
        # makes the text wrap if it's too wide
        self.mainLabel.setMinimumWidth(300)
        # sets a minimum size for the label
        self.consoleScroll.setWidget(self.mainLabel)
        # sets the "console" to use the mainLabel

    ### Messages ###

        self.messages = deque(maxlen = 100)
        # a deque (a self-deleting list) of messages

    ### STDIN Read ###

        self.stdinWorker.moveToThread(self.stdinThread)
        # moves the worker to its own thread
        self.stdinThread.started.connect(self.stdinWorker.stdinRead)
        # on thread start, runs the worker reader

        self.stdinWorker.newMessageSignal.connect(self.consoleForm)
        # the new message from SBOT -> read -> connects to consoleForm to update console

        self.stdinWorker.finished.connect(self.stdinThread.quit)
        # when the worker is done, quits the thread
        self.stdinThread.finished.connect(self.stdinWorker.deleteLater)
        # deletes the worker after the thread is done
        self.stdinThread.finished.connect(self.close)
        # closes the whole window when the thread is done

        self.show()
        # enables the window
        self.stdinThread.start()
        # starts the thread

### Console Former ###

    def consoleForm(self, newLine:str):
        """Function to add new lines of code to the console"""

        self.messages.append((newLine))
        # adds the text to the list

        fullConsole = ("\n".join(self.messages))
        # joins all the messages together for one console experience
        self.mainLabel.setText(f"{fullConsole}")
        # sets the main label to use the joined text
        QTimer.singleShot(500, self.autoScroll)
        # runs the autoscroller after half a second to let the text sit

### Auto-Scroll ###

    def autoScroll(self):
        """Function to scroll the 'console' to the bottom"""

        scroller = self.consoleScroll.verticalScrollBar()
        # definition
        scroller.setValue(scroller.maximum())
        # uses the max value (pushes to bottom)



### STDIN ###

class StdinWorker(QObject):
    """Class for the STDIN reader to sit in"""

    newMessageSignal = pyqtSignal(str)
    # a signal that gets sent when a new message is found
    finished = pyqtSignal()
    # work done signal

    def stdinRead(self):
        """Function to read the stdin and fill the chat"""

        try:
            for line in sys.stdin:
            # reads the standard input
                line = line.rstrip("\n")
                # removes new line markers
                
                if not line:
                # if there's an empty line
                    continue
                    # resets loop

                if "SBOT" in line:
                # if the command is from SBOT
                    self.newMessageSignal.emit(f"{line}\n")
                    # adds a new line after the message (spacer)
                else:
                # not SBOT
                    self.newMessageSignal.emit(line)
                    # sends the line across the signal

        finally:
        # once it fails (stdin closed)
            self.finished.emit()
            # sends the signal to close the thread/worker

### Starter ###

if __name__ == "__main__":
# runs at start

    app = QApplication(sys.argv)
    # creates a Qt Application
    botWin = botChatWindow()
    # instantiates the UI class

    sys.exit(app.exec())
    # waits for the app to be done, then exits