import sys
from functools import partial
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QGroupBox, QGridLayout
from paho.mqtt import client as mqtt_client

from controls_groupbox import ButtonGridGroupBox

mqtt_broker = '10.69.0.69'
mqtt_port = 1883

class mqtt_actor:
	def __init__(self):
		self.client = mqtt_client.Client("lightcontroller_frontend")
		# self.client.on_message = self.on_message
		try:
			self.client.connect(mqtt_broker, mqtt_port)
			print("Connected to MQTT Broker")
			self.client.loop_start()
		except:
			print("Could not connect to MQTT Broker")
	
	def send_message(self, topic, message):
		self.client.publish("actor/lightcontroller/" + topic, message)

mqtt = mqtt_actor()

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
		self.preset_buttons = []
		for i in range(9):
			button = QPushButton(f"Preset {i+1}")
			button.setFixedSize(100, 50) # set fixed size
			self.preset_buttons.append(button)
			presets_grid.addWidget(button, 0, i)
			button.clicked.connect(partial(handle_preset_button_click, i+1))

	def keyPressEvent(self, event):
		# Check if the pressed key is a number between 1 and 9
		if event.text().isdigit() and 1 <= int(event.text()) <= 9:
			# call the animateClick method of the button with the same number
			self.preset_buttons[int(event.text())-1].animateClick()
		else:
			# Print the key that was pressed to the console
			print("Keypress: " + event.text())

def handle_preset_button_click(n):
	print(f"Preset {n} clicked")
	mqtt.send_message("preset", str(n))



if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
