import sys
from functools import partial
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QGroupBox, QGridLayout

from lightcontroller.mqtt_sender import mqtt
from lightcontroller.controls_groupbox import ButtonGridGroupBox


class LightController(QWidget):
	def __init__(self):
		super().__init__()

		# ==================== Layouting the Main Window ====================
		# divide the main window into a top bar containing presets, and the bottom part containing the actual controls
		main_layout = QVBoxLayout()
		self.setLayout(main_layout)

		presets_groupbox = QGroupBox("Presets")
		presets_groupbox.setFixedHeight(100)
		presets_grid = QGridLayout()
		presets_groupbox.setLayout(presets_grid)
		main_layout.addWidget(presets_groupbox)

		variations_groupbox = QGroupBox("Variations")
		variations_groupbox.setFixedHeight(100)
		variations_grid = QGridLayout()
		variations_groupbox.setLayout(variations_grid)
		main_layout.addWidget(variations_groupbox)

		hotbuttons_groupbox = QGroupBox("Hotbuttons")
		hotbuttons_groupbox.setFixedHeight(100)
		hotbuttons_grid = QGridLayout()
		hotbuttons_groupbox.setLayout(hotbuttons_grid)
		main_layout.addWidget(hotbuttons_groupbox)

		palettes_groupbox = QGroupBox("Palettes")
		palettes_groupbox.setFixedHeight(100)
		palettes_grid = QGridLayout()
		palettes_groupbox.setLayout(palettes_grid)
		main_layout.addWidget(palettes_groupbox)

		controls_groupbox = QGroupBox("Controls")
		self.controls_layout = QHBoxLayout() # this layout will be filled with ButtonGridGroupBox instances
		controls_groupbox.setLayout(self.controls_layout)
		main_layout.addWidget(controls_groupbox)
		# ====================================================================

		# populating the presets grid with buttons
		self.preset_buttons = []
		for i in range(9):
			button = QPushButton(f"Preset {i}")
			button.setFixedSize(100, 50) # set fixed size
			self.preset_buttons.append(button)
			presets_grid.addWidget(button, 0, i)
			button.clicked.connect(partial(handle_preset_button_click, i))

		self.variation_buttons = []
		self.variation_buttons_LUT = {"q": 0, "w": 1, "e": 2, "r": 3, "t": 4, "z": 5, "u": 6, "i": 7, "o": 8}
		for i in range(9):
			button = QPushButton(f"Variation {i}")
			button.setFixedSize(100, 50)
			self.variation_buttons.append(button)
			variations_grid.addWidget(button, 1, i)
			button.clicked.connect(partial(handle_variation_button_click, i))

		self.hotbuttons = []
		for i in range(8):
			button = QPushButton(f"Hotbutton {i}")
			button.setFixedSize(100, 50)
			self.hotbuttons.append(button)
			hotbuttons_grid.addWidget(button, 2, i)
			button.clicked.connect(partial(handle_hotbutton_click, i))

		self.palette_buttons = []
		for i in range(5):
			button = QPushButton(f"Palette {i}")
			button.setFixedSize(100, 50)
			self.palette_buttons.append(button)
			palettes_grid.addWidget(button, 2, i)
			button.clicked.connect(partial(handle_palette_button_click, i))

		self.control_groupboxes = []
		for i in range(4):
			groupbox = ButtonGridGroupBox(f"Controls {i}")
			self.controls_layout.addWidget(groupbox)
			self.control_groupboxes.append(groupbox)

	def keyPressEvent(self, event):
		# Check if the pressed key is a number between 1 and 9
		if event.text().isdigit() and 1 <= int(event.text()) <= 9:
			# call the animateClick method of the button with the same number
			self.preset_buttons[int(event.text())-1].animateClick()
		# Check if the pressed key is a letter between q and o
		elif event.text() in self.variation_buttons_LUT:
			# call the animateClick method of the button with the same letter
			self.variation_buttons[self.variation_buttons_LUT[event.text()]].animateClick()
		else:
			# Print the key that was pressed to the console
			print("Keypress: " + event.text())

def handle_preset_button_click(n):
	print(f"Preset {n} clicked")
	mqtt.apply_preset(n)

def handle_variation_button_click(n):
	print(f"Variation {n} clicked")
	mqtt.apply_variation(n)

def handle_hotbutton_click(n):
	print(f"Hotbutton {n} clicked")
	mqtt.apply_hotbutton(n)

def handle_palette_button_click(n):
	print(f"Palette {n} clicked")
	mqtt.apply_palette(n)



if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = LightController()
	window.show()
	sys.exit(app.exec_())
