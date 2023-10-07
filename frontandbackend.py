import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from fartnet import fartnet
from lightcontroller.frontend_qt import LightController
from lightcontroller.mqtt_sender import mqtt

class FartnetThread(QThread):
	def __init__(self, fartnet):
		super().__init__()
		self.fartnet = fartnet
		self.running = True

	def run(self):
		while self.running:
			self.fartnet.loop()

	def update_hotbuttons(self, hotbutton_states):
		self.fartnet.update_hotbuttons(hotbutton_states)

	def stop(self):
		self.running = False
		self.fartnet.close()

class MainWindow(QMainWindow):
	closed = pyqtSignal()
	def __init__(self):
		super().__init__()
	def closeEvent(self, event):
		self.closed.emit()
		event.accept()


def handle_preset_button_click(n):
	print(f"Preset {n} clicked")
	mqtt.apply_preset(n)

def handle_variation_button_click(n):
	print(f"Variation {n} clicked")
	mqtt.apply_variation(n)

def handle_palette_button_click(n):
	print(f"Palette {n} clicked")
	mqtt.apply_palette(n)


if __name__ == "__main__":
	# ==================== Initialize the Fartnet ====================
	fartnet = fartnet(["127.0.0.1"])
	fartnet_thread = FartnetThread(fartnet)
	fartnet_thread.start()

	# ==================== Initialize the GUI ====================
	app = QApplication(sys.argv)
	lightcontroller = LightController()
	main_window = MainWindow()
	main_window.setCentralWidget(lightcontroller)
	main_window.show()

	lightcontroller.preset_panel.clicked.connect(handle_preset_button_click)
	lightcontroller.variation_panel.clicked.connect(handle_variation_button_click)
	lightcontroller.hotbutton_panel.updated.connect(fartnet_thread.update_hotbuttons)
	lightcontroller.palette_panel.clicked.connect(handle_palette_button_click)

	main_window.closed.connect(fartnet_thread.stop)
	main_window.closed.connect(app.exit)
 
	sys.exit(app.exec_())