from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
import json, os, sys, webbrowser
# Required for config management



class BotConfWindow(object):
    """The window class"""
    def setupUi(self, BotWindow):
    # setup
        if not BotWindow.objectName():
        # checks for a name 
            BotWindow.setObjectName(u"BotWindow")
            # sets the name
        BotWindow.setMinimumSize(925, 350)
        # sets the window size 
        self.window = BotWindow
        # stores a reference in self to the actual window (so that it can be closed later)

        self.main = QWidget(BotWindow)
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
        self.configPath = os.path.join(self.configFolderPath, "botConfig.json")
        # stores the config file's path
        self.ownPath = os.path.join(self.mainFolder, "runtime", "Qt", "botWindow", "botWindow.exe")
        # stores the configuration window path

        self.cmdCfgExePath = os.path.join(self.mainFolder, "runtime", "Qt", "cmdWindow", "cmdWindow.exe")
        # stores the command config window file path
        self.cmdCfgPath = os.path.join(self.configFolderPath, "commandConfig.json")
        # stores the command config .json file path

        self.window.setWindowIcon(QIcon(self.mainIcon))
        # the window icon

        self.window.setWindowTitle("SBO Twitch Bot Configuration")
        # sets title name

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

                defaultConfig = {
                    "commandPrefix": "!",
                    "cooldownMessages": False,
                    "cooldownMessageFormat": "Command is on cooldown ({duration})",
                    "controlLiveOnly": False,
                    "useSeparateBot": True
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

        self.centralWidget = QWidget(BotWindow)
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
        # sets the option layout into the main

    ### Filters ###

        self.twitchIDfilter = QRegularExpressionValidator(QRegularExpression(r"\d+"))
        # Twitch ID filter (accepts any integer-based response)



    ### Inform Prompt ###

        self.informPrompt = QLabel("Configure Twitch Bot Function\nHover any option for more information")
        # user inform prompt
        self.informPrompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.informPrompt.setToolTip("Help text")
        # tooltip

        self.informLayout.addWidget(self.informPrompt, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout


    ### Command Prefix ###

        self.commandPrefixLabel = QLabel("Command Prefix")
        # label for the command prefix
        self.commandPrefixLabel.setToolTip("What symbol the bot should use to interpret commands\nDefault: !")
        # tooltip

        self.commandPrefixLine = QLineEdit()
        # line edit for the command prefix
        self.commandPrefixLine.setFixedSize(30, 30)
        self.commandPrefixLine.setText(self.loadedConfig.get("commandPrefix", "!"))
        # sets the text based on the config (defaults to !)

        self.optionLayout.addWidget(self.commandPrefixLabel, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.commandPrefixLine, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Cooldown Messages ###

        self.cooldownMsgLabel = QLabel("Enable Cooldown Messages")
        # label for the cooldown message
        self.cooldownMsgLabel.setToolTip("Whether to reply to users in chat with a message if they're on a command cooldown\nDisabling means the bot won't reply at all until the cooldown is over\nDefault: Disabled")
        # tooltip

        self.cooldownMsgCheck = QCheckBox()
        # the checkbox for the cooldown message
        self.cooldownMsgCheck.setChecked(self.loadedConfig.get("cooldownMessages", False))
        # sets the check state based on the config (defaults to False)

        self.optionLayout.addWidget(self.cooldownMsgLabel, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.cooldownMsgCheck, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Cooldown Message Format ###

        self.cooldownMsgFormatLabel = QLabel("Cooldown Message Format")
        # label for the cooldown message format 
        self.cooldownMsgFormatLabel.setToolTip("What should the cooldown message say, when replying to a chatter with the command on cooldown"
                                               "\nFormatting: {command} includes the command name, {cooldown} includes the duration of the cooldown remaining, {chatter} includes the chatter's name"
                                               "\nExample: '{command} is on cooldown to {chatter} for {duration} seconds!'"
                                               "\nDefault: Command is on cooldown ({duration})")
        # tooltip

        self.cooldownMsgFormatLine = QLineEdit()
        # lineedit for the cooldown message format
        self.cooldownMsgFormatLine.setText(self.loadedConfig.get("cooldownMessageFormat", "Command is on cooldown ({duration})"))
        # sets the text based on the config
        self.cooldownMsgFormatLine.setMinimumWidth(250)
        # makes the field wider to fit user input better

        self.optionLayout.addWidget(self.cooldownMsgFormatLabel, 3, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.cooldownMsgFormatLine, 3, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Override Live Check ###

        self.liveControlLabel = QLabel("Control Only When Live")
        # label for live override
        self.liveControlLabel.setToolTip("Whether the bot should wait for the stream to be live to allow command usage\nRecommended to keep on, outside of testing - may lead to unwanted Spotify control via chat if left off")
        # tooltip

        self.liveControlCheck = QCheckBox()
        # the checkbox for the live control
        self.liveControlCheck.setChecked(self.loadedConfig.get("controlLiveOnly", True))
        # sets the check state based on the config (defaults to True)

        self.optionLayout.addWidget(self.liveControlLabel, 4, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.liveControlCheck, 4, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Separate Bot Account ###

        self.separateBotLabel = QLabel("Separate Bot Account")
        # label for bot account
        self.separateBotLabel.setToolTip("Whether to use a completely separate Twitch account to run the commands\nNot required, but recommended for visuals/chat management")
        # tooltip

        self.separateBotCheck = QCheckBox()
        # the checkbox for the bot account
        self.separateBotCheck.setChecked(self.loadedConfig.get("useSeparateBot", True))
        # sets the check state based on the config (defaults to True)

        self.optionLayout.addWidget(self.separateBotLabel, 5, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.separateBotCheck, 5, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout



    ### Buttons ###

        self.buttonLayout = QGridLayout()
        # makes a button layout
        self.buttonLayout.setVerticalSpacing(15)
        # sets spacing

        self.mainLayout.addLayout(self.buttonLayout, 2, 0)
        # adds the layout to main (row 2, under the options)

        self.saveQuitButton = QPushButton("Save and close\nEnsure you press this to save the config!")
        # a button to close and start SBO
        self.saveQuitButton.setToolTip("Saves and closes this configuration window")
        # tooltip
        self.saveQuitButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.openCmdCfgButton = QPushButton("Configure Commands")
        # a button to open the comWindow.exe file
        self.openCmdCfgButton.setToolTip("Opens the command configuration window")
        # tooltip
        self.openCmdCfgButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.saveQuitButton.clicked.connect(self.writeConfig)
        # connects the SBO start button to the config write + exit
        self.openCmdCfgButton.clicked.connect(self.runCmdConfig)
        # connects the command config button to the command config window runner

        self.buttonLayout.addWidget(self.openCmdCfgButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.addWidget(self.saveQuitButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the layout
  
    ### Central Widget ###

        BotWindow.setCentralWidget(self.centralWidget)
        # sets central widget



### Twitch ID Lookup Open ###

    def openTwitchURL(self):
        """Function to open the conversion website"""
        webbrowser.open("https://streamscharts.com/tools/convert-username")
        # opens a good Twitch ID lookup site

### Show/Hide Dev Items ###

    def showHideText(self, line:QLineEdit, button:QPushButton):
        """Function to show/hide specific text"""

        if line.echoMode() == QLineEdit.EchoMode.Password:
        # if the slot is already in 'Password' mode
            line.setEchoMode(QLineEdit.EchoMode.Normal)
            # sets to normal (text visible)
            button.setText("Hide")
            # changes the button to say it hides on press
        else:
        # not yet in password mode
            line.setEchoMode(QLineEdit.EchoMode.Password)
            # sets to password mode (text hidden)
            button.setText("Show")
            # changes the button to say it shows on press

### Command Config Window Run ###

    def runCmdConfig(self):
        """Function to run the bot command configuration window"""
        self.cmdProcess = QProcess()
        # creates a QProcess for the command config
        self.cmdProcess.start(self.cmdCfgExePath)
        # runs the command configuration window as a QProcess

### Config Write ###

    def writeConfig(self):
        """Function to write the config json file (and exit)"""

        if not os.path.exists(self.cmdCfgPath):
        # if the command config doesn't exist
            self.informPrompt.setText(f"Command configuration not set up yet!\nCannot save before setting up\nOpening command config...")
            # user warning
            self.runCmdConfig()
            # runs the command config
            return
            # stops this function

        self.informPrompt.setText("Saving configuration...")
        # sets saving text

        configuration = {
            "commandPrefix": self.commandPrefixLine.text().strip(),
            "cooldownMessages": self.cooldownMsgCheck.isChecked(),
            "cooldownMessageFormat": self.cooldownMsgFormatLine.text().strip(),
            "controlLiveOnly": self.liveControlCheck.isChecked(),
            "useSeparateBot": self.separateBotCheck.isChecked()
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

    botCfgWindow = QMainWindow()
    # creates a window
    ui = BotConfWindow()
    # takes the UI class
    ui.setupUi(botCfgWindow)
    # "populates" the UI class

    botCfgWindow.show()
    # displays the window

    sys.exit(app.exec())
    # waits for the app to be done, then exits