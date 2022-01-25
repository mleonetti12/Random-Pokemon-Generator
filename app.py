# Random Pokemon Generator
# Maxwell Leonetti mleonetti12
# 1/20/2022

import sys
from PyQt6.QtCore import Qt, QSize, QFile, QTextStream
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QGridLayout, 
    QDateEdit,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtGui import (
    QPalette, 
    QColor, 
    QPixmap,
    QIcon,
    QImage, 
    QFont,
    QFontDatabase,
)
import random
from itertools import groupby
import datetime
import requests

# choose selections from data with weight weightNum
def weightedChoice(numSelections, data, weightNum):
    selections = []
    while(numSelections > 0):
        selection = data[weightNum % len(data)]
        selections.append(selection)
        data.remove(selection)
        numSelections-=1
    return selections

# convert input data into a num of length 50 to pass into data retrieval
def generate(name, seed, date, region="None"):
    if name: # if name and date inputs
        converted = ""
        for char in name:
            converted += str(ord(char))
        stringDate = date.strftime("%m%d%Y")
        inString = converted + stringDate
        inString = inString.ljust(50, '0')
    elif seed: # if gen based on seed instead
        converted = ""
        for char in seed:
            converted += str(ord(char))
        inString = converted.ljust(50, '0')
    else: # random gen
        inList = random.sample(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], 
            counts=[50, 50, 50, 50, 50, 50 ,50, 50 , 50, 50], k=50)
        inString = ''.join(str(e) for e in inList)
    return retrieveData(int(inString), region.lower())

# take preNum len 50 and hash it to a length of 7
# use this hash to index a dex number, shiny status, moves, and ability
# in the range of the specified region, any if none
def retrieveData(preNum, region):
    hashNum = pow(preNum, 2) % 3576667
    ranges = {'kanto': [151, 0], 'johto': [100, 151], 'hoenn': [135, 251], 'sinnoh': [107, 386], 'unova': [156, 493], 'kalos': [72, 649], 'alola': [88, 721], 'galar': [89, 809], 'none': [898, 0]}
    dexNum = (hashNum % ranges[region][0]) + ranges[region][1] + 1

    # make shiny if triple repeating nums
    groups = groupby(str(hashNum))
    result = [(label, sum(1 for _ in group)) for label, group in groups] # https://stackoverflow.com/questions/34443946/count-consecutive-characters
    shiny = False
    for num, count in result:
        if count >= 3:
            shiny = True

    # retrieve data from pokeapi
    url = "https://pokeapi.co/api/v2/pokemon-species/" + str(dexNum) + "/"
    res = requests.get(url)
    forms = res.json()["varieties"]
    form = hashNum % len(forms)
    name = forms[form]["pokemon"]["name"]

    # subdata need seperate request, cannot query info based on dex num
    supUrl = "https://pokeapi.co/api/v2/pokemon/" + name
    supRes = requests.get(supUrl)

    abilities = supRes.json()["abilities"]
    selectedAbility = weightedChoice(1, abilities, hashNum)
    ability = selectedAbility[0]["ability"]["name"]

    moves = supRes.json()["moves"]
    i = 4 if len(moves) >= 4 else len(moves)
    selectedMoves = weightedChoice(i, moves, hashNum)
    returnMoves = []
    for move in selectedMoves:
        returnMoves.append(move["move"]["name"])

    typeInput = supRes.json()["types"]
    types = [typeInput[0]["type"]["name"]]
    if len(typeInput) == 2: types.append(typeInput[1]["type"]["name"])

    sprites = supRes.json()["sprites"]
    if (shiny):
        sprite = sprites["front_shiny"]
    else:
        sprite = sprites["front_default"]

    if sprite:
        imageData = requests.get(sprite).content
    else:
        imageData = None

    return (name, ability, returnMoves, imageData, types)

# main app window
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # setup custom font
        fontID = QFontDatabase.addApplicationFont("pokemon-b-w.ttf")
        families = QFontDatabase.applicationFontFamilies(fontID)

        self.setObjectName('MainWindow')
        self.setWindowIcon(QIcon('icon.png'))
        self.setWindowTitle("Random Pokemon Generator")
        self.setFixedSize(QSize(510, 380))

        # set main layout of app window
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setVerticalSpacing(0)

        # set layout of pokemon display section
        pokemonLayout = QVBoxLayout()
        pokemonLayout.setSpacing(0)
        pokemonLayout.setContentsMargins(4, 0, 4, 0)
        pokemonFrame = QFrame()
        pokemonFrame.setFixedSize(240, 350)
        pokemonFrame.setLayout(pokemonLayout)
        layout.addWidget(pokemonFrame, 0, 0)

        # set layout for the pkmn name and type icon inside pokemon display
        nameiconLayout = QHBoxLayout()
        nameiconLayout.setContentsMargins(0, 0, 0, 60)
        nameiconLayout.setSpacing(0)
        nameiconFrame = QFrame()
        nameiconFrame.setObjectName('nameiconFrame')
        nameiconFrame.setFixedHeight(40)
        nameiconFrame.setLayout(nameiconLayout)
        pokemonLayout.addWidget(nameiconFrame)

        # add widget to display pkmn name
        self.nameDisp = QLabel("")
        self.nameDisp.setFixedHeight(40)
        self.nameDisp.setFont(QFont(families[0], 15))
        nameiconLayout.addWidget(self.nameDisp)

        # widget and layout to display type icons
        typeIcons = QFrame()
        typeIcons.setObjectName("typeIcons")
        typeIcons.setFixedSize(50, 30)
        typeLayout = QHBoxLayout()
        typeLayout.setContentsMargins(0, 6, 0, 0)
        typeLayout.setSpacing(3)
        typeIcons.setLayout(typeLayout)
        self.typeIcon0 = QLabel()
        self.typeIcon1 = QLabel()
        typeLayout.addWidget(self.typeIcon1)
        typeLayout.addWidget(self.typeIcon0)
        nameiconLayout.addWidget(typeIcons)
        self.typesRef = [self.typeIcon0, self.typeIcon1]

        # widget to display pokemon sprite
        self.imageDisp = QLabel()
        self.imageDisp.setPixmap(QPixmap('pkball.png').scaled(150, 150))
        self.imageDisp.setObjectName('imageDisp')
        self.imageDisp.setFixedSize(170, 170)
        self.imageDisp.setContentsMargins(15, 0, 0, 10)
        pokemonLayout.addWidget(self.imageDisp, Qt.AlignmentFlag.AlignCenter)

        # layout and widgets to display ability
        abilityLayout = QHBoxLayout()
        abilityLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.abilityDisp = QLabel("")
        self.abilityDisp.setFixedHeight(25)
        self.abilityDisp.setVisible(False) 
        self.abilityDisp.setObjectName('abilityDisp')
        self.abilityDisp.setFont(QFont(families[0], 15))
        abilityLayout.addWidget(self.abilityDisp)
        abilityLayout.addStretch()
        pokemonLayout.addLayout(abilityLayout)

        # layout to display grid of moves
        moveLayout = QGridLayout()
        moveLayout.setContentsMargins(10, 15, 2, 25)
        moveLayout.setSpacing(10)
        pokemonLayout.addLayout(moveLayout)

        # widgets to display each selected move
        policy = QSizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.skillDisp0 = QLabel("")
        self.skillDisp0.setFixedHeight(25)
        self.skillDisp0.setSizePolicy(policy)
        self.skillDisp0.setVisible(False) 
        self.skillDisp0.setObjectName('skillDisp')
        self.skillDisp0.setFont(QFont(families[0], 14))
        moveLayout.addWidget(self.skillDisp0, 0, 0)
        self.skillDisp1 = QLabel("")
        self.skillDisp1.setFixedHeight(25)
        self.skillDisp1.setSizePolicy(policy)
        self.skillDisp1.setVisible(False) 
        self.skillDisp1.setObjectName('skillDisp')
        self.skillDisp1.setFont(QFont(families[0], 14))
        moveLayout.addWidget(self.skillDisp1, 0, 1)
        self.skillDisp2 = QLabel("")
        self.skillDisp2.setFixedHeight(25)
        self.skillDisp2.setSizePolicy(policy)
        self.skillDisp2.setVisible(False) 
        self.skillDisp2.setObjectName('skillDisp')
        self.skillDisp2.setFont(QFont(families[0], 14))
        moveLayout.addWidget(self.skillDisp2, 1, 0)
        self.skillDisp3 = QLabel("")
        self.skillDisp3.setFixedHeight(25)
        self.skillDisp3.setSizePolicy(policy)
        self.skillDisp3.setVisible(False) 
        self.skillDisp3.setObjectName('skillDisp')
        self.skillDisp3.setFont(QFont(families[0], 14))
        moveLayout.addWidget(self.skillDisp3, 1, 1)
        self.movesRef = [self.skillDisp0, self.skillDisp1, self.skillDisp2, self.skillDisp3]

        # layout and widget to display title of app inside input layout
        titleLayout = QHBoxLayout()
        self.title = QLabel("Random Pokemon Generator")
        self.title.setFont(QFont(families[0], 18))
        self.title.setObjectName('title')
        self.title.setFixedHeight(40)
        self.title.setContentsMargins(0, 0, 0, 0)
        self.icon = QLabel()
        self.icon.setContentsMargins(0, 0, 0, 2)
        self.icon.setPixmap(QPixmap("icon.png").scaled(30, 30))
        titleLayout.setSpacing(7)
        titleLayout.addWidget(self.title)
        titleLayout.addWidget(self.icon)
        titleLayout.setContentsMargins(0, 0, 0, 20)

        # layout for all inputs and title
        inputLayout = QVBoxLayout()
        inputLayout.setSpacing(10)
        inputLayout.setContentsMargins(20, 0, 0, 40)
        inputLayout.addLayout(titleLayout)

        layout.addLayout(inputLayout, 0, 1, 1, 2)

        # add widget for inputting name
        self.nameInput = QLineEdit()
        self.nameInput.setFixedSize(240, 30)
        self.nameInput.setFont(QFont(families[0], 14))
        self.nameInput.setMaxLength(20)
        self.nameInput.setPlaceholderText("Enter your name (max 20 characters)")
        inputLayout.addWidget(self.nameInput)

        # add widget + layout for inputting birthday/date
        dateLayout = QHBoxLayout()
        dateLayout.setContentsMargins(0, 0, 0, 0)
        dateLayout.setSpacing(10)
        inputLayout.addLayout(dateLayout)
        self.bdayInput = QDateEdit()
        self.bdayInput.setFixedSize(90, 30)
        self.bdayInput.setFont(QFont(families[0], 15))
        dateLayout.addWidget(self.bdayInput)
        bdayLabel = QLabel("Enter your birthday")
        bdayLabel.setObjectName('bdayLabel')
        bdayLabel.setFont(QFont(families[0], 15))
        dateLayout.addWidget(bdayLabel)

        # add region select box to inputs
        self.regionSelect = QComboBox()
        self.regionSelect.setFixedSize(150, 30)
        self.regionSelect.setFont(QFont(families[0], 14))
        self.regionSelect.setPlaceholderText("Region")
        self.regionSelect.addItems(['Kanto', 'Johto', 'Hoenn', 'Sinnoh', 'Unova', 'Kalos', 'Alola', 'Galar', 'None'])
        inputLayout.addWidget(self.regionSelect)

        # checkbox to gen on seed only
        self.seedCheck = QCheckBox("Generate based on seed only")
        self.seedCheck.setFont(QFont(families[0], 14))
        self.seedCheck.stateChanged.connect(self.seedToggle)
        inputLayout.addWidget(self.seedCheck)

        # seed input box
        self.seedInput = QLineEdit()
        self.seedInput.setFont(QFont(families[0], 14))
        self.seedInput.setMaxLength(5)
        self.seedInput.setFixedSize(220, 30)
        self.seedInput.setPlaceholderText("Enter a seed (max 5 characters)")
        inputLayout.addWidget(self.seedInput)

        # checkbox to ignore all inputs and gen random
        self.ignoreCheck = QCheckBox("Ignore inputs and generate random")
        self.ignoreCheck.setFont(QFont(families[0], 14))
        self.ignoreCheck.stateChanged.connect(self.ignoreToggle)
        inputLayout.addWidget(self.ignoreCheck)

        # button to generate pkmn based on inputs
        buttonLayout = QHBoxLayout()
        self.genButton = QPushButton("Generate!")
        self.genButton.setFixedSize(90, 30)
        self.genButton.setFont(QFont(families[0], 15))
        # call this fcn when button is clicked
        self.genButton.clicked.connect(self.generateClicked)
        buttonLayout.setContentsMargins(165, 0, 0, 0)
        buttonLayout.addWidget(self.genButton)
        layout.addLayout(buttonLayout, 2, 0, 1, 2)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    # funct to run on generate click
    def generateClicked(self):
        # run generate with the correct inputs corres to seed and rand check status
        if self.ignoreCheck.isChecked():
            if self.regionSelect.currentText():
                data = generate(None, None, None, region=self.regionSelect.currentText())
            else:
                data = generate(None, None, None)
        elif self.seedCheck.isChecked():
            if self.regionSelect.currentText():
                data = generate(None, self.seedInput.text(), None, region=self.regionSelect.currentText())
            else:
                data = generate(None, self.seedInput.text(), None)
        else:
            if self.regionSelect.currentText():
                data = generate(self.nameInput.text(), None, self.bdayInput.date().toPyDate(), region=self.regionSelect.currentText())
            else:
                data = generate(self.nameInput.text(), None, self.bdayInput.date().toPyDate())
        (name, ability, returnMoves, imageData, types) = data

        # set name disp, trim if too long
        if len(name) <= 20:
            self.nameDisp.setText(name.replace("-", " ").title())
        else:
            tempString = name.replace("-", " ").title()[0:16] + "..."
            self.nameDisp.setText(tempString)

        # set ability disp
        self.abilityDisp.setText(ability.replace("-", " ").title())
        self.abilityDisp.setVisible(True)
        self.abilityDisp.adjustSize()

        # set move disps
        for i in range(len(self.movesRef)):
            if i < len(returnMoves):
                self.movesRef[i].setText(returnMoves[i].replace("-", " ").title())
                self.movesRef[i].setVisible(True) 
            else:
                self.movesRef[i].setText("None")
                self.movesRef[i].setVisible(False) 

        # set type icons
        for i in range(len(self.typesRef)):
            if i < len(types):
                path = "pngs/" + types[i] + ".png"
                self.typesRef[i].setPixmap(QPixmap(path).scaled(20, 20))
            else:
                self.typesRef[i].setPixmap(QPixmap())

        # set pkmn sprite
        sprite = QPixmap()
        if imageData:
            sprite.loadFromData(imageData)
        else:
            sprite = QPixmap("pkball.png")
        self.imageDisp.setPixmap(sprite.scaled(150, 150))

    # grey out inputs when ignore checked
    def ignoreToggle(self):
        if self.ignoreCheck.isChecked():
            self.seedCheck.setEnabled(False)
            self.seedInput.setEnabled(False)
            self.nameInput.setEnabled(False)
            self.bdayInput.setEnabled(False)
        else:
            self.seedCheck.setEnabled(True)
            self.seedInput.setEnabled(True)
            self.nameInput.setEnabled(True)
            self.bdayInput.setEnabled(True)

    # grey out other inputs when seed is checked
    def seedToggle(self):
        if self.seedCheck.isChecked():
            self.ignoreCheck.setEnabled(False)
            self.nameInput.setEnabled(False)
            self.bdayInput.setEnabled(False)
        else:
            self.ignoreCheck.setEnabled(True)
            self.nameInput.setEnabled(True)
            self.bdayInput.setEnabled(True)

stylesheet = """
QMainWindow#MainWindow {
    background-image: url(background.png);
    background-repeat: no-repeat; 
    background-position: center;
}

QLabel#abilityDisp {
    color:aqua;
    border-style: solid;
    border-width: 2px;
    border-color: black;
}

QLabel#skillDisp {
    border-style: solid;
    border-width: 2px;
    border-color: black;
}

QLabel#title {
    color:aqua;
}

QLabel#bdayLabel {
    color:aqua;
}

QLabel {
    color:white;
}

QDateEdit, QComboBox, QLineEdit {
    /*background-color: dimgrey;*/
    background: transparent;
    color:white;
    border-style: solid;
    border-width: 2px;
    border-color: black; 
    border-radius: 0px 0px 0px 0px;    
}

QComboBox QAbstractItemView {
    background: dimgrey;
    border-style: solid;
    border-width: 2px;
    border-color: black; 
    border-radius: 0px 0px 0px 0px;
    selection-color: blue;
}

QCheckBox {
    /*background-color: dimgrey;*/
    /*background: transparent;*/
    color:crimson;   
}

QCheckBox::indicator:unchecked {
    border-style: solid;
    border-width: 2px;
    border-color: black; 
    border-radius: 0px 0px 0px 0px;
}

QCheckBox::indicator:checked {
    background-color: crimson;
    border-style: solid;
    border-width: 2px;
    border-color: black; 
    border-radius: 0px 0px 0px 0px;
}

QPushButton {
    background: transparent;
    color: crimson;
    border-style: solid;
    border-width: 2px;
    border-color: black; 
    border-radius: 0px 0px 0px 0px;
}
"""

app = QApplication(sys.argv)
app.setStyle('Fusion')
app.setStyleSheet(stylesheet)

window = MainWindow()
window.show()

app.exec()