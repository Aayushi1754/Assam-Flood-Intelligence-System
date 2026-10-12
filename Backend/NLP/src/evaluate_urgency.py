import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from urgency_score import analyze_flood_message


# Locate the dataset relative to this script
DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "dataset"
    / "FloodSense_Dataset_Ground_Truth.csv"
)


def normalize_label(label):
    """Normalize urgency labels for comparison."""
    return str(label).strip().casefold()


def main():
    # Load dataset
    df = pd.read_csv(DATASET_PATH)

    required_columns = {
        "Original_Text",
        "Expected_Urgency_Level",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required CSV columns: {sorted(missing)}"
        )

    # Remove rows without usable messages or expected labels
    df = df.dropna(
        subset=["Original_Text", "Expected_Urgency_Level"]
    ).copy()

    # Run urgency classification
    df["Predicted_Urgency_Level"] = df["Original_Text"].apply(
        lambda text: analyze_flood_message(str(text))[
            "urgency_level"
        ]
    )

    # Normalize capitalization and whitespace
    df["Expected_Normalized"] = df[
        "Expected_Urgency_Level"
    ].apply(normalize_label)

    df["Predicted_Normalized"] = df[
        "Predicted_Urgency_Level"
    ].apply(normalize_label)

    # Calculate metrics
    accuracy = accuracy_score(
        df["Expected_Normalized"],
        df["Predicted_Normalized"],
    )

    labels = sorted(
        set(df["Expected_Normalized"])
        | set(df["Predicted_Normalized"])
    )

    print("\nFloodSense Urgency Evaluation")
    print("=" * 50)
    print(f"Records evaluated: {len(df)}")
    print(f"Accuracy: {accuracy:.2%}")

    print("\nClassification Report")
    print(
        classification_report(
            df["Expected_Normalized"],
            df["Predicted_Normalized"],
            labels=labels,
            zero_division=0,
        )
    )

    print("Confusion Matrix")
    print(
        pd.DataFrame(
            confusion_matrix(
                df["Expected_Normalized"],
                df["Predicted_Normalized"],
                labels=labels,
            ),
            index=[f"Actual: {label}" for label in labels],
            columns=[f"Predicted: {label}" for label in labels],
        )
    )

    # Show incorrect predictions
    errors = df[
        df["Expected_Normalized"]
        != df["Predicted_Normalized"]
    ]

    print("\nMisclassified Messages")
    print("=" * 50)

    if errors.empty:
        print("No misclassified messages in this dataset.")
    else:
        for _, row in errors.iterrows():
            print(f"\nMessage: {row['Original_Text']}")
            print(f"Expected: {row['Expected_Urgency_Level']}")
            print(f"Predicted: {row['Predicted_Urgency_Level']}")

    # Save detailed results
    output_path = (
        Path(__file__).resolve().parent.parent
        / "results"
        / "FloodSense_Urgency_Evaluation.csv"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"\nDetailed results saved to:\n{output_path}")


if __name__ == "__main__":
    main()