# import pandas as pd
# import numpy as np
# import ast
# import plotly.graph_objects as go
# import plotly.express as px
# from sklearn.metrics.pairwise import cosine_similarity
# import umap

# # Load data
# df = pd.read_csv('tweets_with_embeddings_filtered_20250602_125325.csv')

# print(f"Loading {df.shape[0]} rows from CSV...")

# # Process embeddings
# embeddings = []
# tweets = []

# for i, row in df.iterrows():
#     try:
#         embedding_str = row['embedding']
#         if pd.notna(embedding_str) and str(embedding_str) != 'nan':
#             embedding = ast.literal_eval(embedding_str)
#             embeddings.append(embedding)
#             tweet_text = str(row['full_text']) if pd.notna(row['full_text']) else f"Tweet {i}"
#             tweets.append(tweet_text)
#     except:
#         continue

# print(f"Processed {len(embeddings)} valid embeddings")

# # Reduce dimensions to 2D
# embeddings = np.array(embeddings)
# reducer = umap.UMAP(n_components=2, random_state=42)
# embedding_2d = reducer.fit_transform(embeddings)

# # Create plotly scatter plot
# fig = go.Figure(data=go.Scatter(
#     x=embedding_2d[:, 0],
#     y=embedding_2d[:, 1],
#     mode='markers',
#     marker=dict(size=8, color='lightblue'),
#     text=tweets,
#     hovertemplate='<b>Tweet:</b><br>%{text}<extra></extra>',
#     name='Tweets'
# ))

# fig.update_layout(
#     title="Static Tweet Embeddings Visualization",
#     xaxis_title="UMAP 1",
#     yaxis_title="UMAP 2",
#     height=600,
#     template="plotly_dark"
# )

# fig.write_html("static_tweet_plot.html")
# print("Static plot saved as static_tweet_plot.html")