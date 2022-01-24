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

def weightedChoice(numSelections, data, weightNum):
    selections = []
    while(numSelections > 0):
        selection = data[weightNum % len(data)]
        selections.append(selection)
        data.remove(selection)
        numSelections-=1
    return selections

def generate(name, seed, date, region="None"):
    if name:
        converted = ""
        for char in name:
            converted += str(ord(char))
        stringDate = date.strftime("%m%d%Y")
        inString = converted + stringDate
        inString = inString.ljust(50, '0')
    elif seed:
        converted = ""
        for char in seed:
            converted += str(ord(char))
        inString = converted.ljust(50, '0')
    else:
        inList = random.sample(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], 
            counts=[50, 50, 50, 50, 50, 50 ,50, 50 , 50, 50], k=50)
        inString = ''.join(str(e) for e in inList)
    return retrieveData(int(inString), region.lower())

def retrieveData(preNum, region):
    hashNum = pow(preNum, 2) % 3576667 # make shiny if triple repeating nums
    ranges = {'kanto': [151, 0], 'johto': [100, 151], 'hoenn': [135, 251], 'sinnoh': [107, 386], 'unova': [156, 493], 'kalos': [72, 649], 'alola': [88, 721], 'galar': [89, 809], 'none': [898, 0]}
    dexNum = (hashNum % ranges[region][0]) + ranges[region][1] + 1

    groups = groupby(str(hashNum))
    result = [(label, sum(1 for _ in group)) for label, group in groups] # https://stackoverflow.com/questions/34443946/count-consecutive-characters
    shiny = False
    for num, count in result:
        if count >= 3:
            shiny = True

    url = "https://pokeapi.co/api/v2/pokemon-species/" + str(dexNum) + "/"
    res = requests.get(url)
    forms = res.json()["varieties"]
    form = hashNum % len(forms)
    name = forms[form]["pokemon"]["name"]

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

    sprites = supRes.json()["sprites"]
    if (shiny):
        sprite = sprites["front_shiny"]
    else:
        sprite = sprites["front_default"]

    typeInput = supRes.json()["types"]
    types = [typeInput[0]["type"]["name"]]
    if len(typeInput) == 2: types.append(typeInput[1]["type"]["name"])
    if sprite:
        imageData = requests.get(sprite).content
    else:
        imageData = None
    return (name, ability, returnMoves, imageData, types)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        fontID = QFontDatabase.addApplicationFont("pokemon-b-w.ttf")
        families = QFontDatabase.applicationFontFamilies(fontID)

        self.setObjectName('MainWindow')

        self.setWindowIcon(QIcon('icon.png'))

        self.setWindowTitle("Random Pokemon Generator")

        self.setFixedSize(QSize(510, 380))

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setVerticalSpacing(0)

        pokemonLayout = QVBoxLayout()
        pokemonLayout.setSpacing(0)
        pokemonLayout.setContentsMargins(4, 0, 4, 0)

        pokemonFrame = QFrame()

        pokemonFrame.setFixedSize(200, 350)
        pokemonFrame.setLayout(pokemonLayout)

        nameiconLayout = QHBoxLayout()
        nameiconLayout.setContentsMargins(0, 0, 0, 60)
        nameiconLayout.setSpacing(0)
        nameiconFrame = QFrame()
        nameiconFrame.setObjectName('nameiconFrame')
        nameiconFrame.setFixedHeight(40)
        nameiconFrame.setLayout(nameiconLayout)

        pokemonLayout.addWidget(nameiconFrame)

        self.imageDisp = QLabel()
        self.imageDisp.setPixmap(QPixmap('pkball.png').scaled(150, 150))
        self.imageDisp.setObjectName('imageDisp')
        self.imageDisp.setFixedSize(170, 170)
        self.imageDisp.setContentsMargins(15, 0, 0, 10)

        pokemonLayout.addWidget(self.imageDisp, Qt.AlignmentFlag.AlignCenter)

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

        moveLayout = QGridLayout()
        moveLayout.setContentsMargins(10, 15, 2, 25)
        moveLayout.setSpacing(10)

        pokemonLayout.addLayout(moveLayout)

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

        inputLayout = QVBoxLayout()
        inputLayout.setSpacing(10)
        inputLayout.setContentsMargins(60, 0, 0, 40)
        inputLayout.addLayout(titleLayout)

        layout.addLayout(inputLayout, 0, 1, 1, 2)

        self.nameInput = QLineEdit()
        self.nameInput.setFixedSize(240, 30)
        self.nameInput.setFont(QFont(families[0], 14))
        self.nameInput.setMaxLength(20)
        self.nameInput.setPlaceholderText("Enter your name (max 20 characters)")
 
        inputLayout.addWidget(self.nameInput)

        dateLayout = QHBoxLayout()
        dateLayout.setContentsMargins(0, 0, 0, 0)
        dateLayout.setSpacing(10)
        inputLayout.addLayout(dateLayout)

        self.regionSelect = QComboBox()
        self.regionSelect.setFixedSize(150, 30)
        self.regionSelect.setFont(QFont(families[0], 14))
        self.regionSelect.setPlaceholderText("Region")
        self.regionSelect.addItems(['Kanto', 'Johto', 'Hoenn', 'Sinnoh', 'Unova', 'Kalos', 'Alola', 'Galar', 'None'])
        inputLayout.addWidget(self.regionSelect)

        self.seedCheck = QCheckBox("Generate based on seed only")
        self.seedCheck.setFont(QFont(families[0], 14))
        self.seedCheck.stateChanged.connect(self.seedToggle)
        inputLayout.addWidget(self.seedCheck)

        seed = "00000"
        self.seedInput = QLineEdit()
        self.seedInput.setFont(QFont(families[0], 14))
        self.seedInput.setMaxLength(5)
        self.seedInput.setFixedSize(220, 30)
        self.seedInput.setPlaceholderText("Enter a seed (max 5 characters)")

        inputLayout.addWidget(self.seedInput)

        self.ignoreCheck = QCheckBox("Ignore inputs and generate random")
        self.ignoreCheck.setFont(QFont(families[0], 14))
        self.ignoreCheck.stateChanged.connect(self.ignoreToggle)
        inputLayout.addWidget(self.ignoreCheck)

        layout.addWidget(pokemonFrame, 0, 0)

        self.bdayInput = QDateEdit()
        self.bdayInput.setFixedSize(90, 30)
        self.bdayInput.setFont(QFont(families[0], 15))
        dateLayout.addWidget(self.bdayInput)

        bdayLabel = QLabel("Enter your birthday")
        bdayLabel.setObjectName('bdayLabel')
        bdayLabel.setFont(QFont(families[0], 15))
        dateLayout.addWidget(bdayLabel)

        self.nameDisp = QLabel("")
        self.nameDisp.setFixedHeight(40)
        self.nameDisp.setFont(QFont(families[0], 15))
        nameiconLayout.addWidget(self.nameDisp)

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
         
        buttonLayout = QHBoxLayout()

        self.genButton = QPushButton("Generate!")
        self.genButton.setFixedSize(90, 30)
        self.genButton.setFont(QFont(families[0], 15))
        self.genButton.clicked.connect(self.generateClicked)

        buttonLayout.setContentsMargins(165, 0, 0, 0)
        buttonLayout.addWidget(self.genButton)

        layout.addLayout(buttonLayout, 2, 0, 1, 2)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def generateClicked(self):
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

        if len(name) <= 20:
            self.nameDisp.setText(name.replace("-", " ").title())
        else:
            tempString = name.replace("-", " ").title()[0:16] + "..."
            self.nameDisp.setText(tempString)
        self.abilityDisp.setText(ability.replace("-", " ").title())
        self.abilityDisp.setVisible(True)
        self.abilityDisp.adjustSize()
        for i in range(len(self.movesRef)):
            if i < len(returnMoves):
                if len(returnMoves[i]) < 12:
                    self.movesRef[i].setText(returnMoves[i].replace("-", " ").title()) # max length 14 chars, trim to 13.
                else:
                    tempMove = returnMoves[i].replace("-", " ").title()[0:9] + "."
                    self.movesRef[i].setText(tempMove)
                self.movesRef[i].setVisible(True) 
            else:
                self.movesRef[i].setText("None")
                self.movesRef[i].setVisible(False) 

        for i in range(len(self.typesRef)):
            if i < len(types):
                path = "pngs/" + types[i] + ".png"
                self.typesRef[i].setPixmap(QPixmap(path).scaled(20, 20))
            else:
                self.typesRef[i].setPixmap(QPixmap())

        sprite = QPixmap()
        if imageData:
            sprite.loadFromData(imageData)
        else:
            sprite = QPixmap("pkball.png")
        self.imageDisp.setPixmap(sprite.scaled(150, 150))


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