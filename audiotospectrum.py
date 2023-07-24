import pyaudio
import numpy as np
from progress.bar import Bar

# Constants for audio settings
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

# Persistent variable to track the maximum energy encountered
max_energy = 1.0  # Initial value set to 1.0 to avoid division by zero

def normalize_energy(energy):
    global max_energy

    # Update the maximum energy if the current energy is higher
    max_energy = max(max_energy, energy)

    # Normalize the energy value to fit within the progress bar range (0 to 100)
    normalized_energy = energy / max_energy * 100

    return normalized_energy

def audio_stream_callback(in_data, frame_count, time_info, status_flags):
    # Convert the binary audio data to a numpy array of 32-bit floating-point numbers (float32)
    audio_data = np.frombuffer(in_data, dtype=np.int16).astype(np.float32)

    # Calculate the squared magnitude (energy) of the audio data
    energy = np.sum(audio_data**2) / len(audio_data)

    # Normalize the energy value to fit within the progress bar range (0 to 100)
    normalized_energy = normalize_energy(energy)

    # Print the energy (loudness) value as a bar graph
    bar = Bar('Loudness (Energy)', max=100)
    bar.goto(int(normalized_energy))
    bar.finish()

    # Return None for the output audio data (playback stream is not used)
    return None, pyaudio.paContinue

def main():
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
