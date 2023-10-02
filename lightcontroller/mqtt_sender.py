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

	def apply_variation(self, index):
		for reactor in self.current_preset:
			self.send_command_list(self.current_preset[reactor]["variations"][index], reactor)

	def apply_palette(self, index):
		for reactor in self.reactors:
			for i, color in enumerate(self.palettes[int(index)]):
				self.client.publish("reactor/" + reactor + "/color/" + str(i), color) 
  
	reactors = [
		"MagnatBoxen",
		"middle",
		"left",
		"right"
	]

	palettes = [
		[ # palette 1, the entire hue spectrum divided equally into 8 colors
			"FF0000", "FFBF00", "80FF00", "00FF40", "00FFFF", "0040FF", "8000FF", "FF00BF"
		]
	]
	presets = {
		0: { # all simpleSync, Boxen on the Bass, rest on volume. Good for drops.
			"MagnatBoxen": {
				"preset": [
					("focus", "simpleSync"),
					("input/channel", "256"),
     				("input/smooth", "5"),
					("input/colorindex", "0"),
				],
				"variations": {
					0: [("input/colorindex", "0")],
					1: [("input/colorindex", "2")],
					2: [("input/colorindex", "4")],
					3: [("input/colorindex", "6")],
				},
			},
			"middle": {
				"preset": [
					("focus", "simpleSync"),
					("input/channel", "0"),
	 				("input/smooth", "3"),
					("input/colorindex", "1"),
				],
				"variations": {
					0: [("input/colorindex", "1")],
					1: [("input/colorindex", "3")],
					2: [("input/colorindex", "5")],
					3: [("input/colorindex", "7")],
				},
			},
			"left": {
				"preset": [
					("focus", "simpleSync"),
					("input/channel", "128"),
	 				("input/smooth", "5"),
					("input/colorindex", "1"),
				],
				"variations": {
					0: [("input/colorindex", "1")],
					1: [("input/colorindex", "3")],
					2: [("input/colorindex", "5")],
					3: [("input/colorindex", "7")],
				},
			},
			"right": {
				"preset": [
					("focus", "simpleSync"),
					("input/channel", "129"),
	 				("input/smooth", "5"),
					("input/colorindex", "1"),
				],
				"variations": {
					0: [("input/colorindex", "1")],
					1: [("input/colorindex", "3")],
					2: [("input/colorindex", "5")],
					3: [("input/colorindex", "7")],
				},
			},
		},
		1: { # combination of barsync, and simple. Good for anything. Very stereo
			"MagnatBoxen": {
				"preset": [
					("focus", "simpleStereoSync"),
					("input/channel/L", "128"),
					("input/channel/R", "129"),
	 				("input/smooth/L", "3"),
	 				("input/smooth/R", "3"),
					("input/colorindex", "0"),
					("input/colorindexoffset", "1")
				],
				"variations": {
					0: [("input/colorindex", "0")],
					1: [("input/colorindex", "2")],
					2: [("input/colorindex", "4")],
					3: [("input/colorindex", "6")],
				},
			},
			"middle": {
				"preset": [
					("focus", "barFadeStereoSync"),
					("input/channel/L", "128"),
					("input/channel/R", "129"),
	 				("input/smooth/L", "3"),
	 				("input/smooth/R", "3"),
					("input/mode", "IN"),
					("input/colorindex", "1"),
					("input/colorindexoffset", "-1"),
				],
				"variations": {
					0: [("input/colorindex", "1")],
					1: [("input/colorindex", "3")],
					2: [("input/colorindex", "5")],
					3: [("input/colorindex", "7")],
					4: [("input/mode", "IN")],
					5: [("input/mode", "OUT")],
				},
			},
			"left": {
				"preset": [
					("focus", "barFadeSync"),
					("input/channel", "128"),
	 				("input/smooth", "5"),
					("input/mode", "R2L"),
					("input/colorindex", "0"),
				],
				"variations": {
					0: [("input/colorindex", "0")],
					1: [("input/colorindex", "2")],
					2: [("input/colorindex", "4")],
					3: [("input/colorindex", "6")],
					4: [("input/mode", "R2L")],
					5: [("input/mode", "L2R")],
				},
			},
			"right": {
				"preset": [
					("focus", "barFadeSync"),
					("input/channel", "129"),
	 				("input/smooth", "5"),
					("input/mode", "R2L"),
					("input/colorindex", "1")
				],
				"variations": {
					0: [("input/colorindex", "1")],
					1: [("input/colorindex", "3")],
					2: [("input/colorindex", "5")],
					3: [("input/colorindex", "7")],
					4: [("input/mode", "R2L")],
					5: [("input/mode", "L2R")],
				},
			},
		},
		2: { # some rippling, good for calm sections
			"MagnatBoxen": {
				"preset": [
					("focus", "barFadeSync"),
					("input/channel", "256"),
     				("input/smooth", "5"),
				],
				"variations": {
					0: [("input/colorindex", "0")],
					1: [("input/colorindex", "2")],
					2: [("input/colorindex", "4")],
					3: [("input/colorindex", "6")],
				},
			},
			"middle": {
				"preset": [
					("focus", "rippleSync"),
					("input/channel", "0"),
	 				("input/smooth", "3"),
					("input/mode", "IN"),
					("input/interval", "10"),
				],
				"variations": {
					0: [("input/colorindex", "1")],
					1: [("input/colorindex", "3")],
					2: [("input/colorindex", "5")],
					3: [("input/colorindex", "7")],
					4: [("input/mode", "IN")],
					5: [("input/mode", "OUT")],
					6: [("input/mode", "R2L")],
					7: [("input/mode", "L2R")],
				},
			},
			"left": {
				"preset": [
					("focus", "rippleSync"),
					("input/channel", "0"),
	 				("input/smooth", "5"),
					("input/mode", "R2L"),
					("input/interval", "10"),
				],
				"variations": {
					0: [("input/colorindex", "1")],
					1: [("input/colorindex", "3")],
					2: [("input/colorindex", "5")],
					3: [("input/colorindex", "7")],
					4: [("input/mode", "R2L")],
					5: [("input/mode", "L2R")],
					6: [("input/mode", "R2L")],
					7: [("input/mode", "L2R")],
				},
			},
			"right": {
				"preset": [
					("focus", "rippleSync"),
					("input/channel", "0"),
	 				("input/smooth", "5"),
					("input/mode", "R2L"),
					("input/interval", "10"),
				],
				"variations": {
					0: [("input/colorindex", "1")],
					1: [("input/colorindex", "3")],
					2: [("input/colorindex", "5")],
					3: [("input/colorindex", "7")],
					4: [("input/mode", "R2L")],
					5: [("input/mode", "L2R")],
					6: [("input/mode", "L2R")],
					7: [("input/mode", "R2L")],
				},
			},
		},
	}

mqtt = mqtt_sender()