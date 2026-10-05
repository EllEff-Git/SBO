from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
# Required imports to manage the PyQt window
import json, os, sys
# Required for config management
from pathlib import Path
# Required for font file check


class SBOcfgWindow(QMainWindow):
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
        self.previewHtmlPath = os.path.join(self.mainFolder, "overlayPreview.html")
        # stores the overlay preview html file path
        self.configPath = os.path.join(self.configFolderPath, "sboConfig.json")
        # stores the config file's path
        self.fontFolderPath = os.path.join(self.configFolderPath, "fonts")
        #The folder path that should contain any font files

        self.setFixedSize(500, 700)
        # sets the window size
        self.setWindowIcon(QIcon(self.mainIcon))
        # the window icon
        self.setWindowTitle("SBO Visual Configuration")
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
                    "titleColor": "#ffffff",
                    "artistColor": "#ffffff",
                    "albumColor": "#ffffff",
                    "borderColors": "#ff0000, #00ff00, #0000ff",
                    "progressColor": "#1ED760",
                    "progressPauseColor": "#FF2C00",
                    "playerXaxis": 0,
                    "playerYaxis": 0,
                    "overlayFont": "Segoe UI",
                    "overlayFontSizes": {"title": 19, "fields": 14, "timer": 11},
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

        self.playerSizeValidator = QIntValidator(-10000, 10000)
        # an integer validator that ranges from -10,000 to 10,000 (player should never exceed these sizes???)

        self.fontList = sorted(file for file in os.listdir(self.fontFolderPath) if Path(file).suffix.lower() in (".ttf", ".otf", ".woff", ".woff2"))
        # only grabs files in the folder that end in .ttf or .otf, ensures it's sorted (alphabetically)
        self.fontOptions = [
            "Segoe UI", "Arial", "Calibri", "Cambria",
            "Candara", "Consolas", "Constantia", "Corbel",
            "Courier New", "Franklin Gothic Medium", "Georgia", "Tahoma",
            "Impact", "Lucida Console", "Lucida Sans", "Palatino Linotype",
            "Segoe Print", "Segoe Script", "Times New Roman", 
            "Trebuchet MS", "Verdana", "Yu Gothic"
        ]
        # a list of all the options to use for fonts
        self.fontOptions.extend(self.fontList)
        # adds the custom fonts to the options, too

        self.selectedFont = self.loadedConfig.get("overlayFont", "Segoe UI")
        # grabs the selected font via config, fallback to Segoe UI
        self.fontOptions.remove(self.selectedFont)
        # removes the selected font from the list of font options (so there's no duplicate)



    ### Main Layout ###
    
        self.mainWidget = QWidget(self)
        # the main, central widget

        self.mainLayout = QGridLayout(self.mainWidget)
        # sets the main layout to use a grid of the central
        self.mainLayout.setContentsMargins(25, 25, 25, 25)
        # sets margins of 25px 
        self.mainLayout.setVerticalSpacing(25)
        # sets vertical spacing

    ### Option Layout ###

        self.optionLayout = QGridLayout()
        # adds a grid layout for the options
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
        self.informPrompt.setToolTip("Remember to press 'Refresh Overlay' to update this window's configurations")
        # tooltip

        self.mainLayout.addWidget(self.informPrompt, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
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
        self.titleColorLine.setText(f"{self.loadedConfig.get("titleColor", "#ffffff")}")
        # sets the text based on the config (defaults to "ffffff")
        self.titleColorLine.setFixedWidth(175)
        # sets a fixed width

        self.titleColorButton = QPushButton()
        # pick color button for paused progress bar
        self.titleColorButton.setFixedSize(24, 24)
        self.titleColorButton.setStyleSheet(f"background-color: {self.titleColorLine.text().strip()};")
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
        self.artistColorLine.setText(f"{self.loadedConfig.get("artistColor", "#ffffff")}")
        # sets the text based on the config (defaults to "ffffff")
        self.artistColorLine.setFixedWidth(175)
        # sets a fixed width

        self.artistColorButton = QPushButton()
        # pick color button for paused progress bar
        self.artistColorButton.setFixedSize(24, 24)
        self.artistColorButton.setStyleSheet(f"background-color: {self.artistColorLine.text().strip()};")
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
        self.albumColorLine.setText(f"{self.loadedConfig.get("albumColor", "#ffffff")}")
        # sets the text based on the config (defaults to "ffffff")
        self.albumColorLine.setFixedWidth(175)
        # sets a fixed width

        self.albumColorButton = QPushButton()
        # pick color button for paused progress bar
        self.albumColorButton.setFixedSize(24, 24)
        self.albumColorButton.setStyleSheet(f"background-color: {self.albumColorLine.text().strip()};")
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
        self.borderColorLine.setText(self.loadedConfig.get("borderColors", "#ff0000, #00ff00, #0000ff"))
        # sets the text based on the config (defaults to "#ff0000, #00ff00, #0000ff")
        self.borderColorLine.setFixedWidth(175)
        # sets a fixed width

        self.borderColorButton = QPushButton()
        # pick color button for paused progress bar
        self.borderColorButton.setFixedSize(24, 24)
        self.borderColorButton.setStyleSheet(f"background-color: {self.borderColorLine.text().strip()};")
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
        self.progressColorLine.setText(self.loadedConfig.get("progressColor", "#1ED760"))
        # sets the text based on the config (defaults to "1ED760")
        self.progressColorLine.setFixedWidth(175)
        # sets a fixed width

        self.progressColorButton = QPushButton()
        # pick color button for paused progress bar
        self.progressColorButton.setFixedSize(24, 24)
        self.progressColorButton.setStyleSheet(f"background-color: {self.progressColorLine.text().strip()};")
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
        self.progressPauseColorLine.setText(self.loadedConfig.get("progressPauseColor", "#FF2C00"))
        # sets the text based on the config (defaults to "FF2C00")
        self.progressPauseColorLine.setFixedWidth(175)
        # sets a fixed width

        self.progressPauseColorButton = QPushButton()
        # pick color button for paused progress bar
        self.progressPauseColorButton.setFixedSize(24, 24)
        self.progressPauseColorButton.setStyleSheet(f"background-color: {self.progressPauseColorLine.text().strip()};")
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

    ### Player Font Swap ###

        self.previewWindow = FontDemoWindow(self)
        # instantiates the demo window
        self.previewWindow.hide()
        # hides by default

    ### Buttons ###

        self.buttonLayout = QGridLayout()
        # makes a button layout
        self.buttonLayout.setVerticalSpacing(15)
        # sets spacing

        self.mainLayout.addLayout(self.buttonLayout, 3, 0)
        # adds the layout to main (row 2, under the options), spans across both columns (0,1)

        self.updatePreviewButton = QPushButton("Refresh Overlay")
        # overlay visual updater
        self.updatePreviewButton.setToolTip("Refresh the overlay with the configured details")
        # tooltip
        self.updatePreviewButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.openPreviewButton = QPushButton("Modify Overlay")
        # font window opener
        self.openPreviewButton.setToolTip("Open the overlay preview window to visualise changes and edit appearance")
        # tooltip
        self.openPreviewButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.saveCloseButton = QPushButton("Save and close\nEnsure you press this to save the config!")
        # a button to close and start SBO
        self.saveCloseButton.setToolTip("Saves and closes this configuration window")
        # tooltip
        self.saveCloseButton.setMinimumSize(240, 45)
        # sets a minimum size

        self.buttonLayout.addWidget(self.updatePreviewButton, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.addWidget(self.openPreviewButton, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.addWidget(self.saveCloseButton, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to the layout

        self.saveCloseButton.clicked.connect(self.writeConfig)
        # connects the SBO start button to the config write + exit
        self.openPreviewButton.clicked.connect(self.previewWindow.previewUpdate)
        # connects the open button to the preview window updater (which also shows the window)
        self.updatePreviewButton.clicked.connect(self.previewWindow.previewUpdate)
        # connects the update button to the preview window updater

    ### Central Widget ###

        self.setCentralWidget(self.mainWidget)
        # sets central widget

### Color Picker ###

    def colorPick(self, previousColor:str, qLine:QLineEdit, qButton:QPushButton):
        """Function to run the color picker window"""

        colorDialog = QColorDialog(QColor(f"{previousColor}"))
        # creates a color dialog window to pick a color (passes the previous color)

        if colorDialog.exec() == QDialog.DialogCode.Accepted:
        # runs the window, checks for 'result' (how the window was closed)
            pickedColor = colorDialog.selectedColor().name()
            # grabs the color (hex code), if user pressed ok
        else:
        # if user pressed anything but ok (cancel, closed window)
            return
            # stops

        qLine.setText(pickedColor)
        # updates the text field to the color name (eg. ffee33)
        qButton.setStyleSheet(f"background-color: {pickedColor};")
        # updates the button to match the color
        self.previewWindow.previewUpdate()
        # calls the preview update to display the change

### Config Write ###

    def writeConfig(self):
        """Function to write the config json file (and exit)"""

        self.informPrompt.setText("Saving configuration...")
        # user inform

        trackSize = self.previewWindow.trackFontSizeBox.value()
        fieldsSize = self.previewWindow.fieldsFontSizeBox.value()
        timerSize = self.previewWindow.timerFontSizeBox.value()
        # gets the value of the font size selectors
        fontSizes = {"track": trackSize, "fields": fieldsSize, "timer": timerSize}
        # forms a dictionary of the sizes
        overlayFont = self.previewWindow.playerFontDropdown.currentText()
        # gets the font name

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
            "playerYaxis": int(self.playerYaxisLine.text().strip()),
            "overlayFont": overlayFont,
            "overlayFontSizes": fontSizes,
            "overlayFontFile": True if overlayFont in self.fontList else False
        }
        # forms a configuration based on the states of each of the fields

        with open(self.configPath, "w", encoding="utf-8") as cfg:
        # opens the config file
            json.dump(configuration, cfg, indent=3)
            # dumps everything in

        self.close()
        # closes the whole process



class FontDemoWindow(QDialog):
    """Window class to show the font preview"""
    def __init__(self, parentWindow: SBOcfgWindow):
    # init
        super().__init__(parent = parentWindow)

        self.parentWindow = parentWindow
        # stores in self

        self.setWindowTitle("Overlay Preview")
        # title
        self.setMinimumSize(800, 550)
        # sizing

        self.windowLayout = QGridLayout()
        # simple layout
        self.setLayout(self.windowLayout)
        # ties the window layout to the window

        self.fontSizes: dict[str, int] = self.parentWindow.loadedConfig.get("overlayFontSizes", {"track": 19, "fields": 14, "timer": 11})
        # dict to keep the font sizes stored
        self.currentFont: str = self.parentWindow.loadedConfig.get("overlayFont", "Segoe UI")
        # string to keep the font stored
        self.artistPrefix = self.parentWindow.loadedConfig.get("artistPrefix", "by")
        # string to keep the artist prefix stored
        self.albumPrefix = self.parentWindow.loadedConfig.get("albumPrefix", "")
        # string to keep the album prefix stored

    ### Title ###

        self.titleLabel = QLabel("Spotify Browser Overlay Visualiser\nNote that animations aren't available in this preview\n"
                                "Long text scrolling and multi-color gradients apply in the actual overlay")
        # title label
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.windowLayout.addWidget(self.titleLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds to main layout

    ### Fonts ###

        self.fontLayout = QGridLayout()
        # simple vertical layout to stack the previews
        self.fontLayout.setContentsMargins(25, 25, 25, 25)
        self.fontLayout.setColumnMinimumWidth(0, 250)
        self.fontLayout.setColumnMinimumWidth(1, 450)
        self.windowLayout.addLayout(self.fontLayout, 1, 0)
        # adds to main layout

        self.fontPreview = QWebEngineView()
        # instantiates a web view
        settings = self.fontPreview.settings()
        # modifies the settings for the 
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        # sets the setting to allow remote URL lookups (required to load the preview images)

        self.fontPreview.setFixedSize(500, 250)
        # min size to occupy
        self.fontPreview.setUrl(QUrl.fromLocalFile(self.parentWindow.previewHtmlPath))
        # loads the html file from path
        self.fontPreview.page().setBackgroundColor(QColor("#1E1E1E"))
        # sets the background color
        self.fontLayout.addWidget(self.fontPreview, 0, 1, 6, 1, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        # adds to layout, spans all 6 rows, right column (centers horizontally and vertically)

    ### Font Sizes ###

        self.trackFontSizeLabel = QLabel("Title Font Size")
        # track font size label

        self.trackFontSizeBox = QSpinBox()
        # a size toggle to change the font size
        self.trackFontSizeBox.setMinimum(10)
        # min font size 10
        self.trackFontSizeBox.setMaximum(40)
        # max font size 40
        self.trackFontSizeBox.setSingleStep(1)
        # one per click
        self.trackFontSizeBox.setValue(self.fontSizes["track"])
        # sets to font size (default: 14)
        self.trackFontSizeBox.valueChanged.connect(lambda: self.fontResizer(self.trackFontSizeBox.value(), "track"))
        # connects the value changing to the font resizer function

        self.fieldsFontSizeLabel = QLabel("Details' Font Size")
        # fields font size label

        self.fieldsFontSizeBox = QSpinBox()
        # a size toggle to change the font size
        self.fieldsFontSizeBox.setMinimum(5)
        # min font size 5
        self.fieldsFontSizeBox.setMaximum(30)
        # max font size 30
        self.fieldsFontSizeBox.setSingleStep(1)
        # one per click
        self.fieldsFontSizeBox.setValue(self.fontSizes["fields"])
        # sets to font size (default: 14)
        self.fieldsFontSizeBox.valueChanged.connect(lambda: self.fontResizer(self.fieldsFontSizeBox.value(), "fields"))
        # connects the value changing to the font resizer function

        self.timerFontSizeLabel = QLabel("Timer Font Size")
        # track font size label

        self.timerFontSizeBox = QSpinBox()
        # a size toggle to change the font size
        self.timerFontSizeBox.setMinimum(10)
        # min font size 10
        self.timerFontSizeBox.setMaximum(30)
        # max font size 30
        self.timerFontSizeBox.setSingleStep(1)
        # one per click
        self.timerFontSizeBox.setValue(self.fontSizes["timer"])
        # sets to font size (default: 14)
        self.timerFontSizeBox.valueChanged.connect(lambda: self.fontResizer(self.timerFontSizeBox.value(), "timer"))
        # connects the value changing to the font resizer function

        self.fontLayout.addWidget(self.trackFontSizeLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.fontLayout.addWidget(self.trackFontSizeBox, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.fontLayout.addWidget(self.fieldsFontSizeLabel, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.fontLayout.addWidget(self.fieldsFontSizeBox, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.fontLayout.addWidget(self.timerFontSizeLabel, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.fontLayout.addWidget(self.timerFontSizeBox, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds all in sequence

    ### Preview Font Fields ###

        self.previewSongSel = {
            "hurt my feelings": {
                "track": "hurt my feelings",
                "artist": "Tate McRae",
                "album": "THINK LATER",
                "shaa": "622 plays x 1,260.6 minutes",
                "timer": "0:38 / 2:02",
                "progress": 31.147,
                "image": "https://i.scdn.co/image/ab67616d0000e1a3c4258b134ff5756932f9c46f"
            },
            "Stressed Out": {
                "track": "Stressed Out",
                "artist": "Twenty One Pilots",
                "album": "Blurryface",
                "shaa": "15,708 plays x 43,467.2 minutes",
                "timer": "1:05 / 3:22",
                "progress": 32.178,
                "image": "https://i.scdn.co/image/ab67616d0000e1a32df0d98a423025032d0db1f7"
            },
            "HIGHEST IN THE ROOM": {
                "track": "HIGHEST IN THE ROOM",
                "artist": "Travis Scott",
                "album":"HIGHEST IN THE ROOM",
                "shaa": "7,639 plays x 20,421.8 minutes",
                "timer": "2:09 / 2:55",
                "progress": 73.714,
                "image": "https://i.scdn.co/image/ab67616d0000e1a3cc7bfe087a97a09f54c92b28"
            },
            "rockstar (feat. 21 Savage)": {
                "track": "rockstar (feat. 21 Savage)",
                "artist": "Post Malone and 21 Savage",
                "album": "beerbongs & bentleys",
                "shaa": "22,593 plays x 61,952.0 minutes",
                "timer": "0:51 / 3:38",
                "progress": 23.394,
                "image": "https://i.scdn.co/image/ab67616d0000e1a3b1c4b76e23414c9f20242268"
            },
            "No Time for Caution": {
                "track": "No Time for Caution",
                "artist": "Hans Zimmer",
                "album": "Interstellar (Original Motion Picture Soundtrack)",
                "shaa": "925 plays x 2,690.4 minutes",
                "timer": "2:46 / 4:06",
                "progress": 67.480,
                "image": "https://i.scdn.co/image/ab67616d0000e1a381f04c407e0ec68e3dea6b2c"
            }
        }
        # dictionary of song names to full song strings/timers

    ### Bottom Layout ###

        self.bottomLayout = QGridLayout()
        # a layout for the bottom elements to sit in
        self.windowLayout.addLayout(self.bottomLayout, 2, 0)
        # adds the layout

        self.previewSongs = list(self.previewSongSel.keys())
        # stores preview track names to swap between to check

        self.previewTrackLabel = QLabel("Preview Track")
        # label to sit above preview track dropdown

        self.previewTrackDropdown = QComboBox()
        # dropdown menu for all the preview tracks
        self.previewTrackDropdown.setFixedSize(200, 40)
        # sets size to prevent random moving
        self.previewTrackDropdown.addItems(self.previewSongs)
        # adds the list of preview options
        self.previewTrackDropdown.currentTextChanged.connect(self.previewSongSwap)
        # swaps the song when swapping dropdown option

        self.shaaVisualLabel = QLabel("Visualise SHAA")
        # label to sit above the SHAA check
        self.shaaVisualLabel.setToolTip("Whether to display the Spotify History Analyser (Addon) numbers\nThis setting requires DSI with SHA numbers to use\n"
                                    "In practice, it adds 30 pixels of height to the overlay to accomodate the extra field")
        # tooltip

        self.shaaVisualCheck = QCheckBox()
        # checkbox for the shaa field
        self.shaaVisualCheck.setChecked(False)
        # starts off as False (expectation is to not have SHAA/DSI)
        self.shaaVisualCheck.checkStateChanged.connect(self.previewUpdate)
        # updates the visuals when swapping between SHAA/non

        self.playerFontLabel = QLabel("Overlay Font")
        # label for overlay font
        self.playerFontLabel.setToolTip("The font the overlay should use\n"
                                        "Installing any font files (.ttf, .otf, .woff, .woff2) will automatically appear here for use\n"
                                        "Note that certain fonts do not support all Spotify track characters (especially for non-Latin tracks)")
        # tooltip

        self.playerFontDropdown = QComboBox()
        # dropdown for the font options
        self.playerFontDropdown.setFixedSize(200, 40)
        # sets size to prevent random moving
        self.playerFontDropdown.addItem(self.parentWindow.selectedFont)
        self.playerFontDropdown.addItems(self.parentWindow.fontOptions)
        # adds the selected item first, then the rest
        self.playerFontDropdown.currentTextChanged.connect(self.fontChanger)
        # if the dropdown changes, connects to the font changer function

        self.closeSpacer = QSpacerItem(50, 40)
        # spacer item to add a little bit of space between the other stuff and the close button (to mitigate accidental closing)

        self.closeDemo = QPushButton("Close Preview")
        # button to close (hide)
        self.closeDemo.setToolTip("Closes the current preview window\nDoes not save!\nEnsure you press the save button in the configuration window!")
        # tooltip
        self.closeDemo.setFixedSize(200, 60)
        # sets size to prevent random moving
        self.closeDemo.clicked.connect(self.hide)
        # hides the window on click

        self.bottomLayout.addWidget(self.previewTrackLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomLayout.addWidget(self.previewTrackDropdown, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # the preview track selection dropdown (left)
        self.bottomLayout.addWidget(self.shaaVisualLabel, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomLayout.addWidget(self.shaaVisualCheck, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        # the shaa check (middle)
        self.bottomLayout.addWidget(self.playerFontLabel, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomLayout.addWidget(self.playerFontDropdown, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        # the font selection dropdown (right)
        self.bottomLayout.addItem(self.closeSpacer, 2, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottomLayout.addWidget(self.closeDemo, 3, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        # the close button

        QTimer.singleShot(0, lambda: self.fontChanger(self.parentWindow.selectedFont))
        # sets the preview font by running the function once
        self.resize(750, 550)
        # sets the window to the "correct" size by default

### Font Change ###

    def fontChanger(self, currentFont:str):
        """Function to swap the preview font/check if custom is in use"""

        if currentFont in self.parentWindow.fontList:
        # if the selected font is in the list of generated font file names (meaning it's a file)
            currentFontPath = Path(os.path.join(self.parentWindow.fontFolderPath, currentFont)).as_uri()
            # forms the path of the font file as URI (easier for js to read)
            self.fontPreview.page().runJavaScript(f'setFont({json.dumps(currentFontPath)});')
            # runs javascript function in the html itself to set the font
        else:
        # not in the list of files, not a custom -> regular, pre-installed font
            self.fontPreview.page().runJavaScript(f'document.body.style.fontFamily = "{currentFont}";')
            # runs javascript function to modify the given element's font family to match the selection
        self.currentFont = currentFont
        # stores in self


### Font Resizer ###

    def fontResizer(self, newSize: int, element: str):
        """Function to resize element fonts in the preview"""

        self.fontSizes[element] = newSize
        # sets the element to match in the stored dict
        if element == "fields":
        # fields = artist, album and SHAA
            self.fontPreview.page().runJavaScript(f'document.getElementById("artist").style.fontSize = "{newSize}px";')
            self.fontPreview.page().runJavaScript(f'document.getElementById("album").style.fontSize = "{newSize}px";')
            self.fontPreview.page().runJavaScript(f'document.getElementById("shaa").style.fontSize = "{newSize}px";')
            # runs js on all 3 field elements
        else:
        # track/timer
            self.fontPreview.page().runJavaScript(f'document.getElementById("{element}").style.fontSize = "{newSize}px";')
            # runs javascript function to modify the given element's fontsize to match the selection

### Preview Swap ###

    def previewSongSwap(self):
        """Function to swap the preview song"""
        currentListElement = self.previewTrackDropdown.currentIndex()
        # gets the index of the dropdown (0-2)
        selectedSong = self.previewSongSel[self.previewSongs[currentListElement]]
        # grabs the full string to use as demo by getting the dict match ("hurt my feelings" -> full string) by getting the index match (0 -> "hurt my feelings")

        self.fontPreview.page().runJavaScript(f'document.getElementById("track").textContent = "{selectedSong["track"]}";')
        self.fontPreview.page().runJavaScript(f'document.getElementById("shaa").textContent = "{selectedSong["shaa"]}";')
        self.fontPreview.page().runJavaScript(f'document.getElementById("timer").textContent = "{selectedSong["timer"]}";')
        # swaps to match the selected track's texts

        artistText = f"{self.artistPrefix} {selectedSong["artist"]}".strip()
        albumText = f"{self.albumPrefix} {selectedSong["album"]}".strip()
        # pre-forms the texts first (constructs as f-strings and strips so that if the prefix is empty, there won't be empty space)
        self.fontPreview.page().runJavaScript(f'document.getElementById("artist").textContent = "{str(artistText)}";')
        self.fontPreview.page().runJavaScript(f'document.getElementById("album").textContent = "{str(albumText)}";')
        # dumps them with json (something something things went boom without)

        self.fontPreview.page().runJavaScript(f'document.getElementById("cover").src = "{selectedSong["image"]}";')
        self.fontPreview.page().runJavaScript(f'document.getElementById("backgroundCover").src = "{selectedSong["image"]}";')
        # swaps to match the selected track's images

        progressText = f"{selectedSong["progress"]}%"
        # pre-forms the progress percentage to use as bar width
        self.fontPreview.page().runJavaScript(f'document.getElementById("bar").style.width = "{progressText}";')
        # moves the progress bar to match, too

### Hex String -> CSS ###

    def stringToCSS(self, hexString: str, fallback: str):
        """Function to form CSS-complient element variables"""

        if not hexString or len(hexString) < 7:
        # if the hex string isn't defined or it's less than 7 characters long (# + 6 letters/numbers)
            hexString = fallback
            # uses the fallback hex code passed instead (known good)

        colors = [color.strip() for color in hexString.split(",")]
        # makes a list of the passed hex string (or list of hex strings)

        if len(colors) == 1:
        # if there's only 1 color
            return colors[0]
            # returns that single color (0th list element)

        return f"linear-gradient(90deg, {', '.join(colors)})"
        # more than 1 color -> forms a gradient background element by joining the colors again

### Preview Update ###

    def previewUpdate(self):
        """Function to update the config window-defined visuals"""

        self.show()
        # displays the window (since it can be called from open + modifying the preview without being sure it's visible is kind of dumb?)

        widthMod = self.parentWindow.playerXaxisLine.text().strip()
        heightMod = self.parentWindow.playerYaxisLine.text().strip()
        # pre-grabs the modfiers (they can't be letters, but they can be empty, need to get checked)

        try:
            widthMod = int(widthMod)
        except:
            widthMod = 0

        try:
            heightMod = int(heightMod)
        except:
            heightMod = 0
        # there's a few cases where it can go boom (input is "+", "-" or nothing), this tries to ensure it either gets turned into an integer nicely, or gets reset

        config = {
            "trackColor": self.stringToCSS(self.parentWindow.titleColorLine.text().strip(), self.parentWindow.loadedConfig.get("titleColor", "#ffffff")),
            "artistColor": self.stringToCSS(self.parentWindow.artistColorLine.text().strip(), self.parentWindow.loadedConfig.get("artistColor", "#ffffff")),
            "albumColor": self.stringToCSS(self.parentWindow.albumColorLine.text().strip(), self.parentWindow.loadedConfig.get("albumColor", "#ffffff")),
            "borderColor": self.stringToCSS(self.parentWindow.borderColorLine.text().strip(), self.parentWindow.loadedConfig.get("borderColors", "#ff0000, #00ff00, #0000ff")),
            "progressColor": self.stringToCSS(self.parentWindow.progressColorLine.text().strip(), self.parentWindow.loadedConfig.get("progressColor", "#1ED760")),
            "widthMod": widthMod,
            "heightMod": heightMod,
            "shaaCompat": self.shaaVisualCheck.isChecked()
        }
        # forms a config dictionary from the visual configuration window's fields

        self.artistPrefix = self.parentWindow.artistPrefixLine.text().strip()
        self.albumPrefix = self.parentWindow.albumPrefixLine.text().strip()
        # grabs the visual prefixes

        self.fontPreview.page().runJavaScript(f"updatePreview({json.dumps(config)});")
        # runs a javascript function to send the config to the html file
        self.previewSongSwap()
        # runs the preview song swap, too, to check the prefixes

### Starter ###

if __name__ == "__main__":
# runs at start

    app = QApplication(sys.argv)
    # creates a Qt Application

    sboCfgWin = SBOcfgWindow()
    # instantiates the window class
    sboCfgWin.show()
    # displays the window

    sys.exit(app.exec())
    # waits for the app to be done, then exits