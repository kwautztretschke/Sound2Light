from functools import partial
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QGroupBox, QGridLayout

class PresetPanel(QGroupBox):
	clicked = pyqtSignal(int)
	def __init__(self, n_buttons=9): #TODO make n a tuple, and populate a grid with x columns and y rows
		super().__init__("Presets")
		self.n_buttons = n_buttons
		self.setFixedHeight(100)
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		self.buttons = []
		for i in range(n_buttons):
			button = QPushButton(f"Preset {i}")
			button.setFixedSize(100, 50) # set fixed size
			self.buttons.append(button)
			self.grid.addWidget(button, 0, i)
			button.clicked.connect(partial(self.clicked.emit, i))

	def animateClick(self, n):
		if n < self.n_buttons:
			self.buttons[n].animateClick()

class VariationPanel(QGroupBox):
	clicked = pyqtSignal(int)
	def __init__(self, n_buttons=9):
		super().__init__("Variations")
		self.n_buttons = n_buttons
		self.setFixedHeight(100)
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		self.buttons = []
		# self.buttons_LUT = {"q": 0, "w": 1, "e": 2, "r": 3, "t": 4, "z": 5, "u": 6, "i": 7, "o": 8}
		for i in range(n_buttons):
			button = QPushButton(f"Variation {i}")
			button.setFixedSize(100, 50)
			self.buttons.append(button)
			self.grid.addWidget(button, 0, i)
			button.clicked.connect(partial(self.clicked.emit, i))

	def animateClick(self, n):
		if n < self.n_buttons:
			self.buttons[n].animateClick()

class HotbuttonPanel(QGroupBox):
	updated = pyqtSignal(list)
	def __init__(self, n_buttons=8):
		super().__init__("Hotbuttons")
		self.n_buttons = n_buttons
		self.setFixedHeight(100)
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		self.buttons = []
		self.button_states = [0] * n_buttons
		for i in range(n_buttons):
			button = QPushButton(f"Hotbutton {i}")
			button.setFixedSize(100, 50)
			self.buttons.append(button)
			self.grid.addWidget(button, 0, i)
			button.pressed.connect(partial(self.pressed, i))
			button.released.connect(partial(self.released, i))

	def pressed(self, i):
		self.button_states[i] = 255
		self.updated.emit(self.button_states)

	def released(self, i):
		self.button_states[i] = 0
		self.updated.emit(self.button_states)

	def animatePress(self, i):
		if i < self.n_buttons:
			self.buttons[i].setDown(True)
			self.pressed(i)
	
	def animateRelease(self, i):
		if i < self.n_buttons:
			self.buttons[i].setDown(False)
			self.released(i)

class PalettePanel(QGroupBox):
	clicked = pyqtSignal(int)
	def __init__(self, n_buttons=5):
		super().__init__("Palettes")
		self.n_buttons = n_buttons
		self.setFixedHeight(100)
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		self.buttons = []
		for i in range(n_buttons):
			button = QPushButton(f"Palette {i}")
			button.setFixedSize(100, 50)
			self.buttons.append(button)
			self.grid.addWidget(button, 0, i)
			button.clicked.connect(partial(self.clicked.emit, i))

	def animateClick(self, n):
		if n < self.n_buttons:
			self.buttons[n].animateClick()