import os
import shutil
from collections import defaultdict
import random

def group_files_by_patient(source_folder):
    """
    그룹화: 환자 ID를 기준으로 파일을 그룹화합니다.
    Args:
        source_folder (str): 파일이 저장된 원본 폴더 경로.
    Returns:
        dict: 환자 ID를 키로 하고 파일 목록을 값으로 하는 딕셔너리.
    """
    patient_files = defaultdict(list)  # 환자 ID를 키로 하고 파일 목록을 저장할 딕셔너리

    # 원본 폴더의 파일 목록을 순회
    for file_name in os.listdir(source_folder):
        if os.path.isfile(os.path.join(source_folder, file_name)):  # 파일만 처리
            patient_id = file_name.split('_')[0]  # 파일명에서 '_' 이전 부분을 환자 ID로 추출
            patient_files[patient_id].append(file_name)  # 해당 환자 ID에 파일 추가

    return patient_files  # 환자별로 그룹화된 파일 딕셔너리 반환

def copy_patient_files(source_folder, destination_folder, num_files=None):
    """
    환자 파일 그룹에서 특정 개수를 복사합니다. 
    Args:
        source_folder (str): 원본 파일이 저장된 폴더 경로.
        destination_folder (str): 복사된 파일을 저장할 대상 폴더 경로.
        num_files (int, optional): 복사할 파일 수 제한 (기본값은 None으로, 모든 파일 복사).
    Returns:
        list: 복사된 파일 이름 목록.
    """
    os.makedirs(destination_folder, exist_ok=True)  # 대상 폴더가 없으면 생성

    # 원본 폴더의 파일을 환자별로 그룹화
    patient_files = group_files_by_patient(source_folder)

    # 환자 그룹을 리스트로 변환하고 랜덤하게 섞음 (환자 단위 샘플링)
    patient_groups = list(patient_files.items())
    random.shuffle(patient_groups)  # 무작위 순서로 섞음

    copied_files = []  # 복사된 파일 이름을 저장할 리스트
    total_files_copied = 0  # 복사된 파일 총 수를 추적

    # 환자 그룹별로 파일 복사 수행
    for patient_id, files in patient_groups:
        # num_files 제한이 있는 경우, 초과하지 않도록 복사 수행
        if num_files is not None and total_files_copied + len(files) > num_files:
            break  # 남은 파일 수가 num_files를 초과하면 루프 종료

        # 해당 환자의 모든 파일 복사
        for file_name in files:
            source_path = os.path.join(source_folder, file_name)  # 원본 파일 경로
            destination_path = os.path.join(destination_folder, file_name)  # 대상 파일 경로

            shutil.copy2(source_path, destination_path)  # 파일 복사 (메타데이터 포함)
            copied_files.append(file_name)  # 복사된 파일 이름 추가

        # 복사된 파일 수 누적
        total_files_copied += len(files)

    # 복사 결과 출력
    print(f"총 {len(copied_files)}개의 파일이 복사되었습니다.")
    return copied_files  # 복사된 파일 이름 목록 반환

# 실행 코드
if __name__ == "__main__":
    # 사용자 입력을 통해 폴더 경로 및 파일 수 설정 가능
    # source_folder = input("원본 폴더 경로를 입력하세요: ").strip()
    # destination_folder = input("대상 폴더 경로를 입력하세요: ").strip()
    # num_files_input = input("이동할 파일 수를 입력하세요 (전체 이동하려면 Enter): ").strip()
    # num_files = int(num_files_input) if num_files_input else None

    # 예제 경로 및 파일 수 설정
    source_folder = "../../dataset/medical_datasets/Fundus_BCVA-Est/9"  # 원본 폴더 경로
    destination_folder = "./va_datasets/09"  # 대상 폴더 경로
    num_files = 2000  # 복사할 파일 수 제한 (2000개)

    # 복사 함수 실행
    copied_files = copy_patient_files(source_folder, destination_folder, num_files)

    # 복사된 파일 출력
    print("이동된 파일:")
    for file_name in copied_files:
        print(file_name)
    
    # 최종 복사 결과 출력
    print(f"총 {len(copied_files)}개의 파일이 복사되었습니다.")
