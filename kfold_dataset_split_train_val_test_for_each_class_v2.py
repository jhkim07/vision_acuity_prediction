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

def process_folder_v2(folder_path, test_ratio, k_folds, output_base_path):
    """
    Process a single folder, split data into train/val/test and save to JSON in the desired format.
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

    # Test data
    test_data_files = [file for pid in selected_test_ids for file in patients[pid]]

    folds = {}
    labels = {file: label for file in test_data_files}

    n_splits = min(k_folds, len(remaining_ids))
    if n_splits > 1:
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

            # Update labels
            labels.update({file: label for file in train_data_files + val_data_files})

    # Final dataset structure
    dataset = {
        "folds": folds,
        "test": test_data_files,
        "labels": labels
    }

    output_path = os.path.join(output_base_path, f"{label}_dataset.json")
    os.makedirs(output_base_path, exist_ok=True)

    with open(output_path, "w") as json_file:
        json.dump(dataset, json_file, indent=4)
    print(f"Saved dataset for label {label} to {output_path}")

def main_v2():
    BASE_DATA_FOLDER = "./test_datasets"
    TEST_RATIO = 0.15
    K_FOLDS = 5
    OUTPUT_BASE_PATH = "./data_split_v2"

    for folder_name in os.listdir(BASE_DATA_FOLDER):
        folder_path = os.path.join(BASE_DATA_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            process_folder_v2(folder_path, TEST_RATIO, K_FOLDS, OUTPUT_BASE_PATH)

if __name__ == "__main__":
    main_v2()