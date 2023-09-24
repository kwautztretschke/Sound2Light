import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QGroupBox, QGridLayout

class MainWindow(QWidget):
	def __init__(self):
		super().__init__()

		# divide the main window into a top bar containing presets, and the bottom part containing the actual controls
		main_layout = QVBoxLayout()
		presets_layout = QHBoxLayout()
		main_layout.addLayout(presets_layout)
		controls_layout = QHBoxLayout()
		main_layout.addLayout(controls_layout)

		# presets bar (top)
		presets_groupbox = QGroupBox("Presets")
		presets_layout.addWidget(presets_groupbox)

		presets_grid = QGridLayout()
		presets_groupbox.setLayout(presets_grid)

		preset_buttons = []
		for i in range(9):
			button = QPushButton(f"Preset {i+1}")
			preset_buttons.append(button)
			presets_grid.addWidget(button, 0, i)

   
   
		# controls (bottom)
		controls_groupbox = QGroupBox("Controls")
		controls_layout.addWidget(controls_groupbox)

		# Set the main layout for the window
		self.setLayout(main_layout)

	def keyPressEvent(self, event):
		# Print the key that was pressed to the console
		print(event.text())

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
