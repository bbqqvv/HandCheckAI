import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import os
import openpyxl
from openpyxl.styles import Font, Alignment
from datetime import datetime

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.4,  # Tăng độ tin cậy phát hiện
    min_tracking_confidence=0.4,   # Tăng độ tin cậy theo dõi
    model_complexity=1
)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class HandAngleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Angle Measurement Pro")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))

        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create image display area
        self.create_image_display()

        # Create control panel
        self.create_control_panel()

        # Create info panel
        self.create_info_panel()

        # Initialize variables
        self.current_image = None
        self.image_paths = []
        self.current_index = 0
        self.data_to_save = []

        # Bind keyboard shortcuts
        self.root.bind('<Left>', self.prev_image)
        self.root.bind('<Right>', self.next_image)

    def create_image_display(self):
        """Create the image display area with canvas and navigation"""
        img_frame = ttk.Frame(self.main_frame)
        img_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Navigation buttons
        nav_frame = ttk.Frame(img_frame)
        nav_frame.pack(fill=tk.X, pady=5)

        self.prev_btn = ttk.Button(
            nav_frame,
            text="◀ Previous",
            command=self.prev_image,
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(
            nav_frame,
            text="Next ▶",
            command=self.next_image,
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.RIGHT, padx=5)

        # Image canvas
        self.canvas_frame = ttk.Frame(img_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg='white',
            highlightthickness=1,
            highlightbackground='#cccccc'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Status label
        self.status_label = ttk.Label(
            nav_frame,
            text="No images loaded",
            style='Header.TLabel'
        )
        self.status_label.pack(side=tk.TOP, fill=tk.X, pady=5)

    def create_control_panel(self):
        """Create the control panel with buttons"""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Button styles
        self.style.configure('Primary.TButton', foreground='black', background='#0078d7')
        self.style.map('Primary.TButton',
                       background=[('active', '#005fa3'), ('pressed', '#004d84')])

        ttk.Button(
            control_frame,
            text="Open Images",
            command=self.open_images,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Process All",
            command=self.process_all_images,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Save Results",
            command=self.save_results,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Clear All",
            command=self.clear_all,
            style='Primary.TButton'
        ).pack(side=tk.RIGHT, padx=5)

    def create_info_panel(self):
        """Create the information display panel"""
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)

        # Info label
        ttk.Label(
            info_frame,
            text="Measurement Results",
            style='Header.TLabel'
        ).pack(fill=tk.X, pady=(0, 5))

        # Text area with scrollbar
        text_frame = ttk.Frame(info_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.info_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            height=10,
            width=100,
            font=('Consolas', 10),
            padx=5,
            pady=5
        )
        scrollbar = ttk.Scrollbar(text_frame, command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)

        # Add some padding at the bottom
        ttk.Frame(info_frame, height=10).pack(fill=tk.X)

    def calculate_angle_with_vertical(self, a, b):
        """Calculate the angle between two points relative to vertical"""
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

    def preprocess_image(self, image):
        """Apply image preprocessing for better hand detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply GaussianBlur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(blurred)

        # Normalize the image
        normalized = cv2.normalize(equalized, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        # Sharpen the image
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        sharpened = cv2.filter2D(normalized, -1, kernel)

        return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

    def process_image(self, image_path):
        """Process a single image and detect hand angles"""
        image_name = os.path.basename(image_path)
        print(f"Processing image: {image_name}")

        image = cv2.imread(image_path)
        if image is None:
            print(f"Could not read image from path: {image_path}")
            return None, None, None

        # Resize large images to speed up processing
        if max(image.shape) > 1000:
            scale = 1000 / max(image.shape)
            image = cv2.resize(image, (0, 0), fx=scale, fy=scale)

        image = self.preprocess_image(image)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        angles = []
        image_with_landmarks = np.copy(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks with custom style
                mp_drawing.draw_landmarks(
                    image_with_landmarks,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

                # Get wrist and middle finger tip coordinates
                wrist = [
                    hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * image.shape[1],
                    hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * image.shape[0]
                ]
                middle_finger_tip = [
                    hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * image.shape[1],
                    hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * image.shape[0]
                ]

                # Calculate angle and add to results
                angle = self.calculate_angle_with_vertical(wrist, middle_finger_tip)
                angles.append(angle)

                # Draw angle information on the image
                cv2.putText(
                    image_with_landmarks,
                    f"{angle:.1f}°",
                    (int(wrist[0]), int(wrist[1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 0, 0),
                    2
                )

        return image_with_landmarks, angles, image_name

    def display_image(self, image, angles, image_name):
        """Display the processed image with landmarks"""
        # Convert to PIL Image and resize for display
        pil_image = Image.fromarray(image)

        # Calculate display size while maintaining aspect ratio
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:  # Handle initial sizing
            canvas_width = 600
            canvas_height = 400

        img_ratio = pil_image.width / pil_image.height
        canvas_ratio = canvas_width / canvas_height

        if img_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(canvas_width / img_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * img_ratio)

        pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)

        # Display on canvas
        self.current_image = ImageTk.PhotoImage(image=pil_image)
        self.canvas.delete("all")
        self.canvas.create_image(
            (canvas_width - new_width) // 2,
            (canvas_height - new_height) // 2,
            anchor=tk.NW,
            image=self.current_image
        )

        # Update status label
        self.status_label.config(text=f"Image {self.current_index + 1} of {len(self.image_paths)}: {image_name}")

        # Update info text
        self.update_info_text(image_name, angles)

        # Update navigation buttons
        self.update_navigation_buttons()

    def update_info_text(self, image_name, angles):
        """Update the information text area with results"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        self.info_text.insert(tk.END, f"📄 Image: {image_name}\n", 'bold')
        self.info_text.insert(tk.END, f"📅 Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        if angles:
            for i, angle in enumerate(angles):
                self.info_text.insert(tk.END, f"✋ Hand {i + 1}:\n", 'bold')
                self.info_text.insert(tk.END, f"  Angle between wrist and middle finger: {angle:.2f}°\n\n")

                # Add color coding based on angle
                if abs(angle) < 15:
                    self.info_text.insert(tk.END, "  Interpretation: Nearly vertical\n\n", 'good')
                elif angle > 0:
                    self.info_text.insert(tk.END, "  Interpretation: Tilted to the right\n\n", 'warning')
                else:
                    self.info_text.insert(tk.END, "  Interpretation: Tilted to the left\n\n", 'warning')
        else:
            self.info_text.insert(tk.END, "❌ No hands detected in the image\n", 'error')

        self.info_text.tag_config('bold', font=('Consolas', 10, 'bold'))
        self.info_text.tag_config('good', foreground='green')
        self.info_text.tag_config('warning', foreground='orange')
        self.info_text.tag_config('error', foreground='red')
        self.info_text.config(state=tk.DISABLED)

    def update_navigation_buttons(self):
        """Enable/disable navigation buttons based on current position"""
        self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_index < len(self.image_paths) - 1 else tk.DISABLED)

    def open_images(self):
        """Open file dialog to select images"""
        file_paths = filedialog.askopenfilenames(
            title="Select Hand Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )

        if file_paths:
            self.image_paths = list(file_paths)
            self.current_index = 0
            self.data_to_save = []

            if len(self.image_paths) > 0:
                self.process_and_display_current_image()
                messagebox.showinfo(
                    "Images Loaded",
                    f"Successfully loaded {len(self.image_paths)} images.\n\n"
                    "Use the navigation buttons or keyboard arrows to browse."
                )

    def process_and_display_current_image(self):
        """Process and display the current image"""
        if 0 <= self.current_index < len(self.image_paths):
            image_path = self.image_paths[self.current_index]
            image, angles, image_name = self.process_image(image_path)

            if image is not None:
                self.display_image(image, angles, image_name)

                # Save results for Excel export
                if angles:
                    for i, angle in enumerate(angles):
                        self.data_to_save.append([image_name, f"Hand {i + 1}", angle])

    def process_all_images(self):
        """Process all loaded images in batch"""
        if not self.image_paths:
            messagebox.showwarning("No Images", "Please load images first.")
            return

        self.data_to_save = []  # Clear previous results

        progress_window = tk.Toplevel(self.root)
        progress_window.title("Processing Images")
        progress_window.geometry("400x100")
        progress_window.resizable(False, False)

        tk.Label(
            progress_window,
            text="Processing images, please wait...",
            font=('Arial', 10)
        ).pack(pady=10)

        progress = ttk.Progressbar(
            progress_window,
            orient=tk.HORIZONTAL,
            length=300,
            mode='determinate'
        )
        progress.pack(pady=5)
        progress_window.update()

        try:
            for i, image_path in enumerate(self.image_paths):
                image, angles, image_name = self.process_image(image_path)

                if angles:
                    for j, angle in enumerate(angles):
                        self.data_to_save.append([image_name, f"Hand {j + 1}", angle])

                progress['value'] = (i + 1) / len(self.image_paths) * 100
                progress_window.update()

            progress_window.destroy()
            messagebox.showinfo(
                "Processing Complete",
                f"Successfully processed {len(self.image_paths)} images.\n"
                f"Found {len(self.data_to_save)} hand measurements."
            )

            # Show first image
            self.current_index = 0
            self.process_and_display_current_image()

        except Exception as e:
            progress_window.destroy()
            messagebox.showerror("Error", f"An error occurred during processing:\n{str(e)}")

    def save_results(self):
        """Save measurement results to Excel file"""
        if not self.data_to_save:
            messagebox.showwarning("No Data", "No measurement data to save.")
            return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Hand Measurements"

            # Write headers with formatting
            headers = ["Image Name", "Hand", "Angle (Degrees)", "Interpretation"]
            ws.append(headers)

            # Format headers
            for cell in ws[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')

            # Write data rows
            for row in self.data_to_save:
                image_name, hand, angle = row
                interpretation = self.get_interpretation(float(angle))
                ws.append([image_name, hand, float(angle), interpretation])

            # Auto-size columns
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter

                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                adjusted_width = (max_length + 2) * 1.2
                ws.column_dimensions[column].width = adjusted_width

            # Format angle column
            for row in ws.iter_rows(min_row=2, max_col=3, max_row=ws.max_row):
                for cell in row[2:3]:
                    cell.number_format = '0.00'

            # Save file
            default_filename = f"hand_measurements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            excel_file = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=default_filename
            )

            if excel_file:
                wb.save(excel_file)
                messagebox.showinfo(
                    "Save Successful",
                    f"Measurement data saved to:\n{excel_file}"
                )

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save Excel file:\n{str(e)}")

    def get_interpretation(self, angle):
        """Get interpretation text for the angle"""
        if abs(angle) < 15:
            return "Nearly vertical"
        elif angle > 0:
            return f"Tilted {angle:.1f}° to the right"
        else:
            return f"Tilted {abs(angle):.1f}° to the left"

    def prev_image(self, event=None):
        """Show previous image"""
        if self.current_index > 0:
            self.current_index -= 1
            self.process_and_display_current_image()

    def next_image(self, event=None):
        """Show next image"""
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.process_and_display_current_image()

    def clear_all(self):
        """Clear all loaded images and results"""
        self.image_paths = []
        self.current_index = 0
        self.data_to_save = []

        self.canvas.delete("all")
        self.status_label.config(text="No images loaded")

        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "Ready to process hand images.\n\n")
        self.info_text.insert(tk.END, "1. Click 'Open Images' to load hand images\n")
        self.info_text.insert(tk.END, "2. Use 'Process All' to batch process images\n")
        self.info_text.insert(tk.END, "3. Save results to Excel when finished")
        self.info_text.config(state=tk.DISABLED)

        self.update_navigation_buttons()


if __name__ == "__main__":
    root = tk.Tk()
    app = HandAngleApp(root)

    # Set initial info text
    app.clear_all()

    root.mainloop()