import os  # 운영체제와 상호작용을 위한 모듈
import json  # JSON 파일 읽기 및 저장을 위한 모듈
import numpy as np  # 수치 연산을 위한 모듈
from sklearn.model_selection import KFold  # K-Fold 교차검증을 위한 모듈

def read_file_data(folder_path):
    """
    지정된 폴더에서 BMP 파일 목록을 읽어 반환합니다.
    Args:
        folder_path (str): BMP 파일이 있는 폴더 경로
    Returns:
        list: BMP 파일 이름 리스트
    """
    file_data = []
    for file_name in os.listdir(folder_path):  # 폴더 내 모든 파일을 순회
        if file_name.endswith(".bmp"):  # 파일 확장자가 .bmp인지 확인
            file_data.append(file_name)  # BMP 파일을 리스트에 추가
    return file_data  # BMP 파일 리스트 반환

def calculate_test_size_random(patient_ids, patients, test_ratio=0.2, random_state=None):
    """
    테스트 데이터셋에 포함될 환자 ID를 무작위로 선택합니다.
    Args:
        patient_ids (list): 환자 ID 리스트
        patients (dict): 환자 ID와 해당 파일 리스트를 매핑한 딕셔너리
        test_ratio (float): 테스트 데이터 비율 (기본값 0.2)
        random_state (int, optional): 재현 가능한 결과를 위한 랜덤 시드 값
    Returns:
        tuple: (선택된 테스트 환자 ID, 실제 테스트 비율, 사용된 랜덤 시드)
    """
    patient_sizes = [len(patients[pid]) for pid in patient_ids]  # 각 환자의 데이터 개수
    total_data_size = sum(patient_sizes)  # 전체 데이터 개수
    test_data_target_size = int(total_data_size * test_ratio)  # 목표 테스트 데이터 개수

    if random_state is None:
        random_state = np.random.randint(0, 10000)  # 랜덤 시드가 없으면 랜덤 생성
    np.random.seed(random_state)  # 랜덤 시드 설정
    shuffled_patient_ids = np.random.permutation(patient_ids).tolist()  # 환자 ID 무작위 섞기

    selected_test_ids = []  # 선택된 테스트 환자 ID를 저장할 리스트
    current_test_size = 0  # 현재까지 선택된 테스트 데이터 개수
    for pid in shuffled_patient_ids:  # 무작위로 섞은 환자 ID 순회
        size = len(patients[pid])  # 환자 데이터 개수
        if current_test_size + size > test_data_target_size:  # 목표 테스트 데이터 수를 초과하면 중지
            break
        selected_test_ids.append(pid)  # 선택된 환자 ID 추가
        current_test_size += size  # 테스트 데이터 개수 갱신

    actual_test_ratio = current_test_size / total_data_size  # 실제 테스트 비율 계산
    return selected_test_ids, actual_test_ratio, random_state  # 선택된 환자 ID와 비율 반환

def process_folder_v2(folder_path, test_ratio, k_folds, output_base_path, val_ratio=0.2):
    """
    폴더의 데이터를 읽고, train/validation/test 세트로 나눈 후 JSON 파일로 저장합니다.
    Args:
        folder_path (str): 폴더 경로
        test_ratio (float): 테스트 데이터 비율
        k_folds (int): K-Fold 개수
        output_base_path (str): 결과 JSON 파일을 저장할 경로
        val_ratio (float): Validation 데이터 비율 (K_FOLDS=1 일 때만 사용)
    """
    label_str = os.path.basename(folder_path.strip("/"))  # 폴더 이름에서 레이블 추출
    try:
        label = float(label_str) / 10  # 레이블을 숫자로 변환 후 스케일 조정
    except ValueError:  # 변환 실패 시 에러 메시지 출력 후 종료
        print(f"Invalid label format: {label_str}. Skipping folder.")
        return

    print("----------- Label-----------", label)  # 레이블 출력

    data = read_file_data(folder_path)  # BMP 파일 읽기
    if not data:  # 데이터가 없으면 종료
        print(f"No BMP files found in folder: {folder_path}. Skipping.")
        return

    # 환자 ID별 데이터 그룹화
    patients = {}
    for item in data:
        patient_id = item.split("_")[0]  # 파일명에서 환자 ID 추출
        if patient_id not in patients:
            patients[patient_id] = []
        patients[patient_id].append(os.path.join(folder_path, item))

    patient_ids = list(patients.keys())  # 환자 ID 목록 생성

    # 테스트 데이터셋 추출
    selected_test_ids, actual_test_ratio, test_random_state = calculate_test_size_random(
        patient_ids, patients, test_ratio
    )
    remaining_ids = [pid for pid in patient_ids if pid not in selected_test_ids]  # 테스트 제외 환자 ID

    # 테스트 데이터 파일
    test_data_files = [file for pid in selected_test_ids for file in patients[pid]]

    folds = {}  # K-Fold 데이터를 저장할 딕셔너리
    labels = {file: label for file in test_data_files}  # 테스트 데이터 레이블 설정

    # K-Fold가 1인 경우 Train/Validation 분할
    if k_folds == 1:
        remaining_files = [file for pid in remaining_ids for file in patients[pid]]
        total_remaining = len(remaining_files)
        val_size = int(total_remaining * val_ratio)

        val_data_files = remaining_files[:val_size]
        train_data_files = remaining_files[val_size:]

        folds["fold_0"] = {
            "train": train_data_files,
            "val": val_data_files
        }
        labels.update({file: label for file in train_data_files + val_data_files})

        # 통계 출력
        print("K_FOLDS=1, splitting into train/val/test:")
        print(f"  Train Data: {len(train_data_files)}, Validation Data: {len(val_data_files)}, Test Data: {len(test_data_files)}")
        print()

    else:
        # K-Fold 교차검증
        n_splits = min(k_folds, len(remaining_ids))
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=np.random.randint(0, 10000))

        for fold_idx, (train_idx, val_idx) in enumerate(kf.split(remaining_ids)):
            train_patients = [remaining_ids[i] for i in train_idx]
            val_patients = [remaining_ids[i] for i in val_idx]
            train_data_files = [file for pid in train_patients for file in patients[pid]]
            val_data_files = [file for pid in val_patients for file in patients[pid]]

            folds[f"fold_{fold_idx}"] = {
                "train": train_data_files,
                "val": val_data_files
            }
            labels.update({file: label for file in train_data_files + val_data_files})
            # 통계 출력
            print(f"Fold {fold_idx + 1}:")
            print(f"  Train Patients: {len(train_patients)}")
            print(f"  Validation Patients: {len(val_patients)}")
            print(f"  Test Patients (Fixed): {len(selected_test_ids)}")
            print(f"  Train Data: {len(train_data_files)}, Validation Data: {len(val_data_files)}, Test Data: {len(test_data_files)}")
            print()

    # 최종 데이터셋 저장
    dataset = {
        "folds": folds,
        "test": test_data_files,
        "labels": labels
    }
    output_path = os.path.join(output_base_path, f"{label}_dataset.json")
    os.makedirs(output_base_path, exist_ok=True)  # 결과 폴더 생성
    with open(output_path, "w") as json_file:
        json.dump(dataset, json_file, indent=4)

    print(f"Saved dataset for label {label} to {output_path}")

def combine_folds_v2(base_path, output_path):
    """
    여러 폴더에서 생성된 JSON 파일을 읽어와 데이터를 합치고, 하나의 JSON 파일로 저장합니다.
    
    Args:
        base_path (str): JSON 파일이 저장된 폴더 경로.
        output_path (str): 병합된 데이터를 저장할 JSON 파일 경로.
    
    이 함수는 다음 작업을 수행합니다:
    1. `base_path` 폴더에 있는 모든 JSON 파일을 순회하며 데이터를 읽습니다.
    2. 각 JSON 파일에서 Train/Validation/Test 데이터와 레이블 정보를 병합합니다.
    3. 병합된 데이터를 최종 JSON 구조로 저장합니다.
    """
    combined_folds = {}  # 각 Fold별 Train/Validation 데이터를 저장할 딕셔너리 초기화
    combined_test_files = []  # 모든 테스트 데이터 파일 경로를 저장할 리스트
    combined_labels = {}  # 모든 데이터 파일의 레이블을 저장할 딕셔너리

    # `base_path` 디렉토리의 모든 파일을 순회
    for file_name in os.listdir(base_path):  
        if file_name.endswith("_dataset.json"):  # 파일 이름이 "_dataset.json"으로 끝나는 파일만 처리
            file_path = os.path.join(base_path, file_name)  # 파일의 전체 경로 생성
            with open(file_path, "r") as f:  # JSON 파일 읽기
                data = json.load(f)  # 파일 내용을 파싱하여 딕셔너리로 변환
                
                # Fold 데이터를 병합
                for fold_name, fold_data in data["folds"].items():
                    if fold_name not in combined_folds:  # 아직 해당 Fold 이름이 없으면 초기화
                        combined_folds[fold_name] = {"train": [], "val": []}  # Train/Validation 리스트 초기화
                    
                    # Train/Validation 데이터를 각각 병합
                    combined_folds[fold_name]["train"].extend(fold_data["train"])  # Train 데이터 추가
                    combined_folds[fold_name]["val"].extend(fold_data["val"])  # Validation 데이터 추가

                # Test 데이터 병합
                combined_test_files.extend(data["test"])  # Test 데이터 리스트에 추가
                
                # 레이블 병합 (key: 파일 경로, value: 레이블 값)
                combined_labels.update(data["labels"])  # 기존 레이블 딕셔너리에 추가

    # 병합된 데이터를 최종 JSON 구조로 생성
    combined_dataset = {
        "folds": combined_folds,  # Fold별 Train/Validation 데이터
        "test": combined_test_files,  # 병합된 Test 데이터 파일 경로
        "labels": combined_labels  # 병합된 파일 경로와 레이블 매핑 정보
    }

    # `output_path`에 해당하는 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 병합된 데이터를 JSON 파일로 저장
    with open(output_path, "w") as f:
        json.dump(combined_dataset, f, indent=4)  # JSON 데이터 저장 (indent=4: 보기 좋게 들여쓰기)

    print(f"Combined dataset saved to {output_path}")  # 데이터 저장 완료 메시지 출력


def main_v2():
    """
    전체 데이터셋 처리를 위한 메인 함수.
    """
    BASE_DATA_FOLDER = "./preprocessed_va_datasets/"  # 데이터셋 폴더
    TEST_RATIO = 0.15  # 테스트 비율
    VAL_RATIO = 0.15  # Validation 비율
    K_FOLDS = 2  # K-Fold 개수
    OUTPUT_BASE_PATH = "./data_split_v2"  # 개별 데이터셋 저장 경로
    OUTPUT_COMBINED_PATH = "./combined_dataset/combined_dataset.json"  # 병합된 데이터셋 경로

    for folder_name in os.listdir(BASE_DATA_FOLDER):
        folder_path = os.path.join(BASE_DATA_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            process_folder_v2(folder_path, TEST_RATIO, K_FOLDS, OUTPUT_BASE_PATH, VAL_RATIO)
    combine_folds_v2(OUTPUT_BASE_PATH, OUTPUT_COMBINED_PATH)

if __name__ == "__main__":
    main_v2()
