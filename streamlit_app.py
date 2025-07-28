

import streamlit as st
import pandas as pd
import numpy as np
import umap
import plotly.graph_objects as go
import plotly.express as px
import ast
import random
import requests
import json
import pickle
from datetime import datetime


#####################################################################################################
# Streamlit app for dynamic tweet embedding visualization
# This app allows users to visualize tweet embeddings using UMAP and interactively add test tweets.
# It connects to LM Studio API for generating embeddings and manages test tweets in a CSV file.
# run with: streamlit run streamlit_app.py
#####################################################################################################

st.title("Dynamic Tweet Embedding Visualization")

if st.button("Refresh Data"):
    st.cache_data.clear()


#####################################################################################################
# Load and process tweet data from CSV, filter out invalid embeddings, and return valid embeddings and their indices.
# This function reads a CSV file containing tweet embeddings, processes the embeddings to ensure they are valid,
# and returns a NumPy array of valid embeddings along with their corresponding row indices in the original DataFrame.
#####################################################################################################
@st.cache_data 
def load_base_tweets_and_fit_umap():
    """
    Load base tweets (excluding test tweets), fit UMAP model, and return the model and base coordinates.
    This function is cached and should never be cleared to maintain consistent positioning.
    """
    #df = pd.read_csv('tweets_with_embeddings_filtered_20250715_170725.csv')
    df = pd.read_csv('tweets_with_embeddings_filtered_20250714_190010.csv')
    
    base_embeddings = []
    base_indices = []
    
    for i, embedding_str in enumerate(df['embedding']):
        # Skip test tweets (IDs starting with '999')
        tweet_id = str(df.iloc[i].iloc[0])
        if tweet_id.startswith('999'):
            continue
            
        try:
            if pd.notna(embedding_str) and embedding_str != 'nan':
                embedding = ast.literal_eval(embedding_str)
                base_embeddings.append(embedding)
                base_indices.append(i)
        except:
            continue
    
    base_embeddings = np.array(base_embeddings)
    
    # Fit UMAP on base data only
    reducer = umap.UMAP(n_components=2, random_state=42, spread=1.25, min_dist=0.5)
    base_coordinates = reducer.fit_transform(base_embeddings)
    
    return reducer, base_coordinates, base_indices

# @st.cache_data 
############################################################################################################
# Load current CSV data including any test tweets.
# This function gets cleared when test tweets are added/removed.
############################################################################################################
def load_current_data():
    """
    Load current CSV data including any test tweets.
    This function gets cleared when test tweets are added/removed.
    """
    # df = pd.read_csv('tweets_with_embeddings_filtered_20250715_170725.csv')
    df = pd.read_csv('tweets_with_embeddings_filtered_20250714_190010.csv')
    return df

############################################################################################################
# Get real embedding from LM Studio API
# This function connects to the LM Studio API to get embeddings for a given text.
# It handles connection errors and returns None if the request fails.
############################################################################################################
def get_embedding_from_lmstudio(text):
    """Get real embedding from LM Studio API"""
    lm_studio_url = "http://10.0.0.7:1234/v1/embeddings"
    
    try:
        response = requests.post(lm_studio_url,
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
            st.error(f"LM Studio API error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Cannot connect to LM Studio: {e}")
        return None
############################################################################################################
# Add a test tweet with real LM Studio embedding to the CSV file
# This function generates a unique ID for the test tweet, retrieves its embedding,
# and appends it to the specified CSV file in the correct format.
# It handles both 3-column and original tweet formats.
############################################################################################################
def add_test_tweet_to_csv(tweet_text, csv_file_path):
    """Add a test tweet with real LM Studio embedding to the CSV file"""
    
    with st.spinner("Getting embedding from LM Studio..."):
        test_embedding = get_embedding_from_lmstudio(tweet_text)
    
    if test_embedding is None:
        return None
    
    test_embedding_str = str(test_embedding)
    
    # Generate unique ID starting with 999
    unique_id = int(f"999{int(datetime.now().timestamp() * 1000) % 100000000}")
    
    try:
        df_sample = pd.read_csv(csv_file_path, nrows=1)
        columns = df_sample.columns.tolist()
        
        if len(columns) == 3 and 'username' in columns and 'full_text' in columns and 'embedding' in columns:
            csv_row = f'{unique_id},"{tweet_text}","{test_embedding_str}"\n'
        else:
            current_date = datetime.now().strftime('%Y-%m-%d')
            csv_row = f'{unique_id},1,{current_date},{current_date},0,,"{tweet_text}",,,,,0,{current_date},testuser,"{test_embedding_str}"\n'
            
    except Exception as e:
        csv_row = f'testuser,"{tweet_text}","{test_embedding_str}"\n'
    
    with open(csv_file_path, 'a', encoding='utf-8') as f:
        f.write(csv_row)
    
    return unique_id, test_embedding

############################################################################################################
# Remove all test tweets from the CSV file using ID range
# This function filters out rows where the ID starts with '999' and rewrites the CSV.
# It returns the number of removed tweets.
############################################################################################################
def remove_test_tweets_from_csv(csv_file_path):
    """Remove all test tweets from the CSV file using ID range"""
    df = pd.read_csv(csv_file_path)
    
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)
    
    # Filter out rows where ID starts with '999'
    original_df = df[~df.iloc[:, 0].str.startswith('999')]
    
    # Write back to CSV
    original_df.to_csv(csv_file_path, index=False)
    
    return len(df) - len(original_df)

# Initialize session state
if 'test_tweets_coordinates' not in st.session_state:
    st.session_state.test_tweets_coordinates = {}

st.sidebar.header("Add Test Tweet")

with st.sidebar:
    test_tweet_input = st.text_area(
        "Enter your test tweet:",
        placeholder="Type your test tweet here...",
        height=100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Add Test Tweet", type="primary"):
            if test_tweet_input.strip():
                try:
                    # result = add_test_tweet_to_csv(test_tweet_input.strip(), 'tweets_with_embeddings_filtered_20250715_170725.csv')
                    test_id = add_test_tweet_to_csv(test_tweet_input.strip(), 'tweets_with_embeddings_filtered_20250714_190010.csv')
                    
                    if test_id:
                        test_id, test_embedding = test_id
                        
                        # Get the fitted UMAP model
                        reducer, _, _ = load_base_tweets_and_fit_umap()
                        
                        # Transform this single test tweet
                        test_coordinates = reducer.transform([test_embedding])
                        
                        # Store coordinates in session state
                        st.session_state.test_tweets_coordinates[str(test_id)] = {
                            'text': test_tweet_input.strip(),
                            'coordinates': test_coordinates[0]  # Extract the single coordinate pair
                        }
                        
                        # Clear data cache to reload CSV
                        # load_current_data.clear()
                        
                        st.success(f"Test tweet added successfully!")
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"Error adding test tweet: {str(e)}")
            else:
                st.warning("Please enter some text for the test tweet.")
    
    with col2:
        if st.button("Remove All Test Tweets", type="secondary"):
            try:
                # removed_count = remove_test_tweets_from_csv('tweets_with_embeddings_filtered_20250715_170725.csv')
                removed_count = remove_test_tweets_from_csv('tweets_with_embeddings_filtered_20250714_190010.csv')
                
                # Clear session state coordinates
                st.session_state.test_tweets_coordinates = {}
                
                # Clear data cache to reload CSV                               
                if removed_count > 0:
                    st.success(f"Removed {removed_count} test tweets!")
                else:
                    st.info("No test tweets found to remove.")
                    
                st.rerun()
                
            except Exception as e:
                st.error(f"Error removing test tweets: {str(e)}")

    # Display currently added test tweets
    if st.session_state.test_tweets_coordinates:
        st.subheader("Test Tweets Added This Session:")
        for i, (tweet_id, tweet_data) in enumerate(st.session_state.test_tweets_coordinates.items(), 1):
            tweet_text = tweet_data['text']
            st.write(f"{i}. {tweet_text[:50]}{'...' if len(tweet_text) > 50 else ''}")

# Load base model and coordinates (cached)
reducer, base_coordinates, base_indices = load_base_tweets_and_fit_umap()

# Load current data (includes any test tweets in CSV)
df = load_current_data()

st.write(f"Loaded {len(base_coordinates)} base tweets")

# Prepare data for plotting
all_coordinates = []
all_texts = []
all_colors = []

# Add base tweets
for i, coord in enumerate(base_coordinates):
    all_coordinates.append(coord)
    all_texts.append(df.iloc[base_indices[i]]['full_text'])
    all_colors.append(px.colors.qualitative.Set3[0])  # Blue for base tweets

# Add test tweets from session state coordinates
test_tweet_count = 0
for tweet_id, tweet_data in st.session_state.test_tweets_coordinates.items():
    # Verify this test tweet still exists in the CSV
    if any(str(df.iloc[i].iloc[0]) == tweet_id for i in range(len(df))):
        all_coordinates.append(tweet_data['coordinates'])
        all_texts.append(tweet_data['text'])
        all_colors.append('red')  # Red for test tweets
        test_tweet_count += 1

if test_tweet_count > 0:
    st.info(f"Currently showing {test_tweet_count} test tweets in red")

# Convert coordinates to arrays for plotting
if all_coordinates:
    coordinates_array = np.array(all_coordinates)
    
    fig = go.Figure(data=go.Scatter(
        x=coordinates_array[:, 0],
        y=coordinates_array[:, 1],
        mode='markers',
        text=all_texts,
        hovertemplate='<b>Tweet:</b><br>%{text}<extra></extra>',
        marker=dict(
            size=8,
            color=all_colors,
            opacity=0.7
        )
    ))
    
    fig.update_layout(
        title="Tweet Embeddings Cluster",
        xaxis_title="UMAP Dimension 1",
        yaxis_title="UMAP Dimension 2",
        yaxis=dict(autorange=True),
    )
    
    st.plotly_chart(fig, key='tweet_embedding_plot')
    
    st.markdown("**Legend:** 🔴 Red dots = Test tweets | 🔵 Blue dots = Original tweets")
else:
    st.error("No valid coordinates to display")


