from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
import json, os, sys
# Required for config management



class funcConfWindow(object):
    """The window class"""
    def setupUi(self, FuncWindow):
    # setup
        if not FuncWindow.objectName():
        # checks for a name 
            FuncWindow.setObjectName(u"FuncWindow")
            # sets the name
        FuncWindow.setMinimumSize(925, 350)
        # sets the window size 
        self.window = FuncWindow
        # stores a reference in self to the actual window (so that it can be closed later)

        self.main = QWidget(FuncWindow)
        # makes a QWidget out of the main window
        self.main.setObjectName(u"main")
        # sets the object name

        self.thisExeDir = os.path.dirname(sys.executable)
        # the directory this exe is located in
        self.mainIcon = os.path.join(sys._MEIPASS, "SBO.png")
        # the directory containing the program icon png (built-in)
        self.configFolderPath = os.path.join(os.environ["LOCALAPPDATA"], "SBO")
        # the folder path that should contain all the configuration files

        self.mainFolder = os.path.abspath(os.path.join(self.thisExeDir, "..", "..", ".."))
        # stores the "main" folder (SBO, which is 3 folders up)
        self.configPath = os.path.join(self.configFolderPath, "functionConfig.json")
        # stores the config file's path
        self.ownPath = os.path.join(self.mainFolder, "runtime", "Qt", "funcWindow", "funcWindow.exe")
        # stores the configuration window path

        self.sboConfigExePath = os.path.join(self.mainFolder, "runtime", "Qt", "sboWindow", "sboWindow.exe")
        # stores the SBO visual configuration window .exe path
        self.sboConfigPath = os.path.join(self.configFolderPath, "sboConfig.json")
        # stores the SBO visual configuration .json file path

        self.botConfigExePath = os.path.join(self.mainFolder, "runtime", "Qt", "botWindow", "botWindow.exe")
        # stores the Twitch Bot configuration window .exe path
        self.botConfigPath = os.path.join(self.configFolderPath, "botConfig.json")
        # stores the Twitch Bot configuration .json file path

        self.window.setWindowIcon(QIcon(self.mainIcon))
        # the window icon

        self.window.setWindowTitle("SBO Functionality Configuration")
        # sets title name

        self.firstTime = False
        # stores a boolean for the first time launch (False by default)

        def readConfig() -> dict:
            """Function to read the config file, returns the json dictionary"""
            try:
            # tries to read the config.json
                with open(self.configPath, "r", encoding="utf-8") as cfg:
                # opens the config file in read mode
                    newConfig = json.load(cfg)
                    # stores the contents in self.configuration
                    return newConfig
                    # returns the new config 
            except:
            # if it can't (file doesn't exist)

                self.firstTime = True
                # sets the first time boolean to True (this will give a prompt)

                defaultConfig = {
                    "httpPort": 6868,
                    "addressType": "Device",
                    "consoleLength": 25,
                    "hidePlayerTimeout": 15,
                    "enableBot": True,
                    "skipFuncCfgWin": False,
                    "skipSBOcfgWin": False,
                    "skipRequiredCheck": False,
                    "enableShaaCompat": False
                }
                # forms a new configuration file from preset defaults

                with open(self.configPath, "w", encoding="utf-8") as cfg:
                # "opens" the config (doesn't exist, so just makes a new one)
                    json.dump(defaultConfig, cfg, indent=3)
                    # writes the default config
                return defaultConfig
                # returns the default config

        self.loadedConfig = readConfig()
        # runs the config reader to get new config info, stores it

        self.configsNotDone = 0
        # start of counter

        self.centralWidget = QWidget(FuncWindow)
        # the main, central widget
        self.centralWidget.setObjectName("centralWidget")
        # sets name



    ### Main Layout ###

        self.mainLayout = QGridLayout(self.centralWidget)
        # sets the main layout to use a grid of the central
        self.mainLayout.setObjectName("mainLayout")
        # sets name
        self.mainLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins of 25px 
        self.mainLayout.setVerticalSpacing(25)
        # sets vertical spacing

    ### User Inform Layout ###

        self.informLayout = QGridLayout()
        # adds a grid layout for the user inform prompt
        self.informLayout.setObjectName("informLayout")
        # sets name
        self.informLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins of 25px
        self.informLayout.setVerticalSpacing(15)
        # sets vertical spacing
        self.informLayout.setHorizontalSpacing(10)
        # sets horizontal spacing between elements

        self.mainLayout.addLayout(self.informLayout, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the inform layout to main

    ### Option Layout ###

        self.optionLayout = QGridLayout()
        # adds a grid layout for the options
        self.optionLayout.setObjectName("optionLayout")
        # sets name
        self.optionLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins of 25px
        self.optionLayout.setVerticalSpacing(15)
        # sets vertical spacing
        self.optionLayout.setHorizontalSpacing(10)
        # sets horizontal spacing between elements

        self.optionLayout.setColumnStretch(0, 0)
        self.optionLayout.setColumnStretch(1, 0)
        # disables columns stretching automatically

        self.mainLayout.addLayout(self.optionLayout, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the option layout to main

    ### Filters ###

        self.portFilter = QIntValidator(1024, 65535)
        # network port filter
        self.timeoutFilter = QIntValidator(0, 3600)
        # player timeout filter


    
    ### Inform Prompt ###

        self.informPrompt = QLabel("Configure SBO Function\nHover any option for more information")
        # user inform prompt
        self.informPrompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.informPrompt.setToolTip("Help text")
        # tooltip

        self.firstTimeButton = QPushButton()
        # a button to open the first time prompt window
        self.firstTimeButton.setText("Help Window")
        # sets text
        self.firstTimeButton.setToolTip("Opens the help window")
        # tooltip
        self.firstTimeButton.setMinimumSize(75, 30)
        # sets a minimum size

        self.firstTimeButton.clicked.connect(self.firstTimePrompt)
        # connects the first time button to the prompt

        self.informLayout.addWidget(self.informPrompt, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.informLayout.addWidget(self.firstTimeButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout

    ### Http Port ###

        self.httpPortLabel = QLabel("HTTP Port")
        # label for the URI enable option
        self.httpPortLabel.setToolTip("What port the internal websocket should use\nNetwork ports are 1024-65535, default is 6868\nThe program also occupies the subsequent 2 ports for internal communication")
        # tooltip

        self.httpPortLine = QLineEdit()
        # line edit for the http network port
        self.httpPortLine.setText(f"{self.loadedConfig.get("httpPort", 6868)}")
        # sets the text based on the config (defaults to 6868)

        self.optionLayout.addWidget(self.httpPortLabel, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.httpPortLine, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Address Type ###

        self.addressTypeLabel = QLabel("Address Type")
        # label for the refresh timer
        self.addressTypeLabel.setToolTip("What network address type to use\nDevice = 127.0.0.1 (only accessible on-device)\nLocal = 0.0.0.0 (accessible to any device across the same network)\nIf you want to display the overlay on the same device as SBO, keep this on 'Device'\nIf you want to display the overlay on a different device on the same network, use 'Local'")
        # tooltip

        self.addressTypeOptions = ["Device", "Local"]
        # the options available for address type
        self.selectedAddressType = self.loadedConfig.get("addressType", "Device")
        # loads the selected one from config (defaults to Device)
        self.addressTypeOptions.remove(self.selectedAddressType)
        # removes the selected one from the list (leaves only one option)
        
        self.addressTypeDropdown = QComboBox()
        # the dropdown menu for address type
        self.addressTypeDropdown.addItem(self.selectedAddressType)
        self.addressTypeDropdown.addItem(self.addressTypeOptions[0])
        # adds the available options (selected first to make it default)

        self.optionLayout.addWidget(self.addressTypeLabel, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.addressTypeDropdown, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Console Length ###

        self.consoleLengthLabel = QLabel("Console Length")
        # label for the console length
        self.consoleLengthLabel.setToolTip("How many lines of text should be stored in the 'console'\nDefault: 25, minimum: 10")
        # tooltip

        self.consoleLengthLine = QLineEdit()
        self.consoleLengthLine.setText(f"{self.loadedConfig.get("consoleLength", 25)}")
        # sets the text based on the config (defaults to 25)

        self.optionLayout.addWidget(self.consoleLengthLabel, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.consoleLengthLine, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Player Timeout ###

        self.playerTimeoutLabel = QLabel("Player Timeout")
        # label for the player timeout timer
        self.playerTimeoutLabel.setToolTip("How many seconds the player should be paused before disappearing\nAccepted range: 0-3600\nSetting to 0 disables the timeout")
        # tooltip

        self.playerTimeoutLine = QLineEdit()
        self.playerTimeoutLine.setText(f"{self.loadedConfig.get("playerTimeout", 15)}")
        # sets the check state based on the config (defaults to 15)

        self.optionLayout.addWidget(self.playerTimeoutLabel, 3, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.playerTimeoutLine, 3, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Enable Bot ###

        self.enableBotLabel = QLabel("Enable Twitch Bot")
        # label for the twitch bot
        self.enableBotLabel.setToolTip("Whether the included Twitch bot should be enabled\nRequires separate configuration\nDefault: Enabled")
        # tooltip

        self.enableBotCheck = QCheckBox()
        self.enableBotCheck.setChecked(self.loadedConfig.get("enableBot", True))
        # sets the check state based on the config (defaults to True)

        self.optionLayout.addWidget(self.enableBotLabel, 4, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.enableBotCheck, 4, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Skip Functional Config ###

        self.skipFuncCfgLabel = QLabel("Skip Function Config")
        # label for functional config window disabling
        self.skipFuncCfgLabel.setToolTip("Skip opening the functional configuration window\nDefault: Disabled")
        # tooltip

        self.skipFuncCfgCheck = QCheckBox()
        self.skipFuncCfgCheck.setChecked(self.loadedConfig.get("skipFuncCfgWin", False))
        # sets the check state based on the config (defaults to False)

        self.optionLayout.addWidget(self.skipFuncCfgLabel, 5, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.skipFuncCfgCheck, 5, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Skip SBO Config ###

        self.skipSBOcfgLabel = QLabel("Skip SBO Config")
        # label for sbo config window disabling
        self.skipSBOcfgLabel.setToolTip("Skip opening the SBO configuration window\nDefault: Disabled")
        # tooltip

        self.skipSBOcfgCheck = QCheckBox()
        self.skipSBOcfgCheck.setChecked(self.loadedConfig.get("skipSBOcfgWin", False))
        # sets the check state based on the config (defaults to False)

        self.optionLayout.addWidget(self.skipSBOcfgLabel, 6, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.skipSBOcfgCheck, 6, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Skip Required Item Check ###

        self.skipRequiredLabel = QLabel("Skip Spotify Auth")
        # label for spotify auth required item skipping
        self.skipRequiredLabel.setToolTip("Skip required Spotify client credential request\nOnly enable if using DSI data hosting + no Twitch Bot!\nTwitch Bot requires Spotify authentication to pass commands")
        # tooltip

        self.skipRequiredCheck = QCheckBox()
        self.skipRequiredCheck.setChecked(self.loadedConfig.get("skipRequiredCheck", False))
        # sets the check state based on the config (defaults to False)

        self.optionLayout.addWidget(self.skipRequiredLabel, 7, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.skipRequiredCheck, 7, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Use SHAA Compat ###

        self.shaaCompatLabel = QLabel("Enable SHAA Compatibility")
        # label for SHAA compat
        self.shaaCompatLabel.setToolTip("Enables a field in the overlay to pass Spotify playback numbers via DSI/SHAA\nUses the field 2 string from DSI, adds 30 pixels to the height of the overlay")
        # tooltip

        self.shaaCompatCheck = QCheckBox()
        # checkbox for SHAA compat
        self.shaaCompatCheck.setChecked(self.loadedConfig.get("enableShaaCompat", False))
        # sets the check state based on teh config (defaults to False)

        self.optionLayout.addWidget(self.shaaCompatLabel, 8, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.shaaCompatCheck, 8, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout



    ### Buttons ###

        self.buttonLayout = QGridLayout()
        # makes a button layout
        self.buttonLayout.setVerticalSpacing(15)
        # sets spacing

        self.mainLayout.addLayout(self.buttonLayout, 2, 0)
        # adds the layout to main (row 2, under the options)

        self.sboConfigButton = QPushButton("Configure SBO Visuals")
        # a button to run the SBO configuration
        self.sboConfigButton.setToolTip("Opens a configuration window to change SBO details")
        # tooltip
        self.sboConfigButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.botConfigButton = QPushButton("Configure Twitch Bot")
        # a button to run the SBO-Bot configuration
        self.botConfigButton.setToolTip("Opens a window to configure the Twitch Bot details")
        # tooltip
        self.botConfigButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.startSBObutton = QPushButton("Save and close\nEnsure you press this to save the config!")
        # a button to close and start SBO
        self.startSBObutton.setToolTip("Closes this configuration window and continues SBO function")
        # tooltip
        self.startSBObutton.setMinimumSize(240, 45)
        # sets a minimum size

        self.buttonLayout.addWidget(self.sboConfigButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.addWidget(self.botConfigButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.addWidget(self.startSBObutton, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all to the layout, vertically aligned

        self.sboConfigButton.clicked.connect(lambda: self.checkConfigs(1))
        # connects the SBO config button to the async config runner
        self.botConfigButton.clicked.connect(lambda: self.checkConfigs(2))
        # connects the bot config button to the async config runner
        self.startSBObutton.clicked.connect(self.checkConfigs)
        # connects the SBO start button to the config write + exit

    ### Central Widget ###

        FuncWindow.setCentralWidget(self.centralWidget)
        # sets central widget

### First Time Prompt ###

        if self.firstTime:
            # if the first time flag is enabled
            QTimer.singleShot(500, self.firstTimePrompt)
            # runs the first time prompt window after loading is done

    def firstTimePrompt(self):
        """Function that runs the first time prompt message box"""

        self.ftPrompt = QMessageBox()
        # creates a prompt for first time users
        self.ftPrompt.setWindowTitle("SBO Helper")
        # window title
        self.ftPrompt.setWindowIcon(QIcon(self.mainIcon))
        # icon
        self.ftPrompt.setText(
            "Hello and welcome to the SBO Configurator!\n\n"
            "This is the first step, and this handles all the functional stuff\n"
            "Options selected here change how the program runs\n"
            "If you need any more information about an option, try hovering over it :)\n\n"
            "To configure the visuals of your overlay, press the 'Configure SBO' button (required to configure once)\n\n"
            "If you wish to use the Twitch Bot, press the 'Configure Twitch Bot' button (if this option is enabled, required to configure once)\n\n"
            "Any questions, concerns, bugs, ideas, etc. can be sent via GitHub or on Discord (LilPiffer)\n\n"
            "I hope you enjoy SBO, thank you for installing <3"
            )
        # the window text

        self.closeft = self.ftPrompt.exec()
        # close first time prompt button

        if self.closeft == QMessageBox.StandardButton.Ok:
        # if everything is ok
            None
            # closes

### SBO Window Run ###

    def runSBOconfig(self):
        """Function to run the SBO configuration window"""
        self.sboProcess = QProcess()
        # creates a QProcess for the SBO config
        self.sboProcess.start(self.sboConfigExePath)
        # runs the SBO configuration window as a QProcess

### SBO-Bot Window Run ###

    def runBotConfig(self):
        """Function to run the SBO-Bot configuration window"""
        self.sboBotProcess = QProcess()
        # creates a QProcess for the SBO-Bot config
        self.sboBotProcess.start(self.botConfigExePath)
        # runs the SBO-Bot configuration window as a QProcess

### Check Other Configs ###

    def checkConfigs(self, state:int=0):
        """Function to check the configs before allowing save + exit"""

        if state == 1:
        # if the command is to open the sbo config
            self.runSBOconfig()
            # bypasses all, runs the SBO config
            return
            # stops

        elif state == 2:
        # if the command is to open the bot config
            self.runBotConfig()
            # bypasses all, runs the bot config
            return
            # stops

        if not os.path.exists(self.sboConfigPath):
        # if the sbo config file doesn't exist when trying to exit
            self.informPrompt.setText("SBO Visuals have not been configured!\nCannot save before configuration!")
            # user inform
            self.configsNotDone += 1
            # adds 1 to the counter
            self.runSBOconfig()
            # runs the SBO configuration window
            return
            # stops so it doesn't open both at once

        if self.enableBotCheck.isChecked() and not os.path.exists(self.botConfigPath):
        # if the bot is enabled but the config isn't done
            self.informPrompt.setText("Twitch Bot is enabled, but has not been configured!\nCannot save before configuration!")
            # user inform
            self.configsNotDone += 1
            # adds 1 to the counter
            self.runBotConfig()
            # runs the bot configuration window
            return
            # stops so it doesn't progress without double-checking

        self.writeConfig()
        # save + exit if it makes this far (no tasks)

### Config Write ###

    def writeConfig(self):
        """Function to write the config json file (and exit)"""

        self.informPrompt.setText("Saving configuration...")
        # user inform

        httpPort = self.httpPortLine.text().strip()
        # grabs the text from the http port edit line

        try:
        # tries to convert
            httpPort = int(httpPort)
            # turns it into integer
        except:
        # if it can't
            httpPort = 6868
            # sets safe number

        consoleLength = self.consoleLengthLine.text().strip()
        # grabs the text from the console length edit line

        try:
        # tries to convert
            consoleLength = int(consoleLength)
            # turns it into integer
        except:
        # if it can't
            consoleLength = 25
            # sets safe number

        playerTimeout = self.playerTimeoutLine.text().strip()
        # grabs the text from the timeout edit line

        try:
        # tries to convert
            playerTimeout = int(playerTimeout)
            # turns it into integer
        except:
        # if it can't
            playerTimeout = 15
            # sets safe number

        configuration = {
            "httpPort": httpPort,
            "addressType": self.addressTypeDropdown.currentText().strip(),
            "consoleLength": consoleLength,
            "hidePlayerTimeout": playerTimeout,
            "enableBot": self.enableBotCheck.isChecked(),
            "skipFuncCfgWin": self.skipFuncCfgCheck.isChecked(),
            "skipSBOcfgWin": self.skipSBOcfgCheck.isChecked(),
            "skipRequiredCheck": self.skipRequiredCheck.isChecked(),
            "enableShaaCompat": self.shaaCompatCheck.isChecked()
        }
        # forms a configuration based on the states of each of the fields

        with open(self.configPath, "w", encoding="utf-8") as cfg:
        # opens the config file
            json.dump(configuration, cfg, indent=3)
            # dumps everything in

        self.window.close()
        # closes the whole process


### Starter ###


if __name__ == "__main__":
# runs at start

    app = QApplication(sys.argv)
    # creates a Qt Application

    FuncCfgWindow = QMainWindow()
    # creates a window
    ui = funcConfWindow()
    # takes the UI class
    ui.setupUi(FuncCfgWindow)
    # "populates" the UI class

    FuncCfgWindow.show()
    # displays the window

    sys.exit(app.exec())
    # waits for the app to be done, then exits