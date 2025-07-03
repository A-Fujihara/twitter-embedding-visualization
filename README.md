# Twitter Embedding Visualization

A dynamic web application for visualizing tweet embeddings using UMAP dimensionality reduction and Streamlit.

## Features

- **Tweet Collection**: Collects tweets from specified users via Supabase API
- **Semantic Embeddings**: Generates 768-dimensional embeddings using LM Studio with Nomic Embed Text v1.5 model
- **Interactive Visualization**: 2D UMAP visualization with hover tooltips showing tweet content
- **Test Tweet Support**: Add test tweets to demonstrate clustering behavior
- **Real-time Updates**: Refresh button to reload data without restarting the application

## Demo

The visualization displays tweets as points in 2D space where:
- Similar tweets cluster together based on semantic meaning
- Test tweets appear as red dots for easy identification
- Hover over any point to see the full tweet text
- Points are positioned using UMAP dimensionality reduction

## Installation

### Prerequisites

- Python 3.8+
- LM Studio with Nomic Embed Text v1.5 model
- Access to tweet data (Supabase API or CSV files)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/A-Fujihara/twitter-embedding-visualization.git
cd twitter-embedding-visualization
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up LM Studio:
   - Install LM Studio
   - Download the Nomic Embed Text v1.5 model
   - Start the server on port 1234
   - Enable "Serve on Local Network" in settings

## Usage

### 1. Collect Tweets
```bash
python collect_tweets.py
```
This creates a CSV file with tweet data from specified users.

### 2. Generate Embeddings
```bash
python generate_embeddings_filtered.py
```
This processes tweets through LM Studio to create semantic embeddings.

### 3. Run Visualization
```bash
streamlit run streamlit_app.py
```
Opens the interactive web application in your browser.

### 4. Add Test Tweets (Optional)
```bash
python -c "
import random
test_embedding = [random.random() for _ in range(768)]
test_embedding_str = str(test_embedding)
print(f'999997,1,2025-06-19,2025-06-19,0,,\"This is test tweet 1\",,,,,0,2025-06-19,testuser,\"{test_embedding_str}\"')
" >> tweets_with_embeddings_filtered_YYYYMMDD_HHMMSS.csv
```
Then click "Refresh Data" in the Streamlit app to see the test tweet appear as a red dot.

### 5. Remove tweets (Optional)
```bash
grep -v "test tweet" tweets_with_embeddings_filtered_20250629_144705.csv > clean.csv && mv clean.csv tweets_with_embeddings_filtered_20250629_144705.csv
```
Note: This is hardcoded to find and remove tweets that contain the substring: 'test tweet'


## Configuration

### Target Users
Edit the `target_users` list in `collect_tweets.py` and `generate_embeddings_filtered.py`:
```python
target_users = ['username1', 'username2', 'username3']
```

### UMAP Parameters
Adjust clustering in `streamlit_app.py`:
```python
reducer = umap.UMAP(
    n_components=2, 
    random_state=42, 
    spread=1.25, 
    min_dist=0.5
)
```

## File Structure

```
├── streamlit_app.py                    # Main web application
├── collect_tweets.py                   # Tweet collection script
├── generate_embeddings_filtered.py     # Embedding generation
├── analyze_users.py                    # User analysis utility
├── check_columns.py                    # CSV structure checker
├── tweets_data_*.csv                   # Raw tweet data
├── tweets_with_embeddings_*.csv        # Processed data with embeddings
├── requirements.txt                    # Python dependencies
└── README.md                          # This file
```

## Technical Details

- **Embedding Model**: Nomic Embed Text v1.5 (768 dimensions)
- **Dimensionality Reduction**: UMAP with deterministic random seed
- **Web Framework**: Streamlit with Plotly for interactive visualizations
- **Data Processing**: Pandas for CSV handling, NumPy for numerical operations

## System Requirements

### For ARM64 Windows Users
This project requires WSL (Windows Subsystem for Linux) due to library compatibility issues with ARM64 Windows. The visualization components work best in a Linux environment.

### Supported Platforms
- Linux (recommended)
- macOS
- Windows x64
- Windows ARM64 (via WSL)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request


## Troubleshooting

### Common Issues

**LM Studio Connection Errors**
- Ensure LM Studio server is running on port 1234
- Enable "Serve on Local Network" in LM Studio settings
- For WSL users: Use Windows IP address instead of localhost

**Embedding Generation Slow**
- Embedding generation may take time depending on dataset size
- Progress is shown every 25 tweets processed

**Visualization Issues**
- Use "Refresh Data" button to reload CSV changes
- Check that CSV files have valid embedding data
- Ensure test tweets have 768-dimensional embeddings