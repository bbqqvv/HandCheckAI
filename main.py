import tkinter as tk

from hand_angle_measurement import HandAngleApp

if __name__ == "__main__":
    root = tk.Tk()
    app = HandAngleApp(root)
    root.mainloop()