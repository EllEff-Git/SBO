from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
import json, os, sys, webbrowser
# Required for config management



class BotConfWindow(QMainWindow):
    """The window class"""
    def __init__(self):
    # setup
        super().__init__()
        # init

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

        self.setMinimumSize(300, 500)
        # sets the window size 
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setWindowTitle("SBO Twitch Bot Configuration")
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
                    "useSeparateBot": True,
                    "announcePresence": True,
                    "modCooldowns": "Bypass",
                    "vipCooldowns": "Short"
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
        self.mainWidget = QWidget()
        # the main, central widget

        self.modCooldownOptions = ["Default", "Bypass", "Short", "Halved"]
        self.vipCooldownOptions = ["Default", "Bypass", "Short", "Halved"]
        # lists of options for cooldowns for VIPs/mods

        self.selectedModCooldown = self.loadedConfig.get("modCooldowns", "Bypass")
        # grabs the selected mod cooldown option
        self.selectedVipCooldown = self.loadedConfig.get("vipCooldowns", "Short")
        # grabs the selected vip cooldown option

        if self.selectedModCooldown in self.modCooldownOptions:
        # if the config-set value is in the list of options 
            self.modCooldownOptions.remove(self.selectedModCooldown)
            # removes it from the list of options
        else:
        # if it's somehow not
            self.selectedModCooldown = "Bypass"
            # uses the default value
            self.modCooldownOptions.remove(self.selectedModCooldown)
            # removes it from the list of options

        if self.selectedVipCooldown in self.vipCooldownOptions:
        # if the config-set value is in the list of options
            self.vipCooldownOptions.remove(self.selectedVipCooldown)
            # removes it from the list of options
        else:
        # if it's somehow not
            self.selectedVipCooldown = "Short"
            # uses the default value
            self.vipCooldownOptions.remove(self.selectedVipCooldown)
            # removes it from the list of options

    ### Main Layout ###

        self.mainLayout = QGridLayout(self.mainWidget)
        # sets the main layout to use a grid of the central
        self.mainLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins of 25px 
        self.mainLayout.setVerticalSpacing(25)
        # sets vertical spacing

    ### User Inform Layout ###

        self.informLayout = QGridLayout()
        # adds a grid layout for the user inform prompt
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

    ### Presence Announce ###

        self.sayHiLabel = QLabel("Announce Presence")
        # label for presence announce
        self.sayHiLabel.setToolTip("Whether the bot should send a message in chat when it connects\n"
                                "Sends a message on program start (only if stream is not live yet)\n"
                                "Sends a message when stream goes live")
        # tooltip

        self.sayHiCheck = QCheckBox()
        # the checkbox for the presence announce
        self.sayHiCheck.setChecked(self.loadedConfig.get("announcePresence", True))
        # sets the check state based on the config (defaults to True)

        self.optionLayout.addWidget(self.sayHiLabel, 5, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.sayHiCheck, 5, 0, alignment=Qt.AlignmentFlag.AlignRight)
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

        self.optionLayout.addWidget(self.separateBotLabel, 6, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.separateBotCheck, 6, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Mod Cooldowns ###

        self.modCooldownLabel = QLabel("Moderator Cooldowns")
        # label for mod cooldowns
        self.modCooldownLabel.setToolTip("How moderator cooldowns should work\n"
                                        "Default means they have the same cooldowns as everyone else\n"
                                        "Halved splits the cooldowns down to half of the default duration\n"
                                        "Short cuts the cooldowns down to 1/3rd of the default duration\n"
                                        "Bypass skips the cooldowns completely")
        # tooltip

        self.modCooldownDropdown = QComboBox()
        # the dropdown for the mod cooldown
        self.modCooldownDropdown.addItem(self.selectedModCooldown)
        self.modCooldownDropdown.addItems(self.modCooldownOptions)
        # the dropdown options (adds the seelcted item first, then the rest)

        self.optionLayout.addWidget(self.modCooldownLabel, 7, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.modCooldownDropdown, 7, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### VIP Cooldowns ###

        self.vipCooldownLabel = QLabel("VIP Cooldowns")
        # label for VIP cooldowns
        self.vipCooldownLabel.setToolTip("How VIP cooldowns should work\n"
                                        "Default means they have the same cooldowns as everyone else\n"
                                        "Halved splits the cooldowns down to half of the default duration\n"
                                        "Short cuts the cooldowns down to 1/3rd of the default duration\n"
                                        "Bypass skips the cooldowns completely")
        # tooltip

        self.vipCooldownDropdown = QComboBox()
        # the dropdown for the VIP cooldown
        self.vipCooldownDropdown.addItem(self.selectedVipCooldown)
        self.vipCooldownDropdown.addItems(self.vipCooldownOptions)
        # the dropdown options (adds the seelcted item first, then the rest)

        self.optionLayout.addWidget(self.vipCooldownLabel, 8, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.vipCooldownDropdown, 8, 0, alignment=Qt.AlignmentFlag.AlignRight)
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

        self.saveQuitButton.clicked.connect(self.writeConfig)
        # connects the SBO start button to the config write + exit

        self.buttonLayout.addWidget(self.saveQuitButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the layout
  
    ### Central Widget ###

        self.setCentralWidget(self.mainWidget)
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

### Config Write ###

    def writeConfig(self):
        """Function to write the config json file (and exit)"""

        self.informPrompt.setText("Saving configuration...")
        # sets saving text

        configuration = {
            "commandPrefix": self.commandPrefixLine.text().strip(),
            "cooldownMessages": self.cooldownMsgCheck.isChecked(),
            "cooldownMessageFormat": self.cooldownMsgFormatLine.text().strip(),
            "controlLiveOnly": self.liveControlCheck.isChecked(),
            "useSeparateBot": self.separateBotCheck.isChecked(),
            "announcePresence": self.sayHiCheck.isChecked(),
            "modCooldowns": self.modCooldownDropdown.currentText(),
            "vipCooldowns": self.vipCooldownDropdown.currentText()
        }
        # forms a configuration based on the states of each of the fields

        with open(self.configPath, "w", encoding="utf-8") as cfg:
        # opens the config file
            json.dump(configuration, cfg, indent=3)
            # dumps everything in

        self.close()
        # closes the whole process


### Starter ###


if __name__ == "__main__":
# runs at start

    app = QApplication(sys.argv)
    # creates a Qt Application

    botCfgWindow = BotConfWindow()
    # instantiates a window
    botCfgWindow.show()
    # displays the window

    sys.exit(app.exec())
    # waits for the app to be done, then exits