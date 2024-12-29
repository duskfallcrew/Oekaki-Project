# data_io.py
import os
from PyQt6.QtWidgets import QMessageBox, QFileDialog
def save_image_and_label(canvas, text, file_path):
    if file_path:
            # Generate the image name and description name
            base_name = os.path.splitext(file_path)[0]

            image_path = f"{base_name}.png"
            description_path = f"{base_name}.txt"

            # Save image and label
            canvas.save_canvas(image_path)

            with open(description_path, "w") as f:
                f.write(text)

            QMessageBox.information(None, "Success!",
                                    f"Image and label saved to {os.path.basename(os.path.dirname(file_path))}\\{os.path.basename(base_name)}.[png or txt]")
