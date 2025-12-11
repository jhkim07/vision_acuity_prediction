# Fundus 이미지를 이용한 시력(VA) 예측 프로젝트

## 프로젝트 개요

이 프로젝트는 안저 사진(Fundus Image)을 분석하여 시력(Visual Acuity, VA)을 예측하는 딥러닝 프로젝트입니다. 특히 BCVA(Best Corrected Visual Acuity) 값을 안저 이미지로부터 추정하는 것을 목표로 합니다.

## 프로젝트 목적

- 펀더스 안저 사진을 입력으로 받아 시력 값을 예측
- 환자 단위 데이터 분할을 통한 일반화 성능 향상
- K-Fold 교차 검증을 통한 모델 성능 평가
- EfficientNet 및 Vision Transformer 모델을 활용한 분류

## 기술 스택

- **프레임워크**: PyTorch
- **모델 아키텍처**: 
  - EfficientNet-B0/B4
  - Vision Transformer (ViT)
- **전처리 기법**: 
  - CLAHE (Contrast Limited Adaptive Histogram Equalization)
  - ColorJitter
  - RandomFlip (Horizontal/Vertical)
- **평가 방법**: 
  - K-Fold Cross-Validation
  - Confusion Matrix
  - F1-Score
  - Accuracy

## 프로젝트 구조

```
va_prediction/
├── step_3_copy_patient_files.py          # 환자 파일 샘플링 및 복사
├── step_4_crop2.py                       # 이미지 크롭 (검은 모서리 제거)
├── step_5_kfold_dataset_split_train_val_test_for_all_class_v2.py  # K-Fold 데이터셋 분할
├── step_6_compuate_mean_std.py          # 이미지 통계 계산 (평균/표준편차)
├── step_7_va_measurement_v1.ipynb       # 메인 학습 노트북
├── step_7_va_measurement_v1.py          # 학습 스크립트 (import만 포함)
├── step_11_convert_label_4_classes.py   # 레이블을 4개 클래스로 변환
├── va_datasets/                          # 환자별 샘플링된 원본 데이터
├── preprocessed_va_datasets/             # 크롭된 전처리 이미지
├── data_split_v2/                        # 개별 클래스별 JSON 파일
├── combined_dataset/                     # 병합된 데이터셋 JSON 파일
├── cnn_models/                           # 학습된 모델 저장
└── simple_test/                          # 테스트 및 실험 스크립트
```

## 워크플로우

```
1. 원본 데이터 (Fundus_BCVA-Est/)
   ↓
2. 환자별 샘플링 및 복사 (step_3)
   → va_datasets/ 폴더에 저장
   ↓
3. 이미지 크롭 및 전처리 (step_4)
   → 검은 모서리 제거
   → preprocessed_va_datasets/ 폴더에 저장
   ↓
4. 이미지 통계 계산 (step_6)
   → RGB 채널별 평균/표준편차 계산
   → 정규화에 사용
   ↓
5. 데이터셋 분할 (step_5)
   → 환자 단위 Train/Validation/Test 분할
   → K-Fold 교차 검증 지원
   → combined_dataset/combined_dataset.json 생성
   ↓
6. 레이블 변환 (선택사항, step_11)
   → 연속 레이블을 4개 클래스로 변환
   ↓
7. 모델 학습 (step_7)
   → EfficientNet 또는 ViT 모델 학습
   → K-Fold 교차 검증 수행
   → 모델 저장 및 평가
```

## 주요 파일 설명

### 1. `step_3_copy_patient_files.py`
**기능**: 원본 데이터에서 환자별로 그룹화하여 샘플링 및 복사

**특징**:
- 환자 ID 기준으로 파일 그룹화 (파일명의 `_` 이전 부분이 환자 ID)
- 환자 단위 샘플링으로 데이터 누수 방지
- 무작위 순서로 환자 선택

**사용 예시**:
```python
source_folder = "../../dataset/medical_datasets/Fundus_BCVA-Est/9"
destination_folder = "./va_datasets/09"
num_files = 2000  # 복사할 파일 수 제한
```

### 2. `step_4_crop2.py`
**기능**: 안저 이미지의 검은 모서리 영역을 자동 감지하여 제거

**알고리즘**:
- 이미지 중심에서 시작하여 확장되는 사각형 영역 확인
- 네 모서리가 모두 검은색인 최대 사각형 영역 찾기
- 해당 영역으로 이미지 크롭

**입력/출력**:
- 입력: `./va_datasets/06`
- 출력: `./preprocessed_va_datasets/06`

### 3. `step_5_kfold_dataset_split_train_val_test_for_all_class_v2.py`
**기능**: 환자 단위로 Train/Validation/Test 데이터셋 분할 및 K-Fold 교차 검증 설정

**주요 특징**:
- 환자 단위 분할로 데이터 누수 방지
- K-Fold 교차 검증 지원 (기본값: 2-fold)
- 폴더명을 레이블로 사용 (예: "09" → 0.9)

**설정 파라미터**:
```python
TEST_RATIO = 0.15      # 테스트 데이터 비율
VAL_RATIO = 0.15       # Validation 데이터 비율
K_FOLDS = 2            # K-Fold 개수
```

**출력 파일**:
- 개별 클래스별: `data_split_v2/{label}_dataset.json`
- 병합된 데이터셋: `combined_dataset/combined_dataset.json`

### 4. `step_6_compuate_mean_std.py`
**기능**: 전처리된 이미지들의 RGB 채널별 평균 및 표준편차 계산

**용도**: 이미지 정규화를 위한 통계값 계산

**출력 예시**:
```
Channel-wise Mean: [0.45242608, 0.27754296, 0.16601739]
Channel-wise Std: [0.13136276, 0.09985017, 0.07743429]
```

### 5. `step_7_va_measurement_v1.ipynb`
**기능**: 메인 학습 및 평가 노트북

**주요 기능**:
- EfficientNet-B0/B4 모델 학습
- Vision Transformer 모델 학습 (선택사항)
- K-Fold 교차 검증 수행
- 이미지 전처리 파이프라인 (CLAHE, Augmentation 등)
- 모델 평가 (Confusion Matrix, F1-Score, Accuracy)
- 학습 곡선 시각화

**전처리 파이프라인**:
```python
transform = transforms.Compose([
    ApplyCLAHE(),                    # 대비 향상
    transforms.Resize((224, 224)),   # 이미지 크기 조정
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.5),
    transforms.ColorJitter(...),     # 색상 조정
    transforms.ToTensor(),
    transforms.Normalize(mean=[...], std=[...])
])
```

**학습 설정**:
- Epochs: 50
- Batch Size: 32
- Loss Function: CrossEntropyLoss
- Optimizer: Adam

**모델 저장**:
- Epoch 단위 최적 모델: `best_epoch_model.pth`
- Fold 단위 최적 모델: `best_model_fold_fold_{n}.pth`
- 전체 최적 모델: `best_model_overall.pth`

### 6. `step_11_convert_label_4_classes.py`
**기능**: 연속 레이블(0.0~1.0)을 4개 클래스로 변환

**레이블 매핑**:
```python
{
    0.0: 0,        # 클래스 0
    0.1-0.2: 1,    # 클래스 1
    0.3-0.7: 2,    # 클래스 2
    0.8-1.0: 3     # 클래스 3
}
```

## 데이터셋 구조

### 레이블 형식
- 폴더명이 레이블을 나타냄 (예: "09" → 0.9, "05" → 0.5)
- 기본적으로 11개 클래스 (0.0, 0.1, 0.2, ..., 1.0)
- 선택적으로 4개 클래스로 변환 가능

### JSON 파일 구조
```json
{
    "folds": {
        "fold_0": {
            "train": ["path/to/image1.bmp", ...],
            "val": ["path/to/image2.bmp", ...]
        },
        "fold_1": {
            "train": [...],
            "val": [...]
        }
    },
    "test": ["path/to/test_image.bmp", ...],
    "labels": {
        "path/to/image1.bmp": 0.9,
        "path/to/image2.bmp": 0.5,
        ...
    }
}
```

## 사용 방법

### 1. 데이터 준비
```bash
# 1단계: 환자 파일 샘플링 및 복사
python step_3_copy_patient_files.py

# 2단계: 이미지 크롭
python step_4_crop2.py

# 3단계: 이미지 통계 계산
python step_6_compuate_mean_std.py
```

### 2. 데이터셋 분할
```bash
# K-Fold 데이터셋 분할
python step_5_kfold_dataset_split_train_val_test_for_all_class_v2.py
```

### 3. 레이블 변환 (선택사항)
```bash
# 4개 클래스로 변환
python step_11_convert_label_4_classes.py
```

### 4. 모델 학습
```bash
# Jupyter Notebook 실행
jupyter notebook step_7_va_measurement_v1.ipynb
```

## 디렉토리 구조

- **va_datasets/**: 환자별 샘플링된 원본 이미지
- **preprocessed_va_datasets/**: 크롭된 전처리 이미지
- **data_split_v2/**: 클래스별 데이터셋 JSON 파일
- **combined_dataset/**: 병합된 데이터셋 JSON 파일
- **cnn_models/**: 학습된 모델 파일
- **best_epoch_model.pth**: Epoch 단위 최적 모델
- **best_model_overall.pth**: 전체 최적 모델

## 주요 특징

1. **환자 단위 데이터 분할**: 데이터 누수 방지를 위해 환자 단위로 Train/Val/Test 분할
2. **K-Fold 교차 검증**: 모델 성능의 신뢰성을 높이기 위한 교차 검증
3. **고급 전처리**: CLAHE를 통한 대비 향상 및 다양한 Augmentation 기법 적용
4. **다양한 모델 지원**: EfficientNet 및 Vision Transformer 모델 실험

## 의존성 패키지

주요 패키지:
- `torch`, `torchvision`: 딥러닝 프레임워크
- `PIL`, `opencv-python`: 이미지 처리
- `scikit-learn`: 평가 메트릭
- `matplotlib`, `seaborn`: 시각화
- `timm`: Vision Transformer 모델
- `tqdm`: 진행 표시
- `numpy`, `pandas`: 데이터 처리

## 주의사항

- 환자 ID는 파일명의 첫 번째 `_` 이전 부분으로 추출됩니다
- 데이터 분할 시 환자 단위로 수행되어 데이터 누수를 방지합니다
- 이미지 전처리 전에 `step_6`을 실행하여 정규화 파라미터를 계산해야 합니다

## 라이선스

이 프로젝트는 연구 목적으로 개발되었습니다.

