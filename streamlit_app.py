# import streamlit as st
# import pandas as pd
# import numpy as np
# import umap
# import plotly.graph_objects as go
# import plotly.express as px
# import ast

# # run with: streamlit run streamlit_app.py

# st.title("Dynamic Tweet Embedding Visualization")

# if st.button("Refresh Data"):
#     st.cache_data.clear()

# @st.cache_data 
# def load_and_process_data():
#     """
#     Load tweet data from CSV, filter out invalid embeddings, and return valid embeddings and their indices.
#     This function reads a CSV file containing tweet embeddings, processes the embeddings to ensure they are valid,
#     and returns a NumPy array of valid embeddings along with their corresponding row indices in the original DataFrame.
#     """
#     #df = pd.read_csv('tweets_with_embeddings_filtered_20250602_125325.csv') <-- ORIGINAL FILE -- DO NOT DELETE
#     df = pd.read_csv('tweets_with_embeddings_filtered_20250629_144705.csv')
    
#     embeddings = []
#     valid_indices = []
    
#     for i, embedding_str in enumerate(df['embedding']):
#         try:
#             if pd.notna(embedding_str) and embedding_str != 'nan':
#                 embedding = ast.literal_eval(embedding_str)
#                 embeddings.append(embedding)
#                 valid_indices.append(i)
#         except:
#             continue
#     return np.array(embeddings), valid_indices, df

# # Generate UMAP plot
# embeddings, valid_indices, df = load_and_process_data()

# st.write(f"Loaded {len(embeddings)} valid embeddings")

# reducer = umap.UMAP(n_components=2, random_state=42, spread=1.25, min_dist=0.5)
# print(f"UMAP random_state: {reducer.random_state}")
# embedding_2d = reducer.fit_transform(embeddings)
# print(f"First few coordinates: {embedding_2d[:3]}")

# print(f"Y range: {embedding_2d[:, 1].min()} to {embedding_2d[:, 1].max()}")
# print(f"Test tweet found: {'This is test tweet 3 with correct dimensions' in [df.iloc[i]['full_text'] for i in valid_indices]}")

# print(f"Y range: {embedding_2d[:, 1].min()} to {embedding_2d[:, 1].max()}")
# colors = []
# for i in valid_indices:
#     if 'test tweet' in df.iloc[i]['full_text'].lower():
#         colors.append('red') 
#     else:
#         colors.append(px.colors.qualitative.Set3[0])

# print(f"Colors array length: {len(colors)}")
# print(f"Red colors found: {colors.count('red')}")
# print(f"First few colors: {colors[:10]}")

# fig = go.Figure(data=go.Scatter(
#     x=embedding_2d[:, 0],
#     y=embedding_2d[:, 1],
#     mode='markers',
#     text=[df.iloc[i]['full_text'] for i in valid_indices],
#     hovertemplate='<b>Tweet:</b><br>%{text}<extra></extra>',
#     marker=dict(
#         size=8,
#         color=colors,
#         opacity=0.7
#     )
# ))

# fig.update_layout(
#     title="Tweet Embeddings Cluster",
#     xaxis_title="UMAP Dimension 1",
#     yaxis_title="UMAP Dimension 2",
#     yaxis=dict(autorange=True),
# )

# st.plotly_chart(fig, key='tweet_embedding_plot')

## python -c "   --> Runs python from command line, instad of file
## import random --> import random
## test_embedding = [random.random() for _ in range(768)] --> Generate a random embedding with 768 dimensions
## test_embedding_str = str(test_embedding) --> Convert the list to a string representation
## print(f'999997,1,2025-06-19,2025-06-19,0,,\"This is test tweet 3 with correct dimensions\",,,,,0,2025-06-19,testuser,\"{test_embedding_str}\"') --> This generates a test tweet with a valid embedding 
## " >> tweets_with_embeddings_filtered_20250602_125325.csv


###################################################################################################################################################################



# import streamlit as st
# import pandas as pd
# import numpy as np
# import umap
# import plotly.graph_objects as go
# import plotly.express as px
# import ast
# import random
# from datetime import datetime

# # run with: streamlit run streamlit_app.py

# st.title("Dynamic Tweet Embedding Visualization")

# if st.button("Refresh Data"):
#     st.cache_data.clear()

# @st.cache_data 
# def load_and_process_data():
#     """
#     Load tweet data from CSV, filter out invalid embeddings, and return valid embeddings and their indices.
#     This function reads a CSV file containing tweet embeddings, processes the embeddings to ensure they are valid,
#     and returns a NumPy array of valid embeddings along with their corresponding row indices in the original DataFrame.
#     """
#     #df = pd.read_csv('tweets_with_embeddings_filtered_20250602_125325.csv') <-- ORIGINAL FILE -- DO NOT DELETE
#     df = pd.read_csv('tweets_with_embeddings_filtered_20250629_144705.csv')
    
#     embeddings = []
#     valid_indices = []
    
#     for i, embedding_str in enumerate(df['embedding']):
#         try:
#             if pd.notna(embedding_str) and embedding_str != 'nan':
#                 embedding = ast.literal_eval(embedding_str)
#                 embeddings.append(embedding)
#                 valid_indices.append(i)
#         except:
#             continue
#     return np.array(embeddings), valid_indices, df

# def add_test_tweet_to_csv(tweet_text, csv_file_path):
#     """Add a test tweet with random embedding to the CSV file"""
#     # Generate random 768-dimensional embedding
#     test_embedding = [random.random() for _ in range(768)]
#     test_embedding_str = str(test_embedding)
    
#     # Generate unique ID (using current timestamp)
#     unique_id = int(datetime.now().timestamp() * 1000)
    
#     # Create CSV row - Make sure to prefix with "TEST TWEET: " for easy identification
#     current_date = datetime.now().strftime('%Y-%m-%d')
#     prefixed_tweet = f"TEST TWEET: {tweet_text}"
#     csv_row = f'{unique_id},1,{current_date},{current_date},0,,"{prefixed_tweet}",,,,,0,{current_date},testuser,"{test_embedding_str}"\n'
    
#     # Append to CSV
#     with open(csv_file_path, 'a', encoding='utf-8') as f:
#         f.write(csv_row)

# def remove_test_tweets_from_csv(csv_file_path):
#     """Remove all test tweets from the CSV file"""
#     df = pd.read_csv(csv_file_path)
    
#     # Filter out rows where full_text contains 'TEST TWEET:' (our prefix)
#     # Only remove test tweets, preserve original data
#     original_df = df[~df['full_text'].str.contains('TEST TWEET:', case=False, na=False)]
    
#     # Write back to CSV
#     original_df.to_csv(csv_file_path, index=False)
    
#     return len(df) - len(original_df)  # Return number of removed tweets

# # Initialize session state for managing test tweets
# if 'test_tweets_added' not in st.session_state:
#     st.session_state.test_tweets_added = []

# # Test Tweet Input Section
# st.sidebar.header("Add Test Tweet")

# with st.sidebar:
#     test_tweet_input = st.text_area(
#         "Enter your test tweet:",
#         placeholder="Type your test tweet here...",
#         height=100
#     )
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         if st.button("Add Test Tweet", type="primary"):
#             if test_tweet_input.strip():
#                 try:
#                     # Add to CSV
#                     add_test_tweet_to_csv(test_tweet_input.strip(), 'tweets_with_embeddings_filtered_20250629_144705.csv')
                    
#                     # Track in session state (without the prefix for cleaner display)
#                     st.session_state.test_tweets_added.append(test_tweet_input.strip())
                    
#                     # Clear cache to reload data
#                     st.cache_data.clear()
                    
#                     st.success(f"Test tweet added successfully!")
#                     st.rerun()
                    
#                 except Exception as e:
#                     st.error(f"Error adding test tweet: {str(e)}")
#             else:
#                 st.warning("Please enter some text for the test tweet.")
    
#     with col2:
#         if st.button("Remove All Test Tweets", type="secondary"):
#             try:
#                 removed_count = remove_test_tweets_from_csv('tweets_with_embeddings_filtered_20250629_144705.csv')
                
#                 # Clear session state
#                 st.session_state.test_tweets_added = []
                
#                 # Clear cache to reload data
#                 st.cache_data.clear()
                
#                 if removed_count > 0:
#                     st.success(f"Removed {removed_count} test tweets!")
#                 else:
#                     st.info("No test tweets found to remove.")
                    
#                 st.rerun()
                
#             except Exception as e:
#                 st.error(f"Error removing test tweets: {str(e)}")

#     # Display currently added test tweets
#     if st.session_state.test_tweets_added:
#         st.subheader("Test Tweets Added This Session:")
#         for i, tweet in enumerate(st.session_state.test_tweets_added, 1):
#             st.write(f"{i}. {tweet[:50]}{'...' if len(tweet) > 50 else ''}")

# # Generate UMAP plot
# embeddings, valid_indices, df = load_and_process_data()

# st.write(f"Loaded {len(embeddings)} valid embeddings")

# # Count test tweets
# test_tweet_count = sum(1 for i in valid_indices if 'TEST TWEET:' in df.iloc[i]['full_text'])
# if test_tweet_count > 0:
#     st.info(f"Currently showing {test_tweet_count} test tweets in red")

# reducer = umap.UMAP(n_components=2, random_state=42, spread=1.25, min_dist=0.5)
# print(f"UMAP random_state: {reducer.random_state}")
# embedding_2d = reducer.fit_transform(embeddings)
# print(f"First few coordinates: {embedding_2d[:3]}")

# print(f"Y range: {embedding_2d[:, 1].min()} to {embedding_2d[:, 1].max()}")
# print(f"Test tweet found: {'This is test tweet 3 with correct dimensions' in [df.iloc[i]['full_text'] for i in valid_indices]}")

# print(f"Y range: {embedding_2d[:, 1].min()} to {embedding_2d[:, 1].max()}")
# colors = []
# for i in valid_indices:
#     if 'TEST TWEET:' in df.iloc[i]['full_text']:
#         colors.append('red') 
#     else:
#         colors.append(px.colors.qualitative.Set3[0])

# print(f"Colors array length: {len(colors)}")
# print(f"Red colors found: {colors.count('red')}")
# print(f"First few colors: {colors[:10]}")

# fig = go.Figure(data=go.Scatter(
#     x=embedding_2d[:, 0],
#     y=embedding_2d[:, 1],
#     mode='markers',
#     text=[df.iloc[i]['full_text'] for i in valid_indices],
#     hovertemplate='<b>Tweet:</b><br>%{text}<extra></extra>',
#     marker=dict(
#         size=8,
#         color=colors,
#         opacity=0.7
#     )
# ))

# fig.update_layout(
#     title="Tweet Embeddings Cluster",
#     xaxis_title="UMAP Dimension 1",
#     yaxis_title="UMAP Dimension 2",
#     yaxis=dict(autorange=True),
# )

# st.plotly_chart(fig, key='tweet_embedding_plot')

# # Optional: Display legend
# st.markdown("**Legend:** 🔴 Red dots = Test tweets | 🔵 Blue dots = Original tweets")

################################################################################################################################################################

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
    df = pd.read_csv('tweets_with_embeddings_filtered_20250629_144705.csv')
    
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
    """Add a test tweet with real LM Studio embedding to the CSV file"""
    # Get real embedding from LM Studio
    with st.spinner("Getting embedding from LM Studio..."):
        test_embedding = get_embedding_from_lmstudio(tweet_text)
    
    if test_embedding is None:
        return None
    
    test_embedding_str = str(test_embedding)
    
    # Generate unique ID starting with 999 (for easy identification)
    # Use timestamp to ensure uniqueness
    unique_id = int(f"999{int(datetime.now().timestamp() * 1000) % 100000000}")
    
    # Create CSV row - keep original tweet text, use special ID range for identification
    current_date = datetime.now().strftime('%Y-%m-%d')
    csv_row = f'{unique_id},1,{current_date},{current_date},0,,"{tweet_text}",,,,,0,{current_date},testuser,"{test_embedding_str}"\n'
    
    # Append to CSV
    with open(csv_file_path, 'a', encoding='utf-8') as f:
        f.write(csv_row)
    
    return unique_id  # Return the ID for tracking

def remove_test_tweets_from_csv(csv_file_path):
    """Remove all test tweets from the CSV file using ID range"""
    df = pd.read_csv(csv_file_path)
    
    # Convert the first column to string to handle potential data type issues
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)
    
    # Filter out rows where ID starts with '999' (our test tweet identifier)
    original_df = df[~df.iloc[:, 0].str.startswith('999')]
    
    # Write back to CSV
    original_df.to_csv(csv_file_path, index=False)
    
    return len(df) - len(original_df)  # Return number of removed tweets

# Initialize session state for managing test tweets
if 'test_tweets_added' not in st.session_state:
    st.session_state.test_tweets_added = []

# Test Tweet Input Section
# st.sidebar.header("Add Test Tweet")
# st.sidebar.info("🚀 Using real LM Studio embeddings for semantic clustering!")

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
                    test_id = add_test_tweet_to_csv(test_tweet_input.strip(), 'tweets_with_embeddings_filtered_20250629_144705.csv')
                    
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
                removed_count = remove_test_tweets_from_csv('tweets_with_embeddings_filtered_20250629_144705.csv')
                
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

# Optional: Display legend
st.markdown("**Legend:** 🔴 Red dots = Test tweets | 🔵 Blue dots = Original tweets")