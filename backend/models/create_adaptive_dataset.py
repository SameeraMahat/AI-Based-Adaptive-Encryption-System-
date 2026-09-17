import os
import pandas as pd


# ============================================================
# ADAPTIVE ENCRYPTION DATASET GENERATOR
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "encryption_dataset_v2.csv"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "encryption_dataset_adaptive.csv"
)


def select_algorithm(sensitivity_score, file_size_mb):
    """
    Adaptive encryption strategy:

    0–20
        -> ChaCha20-Poly1305

    21–50
        -> AES-256-GCM

    51–100 + file >= 5 MB
        -> Hybrid AES-256-GCM + RSA-OAEP

    51–100 + file < 5 MB
        -> AES-256-GCM
    """

    sensitivity_score = float(sensitivity_score)
    file_size_mb = float(file_size_mb)

    if sensitivity_score <= 20:
        return "ChaCha20"

    elif sensitivity_score <= 50:
        return "AES"

    elif file_size_mb >= 5:
        return "Hybrid"

    else:
        return "AES"


def main():

    print("=" * 60)
    print("ADAPTIVE ENCRYPTION DATASET GENERATOR")
    print("=" * 60)

    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(
            f"Dataset not found:\n{INPUT_PATH}"
        )

    # Load original dataset
    df = pd.read_csv(INPUT_PATH)

    print(f"\nOriginal dataset shape: {df.shape}")

    required_columns = [
        "sensitivity_score",
        "file_size_mb"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Generate new adaptive labels
    df["algorithm"] = df.apply(
        lambda row: select_algorithm(
            row["sensitivity_score"],
            row["file_size_mb"]
        ),
        axis=1
    )

    # Save as a NEW dataset
    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(f"\nNew dataset saved to:")
    print(OUTPUT_PATH)

    print("\nNew dataset shape:")
    print(df.shape)

    print("\nAdaptive algorithm distribution:")
    print(
        df["algorithm"]
        .value_counts()
        .sort_index()
    )

    print("\nPercentage distribution:")
    print(
        (df["algorithm"].value_counts(normalize=True) * 100)
        .round(2)
        .sort_index()
    )

    print("\nExample adaptive decisions:")

    examples = [
        (10, 0.5),
        (20, 2.0),
        (21, 1.0),
        (40, 3.0),
        (51, 2.0),
        (70, 4.9),
        (70, 5.0),
        (90, 20.0),
    ]

    for sensitivity, size in examples:
        algorithm = select_algorithm(
            sensitivity,
            size
        )

        print(
            f"Sensitivity={sensitivity:>5}, "
            f"Size={size:>5} MB "
            f"-> {algorithm}"
        )

    print("\n" + "=" * 60)
    print("DATASET GENERATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()