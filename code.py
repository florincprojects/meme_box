import time
import board
import digitalio
import os
import random
from audiomp3 import MP3Decoder
from audiopwmio import PWMAudioOut as AudioOut

# Button setup
button = digitalio.DigitalInOut(board.GP22)
button.pull = digitalio.Pull.UP
button_pressed = False
last_button_state = True

# Audio setup
audio = AudioOut(board.GP14)
path = "mp3/"

# File management
mp3_files = []
last_played_file = None

def scan_mp3_files():
    """Scan the mp3 folder and return list of MP3 files"""
    global mp3_files
    try:
        files = os.listdir(path)
        mp3_files = [f for f in files if f.lower().endswith('.mp3')]
        return len(mp3_files) > 0
    except Exception as e:
        print(f"Error scanning MP3 folder: {e}")
        return False

def get_random_file():
    """Get a random MP3 file that's different from the last played file"""
    global last_played_file
    
    if len(mp3_files) == 0:
        return None
    
    # If only one file, return it
    if len(mp3_files) == 1:
        return mp3_files[0]
    
    # Get available files (excluding last played)
    available_files = [f for f in mp3_files if f != last_played_file]
    
    # If somehow all files are filtered out, use all files
    if not available_files:
        available_files = mp3_files
    
    # Select random file
    selected_file = random.choice(available_files)
    last_played_file = selected_file
    
    return selected_file

def play_mp3(filename):
    """Play an MP3 file and wait for completion"""
    try:
        # Open file and create decoder
        mp3_file = open(path + filename, "rb")
        decoder = MP3Decoder(mp3_file)
        
        # Play the audio
        audio.play(decoder)
        
        # Wait for playback to complete
        while audio.playing:
            time.sleep(0.1)  # Small delay to prevent busy waiting
            
    except Exception as e:
        print(f"Error playing {filename}: {e}")
    finally:
        # Clean up resources
        try:
            mp3_file.close()
        except:
            pass

def button_pressed_debounced():
    """Check if button was pressed with debouncing"""
    global button_pressed, last_button_state
    
    current_state = button.value
    
    # Button press detected (transition from high to low)
    if last_button_state and not current_state and not button_pressed:
        button_pressed = True
        last_button_state = current_state
        return True
    
    # Button released (transition from low to high)
    elif not last_button_state and current_state:
        button_pressed = False
        time.sleep(0.05)  # Small debounce delay
    
    last_button_state = current_state
    return False

# Initialize
if not scan_mp3_files():
    print("No MP3 files found! Please add MP3 files to the mp3/ folder.")
    while True:
        time.sleep(1)  # Keep running but do nothing


# Main loop
while True:
    if button_pressed_debounced():
        # Get random file
        filename = get_random_file()
        
        if filename:
            play_mp3(filename)
        else:
            print("No files available to play.")
    
    time.sleep(0.01)  # Small delay to prevent excessive polling

