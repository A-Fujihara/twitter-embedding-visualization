# import pandas as pd
# import numpy as np
# import umap
# import matplotlib.pyplot as plt
# import ast

# # Load the CSV with tweet embeddings in a pandas DataFrame
# df = pd.read_csv('tweets_with_embeddings_filtered_20250602_125325.csv')

# # Convert embedding strings to numpy arrays, skip malformed ones
# # Regular Python list would be inefficient for UMAP operations. UMAP expects numpy arrays.
# embeddings = []
# # this stores which indices in the DataFrame have valid embeddings
# # Possibly useful for further anaylysis (ie mapping back to original tweets)
# valid_indices = []

# # iterates through each embedding string in the DataFrame
# # enumerate returns both the index position and value of each item when iterating through a sequence.
# for i, embedding_str in enumerate(df['embedding']):
#     try:
#         # Check if the embedding string is not NaN
#         if pd.notna(embedding_str) and embedding_str != 'nan':
#             # Convert the string representation of the list to a Python list
#             # ast.literal_eval safely evaluates the string as a Python literal
#             # This is necessary because the embeddings are stored as strings in the CSV
#             # ast.literal_eval is safer than eval as it only evaluates literals
#             embedding = ast.literal_eval(embedding_str)
#             # Convert the list to a numpy array
#             embeddings.append(embedding)
#             # Store the index of the valid embedding
#             # This is useful for mapping back to the original DataFrame if needed
#             valid_indices.append(i)
#     except:
#         print(f"Skipping malformed embedding at row {i}")

# embeddings = np.array(embeddings)
# print(f"Loaded {len(embeddings)} valid embeddings with {embeddings.shape[1]} dimensions")

# # Run UMAP
# # Creates a umap reducer that will compress data to 2 dimensions
# reducer = umap.UMAP(n_components=2, random_state=42)
# # Reduces the high-dimensional embeddings to 2D
# embedding_2d = reducer.fit_transform(embeddings)

# # Create scatter plot
# # Creates 12x8 inch figure for the scatter plot
# plt.figure(figsize=(12, 8))
# # Scatter plot of the 2D UMAP embeddings
# # Uses the first column of the 2D embeddings for x-axis and second for y-axis
# plt.scatter(embedding_2d[:, 0], embedding_2d[:, 1], alpha=0.6, s=30)
# plt.title('UMAP Visualization of Tweet Embeddings')
# plt.xlabel('UMAP 1')
# plt.ylabel('UMAP 2')
# plt.grid(True, alpha=0.3)

# # Save the plot
# plt.savefig('tweet_embeddings_umap.png', dpi=300, bbox_inches='tight')
# print("Visualization saved as tweet_embeddings_umap.png")