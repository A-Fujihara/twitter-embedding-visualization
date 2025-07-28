import csv
import json
import requests
from datetime import datetime
import time


def generate_embeddings():
    """
    Reads tweets from CSV and generates embeddings using LMStudio API
    """

    # LMStudio API configuration
    lm_studio_url = "http://localhost:1234/v1/embeddings"

    # Input and output files
    input_file = "tweets_data_20250602_104228.csv"
    output_file = f"tweets_with_embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    print("=== Generating Embeddings (OPTIMIZED) ===")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")

    # Test connection
    if not test_lmstudio_connection(lm_studio_url):
        return

    # Process tweets
    process_tweets_optimized(input_file, output_file, lm_studio_url)


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
    """Get embedding with faster timeout"""
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


def process_tweets_optimized(input_file, output_file, lm_studio_url):
    """Process tweets with better progress tracking"""

    processed_count = 0
    error_count = 0
    start_time = time.time()

    # First, count total tweets
    with open(input_file, 'r', encoding='utf-8') as f:
        total_tweets = sum(1 for line in f) - 1  # Subtract header

    print(f"📊 Total tweets to process: {total_tweets}")

    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['embedding']

        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
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

                # Progress update every 50 tweets
                if (processed_count + error_count) % 50 == 0:
                    elapsed = time.time() - start_time
                    rate = (processed_count + error_count) / elapsed * 60  # per minute
                    remaining = (total_tweets - processed_count - error_count) / rate if rate > 0 else 0

                    print(f"  📈 {processed_count + error_count}/{total_tweets} tweets | "
                          f"Rate: {rate:.1f}/min | "
                          f"ETA: {remaining:.1f} minutes | "
                          f"Errors: {error_count}")

                writer.writerow(row)

    elapsed = time.time() - start_time
    print(f"\n✅ Complete! Processed {processed_count} tweets in {elapsed / 60:.1f} minutes")
    print(f"   Rate: {processed_count / (elapsed / 60):.1f} tweets/minute")
    print(f"   Errors: {error_count}")
    print(f"   Output: {output_file}")


if __name__ == "__main__":
    generate_embeddings()