# from PIL import Image
# img = Image.open(r"D:\New folder (2)\11566.png")
#
# angle = -100
# rotate_img= img.rotate(angle, expand = True)
# rotate_img.show()

import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, Scrollbar
from PIL import Image, ImageTk
import os
import openpyxl

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7,
                       min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils


def calculate_angle_with_vertical(a, b):
    """Tính góc giữa đường thẳng nối từ a đến b với trục dọc"""
    a = np.array(a)
    b = np.array(b)
    vertical_vector = np.array([0, -1])
    hand_vector = b - a
    hand_vector = hand_vector / np.linalg.norm(hand_vector)

    dot_product = np.dot(hand_vector, vertical_vector)
    cross_product = np.cross(vertical_vector, hand_vector)

    angle_rad = np.arccos(np.clip(dot_product, -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)

    if cross_product < 0:
        angle_deg = -angle_deg

    return angle_deg


def process_image(image_path):
    """Xử lý ảnh và đo góc độ bàn tay"""
    image_name = os.path.basename(image_path)
    print(f"Processing image: {image_name}")

    image = cv2.imread(image_path)
    if image is None:
        print(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
        return None, None, None, None

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    angles = []
    image_with_landmarks = np.copy(image_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image_with_landmarks, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            wrist = [hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * image.shape[1],
                     hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * image.shape[0]]
            middle_finger_tip = [hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * image.shape[1],
                                 hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * image.shape[0]]

            angle = calculate_angle_with_vertical(wrist, middle_finger_tip)
            angles.append(angle)

    if angles:
        return image_with_landmarks, angles, image_name
    else:
        print('Không nhận diện được bàn tay hoặc không đủ điểm đặc trưng.')
        return image_with_landmarks, None, image_name


def display_image(image, angles, image_name):
    """Hiển thị ảnh đã xử lý lên giao diện"""
    image = Image.fromarray(image)
    image.thumbnail((400, 400))
    imgtk = ImageTk.PhotoImage(image=image)

    canvas.delete("all")
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    x_pos = (canvas_width - image.width) / 2
    y_pos = (canvas_height - image.height) / 2
    canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=imgtk)
    canvas.image = imgtk

    info_text.config(state=tk.NORMAL)
    info_text.delete(1.0, tk.END)
    info_text.insert(tk.END, f"Image name: {image_name}\n\n")

    if angles:
        for i, angle in enumerate(angles):
            info_text.insert(tk.END, f'Hand {i + 1}:\n')
            info_text.insert(tk.END, f'Góc giữa cổ tay và ngón tay giữa: {angle:.2f} độ\n\n')

    info_text.config(state=tk.DISABLED)


def save_to_excel(data):
    """Lưu dữ liệu vào file Excel"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hand Angles"

    headers = ["Image Name", "Hand", "Wrist to Middle Finger Angle"]
    ws.append(headers)

    for row in data:
        ws.append(row)

    excel_file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if excel_file:
        wb.save(excel_file)
        print(f"Dữ liệu đã được lưu vào file Excel: {excel_file}")


def open_file_dialog():
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    data_to_save = []

    for file_path in file_paths:
        image, angles, image_name = process_image(file_path)
        if image is not None:
            display_image(image, angles, image_name)

            if angles:
                for i, angle in enumerate(angles):
                    data_to_save.append([image_name, f"Hand {i + 1}", angle])

    if data_to_save:
        save_to_excel(data_to_save)


root = tk.Tk()
root.title("Hand Angle Measurement")
root.geometry("800x600")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(frame, width=600, height=400)
canvas.pack(pady=20)

info_text = tk.Text(frame, wrap=tk.WORD, height=10, width=100)
info_text.pack()

scrollbar = Scrollbar(frame, command=info_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
info_text.config(yscrollcommand=scrollbar.set)

open_button = ttk.Button(root, text="Open Images", command=open_file_dialog)
open_button.pack()

root.mainloop()
