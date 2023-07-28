import socket
from progress.bar import Bar

def receive_art_dmx_packet():
	UDP_IP = "0.0.0.0"  # Listen on all available network interfaces
	UDP_PORT = 6454

	# Create a UDP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))

	while True:
		data, addr = sock.recvfrom(530)  # Receive up to 530 bytes (header + 512 data bytes)
		
		for b in range(0, 18):
			print(f"{data[b]:02X} ", end='')
		print()

		# Check if the packet starts with "Art-Net" in the header
		if data[:8] == b'Art-Net\x00':
			# Extract information from the header
			opcode = int.from_bytes(data[8:10], byteorder='little')
			protocol_version = int.from_bytes(data[10:12], byteorder='big')
			sequence_number = int(data[12])
			physical_port = int(data[13])
			universe = int.from_bytes(data[14:16], byteorder='big')
			data_length = int.from_bytes(data[16:18], byteorder='big') 

			# Extract the first byte of the data
			first_data_byte = data[18]

			print(f"Received Art-Net packet from {addr}:")
			print(f"  OpCode: 0x{opcode:X}")
			print(f"  Protocol Version: {protocol_version}")
			print(f"  Sequence Number: {sequence_number}")
			print(f"  Physical Port: {physical_port}")
			print(f"  Universe: {universe}")
			print(f"  Data Length: {data_length}")
			bar = Bar('  First Data Byte', max=255)
			bar.goto(first_data_byte)
			bar.finish()
			print()

# Start listening for Art-Net packets
print("Listening for Art-Net packets...")
receive_art_dmx_packet()