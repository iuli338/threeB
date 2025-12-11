from picamera2 import Picamera2
import time

# Initialize the camera
picam2 = Picamera2()

# Configure video recording settings
video_config = picam2.create_video_configuration(main={"size": (1280, 720), "format": "YUV420"})
picam2.configure(video_config)

# Create an H264 encoder
from picamera2.encoders import H264Encoder
encoder = H264Encoder(bitrate=10000000)  # 10 Mbps bitrate

# Create file output
from picamera2.outputs import FileOutput
output = FileOutput("my_video.h264")

print("Starting recording...")
print("Press Ctrl+C to stop")

try:
    # Start the camera
    picam2.start()
    time.sleep(2)  # Give camera time to adjust to lighting
    
    # Start recording with encoder and output
    picam2.start_recording(encoder, output)
    print("Recording started")
    
    # Record for 10 seconds
    time.sleep(100)
    
    # Stop recording
    picam2.stop_recording()
    print("Recording saved as 'my_video.h264'")

except KeyboardInterrupt:
    # Handle Ctrl+C gracefully
    print("\nStopping recording...")
    picam2.stop_recording()
    print("Recording stopped by user")
    
finally:
    # Stop and close the camera
    picam2.stop()
    print("Camera stopped")