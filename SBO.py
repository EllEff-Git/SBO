import subprocess, socket, requests, datetime
# Required to run the bot, the websocket and the python communication system
import os, sys, time, threading, queue, concurrent.futures
# Required for system information, background tasking and queueing
import spotipy, requests, json, re, random
# Required for basic function of Spotify data requests and storing
from spotipy.oauth2 import SpotifyOAuth
# Required for authorizing with Spotify
from spotipy.exceptions import SpotifyException
# Required to check for token exceptions (errors)
from collections import deque
# Required for custom "console"
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required for the UI 
from SBOver import Version
# Version manager


### Version ###

SBOver = str(Version)
"""The SBO program version (Y.M.DD.HHMM)"""



### Global Variables ###

directory = os.path.dirname(sys.executable)
"""The base directory of the program, where SBO.exe resides"""
iconPath = os.path.join(sys._MEIPASS, "SBO.png")
"""The directory containing the program icon png (built-in)"""

sboWS = None
"""The SBO-WebSocket process"""
sbowsExe = "SBO-WS.exe"
"""The name of the SBO-WS.exe file"""
sbowsDir = os.path.join(directory, "runtime", "SBO-WS")
"""The websocket folder (SBO/runtime/SBO-WS)"""
sbowsPath = os.path.join(sbowsDir, sbowsExe)
"""The full path to the SBO-WS.exe (SBO/runtime/SBO-WS/SBO-WS.exe)"""

### SBO Bot ###

sboBot = None
"""The SBO-Bot process"""
sboBotDir = os.path.join(directory, "runtime", "SBO-Bot")
"""The bot's folder (SBO/runtime/Bot) """
sboBotPath = os.path.join(sboBotDir, "SBO-Bot.exe")
"""The full path to the SBO-Bot.exe (SBO/runtime/SBO-Bot/SBO-Bot.exe)"""

### Config ###

qtFolderPath = os.path.join(directory, "runtime", "Qt")
"""The folder that contains all the Qt window folders/executables (SBO/runtime/Qt)"""
configFolderPath = os.path.join(os.environ["LOCALAPPDATA"], "SBO")
"""The folder path that should contain all the configuration files"""

os.makedirs(configFolderPath, exist_ok=True)
# makes all the directories leading up to the config folder (it's okay if they already exist)

secretConfigPath = os.path.join(configFolderPath, "secretConfig.json")
"""The full path to the secret config file (C:/Users/<user>/AppData/Local/SBO/secretConfig.json)"""
secretConfig = {}
"""Dictionary that contains all the secret configuration settings"""

funcConfigExePath = os.path.join(qtFolderPath, "funcWindow", "funcWindow.exe")
"""The full path to the functonal config program exe (SBO/runtime/Qt/funcWindow/funcWindow.exe)"""
funcConfigPath = os.path.join(configFolderPath, "functionConfig.json")
"""The full path to the functional config file (C:/Users/<user>/AppData/Local/SBO/functionConfig.json)"""
funcConfig = {}
"""Dictionary that contains all the functional configuration settings"""

sboConfigExePath = os.path.join(qtFolderPath, "sboWindow", "sboWindow.exe")
"""The full path to the SBO config program exe (SBO/runtime/Qt/sboWindow/sboWindow.exe)"""
sboConfigPath = os.path.join(configFolderPath, "sboConfig.json")
"""The full path to the SBO config file (C:/Users/<user>/AppData/Local/SBO/sboConfig.json)"""
sboConfig = {}
"""Dictionary that contains all the SBO-related configuration settings"""

cmdConfigExePath = os.path.join(qtFolderPath, "cmdWindow", "cmdWindow.exe")
"""The full path to the bot command config program exe (SBO/runtime/Qt/cmdWindow/cmdWindow.exe)"""

### Spotify Token Cache ###

spotifyCachePath = os.path.join(configFolderPath, "spotifycache.json")
"""The directory where the spotify cache (token) sits in"""

### Colors ###

colorStringFile = "colorStrings.json"
"""The name of the color string map file"""
colorStringPath = os.path.join(configFolderPath, colorStringFile)
"""The full path to the colorStrings.json file (SBO/Data/colorStrings.json)"""

### Request URLs ###

gURL = "https://api.github.com/repos/EllEff-Git/SBO/tags"
"""The GitHub URL to make update check requests to"""
vURL = "http://127.0.0.1:41809/version"
"""The localhost URL to make a DSI check request to"""
pURL = "http://127.0.0.1:41809/spData"
"""The localhost URL to make DSI data requests to"""

# Event Thread / Auth Lock #

songEvent = threading.Event()
"""Creates an empty threading event list for song"""
spotifyLock = threading.Lock()
"""Creates a locking method to prevent multiple API calls stacking"""

### Required Items ###

spotifyClientID = None
"""The Spotify Client ID from Developer Dashboard (string)"""
spotifyClientSecret = None
"""The Spotify Secret from Developer Dashboard (string)"""
spotifyRedirect = None
"""The Spotify redirect URL from Developer Dashboard"""

### Functional Config ###

webHost = None
"""The WebHost socket to use for the Bot PTP connection"""
webHostPortBot = None
"""The port to use for the Bot PTP connection (httpPort + 1, int)"""
webHostPortWS = None
"""The port to use for the WS PTP connection (httpPort + 2, int)"""
consoleLength = 25
"""How many lines of text the console should store (int)"""
skipFuncCfgWin = False
"""Whether to skip the function configuration window automatically (boolean)"""
skipSBOcfgWin = False
"""Whether to skip the SBO configuration window automatically (boolean)"""
enableBot = False
"""Whether to enable the Twitch Bot (boolean)"""
skipRequired = False
"""Whether to skip the required items check"""
DSIoverride = False
"""Whether DSI is active and should override SBO's Spotify logic (boolean)"""

### Color Config ###

songColorHex = artistColorHex = albumColorHex = barColorHex = overlayColorHex = None
"""Saves all the colors as empty, so that they can hold hex codes later"""
customColors = None
"""Variable storing the custom colors from colorStrings.json"""

defaultColorDict = {
    "white": "FFFFFF",
    "silver": "C0C0C0",
    "gray": "808080",
    "black": "000000",
    "red": "FF0000",
    "maroon": "800000",
    "yellow": "FFFF00",
    "olive": "808000",
    "lime": "00FF00",
    "green": "008000",
    "aqua": "00FFFF",
    "teal": "008080",
    "blue": "0000FF",
    "navy": "000080",
    "fuchsia": "FF00FF",
    "purple": "800080"
}
"""The default color mapping (color name : hex code) to use for/instead of colorStrings.json"""

colorFunctionMap = {
    "Overlay Color": "borderColor",
    "Song Color": "titleColor",
    "Artist Color": "artistColor",
    "Album Color": "albumColor",
    "Bar Color": "progressColor"
}
"""A map of the color commands and what their WS/HTML counterpart is"""

colorFunctionHexMap = {
    "Overlay Color": overlayColorHex,
    "Song Color": songColorHex,
    "Artist Color": artistColorHex,
    "Album Color": albumColorHex,
    "Bar Color": barColorHex
}
"""A map of the color commands and what their corresponding hex variable is"""



### DSI Check ###

def dsiStatusCheck() -> bool:
    """Function to make a DSI status check"""
    try:
    # tries to make a request
        dsiCheck = requests.get(vURL, timeout=2)
        # sends a request to localhost address to see if DSI is already up on the same machine

        if dsiCheck.status_code == 200:
        # if the response is status code 200 (all good)
            return True
            # returns True (can connect)
        else:
        # response isn't 200 (everything not good, but is live?)
            return True
            # returns True (can connect, maybe?)
    except:
    # can't connect
        return False
        # returns False (can't connect)

DSIoverride = dsiStatusCheck()
# runs the function to get the status of DSI, stores in global var



### Starter Window ###

class starterWindow(QWidget):
    """The startup window"""

    labelSwap = pyqtSignal(str)
    # a pyQt signal to swap the label

    def __init__(self):
        super().__init__()
        # init

    ### Init / Basic ###

        self.version = SBOver
        # stores the version in self
        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"SBO Starter"
        # stores the program name

        self.windowSizeX = max(800, int(startApp.primaryScreen().size().width() / 4))
        self.windowSizeY = int(self.windowSizeX * (9 / 16))
        # base window sizes (dynamic, based on display res)

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(self.windowSizeX, self.windowSizeY))
        # the window size minimums

    ### Layout ###

        self.mainLayout = QGridLayout()
        # a layout to use
        self.mainLayout.setContentsMargins(50, 50, 50, 50)
        # sets margins of 50px to each edge
        self.setLayout(self.mainLayout)
        # makes the window use that layout

    ### Labels ###

        self.userInstructLabel = QLabel("")
        # label for user instructions
        self.userInstructLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.topSpacer = QSpacerItem(200, 50)
        # a spacer to create gap between the instructions and the inputs

        self.inputField1 = QLineEdit("")
        self.inputField1.hide()
        self.inputLabel1 = QLabel("")
        self.inputLabel1.hide()
        # label + entry field 1

        self.inputField2 = QLineEdit("")
        self.inputField2.hide()
        self.inputLabel2 = QLabel("")
        self.inputLabel2.hide()
        # label + entry field 2

        self.inputField3 = QLineEdit("")
        self.inputField3.hide()
        self.inputLabel3 = QLabel("")
        self.inputLabel3.hide()
        # label + entry field 3

        self.statusLabel = QLabel("Loading SBO...")
        # a simple label to indicate current progress

    ### Buttons ###

        self.buttonSpacer = QSpacerItem(200, 30)
        # a smaller spacer to create gap between the inputs and the buttons

        self.continueButton = QPushButton("Continue")
        self.continueButton.setToolTip("Enter the given fields and proceed")
        self.continueButton.setFixedSize(75, 35)
        self.continueButton.hide()
        # button to move forward

        self.skipButton = QPushButton("Skip")
        self.skipButton.setToolTip("Bypass Spotify auth\nUse this only if using with DSI!")
        self.skipButton.setFixedSize(75, 35)
        self.skipButton.hide()
        # button to skip the step

        self.bottomSpacer = QSpacerItem(200, 50)
        # a spacer to create gap between the buttons and the status

    ### Layout Placement ###

        self.mainLayout.addWidget(self.userInstructLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addItem(self.topSpacer, 1, 0)
        # adds the instruct label and spacer to the top

        self.inputLayout = QGridLayout()
        # a layout for the input fields to go into
        self.mainLayout.addLayout(self.inputLayout, 2, 0)
        # adds to the main layout (3rd row, under instruct label and top spacer)

        self.inputLayout.addWidget(self.inputLabel1, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.inputLayout.addWidget(self.inputField1, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds 1st field label + entry

        self.inputLayout.addWidget(self.inputLabel2, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.inputLayout.addWidget(self.inputField2, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds 2nd field label + entry

        self.inputLayout.addWidget(self.inputLabel3, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.inputLayout.addWidget(self.inputField3, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds 3rd field label + entry

        self.buttonLayout = QGridLayout()
        # layout for the buttons to go into
        self.inputLayout.addLayout(self.buttonLayout, 6, 0)
        # adds to the input layout (bottom row)

        self.buttonLayout.addItem(self.buttonSpacer, 0, 0, 1, 2)
        self.buttonLayout.addWidget(self.skipButton, 1, 0)
        self.buttonLayout.addWidget(self.continueButton, 1, 1)
        self.buttonLayout.addItem(self.bottomSpacer, 2, 0, 1, 2)
        # adds buttons to their layout

        self.mainLayout.addWidget(self.statusLabel, 7, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all to the layouts

    ### Run ###

        self.labelSwap.connect(self.statusLabelSwap)
        # connects the pyqt signal to the function responsible for swapping the status label
        self.skipButton.clicked.connect(lambda: self.requiredItemsStore(0))
        self.continueButton.clicked.connect(lambda: self.requiredItemsStore(1))
        # connects the buttons to their commands
        QTimer.singleShot(0, self.funcConfigManager)
        # runs the functional configuration manager when the UI is done loading



### Status Label Swap ###

    def statusLabelSwap(self, text:str):
        """Function to change the current status label"""
        self.statusLabel.setText(text)
        # sets the text to match



### Functional Config ###

    def funcConfigManager(self):
        """Function that manages the functional configuration"""
        global funcConfig
        # global -> local

        if os.path.exists(funcConfigPath):
        # if the config file exists
            try:
            # tries to read the config file (try because it could fail)
                with open(funcConfigPath, "r", encoding="utf-8") as fncCfg:
                # opens the SHAA config
                    funcConfig = json.load(fncCfg)
                    # stores the loaded config
                    if os.path.exists(sboConfigPath):
                    # checks if the visual config file exists (both need to exist)
                        self.funcConfigCheckWin()
                        # moves to check if the config window should be skipped
                    else:
                    # visual config doesn't exist, must re-run base config
                        self.funcConfigRun()
                        # runs the configuration window runner
            except:
            # if the file can't be found/opened
                self.funcConfigRun()
                # runs the configuration window runner
        else:
        # file doesn't exist
            self.funcConfigRun()
            # runs the configuration window runner

    def funcConfigRun(self):
        """Function to run the functional configuration window if necessary"""

        self.hide()
        # hides the mainWindow (otherwise appears frozen)
        funcConfigProc = subprocess.run([funcConfigExePath], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # runs the functionality configurator (as blocking), continues task once it's done writing config
        if funcConfigProc.returncode == 0:
        # checks if there's a return code 0 (process ended gracefully)
            self.show()
            # re-shows itself
            self.labelSwap.emit("Configuration complete, proceeding...")
            # sends the return code
            QTimer.singleShot(1500, self.funcConfigManager)
            # moves to reading the config

    def funcConfigCheckWin(self):
        """Function to check if the window should be skipped"""
        global skipFuncCfgWin
        # global -> local

        skipFuncCfgWin = funcConfig.get("skipFuncCfgWin", False)
        # checks whether the function configuration window should be skipped

        if not skipFuncCfgWin:
        # if the window shouldn't be skipped
            self.funcConfigRun()
            # runs the subprocess spawn
        else:
        # should be skipped
            self.funcConfigRead()
            # moves to reading the config

    def funcConfigRead(self):
        """Function to read the functional configuration"""
        global webHostPortBot, webHostPortWS, enableBot, consoleLength, skipRequired
        # global -> local

        webHostPortBot = (int(funcConfig.get("httpPort", 6868)) + 1)
        # adds 1 to the default web host port to get the SBO-Bot port (webhost default: 6868), adds 1 (-> Bot default: 6869)
        webHostPortWS = (webHostPortBot + 1)
        # adds 1 to the SBO-Bot to get the SBO-WS port (default: 6870)
        consoleLength = int(funcConfig.get("consoleLength", 25))
        # gets the length of the console
        enableBot = funcConfig.get("enableBot", False)
        # gets the Twitch bot enabling boolean
        skipRequired = funcConfig.get("skipRequiredCheck", False)
        # gets the required item skip check

        if skipRequired and DSIoverride:
        # if the required items skip is enabled and DSI is detected
            QTimer.singleShot(1000, self.startupDone)
            # moves directly to startup done
        else:
        # if one of them is false
            QTimer.singleShot(1000, self.requiredSetup)
            # moves to checking required items



### Required Setup ###

    def requiredSetup(self):
        """Function that ensures all the required client information is passed"""
        global spotifyClientID, spotifyClientSecret, spotifyRedirect, secretConfig
        # global -> local

        self.show()
        # ensures window is visible
        self.labelSwap.emit("Loading required configuration...")
        # user update        

        if os.path.exists(secretConfigPath):
        # if the "secret" configuration file does exist
            try:
            # tries to read the config file (try because it could fail)
                with open(secretConfigPath, "r", encoding="utf-8") as scrtCfg:
                # opens the SHAA config
                    secretConfig = json.load(scrtCfg)
                    # stores the loaded config
                    self.requiredItemGrab()
                    # calls the next stage
            except:
            # if the file can't be found/opened
                self.requiredItemsFail()
                # calls the fail function to reconstruct
        else:
        # if the file doesn't exist
            self.requiredItemsFail()
            # calls the fail function to reconstruct

    def requiredItemGrab(self):
        """Function to grab and push the required items, when they're found"""
        global spotifyClientID, spotifyClientSecret, spotifyRedirect
        # global -> local

        self.labelSwap.emit("Reading required configuration...")
        # user update

        try:
        # tries to grab the IDs and such
            spotifyClientID = secretConfig["Spotify_Client_ID"]
            spotifyClientSecret = secretConfig["Spotify_Client_Secret"]
            spotifyRedirect = secretConfig["Spotify_Redirect_URI"]
            # updates all the global variables
            self.labelSwap.emit("Required configuration loaded...")
            # user update
            self.startupDone()
            # moves to next stage
        except:
        # if it fails (something's wrong with the file/input)
            self.requiredItemsFail()
            # calls the fail function to reconstruct

    def requiredItemsFail(self):
        """Function to handle missing required items (re-input)"""

        self.labelSwap.emit("Unable to read required config...")
        # user inform
        self.userInstructLabel.setText("Please enter your Spotify client information\nIf using with DSI, you can skip this step")
        # user instruct

        self.inputLabel1.setText("Enter your Spotify Client ID:")
        self.inputLabel2.setText("Enter your Spotify Client Secret:")
        self.inputLabel3.setText("Enter your Spotify Redirect URI:")
        # changes the labels

        self.continueButton.show()
        self.skipButton.show()
        # shows both the continue and skip buttons

        self.inputField1.show()
        self.inputField2.show()
        self.inputField3.show()
        # shows all 3 user input fields

        self.inputLabel1.show()
        self.inputLabel2.show()
        self.inputLabel3.show()
        # shows all the labels for input

    def requiredItemsStore(self, state: int):
        """Function to read the required items from input and store them"""
        global secretConfig, spotifyClientID, spotifyClientSecret, spotifyRedirect
        # global -> local

        success = True
        # internal boolean

        if state == 1:
        # if given state 1 (continue button)
            self.labelSwap.emit("Storing required items...")
            # user update

            spotifyClientID = self.inputField1.text().strip()
            secretConfig["Spotify_Client_ID"] = spotifyClientID
            # stores the client ID 

            spotifyClientSecret = self.inputField2.text().strip()
            secretConfig["Spotify_Client_Secret"] = spotifyClientSecret
            # stores the client secret

            spotifyRedirect = self.inputField3.text().strip()
            secretConfig["Spotify_Redirect_URI"] = spotifyRedirect
            # stores the redirect URL

            with open(secretConfigPath, "w", encoding="utf-8") as scrtCfg:
            # opens the secret config/makes new one
                json.dump(secretConfig, scrtCfg, indent=3)
                # saves the config to file

            self.labelSwap.emit("Required items stored successfully, proceeding...")
            # user update
        else:
        # not state 1 (skip)
            if not DSIoverride:
            # if the DSI override hasn't been detected yet (not up)
                self.userInstructLabel.setText("DSI webhost not detected, can't skip Spotify authentication with no DSI session!")
                # user warning
                success = False
                # sets the boolean
            else:
            # override is active and all good
                self.labelSwap.emit("Skipping Spotify requirements...")
                # user update

        self.userInstructLabel.setText("")
        # clears the user inform text
        self.inputLabel1.hide()
        self.inputLabel2.hide()
        self.inputLabel3.hide()
        # hides the labels
        self.inputField1.setText("")
        self.inputField2.setText("")
        self.inputField3.setText("")
        # clears the texts
        self.inputField1.hide()
        self.inputField2.hide()
        self.inputField3.hide()
        # hides the inputs
        self.continueButton.hide()
        self.skipButton.hide()
        # hides the buttons

        if success:
        # override is on
            QTimer.singleShot(1000, self.startupDone)
            # moves to next stage
        else:
        # override isn't on + user pressed skip
            QTimer.singleShot(1000, self.requiredItemsFail)
            # runs the required item fail function again



### Startup Done ###

    def startupDone(self):
        """Function to move on, once all configs are done"""
        self.mainWindow = MainWindow()
        # instantiates the main window
        self.mainWindow.show()
        # displays the main window
        self.close()
        # closes the startup window



### Main Window ###

class MainWindow(QMainWindow):
    """Class that hosts the whole program's main window"""

    labelSwap = pyqtSignal(str, int)
    # a pyQt signal to swap the label
    restartSignal = pyqtSignal(str)
    # a pyQt signal to restart a process

    def __init__(self):
        super().__init__()
        # init

    ### Init / Basic ###

        self.version = SBOver
        # stores the version in self
        self.mainIcon = iconPath
        # the program's main icon
        self.programName = f"Spotify Browser Overlay"
        # stores the program name

        self.windowSizeX = max(900, int(startApp.primaryScreen().size().width() / 2))
        self.windowSizeY = int(self.windowSizeX * (9 // 16))
        # base window sizes (uses the larger of the two, 900 or ~50% of the monitor's width/height and 16:9 aspect ratio)

    ### Basic Window Setup ###

        self.setWindowTitle(self.programName)
        # the window title
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setMinimumSize(QSize(self.windowSizeX, self.windowSizeY))
        # the window size minimums

    ### UI Element Base ###

        self.container = QWidget()
        # a container to hold elements
        self.mainLayout = QGridLayout()
        # new grid layout to put elements into
        self.mainLayout.setSpacing(25)
        # sets spacing of 25px between elements

        self.mainLayout.setRowMinimumHeight(0, 50)
        self.mainLayout.setRowMinimumHeight(1, 150)
        self.mainLayout.setRowMinimumHeight(2, 100)
        self.mainLayout.setRowMinimumHeight(3, 50)
        self.mainLayout.setRowMinimumHeight(4, 50)
        self.mainLayout.setRowMinimumHeight(5, 50)
        # sets the minimum height for rows

        self.mainLayout.setColumnMinimumWidth(0, 150)
        self.mainLayout.setColumnMinimumWidth(1, 200)
        self.mainLayout.setColumnMinimumWidth(2, 300)
        self.mainLayout.setColumnMinimumWidth(3, 200)
        self.mainLayout.setColumnMinimumWidth(4, 150)
        # sets the minimum width for columns

        self.mainLayout.setColumnStretch(0, 0)
        self.mainLayout.setColumnStretch(1, 1)
        self.mainLayout.setColumnStretch(2, 1)
        self.mainLayout.setColumnStretch(3, 1)
        self.mainLayout.setColumnStretch(4, 0)
        # allows columns 1, 2 and 3 (center) to stretch

        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setRowStretch(2, 1)
        # allows rows 1 (console) and 2 (center) to stretch

        self.container.setLayout(self.mainLayout)
        # sets the container to use layout

    ### Main Label ("Console") ###

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
        self.consoleScroll.setMinimumSize(400, 525)
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
        self.mainLabel.setText("SBO")
        # initial text
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        # centers the label to the bottom
        self.mainLabel.setWordWrap(True)
        # makes the text wrap if it's too wide
        self.mainLabel.setMinimumWidth(400)
        # sets a minimum size for the label
        self.consoleScroll.setWidget(self.mainLabel)
        # sets the "console" to use the mainLabel

    ### Exit Button ###

        self.bottomButtonLayout = QGridLayout()
        # a layout for the bottom middle buttons
        self.bottomButtonLayout.setColumnStretch(0, 1)
        self.bottomButtonLayout.setColumnStretch(1, 1)
        self.bottomButtonLayout.setColumnStretch(2, 1)
        self.bottomButtonLayout.setColumnStretch(3, 1)
        self.bottomButtonLayout.setColumnStretch(4, 1)
        # forces all columns to stretch
        self.mainLayout.addLayout(self.bottomButtonLayout, 5, 0, 1, 5, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout to the bottom middle of the main layout (spans all 5 columns)

        self.exitButton = QPushButton("Exit")
        # a button to exit the program
        self.exitButton.setToolTip("Close the program")
        # tooltip
        self.exitButton.setFixedSize(150, 50)
        # sets size
        self.exitButton.clicked.connect(self.close)
        # closes the program on click

        self.versionTag = QLabel(f"SBO v{self.version}\n ")
        # label for the semantic version
        self.versionTag.setToolTip("Current SBO version")
        # tooltip
        self.versionTag.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        # aligns the text itself to the left
        self.versionTag.setOpenExternalLinks(True)
        # allows opening links (in case of new update)

        self.directoryButton = QPushButton("...")
        # a button to open the directory
        self.directoryButton.setFixedSize(50, 50)
        # sets size
        self.directoryButton.setToolTip("Open the configuration location")
        # tooltip
        self.directoryButton.clicked.connect(lambda: os.startfile(configFolderPath))
        # connects the button to just opening the installation directory

        self.bottomButtonLayout.addWidget(self.versionTag, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomButtonLayout.addWidget(self.directoryButton, 0, 4, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomButtonLayout.addWidget(self.exitButton, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all the items

    ### Function Elements ###

        self.functionLayout = QGridLayout()
        # a layout that holds functional buttons
        self.functionLayout.setVerticalSpacing(25)
        # sets 25 x gaps between buttons
        self.mainLayout.addLayout(self.functionLayout, 3, 4, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout to the main in the mirrored spot bottom row, right column (spans 2 rows)

    ### Playback Control ###

        self.pausePlaybackCtrlButton = QPushButton("Pause\nPlayback Control")
        # a button to disable playback controls
        self.pausePlaybackCtrlButton.setFixedSize(150, 50)
        # sets fixed size
        self.pausePlaybackCtrlButton.setToolTip("Disable Twitch Bot's control over Spotify playback")
        # tooltip

        self.pausePlaybackCtrlButton.clicked.connect(lambda: self.controlChecks("Playback", False))
        # connects the button click to the pausing function
        self.pausePlaybackCtrlButton.hide()
        # hides the button on start

        self.resumePlaybackCtrlButton = QPushButton("Resume\nPlayback Control")
        # a button to re-enable bot controls
        self.resumePlaybackCtrlButton.setFixedSize(150, 50)
        # sets fixed size
        self.resumePlaybackCtrlButton.setToolTip("Enable Twitch Bot's control over Spotify playback")
        # tooltip

        self.resumePlaybackCtrlButton.clicked.connect(lambda: self.controlChecks("Playback", True))
        # connects the button to the resuming function
        self.resumePlaybackCtrlButton.hide()
        # hides the button on start

    ### Overlay Control ###

        self.pauseOverlayCtrlButton = QPushButton("Pause\nOverlay Control")
        # a button to disable overlay controls
        self.pauseOverlayCtrlButton.setFixedSize(150, 50)
        # sets fixed size
        self.pauseOverlayCtrlButton.setToolTip("Disable Twitch Bot's control over Spotify overlay")
        # tooltip

        self.pauseOverlayCtrlButton.clicked.connect(lambda: self.controlChecks("Overlay", False))
        # connects the button click to the pausing function
        self.pauseOverlayCtrlButton.hide()
        # hides the button on start

        self.resumeOverlayCtrlButton = QPushButton("Resume\nOverlay Control")
        # a button to re-enable bot controls
        self.resumeOverlayCtrlButton.setFixedSize(150, 50)
        # sets fixed size
        self.resumeOverlayCtrlButton.setToolTip("Enable Twitch Bot's control over Spotify overlay")
        # tooltip

        self.resumeOverlayCtrlButton.clicked.connect(lambda: self.controlChecks("Overlay", True))
        # connects the button to the resuming function
        self.resumeOverlayCtrlButton.hide()
        # hides the button on start

    ### Commands ###

        self.openFuncConfigButton = QPushButton("Configure")
        # a button to open the functional config (gateway to other configs)
        self.openFuncConfigButton.setFixedSize(150, 50)
        # sets fixed size
        self.openFuncConfigButton.setToolTip("Enter the config")
        # tooltip

        self.openFuncConfigButton.clicked.connect(self.openFuncConfigWin)
        # connects the button click to the detail display
        self.openFuncConfigButton.hide()
        # hides the button on start

        self.functionLayout.addWidget(self.pausePlaybackCtrlButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.functionLayout.addWidget(self.resumePlaybackCtrlButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.functionLayout.addWidget(self.pauseOverlayCtrlButton, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.functionLayout.addWidget(self.resumeOverlayCtrlButton, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.functionLayout.addWidget(self.openFuncConfigButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the buttons
    
    ### Intermediary ###

        self.setCentralWidget(self.container)
        # sets the container to fill the window
        self.labelSwap.connect(self.changeLabel)
        # connects the label swap signal to the change label function
        self.restartSignal.connect(self.restartProcess)
        # connects the process restart signal to the restarting function

    ### Line "Storage" ###

        self.lines = deque(maxlen = consoleLength)
        # creates a "deque" to hold lines (strings), to form a "pseudo-console"

    ### Run Arguments ###

        QTimer.singleShot(0, self.checkUpdate)
        # runs the GitHub update check
        QTimer.singleShot(500, lambda: mainStart(True, None))
        # runs the mainStart function once it's done loading
        QTimer.singleShot(1000, lambda: self.controlChecks("Startup", True, True))
        # runs the controlChecks function to enable all the buttons



### Update Checker ###

    def checkUpdate(self):
        """Function that checks if there's a new version of the program"""

        updateAvailable = 0
        # update check, defaults to 0
        # 0 = no update, 1 = update, 2 = program newer than github

        try:
        # tries to get tags
            gitTags = requests.get(
                gURL,
                headers={"User-Agent": "SBO"},
                timeout=5)
            # the request to get the github tags

            if gitTags.status_code == 200:
            # 200 is all good
                tags = gitTags.json()
                # grabs the json dictionary

                latestTagRaw = str(tags[0]["name"])
                # grabs the 0th element's name (latest)
                latestTag = latestTagRaw.replace("v", "").strip()
                # strips the v(ersion) identifier, cleans up
                latestList = latestTag.split(".")
                # splits the latest tag into a list of date elements (year num, month, day, hour/min)
                currentList= self.version.split(".")
                # splits the current tag into a list of date elements

                if latestList[0] == currentList[0]:
                # if the year elements are the same
                    if latestList[1] == currentList[1]:
                    # if the month elements are the same
                        if latestList[2] == currentList[2]:
                        # if the day elements are the same
                            if latestList[3] == currentList[3]:
                            # if the hour elements are the same
                                updateAvailable = 0
                                # sets to 0 (no update)
                            elif latestList[3] > currentList[3]:
                            # if the latest is newer than current
                                updateAvailable = 1
                                # sets the boolean to True
                            else:
                            # current is newer than latest
                                updateAvailable = 2
                                # sets the check to 2
                        elif latestList[0] > currentList[0]:
                        # if the latest is newer than current
                            updateAvailable = 1
                            # sets the boolean to True
                        else:
                        # current is newer than latest
                            updateAvailable = 2
                            # sets the check to 2
                    elif latestList[1] > currentList[1]:
                    # if the latest is newer than current
                        updateAvailable = 1
                        # sets the boolean to True
                    else:
                    # current is newer than latest
                        updateAvailable = 2
                        # sets the check to 2
                elif latestList[0] > currentList[0]:
                # if the latest is newer than current
                    updateAvailable = 1
                    # sets the boolean to True
                else:
                # current is newer than latest
                    updateAvailable = 2
                    # sets the check to 2

                if updateAvailable == 1:
                # if there's a newer version (higher number)
                    latestURL = "https://github.com/EllEff-Git/SBO/releases/latest"
                    # the URL to set
                    self.versionTag.setText(
                        f'SBO v{self.version}<br>'
                        f'Update available: '
                        f'<a href="{latestURL}">'
                        f'{latestTagRaw}'
                        f'</a>'
                    )
                    # updates text to include a prompt + link to the newest update
                elif updateAvailable == 2:
                # if the current is higher than the latest github release (test build)
                    self.versionTag.setText(f"SBO v{self.version}\nBleeding Edge!")
                    # you should never see this, this is a testing tag
                else:
                # if the version == latest
                    self.versionTag.setText(f"SBO v{self.version}\nLatest")
                    # updates text
            else:
            # status code is not 200 (error, something else)
                self.versionTag.setText(f"SBO v{self.version}\nUpdate check failed")
                # error prompt
        except:
        # didn't go through at all
            self.versionTag.setText(f"SBO v{self.version}\nUpdate check failed")
            # error prompt

### Label Changer ###

    def changeLabel(self, text: str, msgType: int):
        """Function to change the passed label"""

        time = (f"{datetime.datetime.now().strftime("%H:%M:%S")}\n")
        # stores the time string with a spacer

        if msgType == 0:
        # type 0 is "all ok"
            None
            # doesn't do anything to the message
        elif msgType == 1:
        # type 1 is "required"
            text = f"{time}{text}"
            # adds the timestamp (if enabled)
        elif msgType == 2 or msgType == 3:
        # type 2 is "error", 3 is "song-related"
            text = f"\n{time}{text}"
            # adds a new line before
        elif msgType == 4:
        # type 4 is critical error
            text = f"\n\nCRITICAL ERROR:\n{time}{text}\n\n"
            # adds a lot of space to ensure attention

        self.lines.append(text)
        # adds the line to the deque of lines
        fullString = ("\n".join(self.lines))
        # joins the lines together by newlines
        self.mainLabel.setText(f"{fullString}")
        # sets the text to match

        QTimer.singleShot(500, self.autoScroll)
        # runs the autoscroller after half a second to let the text sit

### Functional Configuration Window ###

    def openFuncConfigWin(self):
        """Function to open the functional config"""
        def funcThread():
            """Function to run the config and wait for it to close"""

            funcConfigProc = subprocess.Popen([funcConfigExePath], creationflags=subprocess.CREATE_NO_WINDOW)
            # runs the functionality configurator asynchronously
            funcConfigProc.wait()
            # waits for the process to end (blocking)
            self.controlChecks("Config", True, False)
            # sends a signal to the bot to reload the config file
        threading.Thread(target=funcThread, daemon=True).start()
        # starts a thread for the configuration window (so it doesn't block everything with .wait())

### Auto-Scroll ###

    def autoScroll(self):
        """Function to scroll the 'console' to the bottom"""

        scroller = self.consoleScroll.verticalScrollBar()
        # definition
        scroller.setValue(scroller.maximum())
        # uses the max value (pushes to bottom)

### Playback / Overlay Control ###

    def controlChecks(self, control:str, enable:bool, startup:bool=False):
        """Function to modify chat controls"""

        if startup:
        # if called on startup, to init the buttons
            self.openFuncConfigButton.show()
            self.pausePlaybackCtrlButton.show()
            self.pauseOverlayCtrlButton.show()
            # enables the pause buttons
            return
            # stops before either control is called

        if control == "Playback":
        # if it's regarding playback control
            if enable:
            # if it's to enable control
                packetSender("Bot", {"Playback Control": True})
                # sends a signal to the bot to enable playback control
                self.resumePlaybackCtrlButton.hide()
                # hides the resume control button
                self.pausePlaybackCtrlButton.show()
                # enables the pause control button
            else:
            # it's to disable control
                packetSender("Bot", {"Playback Control": False})
                # sends a signal to the bot to disable playback control
                self.pausePlaybackCtrlButton.hide()
                # hides the pause control button
                self.resumePlaybackCtrlButton.show()
                # enables the resume control button
        elif control == "Overlay":
        # regarding overlay control
            if enable:
            # if it's to enable control
                packetSender("Bot", {"Overlay Control": True})
                # sends a signal to the bot to enable overlay control
                self.resumeOverlayCtrlButton.hide()
                # hides the resume control button
                self.pauseOverlayCtrlButton.show()
                # enables the pause control button
            else:
            # it's to disable control
                packetSender("Bot", {"Overlay Control": False})
                # sends a signal to the bot to disable overlay control
                self.pauseOverlayCtrlButton.hide()
                # hides the pause control button
                self.resumeOverlayCtrlButton.show()
                # enables the resume control button
        elif control == "Config":
        # if it's regarding config reload
            packetSender("Bot", {"Config Reload": True})
            # sends a signal to the bot to reload the command config

### Close Event Handler ###

    def closeEvent(self, a0):
        """The pyqt close event handler function"""

        mainStart(False, "Bot", False)
        mainStart(False, "WS", False)
        # runs the mainStart function to shut down processes
        a0.accept()
        # accepts the close event

### Restart Process ###

    def restartProcess(process:str):
        """Function to restart an internal subprocess in case of unexpected termination"""
        QTimer.singleShot(10000, lambda: mainStart(True, process, True))
        # calls the mainStart after 10 seconds (gives a little time to allow the thread to close)



### Webhost Socket ###

def botWebHostDefiner():
    """Function that defines the webhost the Bot uses"""
    global webHost
    # global -> local

    webHost = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # creates the base webHost socket (defines)
    webHost.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # restarts sockets
    webHost.bind(("127.0.0.1", webHostPortBot))
    # sets the address and port
    webHost.listen()
    # creates a websocket listener connection on localhost



### Auth ###

sessionID = requests.Session()
"""Tells the auth to keep one stable connection, rather than re-connecting every request"""
authorisation = None
"""The argument for auth_manager, containing the variables from config + scope of data request"""
main = None
"""Handles the Spotify authentication and user identification"""

def spotifyAuth():
    """Function to form the spotify authorisation details"""
    global authorisation, main
    # global -> local
    
    try:
        authorisation = SpotifyOAuth(
            scope = ["user-read-playback-state", "user-modify-playback-state", "playlist-read-private"], 
            client_id = spotifyClientID, 
            client_secret = spotifyClientSecret, 
            redirect_uri = spotifyRedirect,
            cache_path = spotifyCachePath
            )
        
        main = spotipy.Spotify(auth_manager = authorisation, requests_session = sessionID)
        # reassigns both variables on call
    except:
        startWin.mainWindow.labelSwap.emit("[spAPI]: Could not initialise Spotify authorisation!\nIf you intend to use SBO's Twitch bot or do not have DSI installed, please ensure the required Spotify credentials are passed!", 2)
        # user warning



### Variables ###

currentURI = currentInfo = csPlaylistID = None
"""The current track information (URI is Spotify's idenfitier, Info contains the whole track package as a dict, csPlaylistID is the current track's playlist's ID)"""
pauseUpdated = False
"""Song state boolean checker to see if the pause has been registered"""
oldCount = trackCounter = 0
"""Variables for song counter"""
updateProgress = 0
"""A counter to check when/if progress was updated"""
callSong = False
"""A check to see if song() should be called regardless of song change state (due to a color change)"""
colorUpdate = False
"""A check to see if dsiDataGrabber should send a packet regardless of song change state (due to a color change)"""
lastSBO = {}
"""Dictionary to store previous track identifiers"""
lastSong = lastArtist = lastSongURL = None
"""Previous track's identifiers"""
lastSend = 0
"""Variable to store when the last data packet was sent to WebSocket"""
pauseState = False
"""Boolean to check what the pause state is (was)"""



### Spotify API Request ###

class SpotifyQueue:
    """A class that handles Spotify API calls, with call queueing"""

    def __init__(self, main, spotifyLock):
        self.main = main
        self.spotifyLock = spotifyLock
        # sets the variables in scope
        self.spotifyCallQueue = queue.Queue()
        # creates a queue to place API calls into
        self.spCallQueueTracker = set()
        # creates an empty set to clone the API calls to keep track of the length

    def queueManager(self, call: str, URI: str = None):
        """Function to manage the queue (URI can be empty if call is a playback request or control, future can be empty if no return is expected)"""

        futureObj = concurrent.futures.Future()
        # creates a new future object in case the function wanted a return on data
        nextCall = (call, URI, futureObj)
        # creates the next call from the arguments

        with self.spotifyLock:
        # uses a threading lock, to prevent multiple requests at once
            if nextCall not in self.spCallQueueTracker:
                # ensures the next call isn't already in queue (uses the set to check, since you can't check the queue directly)
                self.spotifyCallQueue.put(nextCall)
                # adds the call to the queue
                self.spCallQueueTracker.add(nextCall)
                # also adds the call into the set

        return futureObj
        # returns the future object so the function can wait for the result

    def spotifyAPIPrepper(self):
        """Function that prepares the calls for spotifyAPICall"""
        while True:
        # while the function is running, keeps running requests (only when it's ready, prevents multiple calls at once)

            nextAPICall = self.spotifyCallQueue.get(block = True)
            # grabs the next call from the queue (removes it at the same time), blocks progress until there's something in the queue
            self.spCallQueueTracker.remove(nextAPICall)
            # deletes the 0th element (first), since that's the same element the queue stores
            call, link, future = nextAPICall
            # splits the queue item into its call, link and future components

            self.controlList = ["Pause", "Resume", "Skip", "Previous"]
            # makes a list of the playback control options (these don't have special conditions and don't return anything)

            if call == "Playback":
            # if the call is to get new data
                success = self.spotifyAPICall(call)
                # calls spotifyAPICall with just a playback request

            elif call == "Playlist":
            # if the call is to get playlist information
                success = self.spotifyAPICall(call, link)
                # calls spotifyAPICall with a playlist command and a link
            
            elif call in self.controlList:
            # if the call is a part of the playback control list (no returns)
                success = self.spotifyAPICall(call)
                # simply passes the call to spotifyAPICall
            
            elif call == "Queue":
            # if the call is to add an item to queue
                success = self.spotifyAPICall(call, link)
                # calls the spotifyAPICall with a queue command and a link

            elif call == "QueueQ":
            # if the call is to search for a spotify track then add to queue
                success = self.spotifyAPICall("QueueQ", link)
                # calls the spotifyAPICall with a queueq command and a "link" (search terms)

            future.set_result(success)
            # sets the future object's return to be the success (if there's a return from the API call, it gets passed back)
            time.sleep(1)
            # waits a second before even starting next call

    def spotifyAPICall(self, call:str, query:str = None):
        """Function to perform Spotify API calls and handle errors gracefully"""

        tokenRefresh = False
        # a boolean to determine whether to print the token refresh or reconnect text (purely QoL)
        internalError = False
        # a boolean to determine if the error was Spotify's internal error (purely QoL)

        for attempt in range(3):
            # tries a max of 3 times to get Spotify data (typically succeeds 1st try, so if it doesn't work in 3, there's a bigger issue)    
            try:

            ### API Requests / Returns ###

                if call == "Playback":
                # if the request is for playback (most calls fall here via looper())
                    success = main.current_playback()
                    # gets the current playback
                elif call == "Playlist":
                # if the request is for playlist info
                    try:
                    # if the request is for a playlist's details
                        playlist = main.playlist(query)
                        # gets the playlist info via URI (takes ID, not link)
                        try:
                        # tries to *also* get the number of tracks
                            tracks = main.playlist_items(query, fields="total")
                            # saves the number of tracks in "tracks"
                            success = playlist, tracks
                            # turns the return into a tuple of the playlist and track information
                        except:
                        # if it can't (error for some reason or another)
                            success = playlist, {"total": 0}
                            # turns success into a tuple, so that the calling function knows there's no track information
                    except:
                    # if the playlist check fails (typically 403 forbidden)
                        success = "Not a playlist", 0
                        # saves a preset string to trip off playlistInfo's fail detection

            ### API Push / No Return ###

                elif call == "Queue":
                # if the call is to add a song to queue
                    try:
                        package = main.track(query)
                        # sends the URI to Spotify to get the track's details
                        if package:
                        # ensures the track information is received first
                            trackName = package.get("name")
                            # gets the name of the track first
                            trackArtistDict = package.get("artists")[0]
                            # gets the dictionary of the first artist
                            trackArtist = trackArtistDict.get("name")
                            # gets the artist name
                            main.add_to_queue(query)
                            # pushes the URI into the Spotify queue
                            success = f"Queued: {trackName} by {trackArtist}"
                            # creates a string from the track and artist
                            startWin.mainWindow.labelSwap.emit(f"[spAPI]: {success}", 2)
                            # prints a confirm message with the song name
                    except:
                        startWin.mainWindow.labelSwap.emit("[spAPI]: Queue failed", 2)
                        # prints a fail message
                        success = f"Unable to queue"
                        # sets a failed success state

                elif call == "QueueQ":
                # if the call is to add a song to queue based on a query
                    try:
                        package = main.search(query, limit=1, type="track")
                        # searches Spotify records for a song matching the passed argument ("URI" is a query formed prior)
                        if package:
                        # ensures the track information is received first
                            tracks = package.get("tracks")
                            # goes one level further
                            track = tracks.get("items")[0]
                            # gets the only track in this dictionary 
                            # (tracks has all the query data, items has all the matching tracks, we're just searching for 1 (limit))
                            trackName = track.get("name")
                            # gets the name of the track first
                            trackArtistDict = track.get("artists")[0]
                            # gets the dictionary of the first artist
                            trackArtist = trackArtistDict.get("name")
                            # gets the artist name
                            trackURI = track.get("uri")
                            # gets the resulting URI
                            main.add_to_queue(trackURI)
                            # pushes the track URI into the Spotify queue
                            success = f"Queued: {trackName} by {trackArtist}"
                            # creates a string from the track and artist
                            startWin.mainWindow.labelSwap.emit(f"[spAPI]: {success}", 2)
                            # prints a confirm message with the song name
                    except:
                        startWin.mainWindow.labelSwap.emit("[spAPI]: Queue failed", 2)
                        # prints a fail message
                        success = f"Unable to queue a matching song"
                        # sets a failed success state

            ### Controls / No Return ###

                elif call == "Pause":
                # if the call is to pause playback
                    playing = main.current_playback()
                    # grabs the current playback status
                    if playing and playing.get("is_playing", False):
                        # checks if the playback state is valid and if it's playing 
                        success = main.pause_playback()
                        # pauses the playback
                        startWin.mainWindow.labelSwap.emit("[spAPI]: Paused playback", 1)
                        # prints a confirm message
                    else:
                        startWin.mainWindow.labelSwap.emit("[spAPI]: Playback already paused", 1)
                        # prints a no-no message
                        success = None

                elif call == "Resume":
                # if the call is to resume playback
                    playing = main.current_playback()
                    # grabs the current playback status
                    if not playing or not playing.get("is_playing", False):
                        # checks if the playback state is valid and if it's paused (not playing)
                        success = main.start_playback()
                        # "starts" playback (continue)
                        startWin.mainWindow.labelSwap.emit("[spAPI]: Resumed playback", 1)
                        # prints a confirm message
                    else:
                        startWin.mainWindow.labelSwap.emit("[spAPI]: Already playing", 1)
                        # prints a no-no message
                        success = None

                elif call == "Skip":
                # if the call is to skip a track
                    playing = main.current_playback()
                    # grabs the current playback status
                    if playing and playing.get("item"):
                    # checks if the playback state is valid 
                        success = main.next_track()
                        # goes to next track (skips)
                        startWin.mainWindow.labelSwap.emit("[spAPI]: Skipped track", 1)
                        # prints a confirm message
                    else:
                    # playstate isn't valid
                        startWin.mainWindow.labelSwap.emit("[spAPI]: Can't skip", 1)
                        # prints a no-no message
                        success = None

                elif call == "Previous":
                # if the call is to go back to previous track
                    playing = main.current_playback()
                    # grabs the current playback status
                    if playing and playing.get("is_playing", False):
                        # checks if the playback state is valid and if it's playing 
                        success = main.previous_track()
                        # goes back to previous track
                        startWin.mainWindow.labelSwap.emit("[spAPI]: Went back to previous track", 1)
                        # prints a confirm message
                    else:
                        startWin.mainWindow.labelSwap.emit("[spAPI]: Couldn't go back", 1)
                        # prints a no-no message
                        success = None

            ### Unregistered Call ###

                else:
                # the command isn't one of the configured ones
                    startWin.mainWindow.labelSwap.emit(f"[spAPI]: Unregistered call: {call}", 2)
                    # if an unintended call sneaks through

            ### Connection Reacquisition ###

                if attempt != 0 and not tokenRefresh:
                # if it's not the first attempt, meaning the reconnect attempt print has already been pushed once after an error
                    startWin.mainWindow.labelSwap.emit("[spAPI]: Reconnect successful!", 1)
                    # prints user update
                elif tokenRefresh:
                # if the tokenRefresh variable is set to true, means a connectionError occurred at least once
                    startWin.mainWindow.labelSwap.emit("[spAPI]: Token refreshed successfully!", 1)
                    # prints user update

                return success
                # sends back the successfully found dictionary to the calling function (should only be looper)

        ### Failure ###

            except (SpotifyException, requests.exceptions.RequestException, ConnectionResetError) as error:
            # if it fails to acquire a Spotify playback package
                if isinstance(error, requests.exceptions.ConnectionError):
                # if the error is a connection error (token expired)
                    startWin.mainWindow.labelSwap.emit("[spAPI]: Refreshing Spotify token", 2)
                    # doesn't sleep because this is a token error and should get fixed nearly instantly
                    # expected to print just about every 3600 seconds (1h)
                    tokenRefresh = True
                    # sets the tokenRefresh mode to true so it prints the token text on success
                elif isinstance(error, requests.exceptions.ReadTimeout):
                # if the error is a read timeout (sort of random)
                    startWin.mainWindow.labelSwap.emit(f"[spAPI]: Spotify API timeout, retrying in 5 seconds ({attempt+1}/3)", 2)
                    time.sleep(2)
                    # sleeps for 2 seconds (because there's a function-wide 3-second cooldown added on top)
                elif isinstance(error, SpotifyException) and error.http_status == 403:
                # if the error is 403 (forbidden)
                    startWin.mainWindow.labelSwap.emit("[spAPI]: Spotify API call failed (Code 403), action not allowed", 2)
                    # prints an "error" message (403 is the result of the API not being able to do something, like pause a paused song)
                    break
                    # breaks here (doesn't let the attempts continue)
                elif isinstance(error, SpotifyException) and error.http_status == 500:
                # if the error is 500 (internal error fail)
                    startWin.mainWindow.labelSwap.emit(f"[spAPI]: Spotify internal error (Code 500). Attempting to reconnect ({attempt+1}/3)]", 2)
                    # prints an error message
                    internalError = True
                    # should never happen, but very very rarely does
                    time.sleep(2)
                    # adds 2 seconds of sleep (just to slow down, maybe catch a lucky reconnect)
                elif isinstance(error, SpotifyException) and error.http_status == 400:
                # if the error is 400 (bad syntax, likely a faulty link)
                    startWin.mainWindow.labelSwap.emit(f"[spAPI]: Faulty link or call syntax, can't process request", 2)
                    # prints "error" message
                    break
                    # stops the try loop (if it's faulty, no point in pushing again)
                else:
                # if the error is anything else
                    startWin.mainWindow.labelSwap.emit(f"[spAPI]: Spotify errored due to {error}. Attempting to reconnect ({attempt+1}/3)", 2)
                    # prints generic error message

            ### Too Many Errors ###

                if attempt == 2 and not internalError:
                # if it's the last attempt (range(3) = 0,1,2) and it fails
                    startWin.mainWindow.labelSwap.emit(f"All attempts to reconnect to Spotify API failed due to {error}", 4)
                    # prints user inform
                elif attempt == 2 and internalError:
                # if it's the last attempt and fails due to internal error
                    startWin.mainWindow.labelSwap.emit(f"All attempts to reconnect to Spotify API failed due to Spotify's internal error", 4)
                    # prints user inform

            time.sleep(3)
            # waits 3 seconds to give it some time between tries

        self.spotifyCallQueue.task_done()
        # tells the queue the task is complete

        return {}
        # on fail, returns an empty dictionary



### Web Host / Listener ###



def webHostListener():
    """Websocket message host/listener for SBO-Bot"""
    startWin.mainWindow.labelSwap.emit(f"[PTP-Bot]: Listening for SBO-Bot commands", 1)
    # prints the message on program start

    while True:
        # while the program is running
        try:
            client_socket, client_address = webHost.accept()
            # waits for a client connection, in a while loop so it can reconnect if it ever disconnects

            while True:
                # while this loop is active
                try:
                    rawMessage = client_socket.recv(1024)
                    # grabs any messages sent (1024 bytes max, shouldn't use more than a few)
                    if not rawMessage:
                        # if the message is empty (disconnect)
                        break
                        # breaks to reset the connection

                    message = rawMessage.decode("utf-8").strip()
                    # decodes it (bytes -> string) and strips empty space
                    startWin.mainWindow.labelSwap.emit(f"[PTP-Bot]: Command received: {message}", 1)
                    # prints a Python to Python (Peer to Peer) inform
                    botCommand(message, client_socket)
                    # calls botCommand with the decoded/stripped message, as well as the client socket (to pass back messages)

                except socket.error as soc:
                # general socket error
                    startWin.mainWindow.labelSwap.emit(f"[PTP-Bot]: Socket error with command: {soc}", 2)
                    # user inform
                    break

                except ConnectionAbortedError:
                # generic windows connection error
                    startWin.mainWindow.labelSwap.emit(f"[PTP-Bot]: Connection aborted by Windows (10053)", 2)
                    # user inform
                    break

        except socket.error as socF:
        # general socket error
            startWin.mainWindow.labelSwap.emit(f"[PTP-Bot]: Error forming connection: {socF}", 2)
            # user inform



### String Cleaner ###

def stringCleaner(string: str):
    """Function that cleans strings (removes invisible characters that will break .split without any reason)"""
    return re.sub(r"[\u0340-\u034f\u200b\u200c\u200d]+", "", string)
    # takes a string parameter, uses regular expression to replace invisible bs characters with nothing



### Bot Commands ###

def botCommand(command: str, socket: socket):
    """Helper function to pick what control function to call"""

    playbackCommands = {
        "Skip": skip,
        "Pause": pause,
        "Resume": resume,
        "Previous": previous
    }
    # list of playback controlling commands

    if command in playbackCommands:
    # if the command is one of the playback controls
        playbackCommands[command]()
        # constructs a call dynamically from the command and calls the function

    elif command == "Playlist":
    # if the command is for Playlist
        playlistID = csPlaylistID
        # saves the current song's playlist's ID as playlistID
        playlistInfo(playlistID, socket)
        # sends a command to the playlist info request function to add the ID into the Spotify call queue

    elif command.startswith("Queue:"):
    # if the command starts with "queue"
        x, uri = command.split(" ", 1)
        # splits the command into scrap (command) and the URI to pass
        queueTrack(uri, socket)
        # sends a command to the queue function to add the URI/URL/ID into the Spotify queue
    
    elif command.startswith("QueueQ:"):
    # if the command starts with "QueueQ"
        x, query = command.split(" ", 1)
        # splits the command into scrap (command) and the query to pass
        if "," in query:
        # if there's a comma in the query
            songQuery, artistQuery = query.split(",", 1)
            # splits the query into the song and artist parts by the comma
            formedQuery = f"track:{songQuery.strip()} artist:{artistQuery.strip()}"
            # forms the actual query from the given segments
        else:
        # if there's no comma
            formedQuery = f"track:{query.strip()}"
            # forms a smaller query
        queueqTrack(formedQuery, socket)
        # calls queueqTrack to send a search query with given terms

    elif command.startswith(("Song Color:", "Artist Color:", "Album Color:", "Bar Color:", "Overlay Color:")):
    # if the command starts with any of the overlay UI elements
        func, color = command.split(": ", 1)
        # splits the command into the function and the color to pass
        colorChanger(func, color.strip())       
        # calls the colorChanger with the parsed function and color as parameters
    
    elif command.startswith("Custom Color:"):
    # if the command starts with the custom color config
        func, arg = command.split(": ", 1)
        # splits the command into the function and the argument(s) to pass
        args = stringCleaner(arg)
        # cleans string because this has a lot of difficulty for some reason
        try:
            method, color = args.split(" ", 1)
            # splits the arguments by the first space
            if " " in color:
                # if color string has a space
                color, hexCode = color.split(" ", 1)
                # takes the hex code as the last parameter
            else:
                # if color doesn't have a space (remove/get)
                hexCode = None
                # sets hexCode to None
            colorManager(method, socket, color, hexCode)
            # calls colorWriter with the given arguments
        except Exception as err:
            # if the split fails
            errorMsg = f"Error parsing {command}, please check parameters and try again"
            # creates a string to send back to bot
            socket.sendall(errorMsg.encode("utf-8"))
            # sends the message to bot -> chat (bot is expecting a return, won't work until one is given)
    else:
    # not a recognized command
        startWin.mainWindow.labelSwap.emit(f"[PTP-Bot]: Unknown command: {command}", 2)
        # if the command is somehow not recognized (shouldn't ever happen, but this way won't break)


def skip():
    """Skips to next song"""
    spotifyQueueInstance.queueManager("Skip")
    # calls the queue manager to add a skip call to the call queue

def pause():
    """Pauses playback"""
    spotifyQueueInstance.queueManager("Pause")
    # calls the queue manager to add a pause call to the call queue

def resume():
    """Resumes playback"""
    spotifyQueueInstance.queueManager("Resume")
    # calls the queue manager to add a resume call to the call queue

def previous():
    """Goes back to previous song"""
    spotifyQueueInstance.queueManager("Previous")
    # calls the queue manager to add a previous call to the call queue

def queueTrack(link: str, client_socket):
    """Queues a given song via Spotify link"""
    futureQT = spotifyQueueInstance.queueManager("Queue", link)
    # calls the queue manager to add a link to the play queue
    trackName = futureQT.result()
    # gets the result via future object
    client_socket.sendall(trackName.encode("utf-8"))
    # sends the track name to Bot to reply with

def queueqTrack(query: str, client_socket):
    """Queues a song matching given query"""
    futureQT = spotifyQueueInstance.queueManager("QueueQ", query)
    # calls the queue manager to add a search query to potentially queue a song
    trackName = futureQT.result()
    # gets the result via future object
    client_socket.sendall(trackName.encode("utf-8"))
    # sends the track name to Bot to reply with

def playlistInfo(link: str, client_socket):
    """Requests playlist information via Spotify link"""
    if link != "Not a playlist":
    # if the current link is NOT set to not a playlist (SBO has detected it's not a playlist and thus set it to that string) 
        futurePL = spotifyQueueInstance.queueManager("Playlist", link)
        # calls the queue manager to add a playlist info request to the call queue
        playlistData, playlistTracks = futurePL.result()
        # gets the results via a future object (waits until it's ready) (returns a tuple of data, tracks)
        if playlistTracks:
        # if the track dictionary exists and is valid
            playlistTracks = playlistTracks.get("total")
            # gets the number only
        else:
            playlistTracks = "a number of"
            # creates a generic string instead
        if playlistData == "Not a playlist":
        # if the return is a preset string
            playlistNameStr = f"A private playlist"
            # sets a private playlist string
        elif playlistData:
        # if there's a return that contains data
            isPublic = playlistData.get("public", False)
            # checks if the playlist is public, defaults to False
            playlistName = playlistData.get("name", "Unknown Playlist")
            # grabs the playlist name from the dictionary (defaults to Unknown Playlist if can't find)
            if isPublic:
            # if the playlist is public
                try:
                # tries to grab the data
                    urls = playlistData.get("external_urls", {})
                    # gets the urls first, uses an empty dict if not found
                    owner = playlistData.get("owner", {})
                    # gets the owner info first, uses an empty dict if not found
                    playlistURL = urls.get("spotify", "Link unavailable")
                    # grabs the Spotify URL from the external urls
                    playlistOwner = owner.get("display_name", "Mystery Owner")
                    # grabs the owner's name from the owner sub-dictionary
                    playlistNameStr = f"'{playlistName}' by {playlistOwner} ({playlistTracks:,.0f} songs) {playlistURL}"
                    # constructs a full response from the given info
                except Exception as fail:
                # if it fails to get valid data from the dictionary (sometimes Spotify sends bricked dictionaries that don't include everything)
                    startWin.mainWindow.labelSwap.emit(f"[spAPI]: Failed to construct playlist information fully due to error {fail}", 2)
                    # console print of failure
                    playlistNameStr = f"A playlist named {playlistName}, further information unavailable"
                    # constructs a response from available data (name)
            else:
            # if the playlist is private
                playlistNameStr = f"A private playlist named {playlistName}"
                # constructs a response to not include a link or anything, just a name
        else:
        # if the return has no data
            playlistNameStr = f"Couldn't find specified playlist"
            # constructs a response to inform of an error
    else:
        playlistNameStr = f"Not currently listening to a playlist"
        # if the playlist link is set to a "not a playlist" string, it means the track is being listened to off-playlist
    client_socket.sendall(playlistNameStr.encode("utf-8"))
    # sends the response back to SBO-Bot to reply with in chat



### Color Mapping ###

def hexCheck(hexCode: str) -> bool:
    """Function that uses regular expression to check if a given hexCode code is valid"""
    if hexCode.startswith("#"):
        # if the hex code has a "#" applied
        hexCode = hexCode[1:]
        # reassigns the hexCode variable without the "#"
    if hexCode.lower() in customColors:
    # if the "hex code" is in the custom colors map (it's a stored color NAME not hex)
        return False
        # automatically returns False (it's not a hex code)
    return bool(re.match(r"^[A-Fa-f0-9]{6}$", hexCode))
    # checks if the given hexCode code fits regular expression (re) conditions for hex codes
    # ^ = start of string, {6} = all 6 characters fit, $ ends the check (if >6 characters present, automatic fail) 
    # (A-F = fits any uppercase character in hex range)
    # (a-f = fits any lowercase character in hex range)
    # (0-9 = fits any number in hex range)
    # if all conditions are met, it cannot be a faulty hex code



def colorLoader() -> dict:
    """Function to load the mapped custom colorStrings.json file"""

    if os.path.exists(colorStringPath):
    # if the colorStrings.json file exists
        try: 
        # attempts to load the colors
            with open(colorStringPath, "r") as colors:
            # opens the colorStrings.json file in read mode
                return json.load(colors)
                # returns the color map to the calling function

        except FileNotFoundError:
        # if it fails because the file doesn't exist
            startWin.mainWindow.labelSwap.emit(f"[COLOR]: Could not find colorStrings.json file, generating a new one...", 2)
            # user inform

            with open(colorStringPath, "w") as colors:
            # opens the colorStrings.json file in write mode
                json.dump(defaultColorDict, colors, indent=4)
                # writes a new file with the default dictionary

            return defaultColorDict
            # returns the default dictionary to caller

        except:
        # if it fails because it can't be read
            startWin.mainWindow.labelSwap.emit(f"[COLOR]: Failed to load colorStrings.json file, using default colors...", 2)
            # user inform (no save, because there may alrady be one)

            return defaultColorDict
            # returns the default dictionary to caller
    else:
    # doesn't exist
        startWin.mainWindow.labelSwap.emit(f"[COLOR]: Generating a new color file...", 2)
        # user inform

        with open(colorStringPath, "w") as colors:
        # opens the colorStrings.json file in write mode
            json.dump(defaultColorDict, colors, indent=4)
            # writes a new file with the default dictionary

        return defaultColorDict
        # returns the default dictionary to caller        



def colorManager(command:str, client_socket, color:str, hexCode:str = None):
    """Function to manipulate custom colors stored in colorStrings.json"""
    global customColors
    # global -> local

    command = command.lower()
    # saves the command as the lowercase version
    color = color.lower()
    # ensures the function only deals with lowercase colors

    try:
    # wraps everything in a try loop, so it doesn't delete the colors if it fails mid-way through
        if hexCode and hexCode.startswith("#"):
            # if the hex code isn't empty and has a "#" applied
            hexCode = hexCode[1:]
            # reassigns the hexCode variable without the "#"

        if command == "get":
        # if the command is to get the color
            if color in customColors:
            # if the color exists in the map
                gotColor = customColors.get(color)
                # stores the color in question
                colorStr = f"{color} is {gotColor}"
                # creates a string from the color and
            elif color == "all":
                # if the "color" is a request for "all"
                colorList = customColors.keys()
                # stores all the color names in a list
                colorStr = ", ".join(colorList)
                # turns the color list into a string separated by commas
                if len(colorStr) > 450:
                    # if the string is very long (Twitch has a limit of 500 characters, this ensures it won't surpass and fail)
                    colorStr = f"Response is too long for Twitch, sorry!"
                    # too long error message
                else:
                    colorStr = f"Stored colors: {colorStr}"
                    # forms a cohesive string
            else:
                # if the color isn't in the map
                colorStr = f"Could not find the color specified"
                # sets default string

        elif command == "set":
        # if the command is to set a color
            if hexCode and hexCheck(hexCode):
            # checks if a hex code was given and it's a valid hex code
                customColors[color] = hexCode
                # sets the given color to that string
                colorStr = f'Setting "{color}" to "{hexCode}"'
                # success string
            else:
                colorStr = f'No hex or invalid hex given: "{hexCode}"'
                # sets fail string

        elif command == "remove":
        # if the command is to remove a color
            if color in customColors:
            # checks if the color is in the map
                customColors.pop(color)
                # removes the color
                colorStr = f'Removing "{color}" from color map'
                # success string
            else:
                colorStr = f'"{color}" not found in color map'
                # sets an unfound string

        else:
        # if the command doesn't exist
            colorStr = f"{command} is not a valid command"
            # sets the string to error
            
        client_socket.sendall(colorStr.encode("utf-8"))
        # sends the color string back to bot

    except:
    # if it fails (happens occasionally with incorrect parameters, connection errors, etc)
        failStr = f"Failed to manipulate custom color, sorry!"
        # generic fail message
        client_socket.sendall(failStr.encode("utf-8"))
        # bot expects a response, sends generic one
        return
        # doesn't progress to writing the color file (if it did, it'd likely delete everything)

    try:
    # if the color get/set/remove works, tries to save the new file
        with open(colorStringPath, "w") as newColors:
            # opens the colorStrings.json file in write mode
            json.dump(customColors, newColors, indent=4)
            # dumps the new color map into the json file
            startWin.mainWindow.labelSwap.emit(f"[COLOR]: Color map saved successfully!", 2)
            # user inform on success
    except Exception as cErr:
    # if the file save fails
        startWin.mainWindow.labelSwap.emit(f"[COLOR]: Color map saving failed due to {cErr}", 2)
        # prints debug message



### Color Changing ###

def colorChanger(func: str, color: str):
    """Color function to handle the chat -> WS color sending"""
    global overlayColorHex, songColorHex, artistColorHex, albumColorHex, barColorHex
    # global -> local

    funcName = func.split(" ")[0]
    # gets the first part of the function (eg. "Artist" vs "Artist Color")
    hexCode = None
    # starts the variable as None
    color = color.lower().strip()
    # ensures there's no case-sensitive or invisible character stuff going on


    if color == "clear":
    # if the command is to clear, not to set a color
        readyColorString = f"{colorFunctionMap[func]}: clear"
        # forms a string from the passed function and clear

    elif not " " in color and not color.startswith("#"):
    # if there's only one color (no spaces), and there's no hex identifier
        if hexCheck(color):
        # if the color passes hexcheck (not in the map, fits hex criteria)
            hexCode = f"#{color}"
            # uses that as the hexcode
        elif color in customColors:
        # if the color is in the map of custom colors
            hexCode = f"#{customColors[color]}"
            # uses that instead
        readyColorString = f"{colorFunctionMap[func]}: {hexCode}"
        # forms a string from the passed function and color

    elif not " " in color and color.startswith("#"):
    # single color, starts with a hex
        hexCode = color
        # changes variable name
        readyColorString = f"{colorFunctionMap[func]}: {hexCode}"
        # forms a string from the passed function and color

    else:
    # if the command isn't clear and there is a space (or multiple)
        colors = color.split(" ")
        # splits the colors by spaces
        readyColors = []
        # creates an empty list of colors that are ready to go

        for each in colors:
        # goes through each color
            if hexCheck(each):
            # if they pass the hex check (not a registered color name, matches hex format)
                if each.startswith("#"):
                # if the code already starts with a #
                    hexCode = each
                    # doesn't need to do anything, it's already a hex code with a #
                else:
                # if the code doesn't start with a #   
                    hexCode = f"#{each}"
                    # adds the # to the start
            else:
            # if they don't pass the hex check (color name)
                if each in customColors:
                # if the color is in the map
                    hexStr = customColors[each]
                    # grabs the hex code ID from the map
                    hexCode = f"#{hexStr}"
                    # adds the # in front (map doesn't store them)
                else:
                # color not in the map
                    randomColor = random.choice(list(customColors.keys()))
                    # selects a random color key from the map
                    hexCode = f"#{customColors[randomColor]}"
                    # grabs the random color from the map and uses it
                    startWin.mainWindow.labelSwap.emit(f"[COLOR]: No {each} in the colormap/not a valid hex code; using a random color ({randomColor})", 0)
                    # prints fail message

            hexCode = stringCleaner(hexCode)
            # cleans the string (sometimes they have random empty space from Twitch, could be a "can't repeat message" bypass?)
            readyColors.append(hexCode)
            # adds the ready hex code to the list
        readyColorStringColors = ", ".join(readyColors)
        # creates a string by joining all the hex codes together
        readyColorString = f"{colorFunctionMap[func]}: {readyColorStringColors}"
        # adds the websocket color identifier

    if hexCode is not None:
    # if a hex code has been defined
        colorFunctionHexMap[funcName] = hexCode
        # sets the global hex variable of the matching function to match the new hex code

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as webClient:
    # starts a new connection (with the same parameters)
        webClient.connect(("127.0.0.1", webHostPortWS))
        # connects to the existing host
        webClient.sendall(readyColorString.encode("utf-8"))
        # sends the message
        webClient.close()
        # stops the connection when it's done



### SBO WebSocket ###

def runSBOws() -> subprocess.Popen:
    """Function to start the SBO-WS.exe"""
    global sboWS
    # global -> local

    sboWS = subprocess.Popen([sbowsPath], cwd=sbowsDir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    # opens the SBO-WS.exe file and reads its output

    for line in sboWS.stdout:
    # every time a new line is sent
        startWin.mainWindow.labelSwap.emit(f"[WS]: {line.rstrip()}", 3)
        # prints the line (clears right side)



### SBO Twitch Bot ###

def runSBOBot() -> subprocess.Popen:
    """Function to start the SBO Twitch Bot"""
    global sboBot
    # global -> local

    sboBot = subprocess.Popen([sboBotPath], cwd=sboBotDir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    # opens the SBO-Bot.exe file and reads its output 

    for line in sboBot.stdout:
    # every time a new line is sent
        startWin.mainWindow.labelSwap.emit(f"[SBOT]: {line.rstrip()}", 1)
        # prints the line (clears right side)



### SBO WS/Bot Packets ###

def packetSender(process:str, packet:dict):
    """Function to send packets (dictionaries of data) to the SBO-WS or SBO-Bot services"""

    finalPacket = (json.dumps(packet, ensure_ascii=False) + "\n")
    # forms the final packet as a json string with a new line

    if process == "WS" and sboWS:
    # if the requested process is the WebSocket (and it's defined)
        try:
            sboWS.stdin.write(finalPacket)
            sboWS.stdin.flush()
            # flushes (sends all pending packets)
        except Exception as wErr:
        # catches exception
            startWin.mainWindow.labelSwap.emit(f"Could not send packet to WS due to {wErr}", 3)
            # user inform on error

    elif process == "Bot" and sboBot:
    # if the requested process is the Bot (and it's defined)
        try:
            sboBot.stdin.write(finalPacket)
            sboBot.stdin.flush()
            # flushes (sends all pending packets)
        except Exception as bErr:
        # catches exception
            startWin.mainWindow.labelSwap.emit(f"Could not send packet to SBOT due to {bErr}", 3)
            # user inform on error



### DSI Data Grabber ###

def dsiDataGrabber():
    """Function to keep getting data from DSI rather than via song()"""
    global lastSBO, lastSong, lastArtist, lastSongURL, trackCounter, colorUpdate, lastSend, pauseState, csPlaylistID
    # global -> local

    hasWarned = 0
    # internal check for "has the program warned about a disconnect yet"

    while True:
    # keeps running
        try:
        # tries to make a request
            dsiData = requests.get(pURL, timeout=2)
            # sends a network request

            if dsiData.status_code == 200:
            # if the response is status code 200 (all good)
                data = dict(dsiData.json())
                # decodes from json to py dict
                trackID = data.get("Track ID", None)
                # grabs the track identifier from the data packet
                playbackState = data.get("Playback State", True)
                # grabs the playback state (defaults to True)

                pauseNow = data.get("Pause", False)
                # grabs the pause state right now

                now = round(time.time(), 0)
                # saves the current time

                if not playbackState:
                # if playback state is false
                    packetSender("WS", data)
                    # sends to the websocket
                    if enableBot:
                    # if the bot is enabled
                        packetSender("Bot", data)
                        # sends to the bot, too

                elif (trackID and (trackID != trackCounter)) or (pauseNow != pauseState) or colorUpdate or (lastSend + 10 < now):
                # if it found a track ID and it's not the same as the last one / the pause state now isn't the same as stored / there's a color change that needs to be updated / it's been 10s
                    if trackID != trackCounter:
                    # if it's specifically because the track changed
                        lastSong = lastSBO.get("Song Name")
                        lastArtist = lastSBO.get("Artist Name")
                        lastSongURL = lastSBO.get("Spotify URL")
                        # grabs all variables from the last packet
                        lastSBO = data
                        # swaps the dictionary to use the new data for next check

                    playlistURL = data.get("Playlist URL")
                    # gets the playlist ID from the data packet
                    if playlistURL is not None:
                    # if there's an URL
                        csPlaylistID = playlistURL.split("/playlist/")[1]
                        # splits the string by the /playlist/ segment, updates the global variable, which can then perform playlist info checks via commands
                        # eg. https://open.spotify.com/playlist/5XdXbGXO1XG6XAXFcXzfX8 -> 5XdXbGXO1XG6XAXFcXzfX8 (this is a 'redacted' link to one of my playlists :)

                    trackCounter = trackID
                    # sets the new track counter to match
                    pauseState = pauseNow
                    # sets the new pause state to match

                    data["Pause State"] = pauseNow
                    # adds a cloned pause entry
                    colorUpdate = False
                    # sets the boolean to false to reset it (if it's how this was triggered)

                    data["Last Song"] = lastSong
                    data["Last Artist"] = lastArtist
                    data["Last URI"] = lastSongURL
                    # adds entries

                    data["Song Color"] = songColorHex
                    data["Artist Color"] = artistColorHex
                    data["Album Color"] = albumColorHex
                    data["Bar Color"] = barColorHex
                    data["Overlay Color"] = overlayColorHex
                    # adds all the color data

                    data["Progress Mismatch"] = 0
                    data["Timestamp"] = now
                    # adds entries for status keeping

                    lastSend = now
                    # reassigns the lastSend time too

                    packetSender("WS", data)
                    # sends the data to the websocket program

                    if enableBot:
                    # if the bot is enabled
                        packetSender("Bot", data)
                        # sends to the bot as well
                    
                hasWarned = 0
                # resets the boolean to allow new warnings
            else:
            # response isn't 200 (everything not good, but is live?)
                None
                # doesn't do anything this loop
            time.sleep(1)
            # waits a second between checks

        except Exception as err:
        # can't connect
            if hasWarned == 0 or (hasWarned % 10 == 1):
            # if there hasn't been a warning yet (or every 10 warnings)
                startWin.mainWindow.labelSwap.emit(f"Cannot connect to DSI! Ensure connection ({err})", 2)
                # user warning
            hasWarned += 1
            # adds counter to warning
            time.sleep(5)
            # waits 5 seconds before trying again



### Song Data File Field Selection/Creation ###

def song():
    """The function that handles all song data gathering and parsing, as well as pushing to the websocket via text"""
    global currentInfo, trackCounter, oldCount, songColorHex, artistColorHex, albumColorHex, barColorHex, overlayColorHex
    global lastSBO, lastSong, lastArtist, lastSongURL, updateProgress, csPlaylistID
    # pulls "some" global variables to local

    while True:
    # keeps looping
        songEvent.wait()
        # waits for looper() to set an event
        songNameList = []
        # creates an empty list for strings to get added into as the loop progresses 
        csArtistString = []
        # creates an empty list for artists to get added into as the loop progresses
        songChanged = False
        # a function-contained boolean to check if the song changed later on (used to change the previous song/artist/url)

        csFull = currentInfo
        # gets a huge dictionary containing all the information about current song
        # "cs" in the variables just stands for CurrentSong, which, while descriptive, made the later variables insanely long

        if not csFull or not csFull.get("item"):
            # checks if the dictionary is valid and can be called
            sboFull = {
                "Playback State": False
            }
            # sets the dictionary to just playback state false
        else:
        # dictionary exists and can be called
            csItem = csFull.get("item")
            # takes the first part of the song's info (leaving out device info and various user states)
            csAlbum = csItem.get("album")
            # takes a smaller part of the song's info (still contains a ton of extra)
            csName = csItem.get("name")
            # stores the name of the song

            isLocalSong = csItem.get("is_local")
            # checks if the song is a local song (can't use standard API info requests if so)

            if not isLocalSong:
                # these fields are only valid when it's not a local song

                csImages = csAlbum.get("images")
                # gets the information about the album's images
                csCover = csImages[0].get("url")
                # gets the album cover url (used to pass to Discord if pictureCycle = Spotify)
                csArtists = csItem.get("artists")
                # stores all the artists listed on the song

                csArtistList = []
                # creates an empty list of artists
                for musician in csArtists:
                    # for every artist in the list of artists (from Spotify)
                    artist = musician.get("name")
                    # gets the name of the artist from a dictionary
                    csArtistList.append(artist)
                    # appends it to the list of artists 

                if len(csArtistList) > 1:
                    # if there's more than 1 artist
                    csArtistFirstHalf = csArtistList[0:-1]
                    # grabs all the artists except the last one
                    csArtistLast = csArtistList[-1]
                    # grabs the last artist

                    if len(csArtistFirstHalf) > 1:
                        # checks if there's more than 1 artist in the first half
                        csArtistString = ", ".join(csArtistFirstHalf)
                        # joins together with commas
                    else:
                        # if there's not more than 1 artist in the first half
                        csArtistString = "".join(csArtistFirstHalf)
                        # just joins with nothing (turns into a string basically)

                    csArtistString = (csArtistString + " and ")
                    # adds the "and" in between the first half and the last artist
                    csArtistString = (csArtistString + csArtistLast)
                    # adds the last artist to the string
                    csArtistName = csArtistString
                    # constructs a string from the artist names
                else:
                    # if there's not more (just 1)
                    csArtistName = csArtistList[0]
                    # gets the name of the only artist
                try:
                    csArtistURL = csArtists[0].get("name")
                    # gets the name of the 0th artist
                except:
                    csArtistURL = "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"
                    # uses taylor swift as fallback
                
                csAlbumName = csAlbum.get("name")
                # stores the album name

            csLength = int(csItem.get("duration_ms")/1000)
            # stores the length of the song in seconds
            csProgress = int(csFull.get("progress_ms")/1000)
            # saves the current song progress in seconds

            csUnixStart = int(time.time() - csProgress + 1)
            # stores the start time of the song by taking current time and subtracting progress
            csUnixEnd = (csUnixStart + csLength)
            # stores the end time of the song (by adding up the start + duration)

            csPlayState = bool(csFull.get("is_playing"))
            # grabs the playback state (true/false)
            paused = not(csPlayState)
            # stores the opposite of playstate (if playing, paused = false, if not, paused = true)

            if not csPlayState:
                # if the song is paused
                songNameList.append("Paused on:")
                # adds the "paused on" text to list

            elif trackCounter != oldCount and csPlayState:
                # checks if the song has changed (and song is playing, this way won't activate on paused songs and cause flashing elements)

                oldCount = trackCounter
                # updates the song counter
                songChanged = True
                # changes the songChanged boolean to true, tells the loop to update the song names

            csPlaylist = csFull.get("context")
            # stores the list that contains the playlist/artist/album url (this is "None", if playback isn't on playlist)

            if not isLocalSong and csItem:
                # can't access these if the playing song is local or csItem is None
                cstrackURL = csItem.get("external_urls")
                # stores the list that contains track's url
                csURL = cstrackURL.get("spotify")
                # grabs the spotify track URL
                try: 
                # tries to get the context type (if there isn't any, it would crash)
                    csContextType = csPlaylist.get("type")
                    # gets the context's type (this can be "playlist", "artist", "album" or "show")
                    if csContextType == "playlist":
                    # if the "context's" type is playlist
                        csPlaylistID = csPlaylist.get("uri").split(":")[-1]
                        # grabs the playlist ID by getting the playlist's URI (spotify:playlist:base62) and only taking the ID (base62)
                    else:
                    # if the context doesn't match
                        csPlaylistID = "Not a playlist"
                        # stores a preset string 
                except:
                # if there's no playlist
                    csPlaylistID = "Not a playlist"
                    # stores a preset string
                csAlbumURLs = csAlbum.get("external_urls")
                # stores the album urls 
                sboAlbumURL = csAlbumURLs.get("spotify")
                # gets the spotify url 

            else:
            # if the song is local
                csArtistName = "A local artist"
                csAlbumName = "A local album"
                csURL = "A local song"
                sboAlbumURL = "A local album"
                # sets all the variables to local

            if csPlaylist != None and csPlaylist != "None":
            # checks if user is playing a playlist
                csPlaylistURL = csPlaylist.get("external_urls")
                # gets *all* the URLs for the playlist
                csPlaylistURL = csPlaylistURL.get("spotify")
                # gets only the playlist URL (only one in there, unsure why it's a dictionary but ok Spotify)
            
            else:
                # if there's no playlist
                csPlaylistURL = "No playlist"
                csPlaylist = "Not listening to a playlist"

            songNameList.append(csName)
            # adds the song name to list
            sboSongName = " ".join(songNameList)
            # joins together the list (just paused state + song name)

            sboArtistName = csArtistName
            # assigns the artist name
            sboAlbumName = csAlbumName
            # assigns the album name
            sboURL = csURL
            # assigns the URL (this is the Spotify track URL)

            now = int(time.time())
            # saves the current time (SBO-WS can read this and see if it should do anything)

            sboFull = {
                        "Playback State": True,
                        "Song Name": sboSongName,
                        "Artist Name": sboArtistName,
                        "Artist URL": (csArtistURL if not isLocalSong else "A local artist"),
                        "Album Name": sboAlbumName,
                        "Album URL": (sboAlbumURL if not isLocalSong else "A local album"),
                        "Spotify URL": (sboURL if not isLocalSong else "A local song"),
                        "Spotify Image": (csCover if not isLocalSong else "https://i.imgur.com/FeUsGIz.png"),
                        "Playlist URL": csPlaylistURL,
                        "UNIX Start": str(csUnixStart),
                        "UNIX End": str(csUnixEnd),
                        "Pause State": paused,
                        "Track ID": str(trackCounter),
                        "Song Color": songColorHex,
                        "Artist Color": artistColorHex,
                        "Album Color": albumColorHex,
                        "Bar Color": barColorHex,
                        "Overlay Color": overlayColorHex,
                        "Last Song": lastSong,
                        "Last Artist": lastArtist,
                        "Last Playlist URL": lastSongURL,
                        "Progress Mismatch": updateProgress,
                        "Timestamp": now,
                        "State": " "
            }
            # merges all the song/color/other information together
        
        packetSender("WS", sboFull)
        # sends the packet to the websocket

        if enableBot:
        # if the Bot is on
            packetSender("Bot", sboFull)
            # sends the packet to the Bot, too

        if songChanged:
            # if the song has changed (changes after the packet update)
            lastSong = sboSongName
            # sets the previous song to match
            lastArtist = sboArtistName
            # sets the previous artist to match
            lastSongURL = csPlaylistURL
            # sets the previous playlist URL match
            songChanged = False
            # shouldn't matter, since songChanged is self-contained and should default to false every loop, but just in case, sets to False

        songEvent.clear()
        # clears the event queue, ready to get new requests



### Information Checking Loop ###

def looper():
    """Function that checks song info on a loop"""
    global currentURI, currentInfo, pauseUpdated, trackCounter, callSong, updateProgress, lastSend
    # grabs the "global" variables (outside the function) as local variables
    newSong = True
    # sets the new song boolean once
    while True:
    # this loop checks if the song playing is the same as the previous update, waits if yes, updates the song to match if not

        loopFuture = spotifyQueueInstance.queueManager("Playback", None)
        # sends a call to the Spotify API call queue manager to get a new playback dictionary

        info = loopFuture.result()
        # picks up all the info the Spotify API function sends (dictionary)

        if not info or not info.get("item"):
        # checks if the info has something and if it can be called
            startWin.mainWindow.labelSwap.emit(f"[WARN]: No playing state detected, re-checking in 5 seconds", 2)
            # user inform
            time.sleep(5)
            # waits for a few seconds
            continue
            # goes back to loop start
        
        currentInfo = info
        # sets the global variable to match

        songURI = (info.get("item")).get("uri")
        # grabs the URI of the song, stores it
        songName = (info.get("item").get("name"))
        # stores name for display purposes
        songProg = int((info.get("progress_ms")) / 1000)
        # grabs the progress of the song at the pull time (ms/1000 = seconds)
        timeNow = int(time.time())
        # grabs the current time
        playing = bool(info.get("is_playing"))
        # checks the pause state (True if playing, False if not)
        lastActionTS = int(info.get("timestamp"))
        # stores the timestamp that the last action happened (play, pause, skip, scrub, new song)

        if newSong or currentURI is None:
        # if the song has changed or none is set
            songStart = int(timeNow - songProg)
            # stores the start time of the song by taking current time and subtracting progress
            newSong = False
            # sets the boolean to false, since it's been processed now

        if currentURI is None:
        # when the program first starts, the currentURI will be "None", this updates it, along with other variables
            currentURI = songURI
            # sets the current song to match 
            expectProg = (songProg + 2)
            # calculates the expected progress by taking the current progress and adding 2 seconds (1 cycle time)
            progressMismatch = False
            # initialises the progress boolean as false
            trackCounter += 1
            # adds 1 to counter
            songEvent.set()
            # since this only runs when the program first starts, sets an event immediately to song, to refresh data
            startWin.mainWindow.labelSwap.emit(f"[SONG]: First song: {songName}, has been successfully processed", 1)
            # user inform on first song

        songDur = int((info.get("item")).get("duration_ms")/1000)
        # grabs the length of the song (in seconds)
        songLeft = (songDur - songProg)
        # calculates the time left on the song
        progressOffset = abs(songProg - expectProg)
        # checks if the difference between the Spotify given progress and the calculated progress

        if ((songStart + songDur + 2) > timeNow) and ((timeNow - lastActionTS) >= songDur) and (songProg < 3):
        # if the song "should've" ended (start + duration + slight addition > now) and the song hasn't been touched in any way during its playback
            newSong = True
            # sets the newSong boolean to True, because the song very likely did

        if (currentURI != songURI):
        # if the URIs don't match
            newSong = True
            # sets the newSong boolean to True

        if (progressOffset >= 6 and playing):
        # checks if there's a mismatch between expected and real progress of >= 6 seconds 
            # leaves a delta of 3-4 seconds, any change larger than that is scrubbing, or at the very least worth updating the overlay
            progressMismatch = True
            # if there is, sets the flag to True (will cause an update)
            expectProg = (songProg + 5)
            # calculates the expected progress by taking the current progress and adding 5 seconds (1 cycle time)
        else:
        # if the mismatch isn't big enough and the song is playing
            expectProg = (songProg + 5)
            # calculates the expected progress by taking the current progress and adding 5 seconds (1 cycle time)

        if newSong or (pauseUpdated and playing) or progressMismatch:
        # if there's a reason to update the text file;
            # a song change (the URI has changed, must mean a new song)
            # it mathematically has to be a new song (or something is very broken)
            # if there was a pause, but is now playing (-> removes the "paused on" text)
            # if a progress mismatch has been triggered (-> sets the correct times on overlay)

            if newSong:
            # if the song URI is new, or the starting timestamps are very off
                startWin.mainWindow.labelSwap.emit(f"[SONG]: New song: {songName}, duration: {songDur:,.0f} seconds", 2)
                # user update on new song (makes a new line before itself so it separates tracks)
                trackCounter += 1
                # adds 1 to counter (means track has changed)
                currentURI = songURI
                # changes the internal variable to match new song

            if progressMismatch and playing:
            # checks if there was a progress mismatch (has to be playing)
                progressMismatch = False
                # sets the mismatch flag to false
                updateProgress += 1
                # adds 1 to the updateProgress counter (tracks the progress updates for overlay)

            songEvent.set()
            # sets an event to make song() update the text file
            callSong = False
            # if a new song is set, it'll run the song() normally, no need to separately run

            if pauseUpdated and playing:
            # if it's playing and the pauseUpdate has been set to true
                startWin.mainWindow.labelSwap.emit(f"[SONG]: Unpaused: {songName}", 2)
                # prints the update message
                pauseUpdated = False
                # sets the pauseUpdated to false, so it doesn't run twice

            time.sleep(2.5)
            # waits a second
            continue
            # sends back to the start of looper to check for a new song (2.5 second checks after a song change to check for a song skip)

        if not playing and not pauseUpdated and currentURI == songURI:
        # if the song is paused, hasn't yet updated the pause state *and* the song is the same
            songEvent.set()
            # sets an event to make song() update the text file
            callSong = False
            # if song() gets called anyway, no need to separately run
            pauseUpdated = True
            # sets the pause check to True, meaning it has been checked and acted on
            startWin.mainWindow.labelSwap.emit(f"[SONG]: Paused on: {songName}", 2)
            # user inform (new line to split from main updates, only prints once anyway)
            sleepfor = 5
            # waits a couple seconds

        if callSong:
        # if there's a callSong request from colorChanger, and both checks passed (no new song, no pause state)
            songEvent.set()
            # sets an event to make song() update the file
            callSong = False
            # turns off so it doesn't call again

        else:
        # if the current song is the same, and is not paused
            if songLeft > 5:
            # checks if there's more than 5s left
                sleepfor = 5
                # sets the sleep timer to 5s
            else:
            # if there's less song time left than 5s
                sleepfor = songLeft + 1
                # sleeps for the rest of the song (+1s to ensure the song has ended)

        if (timeNow - lastSend) > 10:
        # if it's been over 10 seconds since last update
            lastSend = timeNow
            # sets the variable to match
            songEvent.set()
            # sets an event to force an update

        time.sleep(sleepfor)
        # sleeps for the determined time



### Startup Commands ###

spotifyQueueInstance = SpotifyQueue(main, spotifyLock)
# creates the Spotify queue instance
spotifyQueueRunner = threading.Thread(target = spotifyQueueInstance.spotifyAPIPrepper, name="Spotify API Process", daemon=True)
# creates the Spotify queue thread for APIPrepper

sbowsThread = threading.Thread(target = runSBOws, name="SBO-WebSocket Process", daemon=True)
# creates a thread for the SBO-WS program to run in - this way it won't stop the main process

songThread = None
"""Thread for the song function to sit in"""
loopThread = None
"""Thread for the looper (song data grabber) to sit in"""
ptpThread = None
"""Thread for the Peer-To-Peer connection manager to sit in"""
botThread = None
"""Thread for the SBO-Bot to sit in"""
dsiThread = None
"""Thread for the DSI data grab to sit in"""

def mainStart(startup:bool = True, process:str = None, restart:bool = False):
    """Function that starts the internal processes when called"""
    global customColors, sboWS, sboBot
    global songThread, ptpThread, botThread, dsiThread, sbowsThread, loopThread
    # global -> local

    if startup:
    # a startup call

        customColors = colorLoader()
        # calls the color loader function, which loads the custom colors into a global variable

        if not DSIoverride or enableBot:
        # if DSI isn't active and there's no intent to use the bot 
        # (if intending to use bot, this needs to be setup for chat commands)
            spotifyAuth()
            # runs the auth function to form the required Spotify access requirements

        spotifyQueueRunner.start()
        # starts the spotifyQueue thread

        if not DSIoverride:
        # if DSI isn't active and not managing song data
            songThread = threading.Thread(target = song, name="Spotify Data Constructor", daemon=True)
            # creates the song thread
            songThread.start()
            # starts the song thread to get updated info

        sbowsThread.start()
        # starts the SBO-WS thread

        if enableBot:
        # if the config option to enable the bot is on (enabled by bot runner if not already)
            botWebHostDefiner()
            # defines the webhost address
            ptpThread = threading.Thread(target = webHostListener, name="SBO PTP Connection", daemon=True)
            # creates a thread for the webhost listener
            ptpThread.start()
            # starts the ptp thread
            botThread = threading.Thread(target = runSBOBot, name="SBO Twitch Bot Process", daemon=True)
            # creates a thread for the SBO-Bot program to run in - this way it won't stop the main process
            botThread.start()
            # starts the SBO-Bot thread

        if not DSIoverride:
        # if DSI isn't active and not managing song data
            startWin.mainWindow.labelSwap.emit("No DSI data host found, using SBO logic", 2)
            # user inform
            loopThread = threading.Thread(target = looper, name = "Song Data Grab Looper", daemon=True)
            # creates a thread for the song data grab looper
            loopThread.start()
            # starts the looper thread
        else:
        # if DSI *is* active
            startWin.mainWindow.labelSwap.emit("Using DSI data, disabling SBO logic", 2)
            # user inform
            dsiThread = threading.Thread(target = dsiDataGrabber, name="DSI Data Grab Process", daemon=True)
            # creates a thread for the DSI data connection
            dsiThread.start()
            # starts the thread

    else:
    # restart call for a process
        if process == "WS":
        # websocket process restart
            if sboWS is not None:
            # if the websocket process already exists
                if sboWS.poll() is None:
                # poll doesn't return
                    sboWS.terminate()
                    # kills the websocket program
                try:
                    sboWS.wait(timeout=2)
                    # waits 2 seconds
                except subprocess.TimeoutExpired:
                # 2 seconds are up
                    sboWS.kill()
                    # goes more aggressive
                    sboWS.wait()
                    # waits till close
            if restart:
            # if there's a call to restart the thread, not just shut down
                sbowsThread = threading.Thread(target = runSBOws, name="SBO-WebSocket Process", daemon=True)
                # creates a thread for the SBO-WS program to run in - this way it won't stop the main process
                sbowsThread.start()
                # starts the SBO-WS thread
        elif process == "Bot":
        # bot process restart
            if sboBot is not None:
            # if the bot process already exists
                if sboBot.poll() is None:
                # poll doesn't return
                    sboBot.terminate()
                    # kills the bot program
                try:
                    sboBot.wait(timeout=2)
                    # waits 2 seconds
                except subprocess.TimeoutExpired:
                # 2 seconds are up
                    sboBot.kill()
                    # goes more aggressive
                    sboBot.wait()
                    # waits till close
            if restart:
            # if there's a call to restart the thread, not just shut down
                botThread = threading.Thread(target = runSBOBot, name="SBO Twitch Bot Process", daemon=True)
                # creates a thread for the SBO-Bot program to run in - this way it won't stop the main process
                botThread.start()
                # starts the SBO-Bot thread



### Window Start ###

startApp = QApplication(sys.argv)
# base app instance (passes command line arguments)
startWin = starterWindow()
# creates a window instance for the starter window
sys.exit(startApp.exec())
# exceutes the app task (runs the QApplication)