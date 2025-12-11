import os
import json
import numpy as np
from sklearn.model_selection import KFold

def read_file_data(folder_path):
    """
    Reads all BMP files in a specified folder.
    Args:
        folder_path (str): Path to the folder containing BMP files.
    Returns:
        list: A list of BMP file names.
    """
    file_data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".bmp"):
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
    patient_sizes = [len(patients[pid]) for pid in patient_ids]
    total_data_size = sum(patient_sizes)
    test_data_target_size = int(total_data_size * test_ratio)

    if random_state is None:
        random_state = np.random.randint(0, 10000)
    np.random.seed(random_state)
    shuffled_patient_ids = np.random.permutation(patient_ids).tolist()

    selected_test_ids = []
    current_test_size = 0
    for pid in shuffled_patient_ids:
        size = len(patients[pid])
        if current_test_size + size > test_data_target_size:
            break
        selected_test_ids.append(pid)
        current_test_size += size

    actual_test_ratio = current_test_size / total_data_size
    return selected_test_ids, actual_test_ratio, random_state

def process_folder(folder_path, test_ratio, k_folds, output_base_path):
    """
    Process a single folder, split data into train/val/test and save to JSON.
    """
    label_str = os.path.basename(folder_path.strip("/"))
    try:
        label = float(label_str) / 10
    except ValueError:
        print(f"Invalid label format: {label_str}. Skipping folder.")
        return

    data = read_file_data(folder_path)
    if not data:
        print(f"No BMP files found in folder: {folder_path}. Skipping.")
        return

    patients = {}
    for item in data:
        patient_id = item.split("_")[0]
        if patient_id not in patients:
            patients[patient_id] = []
        patients[patient_id].append(os.path.join(folder_path, item))

    patient_ids = list(patients.keys())

    selected_test_ids, actual_test_ratio, test_random_state = calculate_test_size_random(
        patient_ids, patients, test_ratio
    )
    remaining_ids = [pid for pid in patient_ids if pid not in selected_test_ids]

    test_data = [{"file": file, "label": label} for pid in selected_test_ids for file in patients[pid]]

    folds = []
    n_splits = min(k_folds, len(remaining_ids))
    if n_splits > 1:
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=np.random.randint(0, 10000))

        for fold_idx, (train_idx, val_idx) in enumerate(kf.split(remaining_ids)):
            train_patients = [remaining_ids[i] for i in train_idx]
            val_patients = [remaining_ids[i] for i in val_idx]

            train_data = [{"file": file, "label": label} for pid in train_patients for file in patients[pid]]
            val_data = [{"file": file, "label": label} for pid in val_patients for file in patients[pid]]

            folds.append({
                "fold_idx": fold_idx + 1,
                "train_data": train_data,
                "val_data": val_data
            })
            
            # Fold 결과 출력
            total_data_size = len(train_data) + len(val_data) + len(test_data)

            # Calculate ratios
            train_ratio = len(train_data) / total_data_size
            val_ratio = len(val_data) / total_data_size
            test_ratio = len(test_data) / total_data_size

            print(f"Fold {fold_idx + 1}:")
            print(f"  Train Patients: {train_patients}")
            print(f"  Validation Patients: {val_patients}")
            print(f"  Test Patients (Fixed): {selected_test_ids}")
            print(f"  Train Data: {len(train_data)}, Validation Data: {len(val_data)}, Test Data: {len(test_data)}")
            print(f"  Data Ratios -> Train: {train_ratio:.2f}, Validation: {val_ratio:.2f}, Test: {test_ratio:.2f}")
            print()

    output_path = os.path.join(output_base_path, f"{label}_dataset.json")
    os.makedirs(output_base_path, exist_ok=True)

    dataset = {
        "folds": folds,
        "test_data": test_data
    }

    with open(output_path, "w") as json_file:
        json.dump(dataset, json_file, indent=4)
    print(f"Saved dataset for label {label} to {output_path}")

def combine_folds(base_path, output_path):
    """
    Combine folds from multiple JSON files into a single JSON file.
    """
    combined_folds = {}
    combined_test_data = []

    for file_name in os.listdir(base_path):
        if file_name.endswith("_dataset.json"):
            file_path = os.path.join(base_path, file_name)

            with open(file_path, "r") as f:
                data = json.load(f)

                for fold in data["folds"]:
                    fold_idx = fold["fold_idx"]
                    if fold_idx not in combined_folds:
                        combined_folds[fold_idx] = {"train_data": [], "val_data": []}

                    combined_folds[fold_idx]["train_data"].extend(fold["train_data"])
                    combined_folds[fold_idx]["val_data"].extend(fold["val_data"])

                combined_test_data.extend(data["test_data"])

    combined_dataset = {
        "folds": [
            {"fold_idx": idx, "train_data": fold["train_data"], "val_data": fold["val_data"]}
            for idx, fold in sorted(combined_folds.items())
        ],
        "test_data": combined_test_data
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(combined_dataset, f, indent=4)

    print(f"Combined dataset saved to {output_path}")

def main():
    BASE_DATA_FOLDER = "./va_datasets"
    TEST_RATIO = 0.15
    K_FOLDS = 3
    OUTPUT_BASE_PATH = "./data_split"
    OUTPUT_COMBINED_PATH = "./combined_dataset/combined_dataset.json"

    for folder_name in os.listdir(BASE_DATA_FOLDER):
        folder_path = os.path.join(BASE_DATA_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            process_folder(folder_path, TEST_RATIO, K_FOLDS, OUTPUT_BASE_PATH)

    combine_folds(OUTPUT_BASE_PATH, OUTPUT_COMBINED_PATH)

if __name__ == "__main__":
    main()
