import pandas as pd
from datetime import datetime
import csv

def convert_breakfast_data():
    """
    Convert breakfast survey data to simple format for embedding pipeline
    Only creates the columns that generate_embeddings_filtered.py actually uses
    """
    
    print("=== Converting Breakfast Survey Data ===")
    
    df = pd.read_csv('breakfast_survey_data.csv')
    
    print(f"Found {len(df)} breakfast responses")
    
    output_file = f"tweets_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Only create the columns the pipeline actually uses
    fieldnames = ['username', 'full_text']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for index, row in df.iterrows():
            # Use the third column (optional comments)
            full_text = row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else ""
            
            if not full_text:
                continue
            
            # Clean up the text to handle multi-line responses
            full_text = str(full_text)
            full_text = full_text.replace('\n', ' ').replace('\r', ' ')
            full_text = ' '.join(full_text.split())
            full_text = full_text.strip('"\'')
            
            if not full_text.strip():
                continue
            
            breakfast_row = {
                'username': 'breakfast_survey',
                'full_text': full_text
            }
            
            writer.writerow(breakfast_row)
    
    print(f"✅ Converted data saved to: {output_file}")
    print(f"   Total responses converted: {len(df)}")
    print(f"\nNext steps:")
    print(f"1. Update generate_embeddings_filtered.py:")
    print(f"   Change: input_file = '{output_file}'")
    print(f"   Change: target_users = ['breakfast_survey']")
    print(f"2. Run: python generate_embeddings_filtered.py")

if __name__ == "__main__":
    convert_breakfast_data()