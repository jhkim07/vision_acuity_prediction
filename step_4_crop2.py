import cv2
import os
import matplotlib.pyplot as plt


def is_corner_black(image, x, y, size):
    """Checks if all corners of a square region are black."""
    h, w = image.shape[:2]
    half_size = size // 2

    corners = [
        (x - half_size, y - half_size),  # Top-left
        (x + half_size, y - half_size),  # Top-right
        (x - half_size, y + half_size),  # Bottom-left
        (x + half_size, y + half_size)   # Bottom-right
    ]

    for cx, cy in corners:
        if cx < 0 or cy < 0 or cx >= w or cy >= h:
            return False  # Out of bounds
        if image[cy, cx].sum() != 0:  # Not black (non-zero pixel value)
            return False
    return True


def crop_image_to_black_square(image):
    """Crops the image to the largest square centered on the image where all corners are black."""
    h, w = image.shape[:2]
    center_x, center_y = w // 2, h // 2
    size = 1  # Initial size of the square

    while size <= min(w, h):
        if is_corner_black(image, center_x, center_y, size):
            break
        size += 2  # Expand the square (must be an odd number for symmetry)

    # Calculate the cropping region
    half_size = size // 2
    x1 = max(center_x - half_size, 0)
    x2 = min(center_x + half_size, w)
    y1 = max(center_y - half_size, 0)
    y2 = min(center_y + half_size, h)

    return image[y1:y2, x1:x2]


def process_and_save_all_images(input_folder, output_folder):
    """Processes all images in the input folder and saves them in the output folder."""
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)
    
    # **`processed_files` 리스트 초기화**
    processed_files = []  # Processed image pairs (original, cropped)

    # **Recursively list all files in the input folder**
    for root, dirs, files in os.walk(input_folder):
        relative_path = os.path.relpath(root, input_folder)
        save_folder = os.path.join(output_folder, relative_path)
        os.makedirs(save_folder, exist_ok=True)  # Ensure subfolder structure is preserved

        for file_name in files:
            input_path = os.path.join(root, file_name)
            output_path = os.path.join(save_folder, f"{os.path.splitext(file_name)[0]}_crop{os.path.splitext(file_name)[1]}")

            # Load the image
            orig_image = cv2.imread(input_path)
            if orig_image is None:
                print(f"Skipping {file_name}: Unable to read the file.")
                continue

            # Crop the image
            cropped_image = crop_image_to_black_square(orig_image)

            # Save the cropped image
            cv2.imwrite(output_path, cropped_image)
            processed_files.append((orig_image, cropped_image))
            print(f"Processed and saved: {output_path}")

    return processed_files

def display_comparisons(processed_files):
    """Displays comparisons for the first 5 and last 5 processed files with size information."""
    num_files = len(processed_files)

    if num_files < 10:
        print("Not enough files to display comparisons. Need at least 10 files.")
        return

    # First 5 and last 5
    comparisons = processed_files[:5] + processed_files[-5:]

    total_comparisons = len(comparisons)  # Total number of comparisons
    total_subplots = total_comparisons * 2  # Each comparison has 2 subplots

    # Plot comparisons
    plt.figure(figsize=(15, 5 * total_comparisons // 2))
    for i, (orig, cropped) in enumerate(comparisons):
        # Original image dimensions
        orig_h, orig_w = orig.shape[:2]
        cropped_h, cropped_w = cropped.shape[:2]

        # Original image
        plt.subplot(total_comparisons, 2, i * 2 + 1)  # Odd subplot index for original
        plt.imshow(cv2.cvtColor(orig, cv2.COLOR_BGR2RGB))
        plt.axis("off")
        plt.title(f"Original Image {i + 1}\n{orig_w}x{orig_h} (W x H)")

        # Cropped image
        plt.subplot(total_comparisons, 2, i * 2 + 2)  # Even subplot index for cropped
        plt.imshow(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        plt.axis("off")
        plt.title(f"Cropped Image {i + 1}\n{cropped_w}x{cropped_h} (W x H)")

    plt.tight_layout()
    plt.show()


def main(input_folder, output_folder):
    """Main function to process and compare images."""
    processed_files = process_and_save_all_images(input_folder, output_folder)
    display_comparisons(processed_files)

# 실행 코드
if __name__ == "__main__":
    input_folder = './va_datasets/06'  # **탑레벨 폴더**
    output_folder = './preprocessed_va_datasets/06'  # **변환 데이터 저장 폴더**

    main(input_folder, output_folder)