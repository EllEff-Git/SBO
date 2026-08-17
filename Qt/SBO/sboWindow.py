from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
import json, os, sys
# Required for config management



class sboConfWindow(object):
    """The window class"""
    def setupUi(self, SBOwindow):
    # setup
        if not SBOwindow.objectName():
        # checks for a name 
            SBOwindow.setObjectName(u"SBOwindow")
            # sets the name
        SBOwindow.setMinimumSize(500, 350)
        # sets the minimum window size 
        self.window = SBOwindow
        # stores a reference in self to the actual window (so that it can be closed later)

        self.main = QWidget(SBOwindow)
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
        self.configPath = os.path.join(self.configFolderPath, "sboConfig.json")
        # stores the config file's path
        self.ownPath = os.path.join(self.mainFolder, "runtime", "Qt", "sboWindow", "sboWindow.exe")
        # stores the configuration window path

        self.window.setWindowIcon(QIcon(self.mainIcon))
        # the window icon

        self.window.setWindowTitle("SBO Visual Configuration")
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
                    "artistPrefix": "by",
                    "albumPrefix": "",
                    "titleColor": "ffffff",
                    "artistColor": "ffffff",
                    "albumColor": "ffffff",
                    "borderColors": "ff0000, 00ff00, 0000ff",
                    "progressColor": "1ED760",
                    "progressPauseColor": "FF2C00",
                    "playerXaxis": 0,
                    "playerYaxis": 0
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

        self.centralWidget = QWidget(SBOwindow)
        # the main, central widget
        self.centralWidget.setObjectName("centralWidget")
        # sets name

        self.playerSizeValidator = QIntValidator(-10000, 10000)
        # an integer validator that ranges from -10,000 to 10,000 (player should never exceed these sizes???)



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

        self.mainLayout.addLayout(self.optionLayout, 1, 0)
        # adds the option layout into main



    ### Inform Prompt ###

        self.informPrompt = QLabel("Configure overlay visuals\nHover any option for more information\nClick the color boxes to pick a color")
        # user inform prompt
        self.informPrompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text
        self.informPrompt.setToolTip("Be warned, hitting Cancel in the color picker uses the last selected color in the picker window")
        # tooltip

        self.informLayout.addWidget(self.informPrompt, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to layout

    ### Artist Prefix ###

        self.artistPrefixLabel = QLabel("Artist Prefix")
        # label for the artist prefix
        self.artistPrefixLabel.setToolTip("What text should be placed before the artist name\nDefault: by")
        # tooltip

        self.artistPrefixLine = QLineEdit()
        # line edit for the artist prefix
        self.artistPrefixLine.setText(self.loadedConfig.get("artistPrefix", "by"))
        # sets the text based on the config (defaults to "by")
        self.artistPrefixLine.setFixedWidth(100)
        # sets a fixed width 

        self.optionLayout.addWidget(self.artistPrefixLabel, 0, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.artistPrefixLine, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Album Prefix ###

        self.albumPrefixLabel = QLabel("Album Prefix")
        # label for the refresh timer
        self.albumPrefixLabel.setToolTip("What text should be placed before the album name\nDefault: (nothing)")
        # tooltip

        self.albumPrefixLine = QLineEdit()
        # line edit for the album prefix
        self.albumPrefixLine.setText(self.loadedConfig.get("albumPrefix", ""))
        # sets the text based on the config (defaults to "")
        self.albumPrefixLine.setFixedWidth(100)
        # sets a fixed width 

        self.optionLayout.addWidget(self.albumPrefixLabel, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.albumPrefixLine, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Title Color ###

        self.titleColorLabel = QLabel("Song Name Color")
        # label for the update printing
        self.titleColorLabel.setToolTip("What color the song name should be\nAccepts any hexadecimal color code(s), comma-separated\nDefault: ffffff (white)")
        # tooltip

        self.titleColorLine = QLineEdit()
        self.titleColorLine.setText(f"{self.loadedConfig.get("titleColor", "ffffff")}")
        # sets the text based on the config (defaults to "ffffff")
        self.titleColorLine.setFixedWidth(175)
        # sets a fixed width 

        self.titleColorButton = QPushButton()
        # pick color button for paused progress bar
        self.titleColorButton.setFixedSize(24, 24)
        self.titleColorButton.setStyleSheet(f"background-color: #{self.titleColorLine.text().strip()};")
        self.titleColorButton.clicked.connect(lambda: self.colorPick(self.titleColorLine.text().strip(), self.titleColorLine, self.titleColorButton))
        # connects the button to the function

        self.optionLayout.addWidget(self.titleColorLabel, 2, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.titleColorLine, 2, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.optionLayout.addWidget(self.titleColorButton, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds all to the layout

    ### Artist Color ###

        self.artistColorLabel = QLabel("Artist Name Color")
        # label for the error printing
        self.artistColorLabel.setToolTip("What color the artist name should be\nAccepts any hexadecimal color code(s), comma-separated\nDefault: ffffff (white)")
        # tooltip

        self.artistColorLine = QLineEdit()
        self.artistColorLine.setText(f"{self.loadedConfig.get("artistColor", "ffffff")}")
        # sets the text based on the config (defaults to "ffffff")
        self.artistColorLine.setFixedWidth(175)
        # sets a fixed width 

        self.artistColorButton = QPushButton()
        # pick color button for paused progress bar
        self.artistColorButton.setFixedSize(24, 24)
        self.artistColorButton.setStyleSheet(f"background-color: #{self.artistColorLine.text().strip()};")
        self.artistColorButton.clicked.connect(lambda: self.colorPick(self.artistColorLine.text().strip(), self.artistColorLine, self.artistColorButton))
        # connects the button to the function

        self.optionLayout.addWidget(self.artistColorLabel, 3, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.artistColorLine, 3, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.optionLayout.addWidget(self.artistColorButton, 3, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds all to the layout

    ### Album Color ###

        self.albumColorLabel = QLabel("Album Name Color")
        # label for the error printing
        self.albumColorLabel.setToolTip("What color the album name should be\nAccepts any hexadecimal color code(s), comma-separated\nDefault: ffffff (white)")
        # tooltip

        self.albumColorLine = QLineEdit()
        self.albumColorLine.setText(f"{self.loadedConfig.get("artistColor", "ffffff")}")
        # sets the text based on the config (defaults to "ffffff")
        self.albumColorLine.setFixedWidth(175)
        # sets a fixed width 

        self.albumColorButton = QPushButton()
        # pick color button for paused progress bar
        self.albumColorButton.setFixedSize(24, 24)
        self.albumColorButton.setStyleSheet(f"background-color: #{self.albumColorLine.text().strip()};")
        self.albumColorButton.clicked.connect(lambda: self.colorPick(self.albumColorLine.text().strip(), self.albumColorLine, self.albumColorButton))
        # connects the button to the function

        self.optionLayout.addWidget(self.albumColorLabel, 4, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.albumColorLine, 4, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.optionLayout.addWidget(self.albumColorButton, 4, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds all to the layout

    ### Overlay Border Color ###

        self.borderColorLabel = QLabel("Overlay Border Color")
        # label for config window disabling
        self.borderColorLabel.setToolTip("What color the overlay border should be\nAccepts any hexadecimal color code(s), comma-separated\nDefault: ff0000, 00ff00, 0000ff (red, green, blue)")
        # tooltip

        self.borderColorLine = QLineEdit()
        self.borderColorLine.setText(self.loadedConfig.get("borderColors", "ff0000, 00ff00, 0000ff"))
        # sets the text based on the config (defaults to "ff0000, 00ff00, 0000ff")
        self.borderColorLine.setFixedWidth(175)
        # sets a fixed width 
    
        self.borderColorButton = QPushButton()
        # pick color button for paused progress bar
        self.borderColorButton.setFixedSize(24, 24)
        self.borderColorButton.setStyleSheet(f"background-color: #{self.borderColorLine.text().strip()};")
        self.borderColorButton.clicked.connect(lambda: self.colorPick(self.borderColorLine.text().strip(), self.borderColorLine, self.borderColorButton))
        # connects the button to the function

        self.optionLayout.addWidget(self.borderColorLabel, 5, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.borderColorLine, 5, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.optionLayout.addWidget(self.borderColorButton, 5, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to the layout

    ### Progress Bar Color ###

        self.progressColorLabel = QLabel("Progress Bar Color")
        # label for console length
        self.progressColorLabel.setToolTip("What color the progress bar should be\nAccepts any hexadecimal color code(s), comma-separated\nDefault: 1ED760 (Spotify Green)")
        # tooltip

        self.progressColorLine = QLineEdit()
        self.progressColorLine.setText(self.loadedConfig.get("progressColor", "1ED760"))
        # sets the text based on the config (defaults to "1ED760")
        self.progressColorLine.setFixedWidth(175)
        # sets a fixed width 

        self.progressColorButton = QPushButton()
        # pick color button for paused progress bar
        self.progressColorButton.setFixedSize(24, 24)
        self.progressColorButton.setStyleSheet(f"background-color: #{self.progressColorLine.text().strip()};")
        self.progressColorButton.clicked.connect(lambda: self.colorPick(self.progressColorLine.text().strip(), self.progressColorLine, self.progressColorButton))
        # connects the button to the function

        self.optionLayout.addWidget(self.progressColorLabel, 6, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.progressColorLine, 6, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.optionLayout.addWidget(self.progressColorButton, 6, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds all to layout

    ### Progress Bar (Paused) Color ###

        self.progressPauseColorLabel = QLabel("Paused Progress Bar Color")
        # label for console length
        self.progressPauseColorLabel.setToolTip("What color the progress bar should be when paused\nAccepts any hexadecimal color code(s), comma-separated\nDefault: FF2C00 (red)")
        # tooltip

        self.progressPauseColorLine = QLineEdit()
        self.progressPauseColorLine.setText(self.loadedConfig.get("progressPauseColor", "FF2C00"))
        # sets the text based on the config (defaults to "FF2C00")
        self.progressPauseColorLine.setFixedWidth(175)
        # sets a fixed width 

        self.progressPauseColorButton = QPushButton()
        # pick color button for paused progress bar
        self.progressPauseColorButton.setFixedSize(24, 24)
        self.progressPauseColorButton.setStyleSheet(f"background-color: #{self.progressPauseColorLine.text().strip()};")
        self.progressPauseColorButton.clicked.connect(lambda: self.colorPick(self.progressPauseColorLine.text().strip(), self.progressPauseColorLine, self.progressPauseColorButton))
        # connects the button to the function

        self.optionLayout.addWidget(self.progressPauseColorLabel, 7, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.progressPauseColorLine, 7, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.optionLayout.addWidget(self.progressPauseColorButton, 7, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # adds all to layout

    ### Player X-axis Modifier ###

        self.playerXaxisLabel = QLabel("Overlay Width Modifier")
        # label for overlay width modifier
        self.playerXaxisLabel.setToolTip("The number of pixels to add to the player width when constructing\nCan be positive or negative\nDefault: 0 (player width approx. 454 pixels)")
        # tooltip

        self.playerXaxisLine = QLineEdit()
        self.playerXaxisLine.setValidator(self.playerSizeValidator)
        # sets validator to -10k, 10k
        self.playerXaxisLine.setText(f"{self.loadedConfig.get("playerXaxis", 0)}")
        # lineedit for xaxis modifier
        self.playerXaxisLine.setFixedSize(50, 30)
        # sets a fixed size

        self.optionLayout.addWidget(self.playerXaxisLabel, 8, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.playerXaxisLine, 8, 1, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout

    ### Player Y-axis Modifier ###

        self.playerYaxisLabel = QLabel("Overlay Height Modifier")
        # label for overlay height modifier
        self.playerYaxisLabel.setToolTip("The number of pixels to add to the player height when constructing\nCan be positive or negative\nDefault: 0 (player height approx. 124 pixels without SHAA, 154 with SHAA)")
        # tooltip

        self.playerYaxisLine = QLineEdit()
        self.playerYaxisLine.setValidator(self.playerSizeValidator)
        # sets validator to -10k, 10k
        self.playerYaxisLine.setText(f"{self.loadedConfig.get("playerYaxis", 0)}")
        # lineedit for yaxis modifier
        self.playerYaxisLine.setFixedSize(50, 30)
        # sets a fixed size

        self.optionLayout.addWidget(self.playerYaxisLabel, 9, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.optionLayout.addWidget(self.playerYaxisLine, 9, 1, alignment=Qt.AlignmentFlag.AlignRight)
        # adds both to layout



    ### Buttons ###

        self.buttonLayout = QGridLayout()
        # makes a button layout
        self.buttonLayout.setVerticalSpacing(15)
        # sets spacing

        self.mainLayout.addLayout(self.buttonLayout, 2, 0)
        # adds the layout to main (row 2, under the options), spans across both columns (0,1)

        self.saveCloseButton = QPushButton("Save and close\nEnsure you press this to save the config!")
        # a button to close and start SBO
        self.saveCloseButton.setToolTip("Saves and closes this configuration window")
        # tooltip
        self.saveCloseButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.buttonLayout.addWidget(self.saveCloseButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the layout

        self.saveCloseButton.clicked.connect(self.writeConfig)
        # connects the SBO start button to the config write + exit

    ### Central Widget ###

        SBOwindow.setCentralWidget(self.centralWidget)
        # sets central widget

### Color Picker ###

    def colorPick(self, previousColor:str, qLine:QLineEdit, qButton:QPushButton):
        """Function to run the color picker window"""

        colorDialog = QColorDialog(QColor(f"#{previousColor}"))
        # creates a color dialog window to pick a color (passes the previous color with the # added)

        if colorDialog.exec() == QDialog.DialogCode.Accepted:
        # runs the window, checks for 'result' (how the window was closed)
            pickedColor = colorDialog.selectedColor().name().lstrip("#")
            # grabs the color (# removed), if user pressed ok
        else:
        # if user pressed anything but ok (cancel, closed window)
            return
            # stops

        qLine.setText(pickedColor)
        # updates the text field to the color name (eg. ffee33)
        qButton.setStyleSheet(f"background-color: #{pickedColor};")
        # updates the button to match the color

### Config Write ###

    def writeConfig(self):
        """Function to write the config json file (and exit)"""

        self.informPrompt.setText("Saving configuration...")
        # user inform

        configuration = {
            "artistPrefix": self.artistPrefixLine.text().strip(),
            "albumPrefix": self.albumPrefixLine.text().strip(),
            "titleColor": self.titleColorLine.text().strip(),
            "artistColor": self.artistColorLine.text().strip(),
            "albumColor": self.albumColorLine.text().strip(),
            "borderColors": self.borderColorLine.text().strip(),
            "progressColor": self.progressColorLine.text().strip(),
            "progressPauseColor": self.progressPauseColorLine.text().strip(),
            "playerXaxis": int(self.playerXaxisLine.text().strip()),
            "playerYaxis": int(self.playerYaxisLine.text().strip())
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

    sboCfgWin = QMainWindow()
    # creates a window
    ui = sboConfWindow()
    # takes the UI class
    ui.setupUi(sboCfgWin)
    # "populates" the UI class

    sboCfgWin.show()
    # displays the window

    sys.exit(app.exec())
    # waits for the app to be done, then exits