import streamlit as st
import pandas as pd
import numpy as np
import umap
import plotly.graph_objects as go
import plotly.express as px
import ast

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

# Generate UMAP plot
embeddings, valid_indices, df = load_and_process_data()

st.write(f"Loaded {len(embeddings)} valid embeddings")

reducer = umap.UMAP(n_components=2, random_state=42, spread=1.25, min_dist=0.5)
print(f"UMAP random_state: {reducer.random_state}")
embedding_2d = reducer.fit_transform(embeddings)
print(f"First few coordinates: {embedding_2d[:3]}")

print(f"Y range: {embedding_2d[:, 1].min()} to {embedding_2d[:, 1].max()}")
print(f"Test tweet found: {'This is test tweet 3 with correct dimensions' in [df.iloc[i]['full_text'] for i in valid_indices]}")

print(f"Y range: {embedding_2d[:, 1].min()} to {embedding_2d[:, 1].max()}")
colors = []
for i in valid_indices:
    if 'test tweet' in df.iloc[i]['full_text'].lower():
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

## python -c "   --> Runs python from command line, instad of file
## import random --> import random
## test_embedding = [random.random() for _ in range(768)] --> Generate a random embedding with 768 dimensions
## test_embedding_str = str(test_embedding) --> Convert the list to a string representation
## print(f'999997,1,2025-06-19,2025-06-19,0,,\"This is test tweet 3 with correct dimensions\",,,,,0,2025-06-19,testuser,\"{test_embedding_str}\"') --> This generates a test tweet with a valid embedding 
## " >> tweets_with_embeddings_filtered_20250602_125325.csv


