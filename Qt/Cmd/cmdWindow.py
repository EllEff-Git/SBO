from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
import json, os, sys
# Required for config management



class ComConfWindow(object):
    """The window class"""
    def setupUi(self, ComWindow):
    # setup
        if not ComWindow.objectName():
        # checks for a name 
            ComWindow.setObjectName(u"ComWindow")
            # sets the name
        ComWindow.setMinimumSize(925, 350)
        # sets the window size 
        self.window = ComWindow
        # stores a reference in self to the actual window (so that it can be closed later)

        self.main = QWidget(ComWindow)
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
        self.configPath = os.path.join(self.configFolderPath, "commandConfig.json")
        # stores the config file's path

        self.window.setWindowIcon(QIcon(self.mainIcon))
        # the window icon

        self.window.setWindowTitle("SBO Twitch Bot Command Configuration")
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
                    "playlist": {"enabled": True, "chatterCooldown": 600, "channelCooldown": 150, "requiredLevel": "Chatter", "alias": "", "syntax": ""},
                    "artist": {"enabled": True, "chatterCooldown": 180, "channelCooldown": 60, "requiredLevel": "Chatter", "alias": "", "syntax": ""},
                    "album": {"enabled": True, "chatterCooldown": 180, "channelCooldown": 60, "requiredLevel": "Chatter", "alias": "", "syntax": ""},
                    "song": {"enabled": True, "chatterCooldown": 180, "channelCooldown": 60, "requiredLevel": "Chatter", "alias": "", "syntax": ""},
                    "lastSong": {"enabled": True, "chatterCooldown": 180, "channelCooldown": 60, "requiredLevel": "Chatter", "alias": "", "syntax": ""},
                    "pause": {"enabled": True, "chatterCooldown": 600, "channelCooldown": 120, "requiredLevel": "Moderator", "alias": "", "syntax": ""},
                    "resume": {"enabled": True, "chatterCooldown": 600, "channelCooldown": 120, "requiredLevel": "Moderator", "alias": "continue", "syntax": ""},
                    "skip": {"enabled": True, "chatterCooldown": 600, "channelCooldown": 120, "requiredLevel": "Moderator", "alias": "", "syntax": ""},
                    "previous": {"enabled": True, "chatterCooldown": 600, "channelCooldown": 120, "requiredLevel": "Moderator", "alias": "", "syntax": ""},
                    "queue": {"enabled": True, "chatterCooldown": 300, "channelCooldown": 30, "requiredLevel": "Subscriber", "alias": "", "syntax": "Usage: queue {spotifyURI} / queue {spotifyURL} / queue {spotifyID}"},
                    "queueq": {"enabled": True, "chatterCooldown": 300, "channelCooldown": 30, "requiredLevel": "Subscriber", "alias": "", "syntax": "Usage: queueq {song name}, {artist} / queueq {song name}"},
                    "songColor": {"enabled": True, "chatterCooldown": 300, "channelCooldown": 60, "requiredLevel": "Subscriber", "alias": "", "syntax": "Usage: songColor {color} / songColor {hexCode} / songColor {clear}"},
                    "artistColor": {"enabled": True, "chatterCooldown": 300, "channelCooldown": 60, "requiredLevel": "Subscriber", "alias": "", "syntax": "Usage: artistColor {color} / artistColor {hexCode} / artistColor {clear}"},
                    "albumColor": {"enabled": True, "chatterCooldown": 300, "channelCooldown": 60, "requiredLevel": "Subscriber", "alias": "", "syntax": "Usage: albumColor {color} / albumColor {hexCode} / albumColor {clear}"},
                    "barColor": {"enabled": True, "chatterCooldown": 300, "channelCooldown": 60, "requiredLevel": "Subscriber", "alias": "", "syntax": "Usage: barColor {color} / barColor {hexCode} / barColor {clear}"},
                    "overlayColor": {"enabled": True, "chatterCooldown": 300, "channelCooldown": 60, "requiredLevel": "Subscriber", "alias": "", "syntax": "Usage: overlayColor {color} / overlayColor {hexCode} / overlayColor {clear}"},
                    "customColor": {"enabled": True, "chatterCooldown": 600, "channelCooldown": 60, "requiredLevel": "Subscriber", "alias": "", "syntax": "Usage: customColor {get} {color/all} / customColor {set} {color} {hexCode} / customColor {remove} {color}"},
                    "sboHelp": {"enabled": True, "chatterCooldown": 600, "channelCooldown": 60, "requiredLevel": "Chatter", "alias": "", "syntax": "Usage: sboHelp {command} / sboHelp"}
                }
                # forms a new configuration file from preset defaults

                with open(self.configPath, "w", encoding="utf-8") as cfg:
                # "opens" the config (doesn't exist, so just makes a new one)
                    json.dump(defaultConfig, cfg, indent=3)
                    # writes the default config
                return defaultConfig
                # returns the default config

        self.loadedCommandConfig = readConfig()
        # runs the config reader to get new config info, stores it

        self.commandList = []
        # list of commands stored 

        for command in self.loadedCommandConfig.keys():
        # goes through every command
            self.commandList.append(command)
            # adds the name of the command to the list

        self.selectedCommand = self.commandList[0]
        # gets the first element of the command list

        self.centralWidget = QWidget(ComWindow)
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

    ### Command Selection Layout ###

        self.commandLayout = QGridLayout()
        # a layout for the command dropdown/label to sit in
        self.commandLayout.setObjectName("commandLayout")
        # sets name
        self.commandLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins of 25px
        self.commandLayout.setVerticalSpacing(15)
        # sets vertical spacing
        self.commandLayout.setHorizontalSpacing(10)
        # sets horizontal spacing between elements

        self.mainLayout.addLayout(self.commandLayout, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to main layout

    ### Option Layout ###

        self.optionLayout = QGridLayout()
        # adds a grid layout for the options
        self.optionLayout.setObjectName("optionLayout")
        # sets name
        self.optionLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins of 25px
        self.optionLayout.setVerticalSpacing(25)
        # sets vertical spacing
        self.optionLayout.setHorizontalSpacing(10)
        # sets horizontal spacing between elements

        self.mainLayout.addLayout(self.optionLayout, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # sets the option layout into the main

    ### Options ###

        self.levelToStatus = {
            0: "Chatter", 
            1: "Subscriber",
            2: "VIP",
            3: "Moderator",
            4: "Lead Moderator",
            5: "Streamer"
        }
        # all the different levels of options 

        self.statusToLevel = {
            "Chatter": 0, 
            "Subscriber": 1,
            "VIP": 2,
            "Moderator": 3,
            "Lead Moderator": 4,
            "Streamer": 5
        }
        # all the different levels of options 

        self.integerValidator = QIntValidator()
        # a validator to only accept integers


    ### Inform Prompt ###

        self.informPrompt = QLabel("Configure Twitch Bot Command Configuration\nHover any option for more information")
        # user inform prompt
        self.informPrompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.informPrompt.setToolTip("Help text")
        # tooltip

        self.informLayout.addWidget(self.informPrompt, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to inform layout

    ### Command Dropdown ###

        self.commandLabel = QLabel("Selected Command")
        # a label for the command selection
        self.commandLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.commandDropdown = QComboBox()
        # a dropdown menu for the command selection
        self.commandDropdown.setMinimumSize(300, 40)
        # minimum sizes

        for command in self.commandList:
        # goes through each of the configured commands
            self.commandDropdown.addItem(command)
            # adds all the commands as items into the dropdown

        selectedIndex = self.commandDropdown.findText(self.selectedCommand)
        # finds the index of the selected index
        self.commandDropdown.setCurrentIndex(selectedIndex)
        # sets the current text to match the 

        self.commandDropdown.currentIndexChanged.connect(self.selectNewCommand)
        # when the selection changes, calls the function that handles index changes

        self.commandLayout.addWidget(self.commandLabel, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.commandLayout.addWidget(self.commandDropdown, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to main layout (top)

    ### Enabled Checkbox ###

        self.enabledLabel = QLabel("Enable Command")
        # a label for enabled check
        self.enabledLabel.setToolTip("Whether the selected command should be enabled")
        # tooltip

        self.enabledCheckbox = QCheckBox()
        # a checkbox to enable/disable commands
        self.enabledCheckbox.setMinimumSize(40, 30)
        # min size

        self.optionLayout.addWidget(self.enabledLabel, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.enabledCheckbox, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Chatter Cooldown ###

        self.chatterCooldownLabel = QLabel("Cooldown (Per Chatter)")
        # a label for chatter cooldown
        self.chatterCooldownLabel.setToolTip("How long (in seconds) the command should be on cooldown (per individual chatter)")
        # tooltip

        self.chatterCooldownLine = QLineEdit()
        # a lineedit to change the chatter cooldown
        self.chatterCooldownLine.setValidator(self.integerValidator)
        # uses the int-only validation
        self.chatterCooldownLine.setAlignment(Qt.AlignmentFlag.AlignRight)
        # aligns text to right side
        self.chatterCooldownLine.setMinimumSize(80, 30)
        # min size

        self.optionLayout.addWidget(self.chatterCooldownLabel, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.chatterCooldownLine, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Channel Cooldown ###

        self.channelCooldownLabel = QLabel("Cooldown (Channel-Wide)")
        # a label for channel cooldown
        self.channelCooldownLabel.setToolTip("How long (in seconds) the command should be on cooldown (for all chatters)")
        # tooltip

        self.channelCooldownLine = QLineEdit()
        # a lineedit to change the channel cooldown
        self.channelCooldownLine.setValidator(self.integerValidator)
        # uses the int-only validation
        self.channelCooldownLine.setAlignment(Qt.AlignmentFlag.AlignRight)
        # aligns text to right side
        self.channelCooldownLine.setMinimumSize(80, 30)
        # min size

        self.optionLayout.addWidget(self.channelCooldownLabel, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.channelCooldownLine, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Level Dropdown ###

        self.requiredLevelLabel = QLabel("Required Level")
        # a label for required level
        self.requiredLevelLabel.setToolTip("The chatter's level required to allow use of the command")
        # tooltip

        self.requiredLevelDropdown = QComboBox()
        # a dropdown menu for each choosing the requirement level
        self.requiredLevelDropdown.setMinimumSize(200, 30)
        # min size

        self.requiredLevelDropdown.addItem("Chatter")
        self.requiredLevelDropdown.addItem("Subscriber")
        self.requiredLevelDropdown.addItem("VIP")
        self.requiredLevelDropdown.addItem("Moderator")
        self.requiredLevelDropdown.addItem("Lead Moderator")
        self.requiredLevelDropdown.addItem("Streamer")
        # adds all the items to dropdown

        self.optionLayout.addWidget(self.requiredLevelLabel, 3, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.requiredLevelDropdown, 3, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Alias ###

        self.aliasLabel = QLabel("Command Alias(es)")
        # a label for command alias(es)
        self.aliasLabel.setToolTip("A (comma-separated) list of alternate commands that should activate this command\nExample: 'resume' has an alias of 'continue' by default")
        # tooltip

        self.aliasLine = QLineEdit()
        # a lineedit to change the command alias(es)
        self.aliasLine.setMinimumSize(250, 30)
        # min size

        self.optionLayout.addWidget(self.aliasLabel, 4, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.aliasLine, 4, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Syntax / Notes ###

        self.syntaxLayout = QGridLayout()
        # a layout for the syntax/notes
        self.mainLayout.addLayout(self.syntaxLayout, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the layout to the bottom of the options (spans both columns)

        self.syntaxLabel = QLabel("Command Notes")
        # a label for command syntax/notes
        self.syntaxLabel.setToolTip("Notes for how the command should be used, syntax guide, etc")
        # tooltip

        self.syntaxLine = QLineEdit()
        # a lineedit to change the syntax
        self.syntaxLine.setMinimumSize(500, 30)
        # min size

        self.syntaxLayout.addWidget(self.syntaxLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.syntaxLayout.addWidget(self.syntaxLine, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout



    ### Internal Buttons ###

        #self.internalButtonLayout = QGridLayout()
        # makes a button layout for the internal commands
        #self.internalButtonLayout.setVerticalSpacing(25)
        #self.internalButtonLayout.setHorizontalSpacing(0)
        # sets spacing

        #self.mainLayout.addLayout(self.internalButtonLayout, 4, 0)
        # adds the layout to main (under the syntax)

        #self.addCommandButton = QPushButton("Add")
        # button to add a command
        #self.addCommandButton.setMinimumSize(60, 40)
        # min size

        #self.saveCommandButton = QPushButton("Save Command")
        # button to save selected command configuration
        #self.saveCommandButton.setMinimumSize(60, 40)
        # min size
        #self.saveCommandButton.setToolTip("Saves this command's configuration\nAuto-saved on command swap")
        # tooltip

        #self.removeCommandButton = QPushButton("Remove")
        # button to remove selected command
        #self.removeCommandButton.setMinimumSize(60, 40)
        # min size

        #self.addCommandButton.clicked.connect(lambda: self.addRemoveCommand(True))
        # connects the add button to the function with add call
        #self.saveCommandButton.clicked.connect(self.saveCommand)
        # connects the save button to the function
        #self.removeCommandButton.clicked.connect(lambda: self.addRemoveCommand(False))
        # connects the remove button to the function with no add call

        #self.internalButtonLayout.addWidget(self.addCommandButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        #self.internalButtonLayout.addWidget(self.saveCommandButton, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        #self.internalButtonLayout.addWidget(self.removeCommandButton, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all to layout (Add | Save | Remove)

        ### Note: as of right now, adding/removing commands is just not feasible with the system I use ###
        ### I want to add the ability to create full, complex commands yourself, but that's just not in the scope right now ###
        ### This program is mainly designed as an "addon" to my Spotify-related tools, and I just don't have the passion to stray too far ###
        ### I'll leave these elements here, since I did add them, and it feels like a waste to remove them ###

    ### Buttons ###

        self.buttonLayout = QGridLayout()
        # makes a button layout
        self.buttonLayout.setVerticalSpacing(15)
        # sets spacing

        self.mainLayout.addLayout(self.buttonLayout, 5, 0)
        # adds the layout to main (row 4, under the command save button)

        self.saveQuitButton = QPushButton("Save and close\nEnsure you press this to save the config!")
        # a button to close and start SBO
        self.saveQuitButton.setToolTip("Saves and closes this configuration window")
        # tooltip
        self.saveQuitButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.buttonLayout.addWidget(self.saveQuitButton, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the layout

        self.saveQuitButton.clicked.connect(lambda: self.writeConfig(True))
        # connects the SBO start button to the config write + exit

    ### Central Widget ###

        ComWindow.setCentralWidget(self.centralWidget)
        # sets central widget
        
        QTimer.singleShot(0, self.selectNewCommand)
        # calls the selectNewCommand to get the current command's details right away



### Command Selection Function ###

    def selectNewCommand(self):
        """Function to change selected command"""

        newCommand = self.commandDropdown.currentText().strip()
        # grabs the name of the current command

        self.saveCommand(self.selectedCommand)
        # uses the selected command value stored in self to save the details before swapping over to the new command

        self.selectedCommand = newCommand
        # reassigns new command

        self.enabledCheckbox.setChecked(self.loadedCommandConfig.get(newCommand, {}).get("enabled"))
        # sets the status of the command
        self.chatterCooldownLine.setText(f"{self.loadedCommandConfig.get(newCommand, {}).get("chatterCooldown")}")
        # sets the cooldown from config
        self.channelCooldownLine.setText(f"{self.loadedCommandConfig.get(newCommand, {}).get("channelCooldown")}")
        # sets the cooldown from config
        selectedLevel = self.loadedCommandConfig.get(newCommand, {}).get("requiredLevel", "Chatter")
        # gets the required level for the command
        selectedIndex = self.requiredLevelDropdown.findText(selectedLevel)
        # matches the level to an index 
        self.requiredLevelDropdown.setCurrentIndex(selectedIndex)
        # sets the required level dropdown        
        self.aliasLine.setText(self.loadedCommandConfig.get(newCommand, {}).get("alias"))
        # gets the stored alias(es)
        self.syntaxLine.setText(self.loadedCommandConfig.get(newCommand, {}).get("syntax"))
        # gets the stores syntax rules
        
### Add / Remove Command Func ###

    #def addRemoveCommand(self, add:bool):
        #"""Function to add or remove commands from installed commands"""

        #if add:
        # if adding a command
            #command, ok = QInputDialog.getText(self, "Name the command", "Command:")
            # asks for the name of the command

            #if ok and command.strip():
            # if user pressed ok and the command exists
                #self.commandDropdown.addItem(command)
                # adds a temporary item
                #tempIndex = self.commandDropdown.findText(command)
                # finds the new command's index
                #self.commandDropdown.setCurrentIndex(tempIndex)
                # changes the index to match selection

                #self.enabledCheckbox.setChecked(True)
                # checks the enabled box by default
                #self.chatterCooldownLine.setText("300")
                # default of 5-minute cooldown
                #self.channelCooldownLine.setText("150")
                # default of 2.5-minute cooldown
                #reqIndex = self.requiredLevelDropdown.findText("Chatter")
                # gets the index of chatter requirement level
                #self.requiredLevelDropdown.setCurrentIndex(reqIndex)
                # sets the dropdown to match
                #self.syntaxLine.setText("")
                # empties the syntax text
            #else:
            # if not ok or no command name
                #return
                # stops
        #else:
        # if removing a command
            #removableCommand = self.commandDropdown.currentText()
            # gets the name of the command to be removed
            #x = self.loadedCommandConfig.pop(removableCommand, None)
            # removes the command from the config
            #self.commandDropdown.setCurrentIndex(0)
            # goes to the first command

### Save Command ###

    def saveCommand(self, command:str=None):
        """Function to save current command's configuration"""

        if command:
        # if this function is called automatically, and a command is passed
            currentCommand = command
            # uses the passed value
        else:
        # called manually by pressing the button
            currentCommand = self.commandDropdown.currentText()
            # gets the name of the command

        enabled = self.enabledCheckbox.isChecked()
        # grabs the check status
        try: 
        # tries to convert the chatter cooldown text to an integer
            chatterCooldown = int(self.chatterCooldownLine.text().strip())
            # grabs the cooldown
        except:
        # if it can't
            chatterCooldown = 300
            # default 5 min
        try:
        # tries to convert the channel cooldown text to an integer
            channelCooldown = int(self.channelCooldownLine.text().strip())
            # grabs the cooldown
        except:
        # if it can't
            channelCooldown = 150
            # default 2.5 min
        requiredLevel = self.requiredLevelDropdown.currentText().strip()
        # grabs the current text of the required level
        alias = self.aliasLine.text().strip()
        # gets any potential alias(es)
        syntax = self.syntaxLine.text().strip()
        # gets any potential syntax 

        self.loadedCommandConfig[currentCommand] = {"enabled": enabled, "chatterCooldown": chatterCooldown, "channelCooldown": channelCooldown, "requiredLevel": requiredLevel, "alias": alias, "syntax": syntax}
        # stores the command in the config

### Config Write ###

    def writeConfig(self):
        """Function to write the config json file (and exit)"""

        self.saveCommand(self.selectedCommand)
        # calls the savecommand function with the current command to make sure it's saved too

        self.informPrompt.setText("Saving configuration...")
        # user inform

        with open(self.configPath, "w", encoding="utf-8") as cfg:
        # opens the config file
            json.dump(self.loadedCommandConfig, cfg, indent=3)
            # dumps everything to file
        
        self.window.close()
        # closes the whole process


### Starter ###


if __name__ == "__main__":
# runs at start

    app = QApplication(sys.argv)
    # creates a Qt Application

    cmdCfgWindow = QMainWindow()
    # creates a window
    ui = ComConfWindow()
    # takes the UI class
    ui.setupUi(cmdCfgWindow)
    # "populates" the UI class

    cmdCfgWindow.show()
    # displays the window

    sys.exit(app.exec())
    # waits for the app to be done, then exits