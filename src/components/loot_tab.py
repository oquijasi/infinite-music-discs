# -*- coding: utf-8 -*-
#
#Infinite Music Discs loot-tab-specific GUI components module
#Generation tool, datapack design, and resourcepack design by link2_thepast

import atexit
import re
import shutil
import tempfile
import zipfile
from typing import List

from PySide6 import QtWidgets
from PySide6.QtCore import Qt



#color used for the labels of disabled loot options
DISABLED_LABEL_STYLE = 'color: #6e6e6e;'

#matches chest loot tables inside a Minecraft jar, capturing the path relative to the chests folder
#  e.g. data/minecraft/loot_table/chests/trial_chambers/corridor.json -> trial_chambers/corridor.json
#anchored to the start of the path on purpose: the jar also bundles datapacks (e.g. data/minecraft/datapacks/
#  trade_rebalance/data/minecraft/loot_table/chests/...) that override some of these tables, and those
#  copies must not be listed a second time
CHEST_TABLE_REGEX = re.compile(r'^(?:data/)?minecraft/loot_tables?/chests/(.+\.json)$')

#size of the "select jar" button
JAR_BUTTON_MIN_SIZE = (320, 56)
JAR_BUTTON_FONT_SIZE = 18

#limits for the chest loot options
ROLLS_MIN, ROLLS_MAX, ROLLS_DEFAULT = 1, 99, 1
CHANCE_MIN, CHANCE_MAX, CHANCE_DEFAULT = 1, 100, 100


#extract all chest loot table .json files from a Minecraft jar into destDir
#returns the sorted list of their paths relative to the chests folder (using forward slashes)
#raises zipfile.BadZipFile / OSError if the jar can't be read
def extractChestTables(jarPath: str, destDir: str) -> List[str]:
    found = []

    with zipfile.ZipFile(jarPath) as jar:
        for info in jar.infolist():
            if info.is_dir():
                continue

            match = CHEST_TABLE_REGEX.search(info.filename)
            if match:
                jar.extract(info, destDir)
                found.append(match.group(1))

    return sorted(found)



#one row of the loot list: a checkbox and its label
class LootListEntry(QtWidgets.QFrame):
    def __init__(self, label: str, enabled: bool = True, checked: bool = False, parent = None):
        super().__init__(parent=parent)

        self._check = QtWidgets.QCheckBox(self)
        self._label = QtWidgets.QLabel(label)
        self._label.setObjectName('SettingLabel')

        #set initial state before disabling, since a disabled checkbox can't be toggled by the user
        self._check.setChecked(checked)
        self.setActive(enabled)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 5, 5, 5)
        layout.addWidget(self._check)
        layout.addWidget(self._label)
        layout.addStretch(1)

        self.setLayout(layout)

    #enable/disable the option; disabled options can't be toggled or focused, and their label is greyed out too
    def setActive(self, active: bool):
        self._check.setEnabled(active)
        self._check.setFocusPolicy(Qt.StrongFocus if active else Qt.NoFocus)
        self._label.setEnabled(active)
        self._label.setStyleSheet('' if active else DISABLED_LABEL_STYLE)

    def isChecked(self) -> bool:
        return self._check.isChecked()

#one row of a text label with an integer spinbox on the right
class LootSpinEntry(QtWidgets.QFrame):
    def __init__(self, label: str, minValue: int, maxValue: int, default: int, parent = None):
        super().__init__(parent=parent)

        self._label = QtWidgets.QLabel(label)
        self._label.setObjectName('SettingLabel')

        #QSpinBox only accepts whole numbers, and the arrows/keyboard stay inside [min, max]
        self._spin = QtWidgets.QSpinBox(self)
        self._spin.setRange(minValue, maxValue)
        self._spin.setValue(default)
        self._spin.setFixedWidth(80)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(90, 5, 20, 5)
        layout.addWidget(self._label)
        layout.addStretch(1)
        layout.addWidget(self._spin)

        self.setLayout(layout)

    #enable/disable the row; the label is greyed out when disabled
    def setActive(self, active: bool):
        self._spin.setEnabled(active)
        self._label.setEnabled(active)
        self._label.setStyleSheet('' if active else DISABLED_LABEL_STYLE)

    def value(self) -> int:
        return self._spin.value()

#label that toggles its checkbox when clicked
class QCheckLabel(QtWidgets.QLabel):
    def __init__(self, text: str, checkbox: QtWidgets.QCheckBox, parent = None):
        super().__init__(text, parent)
        self._checkbox = checkbox

    def mousePressEvent(self, event):
        event.accept()
        self._checkbox.toggle()



#one row of the chest loot table list
class ChestListEntry(QtWidgets.QFrame):
    def __init__(self, name: str, parent = None):
        super().__init__(parent=parent)

        self._name = name

        self._check = QtWidgets.QCheckBox(self)
        self._label = QCheckLabel(name, self._check, self)
        self._label.setObjectName('SettingLabel')

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 3, 10, 3)
        layout.addWidget(self._check)
        layout.addWidget(self._label)
        layout.addStretch(1)

        self.setLayout(layout)

    def getName(self) -> str:
        return self._name

    def isChecked(self) -> bool:
        return self._check.isChecked()



#scrollable list of checkboxes, one per chest loot table
class ChestTableList(QtWidgets.QScrollArea):
    def __init__(self, parent = None):
        super().__init__(parent=parent)

        self.setObjectName('ChestListScrollArea')
        self._entries = []

        self._childLayout = QtWidgets.QVBoxLayout()
        self._childLayout.setSpacing(0)
        self._childLayout.setContentsMargins(0, 0, 0, 0)
        self._childLayout.addStretch(1)

        widget = QtWidgets.QWidget()
        widget.setObjectName('ChestListChildWidget')
        widget.setLayout(self._childLayout)

        self.setWidget(widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setMinimumHeight(220)

        #keep the list visually transparent so it blends with the tab background
        self.setStyleSheet(
            'QScrollArea#ChestListScrollArea { background: transparent; border: 1px solid #4a4a4a; }'
            'QWidget#ChestListChildWidget { background: transparent; }'
        )
        self.viewport().setAutoFillBackground(False)

    #replace the list contents
    def setItems(self, names: List[str]):
        self.clear()

        for n in names:
            entry = ChestListEntry(n, self)
            self._entries.append(entry)
            #insert before the trailing stretch
            self._childLayout.insertWidget(self._childLayout.count() - 1, entry)

    def clear(self):
        for e in self._entries:
            self._childLayout.removeWidget(e)
            e.deleteLater()

        self._entries = []

    def getSelected(self) -> List[str]:
        return [e.getName() for e in self._entries if e.isChecked()]



#loot tab contents
#reuses the Settings tab's object names so the existing stylesheet gives it the same background
class LootList(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent=parent)

        self.setObjectName('SettingsList')
        self._parent = parent

        self._jarPath = ''
        self._tmpDir = ''

        #make sure the temporary folder never outlives the program
        atexit.register(self.cleanupTmp)

        #button to pick the Minecraft jar, stays enabled
        self._btnJar = QtWidgets.QPushButton('SELECT MINECRAFT JAR', self)
        self._btnJar.setMinimumSize(*JAR_BUTTON_MIN_SIZE)
        self._btnJar.setStyleSheet(f'font-size: {JAR_BUTTON_FONT_SIZE}px;')
        self._btnJar.clicked.connect(self.selectJar)

        #child layout, contains loot entries
        childLayout = QtWidgets.QVBoxLayout()
        childLayout.setSpacing(0)
        childLayout.setContentsMargins(1, 1, 1, 1)

        #centered row for the jar button
        jarLayout = QtWidgets.QHBoxLayout()
        jarLayout.setContentsMargins(5, 10, 5, 10)
        jarLayout.addStretch(1)
        jarLayout.addWidget(self._btnJar)
        jarLayout.addStretch(1)
        jarFrame = QtWidgets.QFrame(self)
        jarFrame.setLayout(jarLayout)

        #list of chest loot tables, filled in once a jar is loaded
        self._chestList = ChestTableList(self)
        self._chestList.setEnabled(False)

        chestListLayout = QtWidgets.QHBoxLayout()
        chestListLayout.setContentsMargins(50, 0, 10, 10)
        chestListLayout.addWidget(self._chestList)
        chestListFrame = QtWidgets.QFrame(self)
        chestListFrame.setLayout(chestListLayout)

        self._entryCreepers = LootListEntry('Creepers can drop custom music discs', enabled=False, checked=True, parent=self)
        self._entryChests = LootListEntry('Add custom music discs to chest loot tables', enabled=False, parent=self)

        self._entryRolls = LootSpinEntry('rolls (how many for each chest)', ROLLS_MIN, ROLLS_MAX, ROLLS_DEFAULT, parent=self)
        self._entryChance = LootSpinEntry('% chance of a succesful roll', CHANCE_MIN, CHANCE_MAX, CHANCE_DEFAULT, parent=self)
        self._entryRolls.setActive(False)
        self._entryChance.setActive(False)

        childLayout.addWidget(self._entryCreepers)
        childLayout.addWidget(jarFrame)
        childLayout.addWidget(self._entryChests)
        childLayout.addWidget(self._entryRolls)
        childLayout.addWidget(self._entryChance)
        childLayout.addWidget(chestListFrame, 1)

        #child widget, contains child layout
        widget = QtWidgets.QWidget()
        widget.setLayout(childLayout)
        widget.setObjectName('SettingsChildWidget')

        #scroll area, contains child widget
        scrollArea = QtWidgets.QScrollArea(self)
        scrollArea.setWidget(widget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollArea.setObjectName('SettingsScrollArea')

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

    def cleanupTmp(self):
        if self._tmpDir:
            shutil.rmtree(self._tmpDir, ignore_errors=True)
            self._tmpDir = ''

    #enable/disable everything that depends on a jar being loaded
    def setChestOptionsActive(self, active: bool):
        self._entryChests.setActive(active)
        self._entryRolls.setActive(active)
        self._entryChance.setActive(active)

    #put the chest options back to their "no jar loaded" state
    def resetChestOptions(self):
        self._jarPath = ''
        self._btnJar.setToolTip('')
        self._chestList.clear()
        self._chestList.setEnabled(False)
        self.setChestOptionsActive(False)

    def selectJar(self):
        f = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Minecraft JAR', '.', 'Minecraft JAR (*.jar)')

        if f[0] == '':
            return

        #extract the chest loot tables to a fresh temporary folder
        self.cleanupTmp()
        tmpDir = tempfile.mkdtemp(prefix='imd_jar_')

        try:
            tables = extractChestTables(f[0], tmpDir)
        except (zipfile.BadZipFile, OSError):
            tables = []
            error = 'The selected file could not be read as a Minecraft JAR.'
        else:
            error = 'No chest loot tables were found in the selected JAR.'

        if not tables:
            shutil.rmtree(tmpDir, ignore_errors=True)
            self.resetChestOptions()
            QtWidgets.QMessageBox.warning(self, 'Loot tables', error)
            return

        #success: remember the jar, fill in the list, and unlock the chest loot option
        self._tmpDir = tmpDir
        self._jarPath = f[0]
        self._btnJar.setToolTip(self._jarPath)

        self._chestList.setItems(tables)
        self._chestList.setEnabled(True)
        self.setChestOptionsActive(True)

    def getJarPath(self) -> str:
        return self._jarPath

    #folder containing the extracted chest loot tables, or '' if no jar is loaded
    def getTmpDir(self) -> str:
        return self._tmpDir

    #relative paths (e.g. 'trial_chambers/corridor.json') of the loot tables the user ticked
    def getSelectedChestTables(self) -> List[str]:
        return self._chestList.getSelected()

    def isChestLootEnabled(self) -> bool:
        return self._entryChests.isChecked()

    def getChestRolls(self) -> int:
        return self._entryRolls.value()

    def getChestChance(self) -> int:
        return self._entryChance.value()
