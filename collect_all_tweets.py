import requests
import json
import csv
from datetime import datetime
import re
import os

###############################################################################################
# collect_all_tweets.py
# This script collects tweets from users in a Supabase database, filters them, and saves them
# to a CSV file with checkpointing support.
# It handles resuming from previous checkpoints, filtering out low-quality tweets, and writing
# tweets incrementally to avoid memory issues.
###############################################################################################
def collect_user_tweets():
    """
    Collects tweets from target users and saves to CSV with checkpointing
    """
    # Supabase API setup
    base_url = "https://fabxmporizzqflnftavs.supabase.co/rest/v1"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhYnhtcG9yaXp6cWZsbmZ0YXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjIyNDQ5MTIsImV4cCI6MjAzNzgyMDkxMn0.UIEJiUNkLsW28tBHmG-RQDW-I5JNlJLt62CSk9D_qG8"

    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}"
    }

    print("=== Collecting Tweet Data with Checkpointing ===")

    # Check for existing checkpoint files
    checkpoint_data, checkpoint_filename = find_existing_checkpoint()

    if checkpoint_data:
        print(f"📁 Resuming from checkpoint: {checkpoint_filename}")
        print(f"   Last completed user: {checkpoint_data.get('current_user', 'None')}")
        print(f"   Total tweets collected so far: {checkpoint_data.get('total_tweets_collected', 0)}")
        print(f"   Completed users: {len(checkpoint_data.get('completed_users', []))}")
        csv_filename = checkpoint_data['csv_filename']
    else:
        print("🆕 Starting fresh collection...")
        # Create filenames with timestamp ONLY for new collections
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"tweets_data_filtered_{timestamp}.csv"
        checkpoint_filename = f"checkpoint_{timestamp}.json"
        
        checkpoint_data = {
            'csv_filename': csv_filename,
            'completed_users': [],
            'current_user': None,
            'current_offset': 0,
            'total_tweets_collected': 0,
            'total_tweets_filtered': 0,
            'start_time': datetime.now().isoformat()
        }

    # Get all account IDs
    user_accounts = get_all_account_ids(base_url, headers)

    # Filter out already completed users
    remaining_users = {k: v for k, v in user_accounts.items()
                       if k not in checkpoint_data.get('completed_users', [])}

    print(f"👥 Total users: {len(user_accounts)}")
    print(f"✅ Completed users: {len(checkpoint_data.get('completed_users', []))}")
    print(f"⏳ Remaining users: {len(remaining_users)}")

    # Initialize CSV file if starting fresh
    if not checkpoint_data.get('completed_users'):
        initialize_csv_file(csv_filename)

    # Collect tweets with checkpointing
    collect_tweets_with_checkpoints(
        base_url, headers, remaining_users,
        csv_filename, checkpoint_filename, checkpoint_data
    )

    print(f"\n=== Collection Complete ===")
    # Clean up checkpoint file when done
    if os.path.exists(checkpoint_filename):
        os.remove(checkpoint_filename)
        print("🗑️ Checkpoint file cleaned up")

###############################################################################################
# Helper functions for checkpointing and CSV management
###############################################################################################
def find_existing_checkpoint():
    """Find existing checkpoint files and return the most recent one"""
    checkpoint_files = [f for f in os.listdir('.') if f.startswith('checkpoint_') and f.endswith('.json')]
    
    if not checkpoint_files:
        return None, None
    
    # Get the most recent checkpoint file
    most_recent = max(checkpoint_files, key=os.path.getmtime)
    
    try:
        with open(most_recent, 'r') as f:
            checkpoint_data = json.load(f)
        return checkpoint_data, most_recent
    except:
        print(f"⚠️ Corrupted checkpoint file: {most_recent}, starting fresh")
        return None, None

################################################################################################
# Functions for loading and saving checkpoints, initializing CSV, and appending tweets
################################################################################################
def load_checkpoint(checkpoint_filename):
    """Load checkpoint data if it exists"""
    if os.path.exists(checkpoint_filename):
        try:
            with open(checkpoint_filename, 'r') as f:
                return json.load(f)
        except:
            print("⚠️ Corrupted checkpoint file, starting fresh")
    return None

#################################################################################################
# Save checkpoint data to file
#################################################################################################
def save_checkpoint(checkpoint_filename, checkpoint_data):
    """Save current progress to checkpoint file"""
    checkpoint_data['last_updated'] = datetime.now().isoformat()
    with open(checkpoint_filename, 'w') as f:
        json.dump(checkpoint_data, f, indent=2)

##################################################################################################
# Initialize CSV file with headers
##################################################################################################
def initialize_csv_file(csv_filename):
    """Initialize CSV file with headers"""
    # Standard tweet fields we expect
    fieldnames = [
        'id', 'full_text', 'created_at', 'retweet_count', 'favorite_count',
        'account_id', 'username', 'collected_at'
    ]

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

    print(f"📄 Initialized CSV file: {csv_filename}")

##################################################################################################
# Append tweets to existing CSV file
##################################################################################################
def append_tweets_to_csv(tweets, csv_filename):
    """Append tweets to existing CSV file"""
    if not tweets:
        return

    # Get existing fieldnames from CSV
    with open(csv_filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        fieldnames = next(reader)  # Read header row

    # Append tweets
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writerows(tweets)

##################################################################################################
# Get all account IDs from the database
##################################################################################################
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

##################################################################################################
# Function to filter out low-quality tweets
##################################################################################################
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
    if len(tweet_text) < 15:
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

##################################################################################################
# Function to collect tweets with checkpoints
##################################################################################################
def collect_tweets_with_checkpoints(base_url, headers, user_accounts, csv_filename, checkpoint_filename,
                                    checkpoint_data):
    """Collect tweets from all users with checkpointing and incremental CSV writing"""

    print("\n2. Collecting tweets with checkpointing...")

    for username, account_id in user_accounts.items():
        print(f"  📥 Processing {username}...")

        # Update checkpoint for current user
        checkpoint_data['current_user'] = username
        checkpoint_data['current_offset'] = 0
        save_checkpoint(checkpoint_filename, checkpoint_data)

        limit = 1000
        offset = 0
        user_tweets_batch = []
        user_tweet_count = 0
        user_filtered_count = 0

        while True:
            try:
                response = requests.get(
                    f"{base_url}/tweets?account_id=eq.{account_id}&limit={limit}&offset={offset}",
                    headers=headers
                )

                if response.status_code == 200:
                    tweets = response.json()
                    if not tweets:
                        break

                    # Process tweets in this batch
                    for tweet in tweets:
                        tweet_text = tweet.get('full_text', '').strip()

                        # Apply filtering
                        if should_filter_tweet(tweet_text):
                            user_filtered_count += 1
                            continue

                        # Add metadata to tweet
                        tweet['username'] = username
                        tweet['collected_at'] = datetime.now().isoformat()
                        user_tweets_batch.append(tweet)
                        user_tweet_count += 1

                    # Write batch to CSV every 1000 processed tweets or when done with user
                    if len(user_tweets_batch) >= 500 or len(tweets) < limit:
                        append_tweets_to_csv(user_tweets_batch, csv_filename)
                        checkpoint_data['total_tweets_collected'] += len(user_tweets_batch)
                        checkpoint_data['total_tweets_filtered'] += user_filtered_count
                        user_tweets_batch = []  # Clear batch
                        user_filtered_count = 0  # Reset for next batch

                    offset += limit
                    checkpoint_data['current_offset'] = offset

                    # Save checkpoint every 5000 tweets processed
                    if offset % 5000 == 0:
                        save_checkpoint(checkpoint_filename, checkpoint_data)
                        print(f"    💾 Checkpoint saved at offset {offset}")

                    print(f"    Processed {offset} tweets | Kept: {user_tweet_count}")

                    if len(tweets) < limit:
                        break

                else:
                    print(f"    ❌ Error getting tweets for {username}: {response.status_code}")
                    break

            except Exception as e:
                print(f"    ⚠️ Exception for {username}: {e}")
                break

        # Mark user as completed
        checkpoint_data['completed_users'].append(username)
        checkpoint_data['current_user'] = None
        checkpoint_data['current_offset'] = 0
        save_checkpoint(checkpoint_filename, checkpoint_data)

        print(f"  ✅ {username}: Kept {user_tweet_count} tweets")

    print(f"\n📊 Final Summary:")
    print(f"  Total tweets collected: {checkpoint_data['total_tweets_collected']}")
    print(f"  Total tweets filtered: {checkpoint_data['total_tweets_filtered']}")


if __name__ == "__main__":
    collect_user_tweets()
