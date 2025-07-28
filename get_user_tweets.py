"""
Supabase API Connection Test Script

This module tests the connection to a Supabase database containing Twitter/X account
and tweet data. It performs three main tests: retrieving accounts, searching for
specific target users, and fetching sample tweets.

Author: Generated for API testing
"""

import requests
import json


def test_supabase_connection():
    """
    Main function to test Supabase API connectivity and data retrieval.

    Performs three tests:
    1. Retrieves available accounts from the database
    2. Searches for specific target usernames
    3. Fetches sample tweets to verify data access

    Returns:
        None: Prints test results to console
    """

    # Supabase API setup
    base_url = "https://fabxmporizzqflnftavs.supabase.co/rest/v1"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhYnhtcG9yaXp6cWZsbmZ0YXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjIyNDQ5MTIsImV4cCI6MjAzNzgyMDkxMn0.UIEJiUNkLsW28tBHmG-RQDW-I5JNlJLt62CSk9D_qG8"

    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}"
    }

    print("=== Testing Supabase API Connection ===")

    # Test 1: Get accounts with usernames
    get_available_accounts(base_url, headers)

    # Test 2: Try to find specific users
    search_target_users(base_url, headers)

    # Test 3: Get some tweets from a user
    test_tweet_retrieval(base_url, headers)

    print("\n=== API Test Complete ===")


def get_available_accounts(base_url, headers):
    """
    Retrieves and displays available accounts from the Supabase database.

    Args:
        base_url (str): The base URL for the Supabase API
        headers (dict): HTTP headers containing API key and authorization

    Returns:
        None: Prints account information to console
    """
    print("\n1. Getting available accounts...")
    response = requests.get(f"{base_url}/account?limit=20", headers=headers)
    print("Status:", response.status_code)

    if response.status_code == 200:
        accounts = response.json()
        print(f"\nFound {len(accounts)} accounts:")
        for account in accounts[:10]:  # Show first 10
            username = account.get('username', 'N/A')
            account_id = account.get('account_id', 'N/A')
            print(f"  - {username} (ID: {account_id})")
    else:
        print("Error getting accounts:", response.text)


def search_target_users(base_url, headers):
    """
    Searches for specific target usernames in the database.

    Args:
        base_url (str): The base URL for the Supabase API
        headers (dict): HTTP headers containing API key and authorization

    Returns:
        None: Prints search results for each target user
    """
    target_users = ['patio11', 'eigenrobot', 'visakanv', 'defenderofbasic']
    print(f"\n2. Looking for target users: {target_users}")

    for username in target_users:
        response = requests.get(f"{base_url}/account?username=eq.{username}", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            if user_data:
                account_id = user_data[0]['account_id']
                print(f"  ✓ Found {username}: {account_id}")
            else:
                print(f"  ✗ {username} not found")
        else:
            print(f"  ✗ Error searching for {username}")


def test_tweet_retrieval(base_url, headers):
    """
    Tests tweet retrieval functionality by fetching sample tweets.

    Args:
        base_url (str): The base URL for the Supabase API
        headers (dict): HTTP headers containing API key and authorization

    Returns:
        None: Prints sample tweet data and available fields
    """
    print("\n3. Testing tweet retrieval...")
    response = requests.get(f"{base_url}/tweets?limit=5", headers=headers)
    if response.status_code == 200:
        tweets = response.json()
        print(f"Sample tweets found: {len(tweets)}")
        if tweets:
            first_tweet = tweets[0]
            print(f"  Sample tweet: {first_tweet.get('full_text', 'N/A')[:100]}...")
            print(f"  Keys available: {list(first_tweet.keys())}")
    else:
        print("Error getting tweets:", response.text)


if __name__ == "__main__":
    test_supabase_connection()