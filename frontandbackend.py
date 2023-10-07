import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from fartnet import fartnet
from lightcontroller.frontend_qt import LightController

class FartnetThread(QThread):
	def __init__(self, fartnet):
		super().__init__()
		self.fartnet = fartnet
		self.running = True

	def run(self):
		while self.running:
			self.fartnet.loop()

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

	main_window.closed.connect(fartnet_thread.stop)
	main_window.closed.connect(app.exit)
 
	sys.exit(app.exec_())