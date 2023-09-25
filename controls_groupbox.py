from PyQt5.QtWidgets import QGroupBox, QPushButton, QGridLayout, QHBoxLayout, QComboBox, QVBoxLayout, QSizePolicy

class ButtonGridGroupBox(QGroupBox):
	def __init__(self, title):
		super().__init__(title)

		# ==================== Layouting the Group Box ====================
		vbox = QVBoxLayout()
		self.setLayout(vbox)

		button_grid_layout = QGridLayout()
		vbox.addLayout(button_grid_layout, stretch=1)

		settings_layout = QHBoxLayout()
		vbox.addLayout(settings_layout)
		# ====================================================================

		# create a horizontal layout with a dummy combobox and a pushbutton "destroy"
		combobox = QComboBox()
		settings_layout.addWidget(combobox)
		destroy_button = QPushButton("Destroy")
		destroy_button.clicked.connect(self.destroy_self)
		settings_layout.addWidget(destroy_button)

		# create a 4x4 grid of push buttons
		for row in range(4):
			for col in range(4):
				button = QPushButton(f"{row+1},{col+1}")
				button.setFixedSize(80, 80) 
				button_grid_layout.addWidget(button, row, col)


	def destroy_self(self):
		self.setParent(None)
