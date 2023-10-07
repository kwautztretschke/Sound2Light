from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QGroupBox, QGridLayout

from lightcontroller.controls_groupbox import ButtonGridGroupBox
from lightcontroller.button_bars import PresetPanel, VariationPanel, HotbuttonPanel, PalettePanel


class LightController(QWidget):
	def __init__(self):
		super().__init__()

		# ==================== Layouting the Main Window ====================
		# divide the main window into a top bar containing presets, and the bottom part containing the actual controls
		main_layout = QVBoxLayout()
		self.setLayout(main_layout)

		self.preset_panel = PresetPanel(9)
		main_layout.addWidget(self.preset_panel)

		self.variation_panel = VariationPanel(9)
		main_layout.addWidget(self.variation_panel)
  
		self.hotbutton_panel = HotbuttonPanel(8)
		main_layout.addWidget(self.hotbutton_panel)
  
		self.palette_panel = PalettePanel(5)
		main_layout.addWidget(self.palette_panel)

		controls_groupbox = QGroupBox("Controls")
		self.controls_layout = QHBoxLayout() # this layout will be filled with ButtonGridGroupBox instances
		controls_groupbox.setLayout(self.controls_layout)
		main_layout.addWidget(controls_groupbox)
		# ====================================================================


		self.control_groupboxes = []
		for i in range(4):
			groupbox = ButtonGridGroupBox(f"Controls {i}")
			self.controls_layout.addWidget(groupbox)
			self.control_groupboxes.append(groupbox)

	def keyPressEvent(self, event):
		preset_LUT = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
		variation_LUT = ["q", "w", "e", "r", "t", "z", "u", "i", "o"]
		hotbutton_LUT = ["a", "s", "d", "f", "g", "h", "j", "k"]

		if event.text() in preset_LUT:
			self.preset_panel.animateClick(preset_LUT.index(event.text()))
		elif event.text() in variation_LUT:
			self.variation_panel.animateClick(variation_LUT.index(event.text()))
		elif event.text() in hotbutton_LUT:
			self.hotbutton_panel.animatePress(hotbutton_LUT.index(event.text()))
		# else:
		# 	print(f"Key pressed: {event.text()}")

	def keyReleaseEvent(self, event):
		# TODO find a good place for the shortcut LUTs
		hotbutton_LUT = ["a", "s", "d", "f", "g", "h", "j", "k"]

		if event.text() in hotbutton_LUT:
			self.hotbutton_panel.animateRelease(hotbutton_LUT.index(event.text()))
		# else:
		# 	print(f"Key released: {event.text()}")
