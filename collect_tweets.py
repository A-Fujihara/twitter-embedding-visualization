import requests
import json
import csv
from datetime import datetime


def collect_user_tweets():
    """
    Collects tweets from target users and saves to CSV
    """

    # Supabase API setup
    base_url = "https://fabxmporizzqflnftavs.supabase.co/rest/v1"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhYnhtcG9yaXp6cWZsbmZ0YXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjIyNDQ5MTIsImV4cCI6MjAzNzgyMDkxMn0.UIEJiUNkLsW28tBHmG-RQDW-I5JNlJLt62CSk9D_qG8"

    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}"
    }

    # Target users
    target_usernames = ['danielgolliher', 'mcd0w', 'maimecat', 'imitationlearn']

    print("=== Collecting Tweet Data ===")
    print(f"Target users: {target_usernames}")

    # Step 1: Get account IDs
    user_accounts = get_account_ids(base_url, headers, target_usernames)

    # Step 2: Collect all tweets
    all_tweets = collect_all_tweets(base_url, headers, user_accounts)

    # Step 3: Save to CSV
    save_tweets_to_csv(all_tweets)

    print(f"\n=== Collection Complete ===")
    print(f"Total tweets collected: {len(all_tweets)}")


def get_account_ids(base_url, headers, usernames):
    """Get account IDs for target usernames"""
    user_accounts = {}

    print("\n1. Getting account IDs...")
    for username in usernames:
        response = requests.get(f"{base_url}/account?username=eq.{username}", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            if user_data:
                account_id = user_data[0]['account_id']
                user_accounts[username] = account_id
                print(f"  ✓ {username}: {account_id}")
            else:
                print(f"  ✗ {username} not found")
        else:
            print(f"  ✗ Error searching for {username}")

    return user_accounts


def collect_all_tweets(base_url, headers, user_accounts):
    """Collect tweets from all users"""
    all_tweets = []

    print("\n2. Collecting tweets...")
    for username, account_id in user_accounts.items():
        print(f"  Getting tweets for {username}...")

        # Start with first batch
        limit = 1000  # Get 1000 tweets at a time
        offset = 0
        user_tweet_count = 0

        while True:
            response = requests.get(
                f"{base_url}/tweets?account_id=eq.{account_id}&limit={limit}&offset={offset}",
                headers=headers
            )

            if response.status_code == 200:
                tweets = response.json()
                if not tweets:  # No more tweets
                    break

                # Add username and collection timestamp to each tweet
                for tweet in tweets:
                    tweet['username'] = username
                    tweet['collected_at'] = datetime.now().isoformat()
                    all_tweets.append(tweet)

                user_tweet_count += len(tweets)
                offset += limit

                print(f"    Collected {user_tweet_count} tweets so far...")

                # Stop if we got less than the limit (reached the end)
                if len(tweets) < limit:
                    break

            else:
                print(f"    Error getting tweets for {username}: {response.status_code}")
                break

        print(f"  ✓ Total for {username}: {user_tweet_count} tweets")

    return all_tweets


def save_tweets_to_csv(tweets):
    """Save tweets to CSV file using built-in csv module"""
    print("\n3. Saving to CSV...")

    if not tweets:
        print("  ✗ No tweets to save")
        return

    # Create filename with timestamp
    filename = f"tweets_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    # Get all possible field names from all tweets
    all_fields = set()
    for tweet in tweets:
        all_fields.update(tweet.keys())

    fieldnames = sorted(list(all_fields))

    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tweets)

    print(f"  ✓ Saved to {filename}")
    print(f"  ✓ Total tweets: {len(tweets)}")
    print(f"  ✓ Columns: {len(fieldnames)}")
    print(f"  ✓ First few columns: {fieldnames[:5]}")


if __name__ == "__main__":
    collect_user_tweets()