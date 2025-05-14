import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from hand_angle_measurement.models.measurement import MeasurementExporter
from hand_angle_measurement.processor import ImageProcessor
from hand_angle_measurement.widgets.image_canvas import ImageCanvas
from hand_angle_measurement.widgets.info_panel import InfoPanel
from datetime import datetime


class HandAngleApp:
    """Main application class for Hand Angle Measurement."""

    def __init__(self, root):
        self.root = root
        self.root.title("Hand Angle Measurement Pro")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # Initialize components
        self.image_processor = ImageProcessor()
        self.measurement_exporter = MeasurementExporter()

        # Create UI
        self.create_widgets()

        # Initialize variables
        self.image_paths = []
        self.current_index = 0

    def create_widgets(self):
        """Create all UI components."""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create image display area
        self.image_canvas = ImageCanvas(self.main_frame)
        self.image_canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create control panel
        self.create_control_panel()

        # Create info panel
        self.info_panel = InfoPanel(self.main_frame)
        self.info_panel.pack(fill=tk.BOTH, expand=True)

        # Bind keyboard shortcuts
        self.root.bind('<Left>', lambda e: self.navigate_image('prev'))
        self.root.bind('<Right>', lambda e: self.navigate_image('next'))

    def create_control_panel(self):
        """Create the control panel with buttons."""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Button styles
        style = ttk.Style()
        style.configure('Primary.TButton', foreground='black', background='#0078d7')
        style.map('Primary.TButton',
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

    def open_images(self):
        """Open file dialog to select images."""
        file_paths = filedialog.askopenfilenames(
            title="Select Hand Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )

        if file_paths:
            self.image_paths = list(file_paths)
            self.current_index = 0
            self.image_canvas.image_paths = self.image_paths
            self.image_canvas.current_index = self.current_index

            if len(self.image_paths) > 0:
                self.process_current_image()
                messagebox.showinfo(
                    "Images Loaded",
                    f"Successfully loaded {len(self.image_paths)} images.\n\n"
                    "Use the navigation buttons or keyboard arrows to browse."
                )

    def process_current_image(self):
        """Process and display the current image."""
        if 0 <= self.current_index < len(self.image_paths):
            image_path = self.image_paths[self.current_index]
            image, angles, image_name = self.image_processor.process_image(image_path)

            if image is not None:
                self.image_canvas.display_image(image, image_name)
                self.info_panel.update_info(image_name, angles)

                # Save results for export
                if angles:
                    for i, angle in enumerate(angles):
                        self.measurement_exporter.add_measurement(
                            image_name, f"Hand {i + 1}", angle
                        )

    def process_all_images(self):
        """Process all loaded images in batch."""
        if not self.image_paths:
            messagebox.showwarning("No Images", "Please load images first.")
            return

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
                image, angles, image_name = self.image_processor.process_image(image_path)

                if angles:
                    for j, angle in enumerate(angles):
                        self.measurement_exporter.add_measurement(
                            image_name, f"Hand {j + 1}", angle
                        )

                progress['value'] = (i + 1) / len(self.image_paths) * 100
                progress_window.update()

            progress_window.destroy()
            messagebox.showinfo(
                "Processing Complete",
                f"Successfully processed {len(self.image_paths)} images.\n"
                f"Found {len(self.measurement_exporter.data)} hand measurements."
            )

            # Show first image
            self.current_index = 0
            self.image_canvas.current_index = self.current_index
            self.process_current_image()

        except Exception as e:
            progress_window.destroy()
            messagebox.showerror("Error", f"An error occurred during processing:\n{str(e)}")

    def save_results(self):
        """Save measurement results to Excel file."""
        if not self.measurement_exporter.data:
            messagebox.showwarning("No Data", "No measurement data to save.")
            return

        default_filename = f"hand_measurements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        excel_file = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=default_filename
        )

        if excel_file:
            success = self.measurement_exporter.export_to_excel(excel_file)
            if success:
                messagebox.showinfo(
                    "Save Successful",
                    f"Measurement data saved to:\n{excel_file}"
                )
            else:
                messagebox.showerror("Save Error", "Failed to save Excel file")

    def navigate_image(self, direction):
        """Navigate between images."""
        if direction == 'prev' and self.image_canvas.prev_image():
            self.current_index = self.image_canvas.current_index
            self.process_current_image()
        elif direction == 'next' and self.image_canvas.next_image():
            self.current_index = self.image_canvas.current_index
            self.process_current_image()

    def clear_all(self):
        """Clear all loaded images and results."""
        self.image_paths = []
        self.current_index = 0
        self.measurement_exporter = MeasurementExporter()
        self.image_canvas.clear()
        self.info_panel.clear()


def main():
    """Entry point for the application."""
    root = tk.Tk()
    app = HandAngleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()