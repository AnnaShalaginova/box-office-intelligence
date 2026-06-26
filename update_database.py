import pandas as pd
import sqlite3
import os

def update_database(csv_path, db_path):
    print(f"--- Starting Pipeline for {csv_path} ---")
    
    # 1. LOAD DATA
    df = pd.read_csv(csv_path)
    print("Step 1: Raw data loaded.")

    # 2. CLEAN DATA
    # Clean 'Rating'
    df['Rating'] = df['Rating'].str.split('/').str[0].astype(float)
    
    # Fill missing values
    df['Genres'] = df['Genres'].fillna('Unknown')
    df['Original_Language'] = df['Original_Language'].fillna('Unknown')

    # Rename columns for SQL compatibility
    df.columns = [
        col.replace('$Worldwide', 'Worldwide_Gross')
           .replace('$Domestic', 'Domestic_Gross')
           .replace('Domestic %', 'Domestic_Pct')
           .replace('$Foreign', 'Foreign_Gross')
           .replace('Foreign %', 'Foreign_Pct')
           .replace(' ', '_')
           .strip()
        for col in df.columns
    ]
    print("Step 2: Data cleaning complete.")

    # 3. CONNECT TO DATABASE
    conn = sqlite3.connect(db_path)

    # 4. SAVE PRIMARY TABLE
    df.to_sql('box_office', conn, if_exists='replace', index=False)
    print(f"Step 3: Table 'box_office' updated in {db_path}.")

    # 5. TRANSFORM GENRES (The 'Engineering' step)
    # Filter only needed columns for the analysis table
    genre_df = df[['Release_Group', 'Worldwide_Gross', 'Rating', 'Genres']].copy()
    genre_df['Genres'] = genre_df['Genres'].str.split(', ')
    exploded_df = genre_df.explode('Genres')

    # Save to the analysis table
    exploded_df.to_sql('genre_analysis', conn, if_exists='replace', index=False)
    print("Step 4: Table 'genre_analysis' transformed and updated.")

    conn.close()
    print("--- Pipeline Complete! ---")

if __name__ == "__main__":
    # Define paths
    CSV_FILE = 'box_office.csv'
    DB_FILE = 'movies.db'
    
    if os.path.exists(CSV_FILE):
        update_database(CSV_FILE, DB_FILE)
    else:
        print(f"Error: {CSV_FILE} not found!")
