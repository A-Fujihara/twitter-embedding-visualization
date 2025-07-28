import requests
import json
import csv
from datetime import datetime
import re


def collect_user_tweets():
    """
    Collects tweets from target users and saves to CSV with filtering
    """

    # Supabase API setup
    base_url = "https://fabxmporizzqflnftavs.supabase.co/rest/v1"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhYnhtcG9yaXp6cWZsbmZ0YXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjIyNDQ5MTIsImV4cCI6MjAzNzgyMDkxMn0.UIEJiUNkLsW28tBHmG-RQDW-I5JNlJLt62CSk9D_qG8"

    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}"
    }

    print("=== Collecting Tweet Data ===")
    print("Getting ALL users from database...")

    user_accounts = get_all_account_ids(base_url, headers)

    all_tweets = collect_all_tweets(base_url, headers, user_accounts)

    save_tweets_to_csv(all_tweets)

    print(f"\n=== Collection Complete ===")
    print(f"Total tweets collected: {len(all_tweets)}")


def get_all_account_ids(base_url, headers):
    """Get ALL account IDs from the database"""
    user_accounts = {}

    print("\n1. Getting all account IDs...")
    
    limit = 1000
    offset = 0
    
    while True:
        response = requests.get(f"{base_url}/account?limit={limit}&offset={offset}", headers=headers)
        if response.status_code == 200:
            accounts = response.json()
            if not accounts:
                break
            
            for account in accounts:
                username = account.get('username')
                account_id = account.get('account_id')
                if username and account_id:
                    user_accounts[username] = account_id
            
            print(f"  Loaded {len(user_accounts)} users so far...")
            offset += limit
            
            if len(accounts) < limit:
                break
        else:
            print(f"  ✗ Error getting accounts: {response.status_code}")
            break
    
    print(f"  ✓ Total users found: {len(user_accounts)}")
    return user_accounts


def should_filter_tweet(tweet_text):
    """
    Determine if a tweet should be filtered out
    Returns True if tweet should be REMOVED
    """
    if not tweet_text or not tweet_text.strip():
        return True
    
    tweet_text = tweet_text.strip()
    
    # Filter retweets
    if tweet_text.startswith('RT @'):
        return True
    
    # Filter very short tweets (likely low content)
    if len(tweet_text) < 4:
        return True
    
    # Filter tweets that are mostly mentions
    words = tweet_text.split()
    if len(words) > 0:
        mention_ratio = sum(1 for word in words if word.startswith('@')) / len(words)
        if mention_ratio > 0.5:  # More than 50% mentions
            return True
    
    # Filter tweets that are just URLs
    url_pattern = r'https?://\S+'
    text_without_urls = re.sub(url_pattern, '', tweet_text).strip()
    if len(text_without_urls) < 10:  # Almost nothing left after removing URLs
        return True
    
    # Filter tweets that are mostly hashtags
    hashtag_ratio = sum(1 for word in words if word.startswith('#')) / len(words) if words else 0
    if hashtag_ratio > 0.6:  # More than 60% hashtags
        return True
    
    return False


def collect_all_tweets(base_url, headers, user_accounts):
    """Collect tweets from all users with filtering"""
    all_tweets = []
    total_collected = 0
    total_filtered = 0

    print("\n2. Collecting tweets...")
    for username, account_id in user_accounts.items():
        print(f"  Getting tweets for {username}...")

        limit = 1000
        offset = 0
        user_tweet_count = 0
        user_filtered_count = 0

        while True:
            response = requests.get(
                f"{base_url}/tweets?account_id=eq.{account_id}&limit={limit}&offset={offset}",
                headers=headers
            )

            if response.status_code == 200:
                tweets = response.json()
                if not tweets:
                    break

                for tweet in tweets:
                    tweet_text = tweet.get('full_text', '').strip()
                
                    if should_filter_tweet(tweet_text):
                        user_filtered_count += 1
                        continue
                    
                    tweet['username'] = username
                    tweet['collected_at'] = datetime.now().isoformat()
                    all_tweets.append(tweet)
                    user_tweet_count += 1

                total_collected += len(tweets)
                offset += limit

                print(f"    Processed {total_collected} tweets | Kept: {user_tweet_count} | Filtered: {user_filtered_count}")

                if len(tweets) < limit:
                    break

            else:
                print(f"    Error getting tweets for {username}: {response.status_code}")
                break

        print(f"  ✓ {username}: Kept {user_tweet_count} tweets, filtered {user_filtered_count}")
        total_filtered += user_filtered_count

    print(f"\n📊 Filtering Summary:")
    print(f"  Total processed: {total_collected}")
    print(f"  Kept for embedding: {len(all_tweets)}")
    print(f"  Filtered out: {total_filtered}")
    print(f"  Filtering rate: {(total_filtered/total_collected)*100:.1f}%")

    return all_tweets


def save_tweets_to_csv(tweets):
    """Save tweets to CSV file using built-in csv module"""
    print("\n3. Saving to CSV...")

    if not tweets:
        print("  ✗ No tweets to save")
        return

    # Create filename with timestamp
    filename = f"tweets_data_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    all_fields = set()
    for tweet in tweets:
        all_fields.update(tweet.keys())

    fieldnames = sorted(list(all_fields))

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
