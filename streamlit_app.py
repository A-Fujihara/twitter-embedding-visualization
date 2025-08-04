import streamlit as st
import pandas as pd
import numpy as np
import umap
import plotly.graph_objects as go
import plotly.express as px
import ast
import requests
from datetime import datetime
import glob
import os
import sys

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
# Auto-detect the most recent embeddings file or use specified file
#####################################################################################################
def get_latest_embeddings_file():
    """Find the most recent tweets_with_embeddings_*.csv file"""
    pattern = "tweets_with_embeddings_*.csv"
    files = glob.glob(pattern)
    
    if not files:
        return None
    
    # Sort by modification time and get the most recent
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

@st.cache_data
def get_embeddings_file():
    """Get embeddings file - either specified via command line or auto-detect most recent"""

    streamlit_args = [arg for arg in sys.argv if not arg.startswith('--')]
    
    if len(streamlit_args) > 1:
        specified_file = streamlit_args[1]
        if os.path.exists(specified_file):
            st.info(f"📁 Using specified file: {specified_file}")
            return specified_file
        else:
            st.error(f"❌ Specified file not found: {specified_file}")
            st.info("Falling back to auto-detection...")
    
    # Fall back to auto-detection
    latest_file = get_latest_embeddings_file()
    if not latest_file:
        st.error("❌ No embeddings files found! Please run the embedding generation first.")
        st.info("Expected filename pattern: tweets_with_embeddings_YYYYMMDD_HHMMSS.csv")
        return None
    
    st.info(f"🔍 Auto-detected file: {latest_file}")
    return latest_file

#####################################################################################################
# UMAP Configuration Panel
#####################################################################################################
st.sidebar.header("🎛️ UMAP Configuration")

with st.sidebar.expander("Clustering Parameters", expanded=True):
    n_neighbors = st.slider("n_neighbors", min_value=5, max_value=200, value=15, 
                           help="Controls local vs global structure. Lower = more local clusters")
    min_dist = st.slider("min_dist", min_value=0.0, max_value=1.0, value=0.1, step=0.05,
                        help="Minimum distance between points. Lower = tighter clusters")
    spread = st.slider("spread", min_value=0.5, max_value=3.0, value=1.0, step=0.1,
                      help="Scale of embedded points. Higher = more spread out")
    
    # Sample size for faster processing
    max_tweets = st.slider("Max tweets to visualize", min_value=1000, max_value=50000, value=21000, step=1000,
                          help="Reduce for faster processing")

#####################################################################################################
# Load and process tweet data from CSV, filter out invalid embeddings, and return valid embeddings and their indices.
# This function reads a CSV file containing tweet embeddings, processes the embeddings to ensure they are valid,
# and returns a NumPy array of valid embeddings along with their corresponding row indices in the original DataFrame.
#####################################################################################################
@st.cache_data 
def load_base_tweets_and_fit_umap(n_neighbors, min_dist, spread, max_tweets):
    """
    Load base tweets (excluding test tweets), fit UMAP model, and return the model and base coordinates.
    This function is cached and should never be cleared to maintain consistent positioning.
    """
    embeddings_file = get_embeddings_file()
    if not embeddings_file:
        return None, None, None
        
    try:
        df = pd.read_csv(embeddings_file, quotechar='"', on_bad_lines='skip', dtype=str)
    except:
        try:
            df = pd.read_csv(embeddings_file, quotechar='"', error_bad_lines=False, warn_bad_lines=False, dtype=str)
        except:
            df = pd.read_csv(embeddings_file, sep=',', quotechar='"', on_bad_lines='skip', engine='python', dtype=str)
    
    # Split into base tweets and test tweets BEFORE sampling
    test_tweets_mask = df.iloc[:, 0].str.startswith('999', na=False)
    base_tweets_df = df[~test_tweets_mask]
    test_tweets_df = df[test_tweets_mask]
    
    if len(base_tweets_df) > max_tweets:
        base_tweets_df = base_tweets_df.sample(n=max_tweets, random_state=42)
        st.info(f"📊 Sampled {max_tweets:,} base tweets from {len(df[~test_tweets_mask]):,} total")
    
    # Combine back together - test tweets are ALWAYS included
    df = pd.concat([base_tweets_df, test_tweets_df], ignore_index=True)
    
    base_embeddings = []
    base_indices = []
    
    for i, embedding_str in enumerate(df['embedding']):
        tweet_id = str(df.iloc[i].iloc[0]) if pd.notna(df.iloc[i].iloc[0]) else ""
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
    
    reducer = umap.UMAP(
        n_components=2, 
        random_state=42, 
        spread=spread, 
        min_dist=min_dist,
        n_neighbors=n_neighbors,
        metric='cosine'
    )
    base_coordinates = reducer.fit_transform(base_embeddings)
    
    return reducer, base_coordinates, base_indices

############################################################################################################
# Load current CSV data including any test tweets.
# This function gets cleared when test tweets are added/removed.
############################################################################################################
def load_current_data():
    """
    Load current CSV data including any test tweets.
    This function gets cleared when test tweets are added/removed.
    """
    embeddings_file = get_embeddings_file()
    if not embeddings_file:
        return None
        
    try:
        df = pd.read_csv(embeddings_file, quotechar='"', on_bad_lines='skip', dtype=str)
    except:
        try:
            df = pd.read_csv(embeddings_file, quotechar='"', error_bad_lines=False, warn_bad_lines=False, dtype=str)
        except:
            df = pd.read_csv(embeddings_file, sep=',', quotechar='"', on_bad_lines='skip', engine='python', dtype=str)
    
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
    
    unique_id = int(f"999{int(datetime.now().timestamp() * 1000) % 100000000}")
    
    # Read the header to get exact column structure
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        header_line = f.readline().strip()
        columns = header_line.split(',')
    
    st.write(f"🔍 CSV has {len(columns)} columns: {columns[:3]}...")
    
    # Create row with exact same number of columns
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Build row data matching exact structure
    row_data = [str(unique_id)]
    
    # Fill remaining columns based on expected structure
    for i in range(1, len(columns)):
        col_name = columns[i].strip('"').lower()
        if 'full_text' in col_name or 'text' in col_name:
            row_data.append(f'"{tweet_text.replace(chr(34), chr(34)+chr(34))}"')
        elif 'embedding' in col_name:
            row_data.append(f'"{test_embedding_str}"')
        elif 'username' in col_name:
            row_data.append('testuser')
        elif 'date' in col_name:
            row_data.append(current_date)
        else:
            row_data.append('')  # Empty for other columns
    
    csv_row = ','.join(row_data) + '\n'
    
    # Append to file
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
    try:
        df = pd.read_csv(csv_file_path, quotechar='"', on_bad_lines='skip', dtype=str)
    except:
        try:
            df = pd.read_csv(csv_file_path, quotechar='"', error_bad_lines=False, warn_bad_lines=False, dtype=str)
        except:
            df = pd.read_csv(csv_file_path, sep=',', quotechar='"', on_bad_lines='skip', engine='python', dtype=str)
    
    df.iloc[:, 0] = df.iloc[:, 0].fillna("")
    
    # Filter out rows where ID starts with '999'
    original_df = df[~df.iloc[:, 0].str.startswith('999')]
    
    # Write back to CSV
    original_df.to_csv(csv_file_path, index=False)
    
    return len(df) - len(original_df)

embeddings_file = get_embeddings_file()
if not embeddings_file:
    st.stop()

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
                    test_id = add_test_tweet_to_csv(test_tweet_input.strip(), embeddings_file)
                    
                    if test_id:
                        test_id, test_embedding = test_id
                        
                        # Get the fitted UMAP model
                        reducer, _, _ = load_base_tweets_and_fit_umap(n_neighbors, min_dist, spread, max_tweets)
                        
                        # Transform this single test tweet
                        test_coordinates = reducer.transform([test_embedding])
                        
                        # Store coordinates in session state
                        st.session_state.test_tweets_coordinates[str(test_id)] = {
                            'text': test_tweet_input.strip(),
                            'coordinates': test_coordinates[0]
                        }
                        
                        st.success(f"Test tweet added successfully!")
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"Error adding test tweet: {str(e)}")
            else:
                st.warning("Please enter some text for the test tweet.")
    
    with col2:
        if st.button("Remove All Test Tweets", type="secondary"):
            try:
                removed_count = remove_test_tweets_from_csv(embeddings_file)
                
                # Clear session state coordinates
                st.session_state.test_tweets_coordinates = {}
                               
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
reducer, base_coordinates, base_indices = load_base_tweets_and_fit_umap(n_neighbors, min_dist, spread, max_tweets)

# Load current data (includes any test tweets in CSV)
df = load_current_data()

st.write(f"Loaded {len(base_coordinates)} base tweets")

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
    
    # Check if this test tweet exists in the CSV
    tweet_found = False
    for i in range(len(df)):
        csv_id = str(df.iloc[i].iloc[0]) if pd.notna(df.iloc[i].iloc[0]) else ""
        if csv_id == tweet_id:
            tweet_found = True
            break
    
    if tweet_found:
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