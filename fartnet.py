import pyaudio
import numpy as np
import socket


# Global variables to store the audio data
new_audio_data = False # Flag to show work needs to be done
audio_raw_r = None
audio_raw_l = None

# global audio stream callback TODO somehow put this in the fartnet class
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

class fartnet:
	# Class variables for some constant parameters
	CHUNK_SIZE = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 44100
	MIN_ENERGY_CAP = 2e7  # Set the minimum cap to 20 million (2e7)
	MIN_FFT_CAP = np.ones(int(CHUNK_SIZE/2))*0.25e6  
	DECAY_FACTOR = 0.995  # Decay factor (adjust as needed)
 
	def __init__(self, artnet_ips, input_device_index=None):
		# set member variables from constructor arguments
		self.input_device_index = input_device_index
		self.artnet_sender = artnet_sender(artnet_ips)

		# Persistent variables for audio processing TODO put these in a closure maybe?
		self.max_energy = 2e7 # Set initial value to 20 million (2e7)
		self.max_energy_fft_l = np.zeros(int(fartnet.CHUNK_SIZE/2))
		self.max_energy_fft_r = np.zeros(int(fartnet.CHUNK_SIZE/2))
 
		# Initialize PyAudio
		self.p = pyaudio.PyAudio()

		# Create the audio stream from the default input source
		self.stream = self.p.open(format=fartnet.FORMAT,
						channels=fartnet.CHANNELS,
						rate=fartnet.RATE,
						input=True,
						input_device_index=self.input_device_index,
						frames_per_buffer=fartnet.CHUNK_SIZE,
						stream_callback=audio_stream_callback)

		# Start the stream
		self.stream.start_stream()

	def loop(self):
		global new_audio_data
		if not self.stream.is_active() or not new_audio_data:
			return False

		new_audio_data = False
		# retreive metrics from the audio data
		energy, energy_l, energy_r, fft_data_l, fft_data_r = self.analyze_audio_data()

		# Update the Art-Net devices with the normalized loudness value
		self.artnet_sender.send_packets(energy, energy_l, energy_r, fft_data_l, fft_data_r)

	def close(self):
		# Close the Art-Net sender
		self.artnet_sender.close()

		# Stop and close the audio stream
		self.stream.stop_stream()
		self.stream.close()

		# Terminate PyAudio
		self.p.terminate()

	def analyze_audio_data(self):
		# Calculate the squared magnitude (energy) of the audio data, update the maximum energy, and apply the decay factor, then normalize
		energy_l = np.sum(audio_raw_l.astype(np.float32)**2) / len(audio_raw_l)
		energy_r = np.sum(audio_raw_r.astype(np.float32)**2) / len(audio_raw_r)
		self.max_energy = max(energy_l, energy_r, self.max_energy * fartnet.DECAY_FACTOR, fartnet.MIN_ENERGY_CAP)
		energy_l = int(energy_l / self.max_energy * 255)
		energy_r = int(energy_r / self.max_energy * 255)
		energy = int((energy_l + energy_r) / 2)

		# do a fourier transform on the audio data, take the absolute value, and only use the first half of the data
		fft_raw_l = np.zeros(int(fartnet.CHUNK_SIZE/2))
		fft_raw_r = np.zeros(int(fartnet.CHUNK_SIZE/2))
		fft_raw_l = np.fft.fft(audio_raw_l)
		fft_raw_l = np.abs(fft_raw_l)
		fft_raw_l = fft_raw_l[:int(fartnet.CHUNK_SIZE/2)]
		fft_raw_r = np.fft.fft(audio_raw_r)
		fft_raw_r = np.abs(fft_raw_r)
		fft_raw_r = fft_raw_r[:int(fartnet.CHUNK_SIZE/2)]

		# update the maximum energy for each bucket, apply the decay factor, and normalize
		self.max_energy_fft_l = np.maximum(fft_raw_l, self.max_energy_fft_l * fartnet.DECAY_FACTOR)
		self.max_energy_fft_r = np.maximum(fft_raw_r, self.max_energy_fft_r * fartnet.DECAY_FACTOR)
		# make sure the max_energy doesn't go below the minimum cap
		self.max_energy_fft_l = np.maximum(self.max_energy_fft_l, fartnet.MIN_FFT_CAP)
		self.max_energy_fft_r = np.maximum(self.max_energy_fft_r, fartnet.MIN_FFT_CAP)

		fft_data_l = fft_raw_l / self.max_energy_fft_l * 255
		fft_data_r = fft_raw_r / self.max_energy_fft_r * 255

		return energy, energy_l, energy_r, fft_data_l, fft_data_r


class artnet_sender:
	def __init__(self, artnet_ips, universe=0):
		self.artnet_ips = artnet_ips
		self.universe = universe
		self.sequence_number = 0
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.datagram = bytearray(512)

	def send_packets(self, energy, energy_l, energy_r, fft_data_l, fft_data_r):
		self.sequence_number = (self.sequence_number + 1) & 0xFF  # Increment and wrap around to 16-bit value

		# Ensure the data length is not greater than 512 bytes
		data = self.compose_dmx_frame(energy, energy_l, energy_r, fft_data_l, fft_data_r)
		# Create the header
		header = bytearray()
		header.extend(b'Art-Net\x00')  # 8 bytes String: Protocol ID (fixed string with null terminator)
		header.extend(b'\x00\x50')     # 2 bytes Little Endian: OpCode (ArtDmx = 0x5000)
		header.extend(b'\x00\x0e')     # 2 bytes Big Endian: Protocol version (14)
		header.extend(self.sequence_number.to_bytes(1, byteorder='big'))  # 1 byte: Sequence number (8-bit)
		header.extend(0x00.to_bytes(1, byteorder='big'))  # 1 byte: Physical port (set to 0)
		header.extend(self.universe.to_bytes(2, byteorder='little'))  # 2 bytes Little Endian: Universe number (15-bit)
		header.extend(len(data).to_bytes(2, byteorder='big'))  # 2 bytes Big Endian: Data length (16-bit)
		# Combine the header and data
		art_dmx_packet = header + data
		# Send the packet to all the Art-Net devices
		for ip in self.artnet_ips:
			self.sock.sendto(art_dmx_packet, (ip, 6454))

	def compose_dmx_frame(self, energy, energy_l, energy_r, fft_data_l, fft_data_r):
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

	def close(self):
		self.sock.close()
	


if __name__ == "__main__":
	# Create the fartnet instance
	fartnet = fartnet(["127.0.0.1"])
	try:
		while True:
			fartnet.loop()
	except KeyboardInterrupt:
		pass
	
	fartnet.close()