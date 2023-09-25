import sys
from functools import partial
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QGroupBox, QGridLayout

class MainWindow(QWidget):
	def __init__(self):
		super().__init__()

		# divide the main window into a top bar containing presets, and the bottom part containing the actual controls
		main_layout = QVBoxLayout()
		presets_groupbox = QGroupBox("Presets")
		presets_groupbox.setFixedHeight(100)
		main_layout.addWidget(presets_groupbox)
		controls_groupbox = QGroupBox("Controls")
		main_layout.addWidget(controls_groupbox)

		# presets bar (top)
		presets_grid = QGridLayout()
		presets_groupbox.setLayout(presets_grid)

		preset_buttons = []
		for i in range(9):
			button = QPushButton(f"Preset {i+1}")
			button.setFixedSize(100, 50) # set fixed size
			preset_buttons.append(button)
			presets_grid.addWidget(button, 0, i)
			button.clicked.connect(partial(handle_preset_button_click, i+1))

		# controls (bottom)
		controls_layout = QHBoxLayout()
		controls_groupbox.setLayout(controls_layout)

		# create three group boxes
		reactor_group_boxes = []
		for i in range(3):
			group_box = QGroupBox(f"Group {i+1}")
			reactor_group_boxes.append(group_box)
			controls_layout.addWidget(group_box)

			# create a 4x4 grid of push buttons for each group box
			grid = QGridLayout()
			group_box.setLayout(grid)
			for row in range(4):
				for col in range(4):
					button = QPushButton(f"{row+1},{col+1}")
					button.setFixedSize(80, 80) # set fixed size
					grid.addWidget(button, row, col)

		# Set the main layout for the window
		self.setLayout(main_layout)

	def keyPressEvent(self, event):
		# Check if the pressed key is a number between 1 and 9
		if event.text().isdigit() and 1 <= int(event.text()) <= 9:
			# Call the handle_preset_button_click function with the corresponding number as argument
			handle_preset_button_click(int(event.text()))
		else:
			# Print the key that was pressed to the console
			print("Keypress: " + event.text())


def handle_preset_button_click(n):
	print(f"Preset {n} clicked")


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
