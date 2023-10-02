from paho.mqtt import client

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
		self.current_preset = self.presets[index]
		for reactor in self.current_preset:
			self.send_command_list(self.current_preset[reactor]["preset"], reactor)
			self.apply_variation(0)

	def apply_variation(self, index):
		for reactor in self.current_preset:
			self.send_command_list(self.current_preset[reactor]["variations"][index], reactor)

	def apply_palette(self, index):
		for reactor in self.reactors:
			for i, color in enumerate(self.palettes[int(index)]):
				self.client.publish("reactor/" + reactor + "/color/" + str(i), color) 
  
	reactors = [
		"MagnatBoxen",
		"RatDerGeleerten",
		"tollerESP"
	]

	palettes = [
		[ # palette 1, the entire hue spectrum divided equally into 8 colors
			"FF0000", "FFBF00", "80FF00", "00FF40", "00FFFF", "0040FF", "8000FF", "FF00BF"
		]
	]
	presets = {
		0: {
			"MagnatBoxen": {
				"preset": [
					("focus", "simpleSync"),
					("input/channel", "256"),
     				("input/smooth", "5")
				],
				"variations": {
					0: [("input/colorindex", "0")],
					1: [("input/colorindex", "4")],
					2: [("input/colorindex", "2")],
					3: [("input/colorindex", "6")],
				}
			}
		},
		1: [
			
		],
	}

mqtt = mqtt_sender()