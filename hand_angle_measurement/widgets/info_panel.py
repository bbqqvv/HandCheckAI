import tkinter as tk
from tkinter import ttk
from datetime import datetime


class InfoPanel(ttk.Frame):
    """Custom widget for displaying measurement information."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.create_widgets()
        self.set_default_text()

    def create_widgets(self):
        """Initialize all UI components."""
        # Header label
        ttk.Label(
            self,
            text="Measurement Results",
            font=('Arial', 12, 'bold')
        ).pack(fill=tk.X, pady=(0, 5))

        # Text area with scrollbar
        text_frame = ttk.Frame(self)
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
        ttk.Frame(self, height=10).pack(fill=tk.X)

    def set_default_text(self):
        """Set the default help text."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "Ready to process hand images.\n\n")
        self.info_text.insert(tk.END, "1. Click 'Open Images' to load hand images\n")
        self.info_text.insert(tk.END, "2. Use 'Process All' to batch process images\n")
        self.info_text.insert(tk.END, "3. Save results to Excel when finished")
        self.info_text.config(state=tk.DISABLED)

    def update_info(self, image_name, angles):
        """Update the information with new measurement results."""
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

    def clear(self):
        """Clear the information panel."""
        self.set_default_text()