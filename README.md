# Tweet Embedding Visualization

A dynamic web application for visualizing text embeddings using UMAP dimensionality reduction and Streamlit. Takes survey data or any text data in CSV format, generates semantic embeddings via LM Studio, and provides interactive 2D visualizations.

## Features

- **CSV Data Processing**: Converts survey data (like breakfast survey responses) into analyzable format
- **Semantic Embeddings**: Generates 768-dimensional embeddings using LM Studio with Nomic Embed Text v1.5 model
- **Interactive Visualization**: 2D UMAP visualization with hover tooltips showing full text content
- **Test Tweet Support**: Add custom test entries to demonstrate clustering behavior in real-time
- **Configurable UMAP**: Adjust clustering parameters (n_neighbors, min_dist, spread) via sidebar controls
- **Auto-detection**: Automatically finds and uses the most recent embeddings file

## Demo

The visualization displays text entries as points in 2D space where:
- Similar content clusters together based on semantic meaning
- Test entries appear as red dots for easy identification
- Original entries appear as blue dots
- Hover over any point to see the full text
- Points are positioned using UMAP dimensionality reduction with cosine similarity

## Installation

### Prerequisites

- Python 3.8+
- LM Studio with Nomic Embed Text v1.5 model

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/twitter-embedding-visualization.git
cd twitter-embedding-visualization
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up LM Studio:
   - Install [LM Studio](https://lmstudio.ai/)
   - Download the Nomic Embed Text v1.5 model
   - Start the server on port 1234
   - Enable "Serve on Local Network" in settings
   - Note: Update the IP address in scripts if needed (currently set to `10.0.0.7`)

## Usage

### 1. Prepare Your Data

Start with a CSV file containing your text data (e.g., `breakfast_survey_data.csv`). The format should have text responses in one of the columns.

### 2. Convert Survey Data to Standard Format

```bash
python convert_breakfast_data.py
```

This converts your survey responses into a standardized format with two columns:
- `username`: Identifier (e.g., "breakfast_survey")
- `full_text`: The actual text content to analyze

The script outputs a timestamped file like: `tweets_data_20250714_185858.csv`

### 3. Generate Embeddings

Edit `generate_embeddings_filtered.py` to set your input file and target users:
```python
input_file = "tweets_data_20250714_185858.csv"
target_users = ['breakfast_survey']
```

Then run:
```bash
python generate_embeddings_filtered.py
```

This processes each text entry through LM Studio and adds a 768-dimensional embedding column. Progress updates appear every 25 entries. Output file: `tweets_with_embeddings_filtered_YYYYMMDD_HHMMSS.csv`

### 4. Run Visualization

**Auto-detect most recent embeddings file:**
```bash
streamlit run streamlit_app.py
```

**Specify a particular embeddings file:**
```bash
streamlit run streamlit_app.py tweets_with_embeddings_filtered_20250629_144705.csv
```

Opens the interactive web application in your browser.

### 5. Add Test Entries (Interactive)

In the Streamlit app:
1. Enter text in the "Enter your test tweet" sidebar box
2. Click "Add Test Tweet"
3. The app generates a real embedding via LM Studio
4. Test entry appears as a red dot in the visualization
5. Use "Remove All Test Tweets" to clear them

### 6. Adjust UMAP Parameters

Use the sidebar controls to adjust clustering:
- **n_neighbors**: Controls local vs global structure (5-200)
- **min_dist**: Minimum distance between points (0.0-1.0)
- **spread**: Scale of embedded points (0.5-3.0)
- **Max tweets**: Limit visualization size for performance (1000-50000)

## Configuration

### LM Studio Connection

Update the IP address in `generate_embeddings_filtered.py` and `streamlit_app.py`:
```python
lm_studio_url = "http://YOUR_IP:1234/v1/embeddings"
```

### Input Data

Edit `convert_breakfast_data.py` to specify your input CSV:
```python
df = pd.read_csv('your_survey_data.csv')
```

The script uses the third column (index 2) by default for text content. Adjust if needed:
```python
full_text = row.iloc[2]  # Change index as needed
```

## File Structure

```
├── streamlit_app.py                      # Main web application
├── convert_breakfast_data.py             # Convert survey data to standard format
├── generate_embeddings_filtered.py       # Generate embeddings for entries
├── analyze_users.py                      # Analyze entry counts per user/category
├── check_columns.py                      # Check CSV column structure
├── requirements.txt                      # Python dependencies
├── README.md                             # This file
├── breakfast_survey_data.csv             # Your source data
├── tweets_data_*.csv                     # Converted data (generated)
└── tweets_with_embeddings_*.csv          # Data with embeddings (generated)
```

### Legacy Files (Not Currently Used)

These files contain old code for different data sources and are not part of the current workflow:
- `collect_all_tweets.py` - Old Supabase tweet collector
- `test_supabase_connection.py` - Supabase API testing
- `generate_embeddings_production.py` - Batch processing version

## Technical Details

- **Embedding Model**: Nomic Embed Text v1.5 (768 dimensions)
- **Dimensionality Reduction**: UMAP with cosine similarity metric
- **Web Framework**: Streamlit with Plotly for interactive visualizations
- **Data Processing**: Pandas for CSV handling, NumPy for numerical operations
- **API**: RESTful requests to LM Studio for embedding generation

## Utilities

### Analyze Entry Distribution
```bash
python analyze_users.py
```
Shows entry count per user/category in your dataset.

### Check CSV Structure
```bash
python check_columns.py
```
Displays available columns in your CSV files.

## System Requirements

### For ARM64 Windows Users

This project requires WSL (Windows Subsystem for Linux) due to library compatibility issues with ARM64 Windows. The visualization components work best in a Linux environment.

### Supported Platforms

- Linux (recommended)
- macOS
- Windows x64
- Windows ARM64 (via WSL)

## Troubleshooting

### LM Studio Connection Errors

- Ensure LM Studio server is running on the correct port (1234)
- Enable "Serve on Local Network" in LM Studio settings
- For WSL users: Use Windows IP address instead of localhost
- Verify the IP address in all scripts matches your LM Studio instance

### Embedding Generation Slow

- Embedding generation time depends on dataset size and hardware
- Progress updates appear every 25 entries
- Average rate: ~60-100 entries/minute on typical hardware

### Visualization Issues

- Use "Refresh Data" button to reload CSV changes
- Check that CSV files have valid embedding data (768-dimensional arrays)
- Ensure test entries have proper embeddings from LM Studio
- Reduce "Max tweets" slider for faster rendering

### CSV Format Issues

- Ensure your source CSV has text data in a consistent column
- Check column structure with `check_columns.py`
- Verify `convert_breakfast_data.py` is reading the correct column index

## Workflow Summary

```
breakfast_survey_data.csv
    ↓ (convert_breakfast_data.py)
tweets_data_YYYYMMDD_HHMMSS.csv
    ↓ (generate_embeddings_filtered.py)
tweets_with_embeddings_filtered_YYYYMMDD_HHMMSS.csv
    ↓ (streamlit run streamlit_app.py)
Interactive Visualization
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

- Built with Streamlit for rapid prototyping
- Uses UMAP for dimensionality reduction
- Powered by LM Studio and Nomic Embed Text v1.5
