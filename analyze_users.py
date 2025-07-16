import csv
from collections import Counter


def analyze_users():
    '''Analyze the number of tweets per user from a CSV file.
    '''
    input_file = "tweets_data_20250602_104228.csv"

    users = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row['username'])

    user_counts = Counter(users)
    print("User tweet counts:")
    for user, count in user_counts.most_common():
        print(f"  {user}: {count} tweets")

    total = sum(user_counts.values())
    print(f"\nTotal: {total} tweets")


if __name__ == "__main__":
    analyze_users()