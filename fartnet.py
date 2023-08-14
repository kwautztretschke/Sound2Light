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
max_energy_fft_l = np.zeros(int(CHUNK_SIZE/2))
max_energy_fft_r = np.zeros(int(CHUNK_SIZE/2))
min_energy_cap = 2e7  # Set the minimum cap to 20 million (2e7)
min_fft_cap = np.ones(int(CHUNK_SIZE/2))*0.25e6  
decay_factor = 0.995  # Decay factor (adjust as needed)

# Global variables to store the audio data
new_audio_data = False # Flag to show work needs to be done
audio_raw_r = None
audio_raw_l = None
fft_raw_l = np.zeros(int(CHUNK_SIZE/2))
fft_raw_r = np.zeros(int(CHUNK_SIZE/2))

# List to store Art-Net IP addresses
fartnet_ips = []
sequence_number = 0 # sequence number for artnet packets

# more global trash for the plot

# Global flags for commandline arguments
console = False
framerate = False
mqtt = False
plot = 0

# Variable to track the frame count
global_frame_count = 0

def parse_arguments():
	parser = argparse.ArgumentParser(description="Stream audio loudness to specified Art-Net IP address.")
	parser.add_argument("-a", "--artnet", metavar="ARTNET_IP_ADDRESS", action='append',
						help="Art-Net IP address to stream loudness to.")
	parser.add_argument("-c", "--console", action='store_true', help="Display the progress bar in the console.")
	parser.add_argument("-p", "--plot", type=int, help="Display a plot of the FFT data.")
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
	global new_audio_data, audio_raw_l, audio_raw_r
	# Convert the binary audio data to a numpy array of 32-bit floating-point numbers (float32)
	audio_data = np.frombuffer(in_data, dtype=np.int16)
	audio_raw_l = audio_data[::2]
	audio_raw_r = audio_data[1::2]
	# Set the flag to symbolize we need to do work
	new_audio_data = True
	# Return None for the output audio data (playback stream is not used)
	return None, pyaudio.paContinue


def analyze_audio_data():
	# Calculate the squared magnitude (energy) of the audio data, update the maximum energy, and apply the decay factor, then normalize
	energy_l = np.sum(audio_raw_l.astype(np.float32)**2) / len(audio_raw_l)
	energy_r = np.sum(audio_raw_r.astype(np.float32)**2) / len(audio_raw_r)
	global max_energy, min_energy_cap, decay_factor
	max_energy = max(energy_l, energy_r, max_energy * decay_factor, min_energy_cap)
	energy_l = int(energy_l / max_energy * 255)
	energy_r = int(energy_r / max_energy * 255)
	energy = int((energy_l + energy_r) / 2)

	# do a fourier transform on the audio data, take the absolute value, and only use the first half of the data
	global fft_raw_l, fft_raw_r
	fft_raw_l = np.fft.fft(audio_raw_l)
	fft_raw_l = np.abs(fft_raw_l)
	fft_raw_l = fft_raw_l[:int(CHUNK_SIZE/2)]
	fft_raw_r = np.fft.fft(audio_raw_r)
	fft_raw_r = np.abs(fft_raw_r)
	fft_raw_r = fft_raw_r[:int(CHUNK_SIZE/2)]
	# update the maximum energy for each bucket, apply the decay factor, and normalize
	global max_energy_fft_l, max_energy_fft_r, min_fft_cap
	max_energy_fft_l = np.maximum(fft_raw_l, max_energy_fft_l * decay_factor)
	max_energy_fft_r = np.maximum(fft_raw_r, max_energy_fft_r * decay_factor)
	# make sure the max_energy doesn't go below the minimum cap
	max_energy_fft_l = np.maximum(max_energy_fft_l, min_fft_cap)
	max_energy_fft_r = np.maximum(max_energy_fft_r, min_fft_cap)

	fft_data_l = fft_raw_l / max_energy_fft_l * 255
	fft_data_r = fft_raw_r / max_energy_fft_r * 255

	return energy, energy_l, energy_r, fft_data_l, fft_data_r

def console_bar(energy_l, energy_r):
	bar1 = Bar('Left  :', max=255)
	bar1.goto(energy_l)
	bar1.finish()
	bar2 = Bar('Right :', max=255)
	bar2.goto(energy_r)
	bar2.finish()

def console_fft(fft_data):
	# clear console
	print("\033c", end='')
	for h in range(0,16):
		print(f"{255-h*16:3d} | ", end='')
		for w in range(0, len(fft_data)):
			if fft_data[w] > (255-h*16):
				print("#", end='')
			else:
				print(" ", end='')
		print()
	# flush the output buffer
	print("\r", end='')
    
def plot_fft(fft_data_l, fft_data_r, datagram):
	plt.clf()
	global fft_raw_l, max_energy_fft_l, plot
	if plot == 1:
		# plot the raw fft data and the maximum in the same diagram
		plt.plot(fft_raw_l, color='blue')
		plt.plot(max_energy_fft_l, color='red')
		plt.ylim(0, 2e6)	
	elif plot == 2:
		# plot the normalized fft data
		plt.plot(fft_data_l, color='blue')
		plt.ylim(0, 255)
	elif plot == 3:
		# plot the raw fft data and the maximum
		plt.subplot(2,1,1)
		plt.plot(fft_raw_l, color='blue')
		plt.plot(max_energy_fft_l, color='red')
		plt.ylim(0, 2e6)
		# add the normalized fft data in a second diagram below the first one
		plt.subplot(2,1,2)	
		plt.plot(fft_data_l, color='blue')
	elif plot == 4:
		plt.plot(datagram)
		plt.ylim(0, 255)
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

def compose_dmx_frame(energy, energy_l, energy_r, fft_data_l, fft_data_r):
	# create a 512 byte bytearray, fill it with zeroes, then populate it with audio data
	datagram = bytearray(512)
	# the first 128 bytes are mono audio data and general information
	datagram[0] = energy
	#todo: low middle and high metrics
	# the next 128 bytes are stereo audio data
	datagram[128] = energy_l
	datagram[129] = energy_r
	#todo: low middle and high metrics (stereo)

	# the next 256 bytes are fft data, but filtered semi logarithmically by frequency
	fft_data = (fft_data_l/2 + fft_data_r/2)
	# the first 128 bytes are just copied from the fft data
	datagram[256:384] = fft_data[:128].astype(np.uint8).tobytes()
	# the next 64 bytes are two buckets of fft data each
	reshaped_half = np.reshape(fft_data[128:256], (-1, 2))
	averages = np.mean(reshaped_half, axis=1)
	datagram[384:448] = averages.astype(np.uint8).tobytes()
	# the last 64 bytes are four buckets of fft data each
	reshaped_quarter = np.reshape(fft_data[256:512], (-1, 4))
	averages = np.mean(reshaped_quarter, axis=1)
	datagram[448:512] = averages.astype(np.uint8).tobytes()
	
	return datagram
	
	

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
					#console_bar(energy_l, energy_r)
					console_fft(fft_data_l[:160])

				# Plot the FFT data
				if plot:
					datagram = compose_dmx_frame(energy, energy_l, energy_r, fft_data_l, fft_data_r)
					plot_fft(fft_data_l, fft_data_r, datagram)	
        
				# Update the Art-Net devices with the normalized loudness value
				if fartnet_ips:
					datagram = compose_dmx_frame(energy, energy_l, energy_r, fft_data_l, fft_data_r)
					for ip in fartnet_ips:
						send_art_dmx_packet(ip, 0, datagram)

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
