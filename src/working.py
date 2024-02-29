import os
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance


def create_directories(*directories):
    """
    Create directories if they do not exist.

    Args:
    - *directories (str): Variable number of directory paths.
    """
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Directory '{directory}' created successfully.")


# Directories
input_dir = "../scanned"
tmp_output_dir = "../tmp/"
box_output_dir = "../boxed/"

# Create directories
create_directories(tmp_output_dir, box_output_dir)


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff)
    # Bounding box given as a 4-tuple defining the left, upper, right, and lower pixel coordinates.
    # If the image is completely empty, this method returns None.
    bbox = diff.getbbox()
    print(bbox)
    if bbox:
        return im.crop(bbox)


def crop_image(m_image_path, m_output_path, m_top_left, m_top_right, m_bottom_left):
    """
    Crop the input image, convert it to grayscale, threshold it, and save the result as a TIFF image.

    Args:
    - m_image_path (str): Path to the input image.
    - m_output_path (str): Path to save the cropped and processed image.
    - m_top_left (tuple): Coordinates of the top-left corner for cropping.
    - m_top_right (tuple): Coordinates of the top-right corner for cropping.
    - m_bottom_left (tuple): Coordinates of the bottom-left corner for cropping.
    """
    # Open the image
    img = Image.open(m_image_path)

    # Crop the image
    cropped_img = img.crop((m_top_left[0], m_top_left[1], m_top_right[0], m_bottom_left[1]))

    # Convert the cropped image to Grayscale
    bw_image = cropped_img.convert("L")

    # Sharpening the image
    sharpen = ImageEnhance.Sharpness(bw_image).enhance(2.0)

    # Threshold the grayscale image to create a binary image
    binary_img = sharpen.point(lambda px: 0 if px < 150 else 255, '1')

    # Save the binary image as a TIFF file
    print('Saving cropped image into:', m_output_path)
    binary_img.save(m_output_path, format='TIFF')


def crop_to_boxes(m_tmp_output_dir, m_box_output_dir):
    odd_row_height = 84
    even_row_height = 118
    file_index = 1

    for file_name in os.listdir(m_tmp_output_dir):
        if file_name.endswith(".tif"):
            tiff_path = os.path.join(m_tmp_output_dir, file_name)
            img = Image.open(tiff_path)
            print('Width:', img.width)
            left, upper, right, lower = 0, 0, img.width, 0

            for row_index in range(1, 31):
                if row_index % 2 == 0:
                    lower += even_row_height
                else:
                    lower += odd_row_height

                print('Lower:', lower)
                cropped_img = img.crop((left, upper, right, lower))

                if row_index % 2 == 0:
                    upper += odd_row_height
                else:
                    upper += even_row_height

                box_output_path = os.path.join(m_box_output_dir, f"line_{file_index}.tif")
                print('Saving: ', box_output_path)
                trimmed_img = trim(cropped_img)
                trimmed_img.save(box_output_path)
                file_index += 1


if __name__ == "__main__":
    # Below dimension specific to the images in scanned directory
    top_left = (236, 236)
    top_right = (2244, 236)
    bottom_left = (236, 3267)
    bottom_right = (2244, 3268)

    """
        Convert PNG images in the input directory to TIFF format and save them in the temporary output directory.

        Args:
        - input_dir (str): Path to the directory containing PNG images.
        - tmp_output_dir (str): Path to the temporary output directory.
        - top_left (tuple): Coordinates of the top-left corner for cropping.
        - top_right (tuple): Coordinates of the top-right corner for cropping.
        - bottom_left (tuple): Coordinates of the bottom-left corner for cropping.
        """
    for filename in os.listdir(input_dir):
        if filename.endswith(".png"):
            try:
                # Input and output paths
                image_path = os.path.join(input_dir, filename)
                output_path = os.path.join(tmp_output_dir, os.path.splitext(filename)[0] + '.tif')

                # Perform image conversion and cropping
                crop_image(image_path, output_path, top_left, top_right, bottom_left)

                print(f"Converted {filename} to TIFF format successfully.")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    crop_to_boxes(tmp_output_dir, box_output_dir)
