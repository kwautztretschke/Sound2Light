import argparse
import pyaudio
import numpy as np
from progress.bar import Bar
import socket
import time

# Constants for audio settings
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

# Persistent variable to track the maximum energy encountered
max_energy = 2e7  # Set initial value to 20 million (2e7)
min_energy_cap = 2e7  # Set the minimum cap to 20 million (2e7)
decay_factor = 0.995  # Decay factor (adjust as needed)

new_audio_data = False # Flag to show work needs to be done
normalized_energy = 0 # this is where the loudness of the current chunk is stored

# List to store Art-Net IP addresses
fartnet_ips = []
sequence_number = 0 # sequence number for artnet packets

# Global flags for commandline arguments
console = False
framerate = False

# Variable to track the frame count
global_frame_count = 0

def parse_arguments():
	parser = argparse.ArgumentParser(description="Stream audio loudness to specified Art-Net IP address.")
	parser.add_argument("-a", "--artnet", metavar="ARTNET_IP_ADDRESS", required=True, action='append',
						help="Art-Net IP address to stream loudness to.")
	parser.add_argument("-c", "--console", action='store_true', help="Display the progress bar in the console.")
	parser.add_argument("-f", "--framerate", action='store_true', help="Display the frequency (frame rate) of the UDP colors being sent out.")
	args = parser.parse_args()

	global fartnet_ips, console, framerate
	fartnet_ips = args.artnet
	console = args.console
	framerate = args.framerate

def normalize_energy(energy):
	global max_energy

	# Update the maximum energy and apply the decay factor
	max_energy = max(energy, max_energy * decay_factor, min_energy_cap)

	# Normalize the energy value to fit within the progress bar range (0 to 255)
	normalized_energy = int(energy / max_energy * 255)

	return normalized_energy

def audio_stream_callback(in_data, frame_count, time_info, status_flags):
	# Convert the binary audio data to a numpy array of 32-bit floating-point numbers (float32)
	audio_data = np.frombuffer(in_data, dtype=np.int16).astype(np.float32)

	# Calculate the squared magnitude (energy) of the audio data
	energy = np.sum(audio_data**2) / len(audio_data)

	# Normalize the energy value to fit within the progress bar range (0 to 255)
	global normalized_energy
	normalized_energy = normalize_energy(energy)

	# Set the flag to symbolize we need to do work
	global new_audio_data
	new_audio_data = True

	# Return None for the output audio data (playback stream is not used)
	return None, pyaudio.paContinue

def send_art_dmx_packet(ip_address, universe, data):
	global sequence_number
	sequence_number = (sequence_number + 1) & 0xFF  # Increment and wrap around to 16-bit value

	# Ensure the data length is not greater than 512 bytes
	data = data[:512]

	# Create the header
	header = bytearray()
	header.extend(b'Art-Net\x00')  # 8 bytes: Protocol ID (fixed string with null terminator)
	header.extend(b'\x00\x50')     # 2 bytes: OpCode (ArtDmx = 0x5000)
	header.extend(b'\x00\x0e')     # 2 bytes: Protocol version (14)
	header.extend(sequence_number.to_bytes(1, byteorder='big'))  # 1 byte: Sequence number (8-bit)
	header.extend(0x00.to_bytes(1, byteorder='big'))  # 1 byte: Physical port (set to 0)
	header.extend(universe.to_bytes(2, byteorder='big'))  # 2 bytes: Universe number (15-bit)
	header.extend(len(data).to_bytes(2, byteorder='big'))  # 2 bytes: Data length (16-bit)

	
	# Combine the header and data
	art_dmx_packet = header + data

	# Send the packet
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(art_dmx_packet, (ip_address, 6454))
	sock.close()

def main():
	# Parse command-line arguments
	parse_arguments()
 
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

	global new_audio_data
 
	try:
		while stream.is_active():
			if new_audio_data:
				new_audio_data = False

				# Print the energy (loudness) value as a bar graph
				if console:
					bar = Bar('Loudness (Energy)', max=255)
					bar.goto(normalized_energy)
					bar.finish()

				# Update the Art-Net devices with the normalized loudness value
				for ip in fartnet_ips:
					send_art_dmx_packet(ip, 0, bytearray([normalized_energy]))

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

	# Terminate PyAudio
	p.terminate()

if __name__ == "__main__":
	main()
