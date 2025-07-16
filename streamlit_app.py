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
from datetime import datetime

# run with: streamlit run streamlit_app.py

st.title("Dynamic Tweet Embedding Visualization")

if st.button("Refresh Data"):
    st.cache_data.clear()

@st.cache_data 
def load_and_process_data():
    """
    Load tweet data from CSV, filter out invalid embeddings, and return valid embeddings and their indices.
    This function reads a CSV file containing tweet embeddings, processes the embeddings to ensure they are valid,
    and returns a NumPy array of valid embeddings along with their corresponding row indices in the original DataFrame.
    """
    #df = pd.read_csv('tweets_with_embeddings_filtered_20250602_125325.csv') <-- ORIGINAL FILE -- DO NOT DELETE
    #df = pd.read_csv('tweets_with_embeddings_filtered_20250629_144705.csv') <-- DO NOT DELETE


    #df = pd.read_csv('tweets_with_embeddings_filtered_20250714_190010.csv') <-- DO NOT DELETE
    df = pd.read_csv('tweets_with_embeddings_filtered_20250715_170725.csv')
    
    embeddings = []
    valid_indices = []
    
    for i, embedding_str in enumerate(df['embedding']):
        try:
            if pd.notna(embedding_str) and embedding_str != 'nan':
                embedding = ast.literal_eval(embedding_str)
                embeddings.append(embedding)
                valid_indices.append(i)
        except:
            continue
    return np.array(embeddings), valid_indices, df

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
    

def add_test_tweet_to_csv(tweet_text, csv_file_path):
    """Add a test tweet with real LM Studio embedding to the CSV file - works with both formats"""
    # Get real embedding from LM Studio
    with st.spinner("Getting embedding from LM Studio..."):
        test_embedding = get_embedding_from_lmstudio(tweet_text)
    
    if test_embedding is None:
        return None
    
    test_embedding_str = str(test_embedding)
    
    # Generate unique ID starting with 999
    unique_id = int(f"999{int(datetime.now().timestamp() * 1000) % 100000000}")
    
    # Read the CSV to detect its format
    try:
        df_sample = pd.read_csv(csv_file_path, nrows=1)
        columns = df_sample.columns.tolist()
        
        if len(columns) == 3 and 'username' in columns and 'full_text' in columns and 'embedding' in columns:
            # Breakfast data format (3 columns) - but we need to modify to include ID in username field
            csv_row = f'{unique_id},"{tweet_text}","{test_embedding_str}"\n'
        else:
            # Original tweet format (15+ columns)
            current_date = datetime.now().strftime('%Y-%m-%d')
            csv_row = f'{unique_id},1,{current_date},{current_date},0,,"{tweet_text}",,,,,0,{current_date},testuser,"{test_embedding_str}"\n'
            
    except Exception as e:
        # Fallback to 3-column format if detection fails
        csv_row = f'testuser,"{tweet_text}","{test_embedding_str}"\n'
    
    # Append to CSV
    with open(csv_file_path, 'a', encoding='utf-8') as f:
        f.write(csv_row)
    
    return unique_id

def remove_test_tweets_from_csv(csv_file_path):
    """Remove all test tweets from the CSV file using ID range"""
    df = pd.read_csv(csv_file_path)
    
    # Convert the first column to string to handle potential data type issues
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)
    
    # Filter out rows where ID starts with '999'
    original_df = df[~df.iloc[:, 0].str.startswith('999')]
    
    # Write back to CSV
    original_df.to_csv(csv_file_path, index=False)
    
    return len(df) - len(original_df)  # Return number of removed tweets

# Initialize session state for managing test tweets
if 'test_tweets_added' not in st.session_state:
    st.session_state.test_tweets_added = []

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
                    # Add to CSV
                    #test_id = add_test_tweet_to_csv(test_tweet_input.strip(), 'tweets_with_embeddings_filtered_20250714_190010.csv')
                    test_id = add_test_tweet_to_csv(test_tweet_input.strip(), 'tweets_with_embeddings_filtered_20250715_170725.csv')
                    
                    # Track in session state with ID for potential individual removal later
                    st.session_state.test_tweets_added.append({
                        'text': test_tweet_input.strip(),
                        'id': test_id
                    })
                    
                    # Clear cache to reload data
                    st.cache_data.clear()
                    
                    st.success(f"Test tweet added successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error adding test tweet: {str(e)}")
            else:
                st.warning("Please enter some text for the test tweet.")
    
    with col2:
        if st.button("Remove All Test Tweets", type="secondary"):
            try:
                #removed_count = remove_test_tweets_from_csv('tweets_with_embeddings_filtered_20250714_190010.csv') <-- DO NOT DELETE
                removed_count = remove_test_tweets_from_csv('tweets_with_embeddings_filtered_20250715_170725.csv')
                
                # Clear session state
                st.session_state.test_tweets_added = []
                
                # Clear cache to reload data
                st.cache_data.clear()
                
                if removed_count > 0:
                    st.success(f"Removed {removed_count} test tweets!")
                else:
                    st.info("No test tweets found to remove.")
                    
                st.rerun()
                
            except Exception as e:
                st.error(f"Error removing test tweets: {str(e)}")

    # Display currently added test tweets
    if st.session_state.test_tweets_added:
        st.subheader("Test Tweets Added This Session:")
        for i, tweet_data in enumerate(st.session_state.test_tweets_added, 1):
            tweet_text = tweet_data['text'] if isinstance(tweet_data, dict) else tweet_data
            st.write(f"{i}. {tweet_text[:50]}{'...' if len(tweet_text) > 50 else ''}")

# Generate UMAP plot
embeddings, valid_indices, df = load_and_process_data()

st.write(f"Loaded {len(embeddings)} valid embeddings")

# Count test tweets
test_tweet_count = sum(1 for i in valid_indices if str(df.iloc[i].iloc[0]).startswith('999'))
if test_tweet_count > 0:
    st.info(f"Currently showing {test_tweet_count} test tweets in red")

reducer = umap.UMAP(n_components=2, random_state=42, spread=1.25, min_dist=0.5)
print(f"UMAP random_state: {reducer.random_state}")
embedding_2d = reducer.fit_transform(embeddings)
print(f"First few coordinates: {embedding_2d[:3]}")

print(f"Y range: {embedding_2d[:, 1].min()} to {embedding_2d[:, 1].max()}")
print(f"Test tweet found: {'This is test tweet 3 with correct dimensions' in [df.iloc[i]['full_text'] for i in valid_indices]}")

print(f"Y range: {embedding_2d[:, 1].min()} to {embedding_2d[:, 1].max()}")
colors = []
for i in valid_indices:
    # Check if this row has an ID starting with '999' (test tweet)
    tweet_id = str(df.iloc[i].iloc[0])  # First column is the ID
    if tweet_id.startswith('999'):
        colors.append('red') 
    else:
        colors.append(px.colors.qualitative.Set3[0])

print(f"Colors array length: {len(colors)}")
print(f"Red colors found: {colors.count('red')}")
print(f"First few colors: {colors[:10]}")

fig = go.Figure(data=go.Scatter(
    x=embedding_2d[:, 0],
    y=embedding_2d[:, 1],
    mode='markers',
    text=[df.iloc[i]['full_text'] for i in valid_indices],
    hovertemplate='<b>Tweet:</b><br>%{text}<extra></extra>',
    marker=dict(
        size=8,
        color=colors,
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