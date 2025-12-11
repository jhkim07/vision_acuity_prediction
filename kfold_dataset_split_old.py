import os
import json
import numpy as np
from sklearn.model_selection import KFold
import random

# === FUNCTION DEFINITIONS ===

def read_file_data(folder_path):
    """
    Reads all BMP files in a specified folder.
    Args:
        folder_path (str): Path to the folder containing BMP files.
    Returns:
        list: A list of BMP file names.
    """
    file_data = []
    for file_name in os.listdir(folder_path):  # 폴더 내 파일 이름 반복
        if file_name.endswith(".bmp"):  # BMP 파일만 선택
            file_data.append(file_name)
    return file_data

def calculate_test_size_random(patient_ids, patients, test_ratio=0.2, random_state=None):
    """
    Randomly selects patient IDs for the test dataset.
    Args:
        patient_ids (list): List of unique patient IDs.
        patients (dict): Dictionary mapping patient IDs to their respective files.
        test_ratio (float): Proportion of the dataset to allocate to testing.
        random_state (int, optional): Random seed for reproducibility.
    Returns:
        tuple: (selected_test_ids, actual_test_ratio, random_state)
    """
    # 각 환자의 데이터 크기 계산
    patient_sizes = [len(patients[pid]) for pid in patient_ids]
    total_data_size = sum(patient_sizes)  # 전체 데이터 크기
    test_data_target_size = int(total_data_size * test_ratio)  # 목표 테스트 데이터 크기

    # 랜덤 시드 설정 및 환자 ID 섞기
    if random_state is None:
        random_state = np.random.randint(0, 10000)
    random.seed(random_state)
    shuffled_patient_ids = random.sample(patient_ids, len(patient_ids))  # 무작위 섞기

    # 테스트 데이터로 선택된 환자 ID
    selected_test_ids = []
    current_test_size = 0
    for pid in shuffled_patient_ids:
        size = len(patients[pid])  # 해당 환자의 데이터 크기
        if current_test_size + size > test_data_target_size:
            break  # 목표 크기를 초과하면 중지
        selected_test_ids.append(pid)
        current_test_size += size

    # 실제 테스트 비율 계산
    actual_test_ratio = current_test_size / total_data_size
    return selected_test_ids, actual_test_ratio, random_state

# === MAIN PROGRAM ===
def main():
    # === CONSTANT VARIABLES ===
    DATA_FOLDER = "./test_datasets/00"  # 데이터 파일이 저장된 폴더 경로
    TEST_RATIO = 0.15               # 테스트 데이터 비율 (20%)
    K_FOLDS = 5                    # K-Fold에서 Fold 수
    OUTPUT_TEST_PATH = "./data_split/test_data.json"         # 테스트 데이터 저장 경로
    OUTPUT_TRAIN_PATH = "./data_split/train_data.json"       # 훈련 데이터 저장 경로
    OUTPUT_VAL_PATH = "./data_split/validation_data.json"    # 검증 데이터 저장 경로
    OUTPUT_ALL_PATIENTS_PATH = "./data_split/all_patients_split.json"  # 모든 환자 ID 저장 경로

    # Step 1: 데이터 읽기
    data = read_file_data(DATA_FOLDER)

    # Step 2: 데이터 환자 ID로 그룹화
    patients = {}
    for item in data:
        patient_id = item.split("_")[0]  # 파일 이름에서 환자 ID 추출
        if patient_id not in patients:
            patients[patient_id] = []
        patients[patient_id].append(item)

    patient_ids = list(patients.keys())

    # Step 3: 테스트 데이터 분리
    selected_test_ids, actual_test_ratio, test_random_state = calculate_test_size_random(
        patient_ids, patients, TEST_RATIO
    )
    remaining_ids = [pid for pid in patient_ids if pid not in selected_test_ids]  # 테스트 제외 환자 ID

    print("selected_test_ids, actual_test_ratio", selected_test_ids, actual_test_ratio)
    print("remaining_ids", remaining_ids)
    # 테스트 데이터 생성 (고정된 데이터)
    test_data = []
    for pid in selected_test_ids:
        test_data.extend(patients[pid])

    # K-Fold 정보를 저장할 리스트 초기화
    train_patients_splits = []
    val_patients_splits = []
    train_dataset = []  # K-Fold 훈련 데이터 리스트
    val_dataset = []    # K-Fold 검증 데이터 리스트

    # Step 4: K-Fold 분할
    n_splits = min(K_FOLDS, len(remaining_ids))  # Fold 수를 남은 환자 수 이하로 조정
    if n_splits > 1:
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=np.random.randint(0, 10000))

        for fold_idx, (train_idx, val_idx) in enumerate(kf.split(remaining_ids)):
            # Train 환자와 Validation 환자 ID 분리
            train_patients = [remaining_ids[i] for i in train_idx]
            val_patients = [remaining_ids[i] for i in val_idx]

            # Train 데이터 생성
            train_data = []
            for pid in train_patients:
                train_data.extend(patients[pid])

            # Validation 데이터 생성
            val_data = []
            for pid in val_patients:
                val_data.extend(patients[pid])

            # 각 Fold의 Train 및 Validation 데이터를 저장
            train_dataset.append({"fold_idx": fold_idx + 1, "data": train_data})
            val_dataset.append({"fold_idx": fold_idx + 1, "data": val_data})

            # 각 Fold의 환자 ID를 저장
            train_patients_splits.append({"fold_idx": fold_idx + 1, "patients": train_patients})
            val_patients_splits.append({"fold_idx": fold_idx + 1, "patients": val_patients})

    # Step 5: JSON 파일 저장
    os.makedirs(os.path.dirname(OUTPUT_TEST_PATH), exist_ok=True)  # 저장 폴더 생성

    with open(OUTPUT_TEST_PATH, "w") as test_file:
        json.dump({"test_random_state": test_random_state, "data": test_data}, test_file, indent=4)

    with open(OUTPUT_TRAIN_PATH, "w") as train_file:
        json.dump(train_dataset, train_file, indent=4)

    with open(OUTPUT_VAL_PATH, "w") as val_file:
        json.dump(val_dataset, val_file, indent=4)

    # === 모든 환자 ID 저장 ===
    all_patients_split = {
        "test_patients": selected_test_ids,
        "train_patients_splits": train_patients_splits,
        "val_patients_splits": val_patients_splits
    }
    with open(OUTPUT_ALL_PATIENTS_PATH, "w") as all_patients_file:
        json.dump(all_patients_split, all_patients_file, indent=4)

    # 저장 경로 출력
    print(f"Test data saved to {OUTPUT_TEST_PATH}")
    print(f"Train data saved to {OUTPUT_TRAIN_PATH}")
    print(f"Validation data saved to {OUTPUT_VAL_PATH}")
    print(f"All patient splits saved to {OUTPUT_ALL_PATIENTS_PATH}")

# 프로그램 실행 진입점
if __name__ == "__main__":
    main()
