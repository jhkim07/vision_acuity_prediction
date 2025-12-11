import os
import numpy as np
from PIL import Image
from torchvision import transforms
from tqdm import tqdm

# 이미지 처리 및 텐서 변환
transform = transforms.Compose([
    transforms.ToTensor()
])

def compute_mean_std(image_folder):
    """
    특정 폴더 내 모든 이미지를 읽어 평균(mean)과 표준 편차(std)를 계산합니다.

    Args:
        image_folder (str): 이미지가 포함된 최상위 폴더 경로.

    Returns:
        tuple: 전체 이미지의 채널별 평균과 표준 편차.
    """
    pixel_sum = np.zeros(3)
    pixel_squared_sum = np.zeros(3)
    total_pixels = 0

    # 모든 하위 폴더를 탐색
    for root, _, files in os.walk(image_folder):
        for file in tqdm(files, desc=f"Processing {root}"):
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff')):
                file_path = os.path.join(root, file)
    
                # 이미지 열기 및 텐서 변환
                try:
                    image = Image.open(file_path).convert('RGB')  # RGB로 변환
                    tensor = transform(image)  # (C, H, W)
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")
                    continue

                # 텐서를 NumPy 배열로 변환
                tensor_np = tensor.numpy()

                # 각 채널의 총합과 제곱 합 계산
                pixel_sum += tensor_np.sum(axis=(1, 2))  # 각 채널의 총합
                pixel_squared_sum += (tensor_np ** 2).sum(axis=(1, 2))  # 각 채널의 제곱합
                total_pixels += tensor_np.shape[1] * tensor_np.shape[2]  # 총 픽셀 수

    # 채널별 평균 및 표준 편차 계산
    mean = pixel_sum / total_pixels
    std = np.sqrt((pixel_squared_sum / total_pixels) - (mean ** 2))

    return mean, std

if __name__ == "__main__":
    folder_path = "./preprocessed_va_datasets"  # 이미지 폴더 경로
    mean, std = compute_mean_std(folder_path)

    print("Channel-wise Mean:", mean)
    print("Channel-wise Std:", std)