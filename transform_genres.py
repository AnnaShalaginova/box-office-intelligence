import sqlite3
import pandas as pd
#Connect to the database
conn = sqlite3.connect('movies.db')
#Load the existing data
df = pd.read_sql_query("SELECT Release_Group, Worldwide_Gross, Rating, Genres FROM box_office", conn)
# 3. "Explode" the Genres
# Convert "Action, Drama" -> ["Action", "Drama"]
df['Genres'] = df['Genres'].str.split(', ')
# Create a new row for every item in those lists
exploded_df = df.explode('Genres')
# 4. Save this to a NEW table called 'genre_analysis'
exploded_df.to_sql('genre_analysis', conn, if_exists='replace', index=False)
print("Transformation Complete! New table 'genre_analysis' created.")
conn.close()
