import sys
from functools import partial
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QGroupBox, QGridLayout

from controls_groupbox import ButtonGridGroupBox

class MainWindow(QWidget):
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

		controls_groupbox = QGroupBox("Controls")
		self.controls_layout = QHBoxLayout() # this layout will be filled with ButtonGridGroupBox instances
		controls_groupbox.setLayout(self.controls_layout)
		main_layout.addWidget(controls_groupbox)
		# ====================================================================

		# populating the presets grid with buttons
		preset_buttons = []
		for i in range(9):
			button = QPushButton(f"Preset {i+1}")
			button.setFixedSize(100, 50) # set fixed size
			preset_buttons.append(button)
			presets_grid.addWidget(button, 0, i)
			button.clicked.connect(partial(handle_preset_button_click, i+1))

	def keyPressEvent(self, event):
		# Check if the pressed key is a number between 1 and 9
		if event.text().isdigit() and 1 <= int(event.text()) <= 9:
			# Call the handle_preset_button_click function with the corresponding number as argument
			handle_preset_button_click(int(event.text()))
		else:
			# Print the key that was pressed to the console
			print("Keypress: " + event.text())

	def closeEvent(self, event):
			# destroy all the ButtonGridGroupBox instances
			for group_box in self.reactor_group_boxes:
				group_box.destroy_self()

def handle_preset_button_click(n):
	print(f"Preset {n} clicked")


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
