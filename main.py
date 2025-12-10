from picamera2 import Picamera2
from PIL import Image, ImageTk
import tkinter as tk

def update_frame():
    frame = picam2.capture_array()
    img = Image.fromarray(frame)

    # păstrăm aspectul, fără stretch
    img = img.resize((640, 480), Image.Resampling.LANCZOS)

    imgtk = ImageTk.PhotoImage(image=img)
    label.imgtk = imgtk
    label.configure(image=imgtk)

    root.after(10, update_frame)

# ---- CAMERA ----
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.set_controls({"ScalerCrop": (0, 0, 640, 480)})
picam2.start()

# ---- TKINTER ----
root = tk.Tk()
root.title("Camera Preview")

label = tk.Label(root, width=640, height=480)
label.pack()

update_frame()
root.mainloop()
