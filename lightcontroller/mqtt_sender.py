from paho.mqtt import client
from .presets_test import presets, palettes, reactors

mqtt_broker = '10.69.0.69'
mqtt_port = 1883

class mqtt_sender:
	def __init__(self):
		self.client = client.Client("lightcontroller_frontend")
		# self.client.on_message = self.on_message
		try:
			self.client.connect(mqtt_broker, mqtt_port)
			print("Connected to MQTT Broker")
			self.client.loop_start()
		except:
			print("Could not connect to MQTT Broker")
	
	def send_command_list(self, list, reactor):
		for topic, message in list:
			self.client.publish("reactor/" + reactor + "/" + topic, message)
 
	current_preset = {} 
	def apply_preset(self, index):
		try:
			self.current_preset = presets[index]
			for reactor in self.current_preset:
				try:
					self.send_command_list(self.current_preset[reactor]["preset"], reactor)
				except: 
					print("Could not apply preset" + str(index) + " to " + reactor)
		except:
			print("Could not apply preset " + str(index))

	def apply_variation(self, index):
		for reactor in self.current_preset:
			try:
				self.send_command_list(self.current_preset[reactor]["variations"][index], reactor)
			except:
				print("Could not apply variation " + str(index) + " to " + reactor)

	def apply_palette(self, index):
		for reactor in reactors:
			for i, color in enumerate(palettes[int(index)]):
				self.client.publish("reactor/" + reactor + "/color/" + str(i), color) 

mqtt = mqtt_sender()