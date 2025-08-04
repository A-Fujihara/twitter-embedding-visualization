import csv
import json
import requests
from datetime import datetime
import time
import sys
import os

## Run this file to generate embeddings for ALL tweets
## Using command:
## python generate_embeddings_production.py <input_csv_file>


def generate_embeddings():
    """
    Reads tweets from CSV and generates embeddings using LMStudio API
    PRODUCTION VERSION - processes ALL users
    """

    lm_studio_url = "http://10.0.0.7:1234/v1/embeddings"

    # Get input file from command line argument
    if len(sys.argv) != 2:
        print("Usage: python generate_embeddings_production.py <input_csv_file>")
        print("Example: python generate_embeddings_production.py tweets_data_filtered_20250729_143022.csv")
        return
    
    input_file = sys.argv[1]
    
    # Verify input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    output_file = f"tweets_with_embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    print("=== Generating Embeddings (Production) ===")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")

    if not test_lmstudio_connection(lm_studio_url):
        return

    process_all_tweets(input_file, output_file, lm_studio_url)


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


def process_all_tweets(input_file, output_file, lm_studio_url):
    """Process ALL tweets without filtering"""

    processed_count = 0
    error_count = 0
    start_time = time.time()

    print("📊 Processing all tweets in file...")

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
                    error_count += 1

                # Progress update every 100 tweets
                total_processed = processed_count + error_count
                if total_processed % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = total_processed / elapsed * 60 if elapsed > 0 else 0

                    print(f"  📈 {total_processed} tweets processed | "
                          f"Rate: {rate:.1f}/min | "
                          f"Successful: {processed_count} | "
                          f"Errors: {error_count}")

                writer.writerow(row)
    
    elapsed = time.time() - start_time
    total_processed = processed_count + error_count
    
    print(f"\n✅ Complete! Processed {total_processed} tweets in {elapsed / 60:.1f} minutes")
    print(f"   Successful embeddings: {processed_count}")
    print(f"   Errors: {error_count}")
    print(f"   Average rate: {processed_count / (elapsed / 60):.1f} tweets/minute")
    print(f"   Output: {output_file}")


if __name__ == "__main__":
    generate_embeddings()