import cv2
import os
import matplotlib.pyplot as plt


def crop_center(image, width, height):
    """Crops the image to the specified width and height centered around the image center."""
    h, w = image.shape[:2]
    center_x, center_y = w // 2, h // 2

    # Calculate crop boundaries
    x1 = max(center_x - width // 2, 0)
    x2 = min(center_x + width // 2, w)
    y1 = max(center_y - height // 2, 0)
    y2 = min(center_y + height // 2, h)

    return image[y1:y2, x1:x2]


def process_and_save_all_images(input_folder, output_folder, crop_width, crop_height):
    """Processes all images in the input folder and saves them in the output folder."""
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # List all files in the input folder
    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    processed_files = []  # To keep track of processed files for comparison

    for file_name in files:
        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}_crop{os.path.splitext(file_name)[1]}")

        # Load the image
        orig_image = cv2.imread(input_path)
        if orig_image is None:
            print(f"Skipping {file_name}: Unable to read the file.")
            continue

        # Crop the image
        cropped_image = crop_center(orig_image, crop_width, crop_height)

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


def main(input_folder, output_folder, crop_width, crop_height):
    """Main function to process and compare images."""
    processed_files = process_and_save_all_images(input_folder, output_folder, crop_width, crop_height)
    display_comparisons(processed_files)


# 실행 코드
if __name__ == "__main__":
    input_folder = './test_datasets/00'
    output_folder = './output_datasets'
    crop_width = 818
    crop_height = 818

    main(input_folder, output_folder, crop_width, crop_height)
