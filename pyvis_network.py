# # import pandas as pd
# # import numpy as np
# # import ast
# # from pyvis.network import Network
# # from sklearn.metrics.pairwise import cosine_similarity

# # # Load data
# # df = pd.read_csv('tweets_with_embeddings_filtered_20250602_125325.csv')

# # print(f"Loading {df.shape[0]} rows from CSV...")

# # # Process embeddings
# # embeddings = []
# # tweets = []
# # valid_indices = []

# # for i, row in df.iterrows():
# #    try:
# #        embedding_str = row['embedding']
# #        if pd.notna(embedding_str) and str(embedding_str) != 'nan':
# #            embedding = ast.literal_eval(embedding_str)
# #            embeddings.append(embedding)
# #            # Use full_text column
# #            tweet_text = str(row['full_text']) if pd.notna(row['full_text']) else f"Tweet {i}"
# #            tweets.append(tweet_text[:100])
# #            valid_indices.append(i)
# #    except Exception as e:
# #        continue

# # print(f"Processed {len(embeddings)} valid embeddings")

# # # Create network
# # embeddings = np.array(embeddings)
# # similarity_matrix = cosine_similarity(embeddings)

# # net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")

# # # Add all nodes
# # for i, tweet in enumerate(tweets):
# #    net.add_node(i, label=f"Tweet {i}", title=tweet, size=15, color="lightblue")

# # # Add edges for similar tweets
# # threshold = 0.6  # Moderate similarity threshold
# # edge_count = 0
# # for i in range(len(tweets)):
# #    for j in range(i+1, len(tweets)):
# #        if similarity_matrix[i][j] > threshold:
# #            net.add_edge(i, j, weight=similarity_matrix[i][j])
# #            edge_count += 1

# # print(f"Created network with {len(tweets)} nodes and {edge_count} edges")

# # # Configure physics for better layout
# # net.set_options("""
# # var options = {
# #  "physics": {
# #    "enabled": true,
# #    "stabilization": {"iterations": 200},
# #    "barnesHut": {
# #      "gravitationalConstant": -2000,
# #      "centralGravity": 0.3,
# #      "springLength": 95,
# #      "springConstant": 0.04
# #    }
# #  }
# # }
# # """)

# # net.save_graph("tweet_network.html")
# # print("Network saved as tweet_network.html")

# import pandas as pd
# import numpy as np
# import ast
# from pyvis.network import Network
# from sklearn.metrics.pairwise import cosine_similarity

# # Load data
# df = pd.read_csv('tweets_with_embeddings_filtered_20250602_125325.csv')

# print(f"Loading {df.shape[0]} rows from CSV...")

# # Process embeddings
# embeddings = []
# tweets = []
# valid_indices = []

# for i, row in df.iterrows():
#     try:
#         embedding_str = row['embedding']
#         if pd.notna(embedding_str) and str(embedding_str) != 'nan':
#             embedding = ast.literal_eval(embedding_str)
#             embeddings.append(embedding)
#             tweet_text = str(row['full_text']) if pd.notna(row['full_text']) else f"Tweet {i}"
#             tweets.append(tweet_text[:100])
#             valid_indices.append(i)
#     except Exception as e:
#         continue

# print(f"Processed {len(embeddings)} valid embeddings")

# # Create network
# embeddings = np.array(embeddings)
# similarity_matrix = cosine_similarity(embeddings)

# net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")

# # Add all nodes
# for i, tweet in enumerate(tweets):
#     net.add_node(i, label=f"Tweet {i}", title=tweet, size=15, color="lightblue")

# # Add edges for similar tweets
# threshold = 0.6
# edge_count = 0
# for i in range(len(tweets)):
#     for j in range(i+1, len(tweets)):
#         if similarity_matrix[i][j] > threshold:
#             net.add_edge(i, j, weight=similarity_matrix[i][j])
#             edge_count += 1

# print(f"Created network with {len(tweets)} nodes and {edge_count} edges")

# # Save the network
# net.save_graph("tweet_network.html")

# # Now manually edit the HTML to disable physics
# with open("tweet_network.html", "r") as f:
#     html_content = f.read()

# # Replace the physics options
# html_content = html_content.replace(
#     '"physics": {"enabled": true',
#     '"physics": {"enabled": false'
# )

# with open("tweet_network.html", "w") as f:
#     f.write(html_content)

# print("Network saved as tweet_network.html with physics disabled")