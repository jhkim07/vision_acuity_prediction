import json

# 파일 경로 설정
input_file = "combined_dataset/combined_dataset.json"
output_file = "combined_dataset/combined_dataset_4_class.json"

# 값 매핑 딕셔너리
label_mapping = {
    0.0: 0,
    0.1: 1,
    0.2: 1,
    0.3: 2,
    0.4: 2,
    0.5: 2,
    0.6: 2,
    0.7: 2,
    0.8: 3,
    0.9: 3,
    1.0: 3
}

# JSON 파일 로드
with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# 레이블 변경
if "labels" in data:
    data["labels"] = {key: label_mapping.get(value, value) for key, value in data["labels"].items()}

# 변경된 JSON 저장
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

print(f"레이블 변경 완료 및 저장 완료: {output_file}")
