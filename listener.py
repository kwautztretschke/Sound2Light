import socket
from progress.bar import Bar

def print_header(data, addr):
	# Check if the packet starts with "Art-Net" in the header
	if data[:8] == b'Art-Net\x00':
		# Extract information from the header
		opcode = int.from_bytes(data[8:10], byteorder='little')
		protocol_version = int.from_bytes(data[10:12], byteorder='big')
		sequence_number = int(data[12])
		physical_port = int(data[13])
		universe = int.from_bytes(data[14:16], byteorder='big')
		data_length = int.from_bytes(data[16:18], byteorder='big') 

		print(f"Received Art-Net packet from {addr}:")
		print(f"  OpCode: 0x{opcode:X}")
		print(f"  Protocol Version: {protocol_version}")
		print(f"  Sequence Number: {sequence_number}")
		print(f"  Physical Port: {physical_port}")
		print(f"  Universe: {universe}")
		print(f"  Data Length: {data_length}")
		print()

def print_bar(name, value):
	bar = Bar(name, max=255)
	bar.goto(value)
	bar.finish()

def print_spectrum(data):
	for h in range(0,5):
		print(f"{255-h*51:3d} |", end='')
		for w in range(0, 127):
			if data[w] > (255-h*51):
				print("#", end='')
			else:
				print(" ", end='')
		print("|")

def print_data(data):
	# First 128 bytes are mono audio data and general information	
	print("Mono audio data and general information:")
	#print_spectrum(data[0:128])
	print_bar("Mono Energy", data[0])
	# Next 128 bytes are stereo data
	print("\nStereo audio data:")
	#print_spectrum(data[128:256])
	print_bar("Left Energy ", data[128])
	print_bar("Right Energy", data[129])
	# last 256 bytes are FFT data, which we print in two lines of equalizer
	print("\nFFT data (lower):")
	print_spectrum(data[256:384])
	print("FFT data (upper):")
	print_spectrum(data[384:512])

def receive_art_dmx_packet():
	UDP_IP = "0.0.0.0"  # Listen on all available network interfaces
	UDP_PORT = 6454

	# Create a UDP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))

	while True:
		data, addr = sock.recvfrom(530)  # Receive up to 530 bytes (header + 512 data bytes)
		print("\033c", end='')
		print_header(data, addr)
		print_data(data[18:])
		print("\r", end='')


# Start listening for Art-Net packets
print("Listening for Art-Net packets...")
receive_art_dmx_packet()