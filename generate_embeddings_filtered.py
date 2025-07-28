import csv
import json
import requests
from datetime import datetime
import time

## Run this file to generate embeddings for tweets from specific users
## Using command:
## python generate_embeddings_filtered.py


def generate_embeddings():
    """
    Reads tweets from CSV and generates embeddings using LMStudio API
    FILTERED for danielgolliner and mcd0w only (proof of concept)
    """

    lm_studio_url = "http://10.0.0.7:1234/v1/embeddings"

    # Input and output files
    
    # input_file = "tweets_data_20250629_131806.csv"
    input_file = "tweets_data_20250714_185858.csv" # <-- DO NOT DELETE

    output_file = f"tweets_with_embeddings_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"


    target_users = ['breakfast_survey'] # <-- Original file DO NOT DELETE
    # target_users = ['mcd0w']

    print("=== Generating Embeddings ===")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Target users: {target_users}")

    # Test connection
    if not test_lmstudio_connection(lm_studio_url):
        return

    process_tweets_filtered(input_file, output_file, lm_studio_url, target_users)

def test_lmstudio_connection(url):
    """Test if LMStudio API is working"""
    try:
        test_response = requests.post(url,
                                      json={
                                          "model": "text-embedding-nomic-embed-text-v1.5",
                                          "input": ["test"]
                                      },
                                      timeout=10
                                      )

        if test_response.status_code == 200:
            print("✅ LMStudio connection successful")
            return True
        else:
            print(f"❌ LMStudio API error: {test_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Cannot connect to LMStudio: {e}")
        return False

def get_embedding_fast(text, url):
    """Get embedding for a single text using LMStudio API"""

    try:
        response = requests.post(url,
                                 json={
                                     "model": "text-embedding-nomic-embed-text-v1.5",
                                     "input": [text]
                                 },
                                 timeout=10
                                 )

        if response.status_code == 200:
            data = response.json()
            return data['data'][0]['embedding']
        else:
            return None

    except Exception as e:
        return None

# Process tweets with filtering for specific users
# This function reads tweets from a CSV file, filters for specific users, and generates embeddings using LMStudio API.
# It writes the results to a new CSV file, including the embeddings for each tweet.
# It also provides progress updates and error handling.
def process_tweets_filtered(input_file, output_file, lm_studio_url, target_users):
    """Process tweets with filtering for specific users"""

    processed_count = 0
    error_count = 0
    skipped_count = 0
    start_time = time.time()

    # First pass: count tweets for target users
    target_tweet_count = 0
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] in target_users:
                target_tweet_count += 1

    print(f"📊 Total tweets from target users: {target_tweet_count}")

    # Second pass: process tweets
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['embedding']

        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                username = row['username']

                # Skip users not in target list
                if username not in target_users:
                    skipped_count += 1
                    continue

                tweet_text = row.get('full_text', '').strip()

                if tweet_text:
                    embedding = get_embedding_fast(tweet_text, lm_studio_url)

                    if embedding:
                        row['embedding'] = json.dumps(embedding)
                        processed_count += 1
                    else:
                        row['embedding'] = ''
                        error_count += 1
                else:
                    row['embedding'] = ''

                # Progress update every 25 tweets
                if (processed_count + error_count) % 25 == 0:
                    elapsed = time.time() - start_time
                    rate = (processed_count + error_count) / elapsed * 60 if elapsed > 0 else 0
                    remaining_tweets = target_tweet_count - processed_count - error_count
                    remaining_time = remaining_tweets / rate if rate > 0 else 0

                    print(f"  📈 {processed_count + error_count}/{target_tweet_count} tweets | "
                          f"Rate: {rate:.1f}/min | "
                          f"ETA: {remaining_time:.1f} minutes | "
                          f"Errors: {error_count}")

                writer.writerow(row)
    
    elapsed = time.time() - start_time
    print(f"\n✅ Complete! Processed {processed_count} tweets in {elapsed / 60:.1f} minutes")
    print(f"   Rate: {processed_count / (elapsed / 60):.1f} tweets/minute")
    print(f"   Errors: {error_count}")
    print(f"   Skipped: {skipped_count} (other users)")
    print(f"   Output: {output_file}")


if __name__ == "__main__":
    generate_embeddings()