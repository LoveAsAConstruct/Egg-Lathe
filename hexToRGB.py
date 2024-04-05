import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def hex_to_rgb(hex_code):
    """Convert hex code to RGB tuple."""
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def create_spectrogram(hex_codes, width=100):
    """
    Create a spectrogram-like visualization from hex codes.
    
    Parameters:
        hex_codes (list): A list of hex code strings.
        width (int): The width of the output image in blocks.
    """
    # Convert hex codes to RGB
    colors = [hex_to_rgb(code) for code in hex_codes if len(code) == 6]
    
    # Calculate the necessary height for the given width
    height = len(colors) // width + (1 if len(colors) % width else 0)
    
    # Create an empty array for the image
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Fill the image array with colors
    for i, color in enumerate(colors):
        row = i // width
        col = i % width
        img[row, col] = color
    
    # Display the image
    plt.figure(figsize=(12, 8))
    plt.imshow(img)
    plt.axis('off')  # Hide axis
    plt.show()

# Example hex codes (shortened for simplicity)

# Load the CSV file
file_path = 'path_to_your_file.csv'  # Update this to your actual file path
df = pd.read_csv(file_path, sep=';')  # Adjust the separator if necessary

# Ensure the 'Data' column is a string type, then concatenate
hex_codes = ' '.join(df['Data'].dropna().astype(str))

print(hex_codes)

# Adjust 'width' as needed to change the visualization's shape
create_spectrogram(hex_codes, width=5)
