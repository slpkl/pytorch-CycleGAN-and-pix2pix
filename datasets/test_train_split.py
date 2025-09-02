import os
import random
import shutil
from pathlib import Path
import argparse
import sys

def split_dataset(input_dir, target_dir, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=42):
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Sum of ratios must be 1"

    for split in ['train', 'val', 'test']:
        os.makedirs(os.path.join(input_dir, split), exist_ok=True)
        os.makedirs(os.path.join(target_dir, split), exist_ok=True)

    input_files = sorted([f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))])
    target_files = sorted([f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))])

    input_basenames = [os.path.splitext(f)[0] for f in input_files]
    target_basenames = [os.path.splitext(f)[0] for f in target_files]
    assert input_basenames == target_basenames, "Base filenames in dataset_A and dataset_B do not match"

    random.seed(seed)
    indices = list(range(len(input_files)))
    random.shuffle(indices)

    total_files = len(input_files)
    train_size = int(total_files * train_ratio)
    val_size = int(total_files * val_ratio)
    test_size = total_files - train_size - val_size

    train_indices = indices[:train_size]
    val_indices = indices[train_size:train_size + val_size]
    test_indices = indices[train_size + val_size:]

    def copy_files(indices, split):
        for idx in indices:
            input_file = input_files[idx]
            target_file = target_files[idx]
            shutil.copy(os.path.join(input_dir, input_file), os.path.join(input_dir, split, input_file))
            shutil.copy(os.path.join(target_dir, target_file), os.path.join(target_dir, split, target_file))

    copy_files(train_indices, 'train')
    copy_files(val_indices, 'val')
    copy_files(test_indices, 'test')

    print(f"Train: {len(train_indices)} files, Val: {len(val_indices)} files, Test: {len(test_indices)} files")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split paired datasets (dataset_A and dataset_B) into train/val/test subfolders.")
    parser.add_argument("input_dir", help="Path to dataset_A (input images)")
    parser.add_argument("target_dir", help="Path to dataset_B (target images)")
    parser.add_argument("--train", type=float, default=0.8, help="Train ratio (default: 0.8)")
    parser.add_argument("--val", type=float, default=0.1, help="Validation ratio (default: 0.1)")
    parser.add_argument("--test", type=float, default=0.1, help="Test ratio (default: 0.1)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Input directory does not exist: {args.input_dir}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(args.target_dir):
        print(f"Target directory does not exist: {args.target_dir}", file=sys.stderr)
        sys.exit(1)

    split_dataset(args.input_dir, args.target_dir, train_ratio=args.train, val_ratio=args.val, test_ratio=args.test, seed=args.seed)

