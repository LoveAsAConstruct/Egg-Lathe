from PIL import Image
import numpy as np

def file_to_image_rgb(file_path, output_image_path):
    # Read file binary data
    with open(file_path, 'rb') as file:
        file_bytes = file.read()

    # Convert to bits
    bits = ''.join(format(byte, '08b') for byte in file_bytes)

    # Since we're now using 3 bits per pixel (for R, G, and B), we need to adjust the calculation of the side length
    # Each pixel now represents 3 bits, so the number of pixels is total bits / 3
    num_pixels = len(bits) // 3
    side_length = int(np.ceil(np.sqrt(num_pixels)))

    # Create an RGB image array filled with 0s (black)
    # The shape is (height, width, 3) where 3 is for the RGB channels
    image_array = np.zeros((side_length, side_length, 3), dtype=np.uint8)

    # Iterate over the bits in steps of 3 to fill the image array with RGB values
    for i in range(0, len(bits) - 2, 3):  # Subtract 2 to ensure we have groups of 3 bits
        r_bit, g_bit, b_bit = bits[i], bits[i+1], bits[i+2]
        # Calculate the pixel position
        pixel_index = i // 3
        x, y = pixel_index // side_length, pixel_index % side_length
        # Set the RGB values based on the bits
        # Each bit (0 or 1) is scaled to 255 for the color value
        image_array[x, y] = [int(r_bit) * 255, int(g_bit) * 255, int(b_bit) * 255]

    # Create and save the image
    img = Image.fromarray(image_array, 'RGB')
    img.save(output_image_path)

# Example usage
file_path = 'Production/Lathe Application.zip'  # Path to your binary file
output_image_path = 'output_rgb_application_file.png'
file_to_image_rgb(file_path, output_image_path)
