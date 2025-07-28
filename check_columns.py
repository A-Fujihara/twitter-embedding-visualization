import csv


def check_columns():
    '''Check the available columns in a CSV file.
    '''
    input_file = "tweets_data_20250602_104228.csv"

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        print("Available columns:")
        for i, col in enumerate(reader.fieldnames):
            print(f"  {i}: {col}")


if __name__ == "__main__":
    check_columns()