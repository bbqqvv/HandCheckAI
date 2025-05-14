import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class ImageCanvas(ttk.Frame):
    """Custom widget for displaying images with navigation."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.current_image = None
        self.image_paths = []
        self.current_index = 0

        self.create_widgets()

    def create_widgets(self):
        """Initialize all UI components."""
        # Navigation frame
        self.nav_frame = ttk.Frame(self)
        self.nav_frame.pack(fill=tk.X, pady=5)

        # Navigation buttons
        self.prev_btn = ttk.Button(
            self.nav_frame,
            text="◀ Previous",
            command=self.prev_image,
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(
            self.nav_frame,
            text="Next ▶",
            command=self.next_image,
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.RIGHT, padx=5)

        # Status label
        self.status_label = ttk.Label(
            self.nav_frame,
            text="No images loaded",
            font=('Arial', 12, 'bold')
        )
        self.status_label.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Canvas for image display
        self.canvas = tk.Canvas(
            self,
            bg='white',
            highlightthickness=1,
            highlightbackground='#cccccc'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def display_image(self, image, image_name):
        """Display the processed image on canvas."""
        pil_image = Image.fromarray(image)

        # Calculate display size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
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

        # Update status
        self.status_label.config(
            text=f"Image {self.current_index + 1} of {len(self.image_paths)}: {image_name}"
        )
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Enable/disable navigation buttons."""
        self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_index < len(self.image_paths) - 1 else tk.DISABLED)

    def prev_image(self):
        """Show previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False

    def next_image(self):
        """Show next image."""
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            return True
        return False

    def clear(self):
        """Clear the canvas."""
        self.image_paths = []
        self.current_index = 0
        self.canvas.delete("all")
        self.status_label.config(text="No images loaded")
        self.update_navigation_buttons()