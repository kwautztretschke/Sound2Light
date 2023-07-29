import argparse
import pyaudio
import numpy as np
from progress.bar import Bar
import matplotlib as mpl
import matplotlib.style as mplstyle
mplstyle.use('fast')
mpl.use('TkAgg')
mpl.rcParams['toolbar'] = 'None'
mpl.rcParams['path.simplify'] = True
mpl.rcParams['path.simplify_threshold'] = 1.0
mpl.rcParams['agg.path.chunksize'] = 10000
import matplotlib.pyplot as plt
import socket
import time
import paho.mqtt.client as paho

# Constants for audio settings
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

# MQTT config
broker_address = "10.69.0.69"

# Persistent variable to track the maximum energy encountered
max_energy = 2e7  # Set initial value to 20 million (2e7)
min_energy_cap = 2e7  # Set the minimum cap to 20 million (2e7)
decay_factor = 0.995  # Decay factor (adjust as needed)

# Global variables to store the audio data
new_audio_data = False # Flag to show work needs to be done
right_channel = None
left_channel = None

# List to store Art-Net IP addresses
fartnet_ips = []
sequence_number = 0 # sequence number for artnet packets

# more global trash for the plot

# Global flags for commandline arguments
console = False
framerate = False
mqtt = False
plot = False

# Variable to track the frame count
global_frame_count = 0

def parse_arguments():
	parser = argparse.ArgumentParser(description="Stream audio loudness to specified Art-Net IP address.")
	parser.add_argument("-a", "--artnet", metavar="ARTNET_IP_ADDRESS", action='append',
						help="Art-Net IP address to stream loudness to.")
	parser.add_argument("-c", "--console", action='store_true', help="Display the progress bar in the console.")
	parser.add_argument("-p", "--plot", action='store_true', help="Display a plot of the FFT data.")
	parser.add_argument("-f", "--framerate", action='store_true', help="Display the frequency (frame rate) of the UDP colors being sent out.")
	parser.add_argument("-m", "--mqtt", action='store_true', help="Send a message over MQTT that music is playing.")
	args = parser.parse_args()

	global fartnet_ips, console, framerate, mqtt, plot
	fartnet_ips = args.artnet
	console = args.console
	framerate = args.framerate
	mqtt = args.mqtt
	plot = args.plot


def audio_stream_callback(in_data, frame_count, time_info, status_flags):
	global new_audio_data, left_channel, right_channel
	# Convert the binary audio data to a numpy array of 32-bit floating-point numbers (float32)
	audio_data = np.frombuffer(in_data, dtype=np.int16)
	left_channel = audio_data[::2]
	right_channel = audio_data[1::2]
	# Set the flag to symbolize we need to do work
	new_audio_data = True
	# Return None for the output audio data (playback stream is not used)
	return None, pyaudio.paContinue


def analyze_audio_data():
	# Calculate the squared magnitude (energy) of the audio data, update the maximum energy, and apply the decay factor, then normalize
	energy_l = np.sum(left_channel**2) / len(left_channel)
	energy_r = np.sum(right_channel**2) / len(right_channel)
	global max_energy, min_energy_cap, decay_factor
	max_energy = max(energy_l, energy_r, max_energy * decay_factor, min_energy_cap)
	energy_l = int(energy_l / max_energy * 255)
	energy_r = int(energy_r / max_energy * 255)
	energy = int((energy_l + energy_r) / 2)

	# do a fourier transform on the audio data, take the absolute value, and only use the first half of the data
	fft_data_l = np.fft.fft(left_channel)
	fft_data_l = np.abs(fft_data_l)
	fft_data_l = fft_data_l[:int(CHUNK_SIZE/2)]
	fft_data_r = np.fft.fft(right_channel)
	fft_data_r = np.abs(fft_data_r)
	fft_data_r = fft_data_r[:int(CHUNK_SIZE/2)]  

	return energy, energy_l, energy_r, fft_data_l, fft_data_r

def console_bar(energy_l, energy_r):
	bar1 = Bar('Left  :', max=255)
	bar1.goto(energy_l)
	bar1.finish()
	bar2 = Bar('Right :', max=255)
	bar2.goto(energy_r)
	bar2.finish()
    
def plot_fft(left_channel, right_channel):
	plt.clf()
	plt.plot(left_channel)
	plt.plot(right_channel)
	plt.ylim(0, 3e6)
	plt.xlim(0, 128)
	#plt.axvline()
	plt.pause(0.001)
	plt.draw()

def send_art_dmx_packet(ip_address, universe, data):
	global sequence_number
	sequence_number = (sequence_number + 1) & 0xFF  # Increment and wrap around to 16-bit value

	# Ensure the data length is not greater than 512 bytes
	data = data[:512]

	# Create the header
	header = bytearray()
	header.extend(b'Art-Net\x00')  # 8 bytes String: Protocol ID (fixed string with null terminator)
	header.extend(b'\x00\x50')     # 2 bytes Little Endian: OpCode (ArtDmx = 0x5000)
	header.extend(b'\x00\x0e')     # 2 bytes Big Endian: Protocol version (14)
	header.extend(sequence_number.to_bytes(1, byteorder='big'))  # 1 byte: Sequence number (8-bit)
	header.extend(0x00.to_bytes(1, byteorder='big'))  # 1 byte: Physical port (set to 0)
	header.extend(universe.to_bytes(2, byteorder='little'))  # 2 bytes Little Endian: Universe number (15-bit)
	header.extend(len(data).to_bytes(2, byteorder='big'))  # 2 bytes Big Endian: Data length (16-bit)

	
	# Combine the header and data
	art_dmx_packet = header + data

	# Send the packet
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(art_dmx_packet, (ip_address, 6454))
	sock.close()

def main():
	# Parse command-line arguments
	parse_arguments()

	# Signal the smart home that music is playing
	if mqtt:
		mqtt_client = paho.Client()
		mqtt_client.connect(broker_address, 1883)
		mqtt_client.publish("state/bedroom/music", "playing", qos=1, retain=True)
 
	# Initialize PyAudio
	p = pyaudio.PyAudio()

	# Create the audio stream from the default input source
	stream = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					input_device_index=None,  # Use the default input source
					frames_per_buffer=CHUNK_SIZE,
					stream_callback=audio_stream_callback)

	# Start the stream
	stream.start_stream()

	# Track the start time for calculating the frame rate
	start_time = time.time()

 
	try:
		while stream.is_active():
			global new_audio_data
			if new_audio_data:
				new_audio_data = False

				# retreive metrics from the audio data
				energy, energy_l, energy_r, fft_data_l, fft_data_r = analyze_audio_data()

				# Print the energy (loudness) value as a bar graph
				if console:
					console_bar(energy_l, energy_r)

				# Plot the FFT data
				if plot:
					plot_fft(fft_data_l, fft_data_r)	
        
				# Update the Art-Net devices with the normalized loudness value
				if fartnet_ips:
					for ip in fartnet_ips:
						send_art_dmx_packet(ip, 0, bytearray([energy]))

				# Increment the frame count
				global global_frame_count
				global_frame_count += 1

	except KeyboardInterrupt:
		pass

	# Calculate the frame rate (frequency) if the -f or --framerate flag is provided
	if framerate:
		elapsed_time = time.time() - start_time
		frames_per_second = global_frame_count / elapsed_time
		print(f"Frequency (Frame Rate): {frames_per_second:.2f} Hz")

	# Stop and close the audio stream
	stream.stop_stream()
	stream.close()

	# Signal the smart home the music is no longer playing
	if mqtt:
		mqtt_client.publish("state/bedroom/music", "off", qos=1, retain=True)
		mqtt_client.disconnect()

	# Terminate PyAudio
	p.terminate()

if __name__ == "__main__":
	main()
