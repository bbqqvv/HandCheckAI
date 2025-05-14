import os
from datetime import datetime


def get_timestamp():
    """Get current timestamp in a standard format."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def validate_image_file(file_path):
    """Check if a file is a valid image file."""
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    return os.path.isfile(file_path) and file_path.lower().endswith(valid_extensions)


def create_output_directory():
    """Create an output directory if it doesn't exist."""
    output_dir = os.path.join(os.getcwd(), 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir