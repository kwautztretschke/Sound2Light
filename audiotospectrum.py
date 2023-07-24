import argparse
import pyaudio
import numpy as np
from progress.bar import Bar
import socket

# Constants for audio settings
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

# Persistent variable to track the maximum energy encountered
max_energy = 2e7  # Set initial value to 20 million (2e7)
min_energy_cap = 2e7  # Set the minimum cap to 20 million (2e7)
decay_factor = 0.995  # Decay factor (adjust as needed)

# List to store IP addresses and their corresponding color hex codes as tuples
ip_colors = []

def parse_arguments():
    parser = argparse.ArgumentParser(description="Stream audio loudness to specified IP addresses with colors.")
    parser.add_argument("-u", "--udp", nargs=2, action='append', metavar=("IP_ADDRESS", "HEX_CODE"),
                        help="IP addresses and color hex codes to stream to. "
                             "Usage: -u <ip address> <hex code> -u <ip address> <hex code>...",
                        required=True)
    args = parser.parse_args()

    # Create a list of tuples with IP addresses and their corresponding color hex codes
    for udp_object in args.udp:
        if len(udp_object) != 2:
            raise ValueError("Each IP address must have a corresponding color hex code.")
        ip_address = udp_object[0]
        hex_code = udp_object[1]
        ip_colors.append((ip_address, hex_code))

def normalize_energy(energy):
    global max_energy

    # Update the maximum energy and apply the decay factor
    max_energy = max(energy, max_energy * decay_factor, min_energy_cap)

    # Normalize the energy value to fit within the progress bar range (0 to 255)
    normalized_energy = int(energy / max_energy * 255)

    return normalized_energy

def send_color_to_ip(ip, color_hex, loudness):
    # Convert the color hex code to RGB values
    red = int(color_hex[1:3], 16)
    green = int(color_hex[3:5], 16)
    blue = int(color_hex[5:7], 16)

    # Scale the RGB values based on the loudness
    scaled_red = red * loudness // 255
    scaled_green = green * loudness // 255
    scaled_blue = blue * loudness // 255

    # Send the color to the specified IP address via UDP
    color_bytes = bytes([4, scaled_red, scaled_green, scaled_blue])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(color_bytes, (ip, 26091))
    sock.close()

def audio_stream_callback(in_data, frame_count, time_info, status_flags):
    # Convert the binary audio data to a numpy array of 32-bit floating-point numbers (float32)
    audio_data = np.frombuffer(in_data, dtype=np.int16).astype(np.float32)

    # Calculate the squared magnitude (energy) of the audio data
    energy = np.sum(audio_data**2) / len(audio_data)

    # Normalize the energy value to fit within the progress bar range (0 to 255)
    normalized_energy = normalize_energy(energy)

    # Print the energy (loudness) value as a bar graph
    bar = Bar('Loudness (Energy)', max=255)
    bar.goto(normalized_energy)
    bar.finish()

    # Update the colors for each IP address with the scaled loudness value
    for ip, color_hex in ip_colors:
        send_color_to_ip(ip, color_hex, normalized_energy)

    # Return None for the output audio data (playback stream is not used)
    return None, pyaudio.paContinue

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

    try:
        while stream.is_active():
            pass
    except KeyboardInterrupt:
        pass

    # Stop and close the audio stream
    stream.stop_stream()
    stream.close()

    # Terminate PyAudio
    p.terminate()

if __name__ == "__main__":
    main()
