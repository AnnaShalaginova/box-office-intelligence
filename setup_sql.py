import pandas as pd
import sqlite3

# Load the dataset
df = pd.read_csv('box_office.csv')

# --- DATA CLEANING (Python Skill) ---

# 1. Clean 'Rating'
df['Rating'] = df['Rating'].str.split('/').str[0].astype(float)

# 2. Fill missing values
df['Genres'] = df['Genres'].fillna('Unknown')
df['Original_Language'] = df['Original_Language'].fillna('Unknown')

# 3. Create a clean version of the column names
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

# --- SAVE TO SQL (SQL Skill Setup) ---

# Connect to SQLite (this creates movies.db)
conn = sqlite3.connect('movies.db')

# Write the data to a table called 'box_office'
df.to_sql('box_office', conn, if_exists='replace', index=False)

print("Database 'movies.db' created successfully with table 'box_office'!")
conn.close()
