import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 1. Connect to the database
conn = sqlite3.connect('movies.db')

# 2. Get Average Revenue per Genre (using our normalized table)
query = """
SELECT Genres, AVG(Worldwide_Gross) as Avg_Revenue, COUNT(*) as Movie_Count
FROM genre_analysis
GROUP BY Genres
HAVING Movie_Count > 50
ORDER BY Avg_Revenue DESC
LIMIT 10;
"""
df = pd.read_sql_query(query, conn)
conn.close()

# 3. Create the Visualization
plt.figure(figsize=(12, 7))
# We use .values to avoid the compatibility error we saw earlier
plt.barh(df['Genres'].values, df['Avg_Revenue'].values, color='seagreen')

# Format the chart
plt.title('Top 10 Most Profitable Genres (Average Worldwide Gross)', fontsize=14)
plt.xlabel('Average Revenue (in USD)', fontsize=12)
plt.ylabel('Genre', fontsize=12)
plt.gca().invert_yaxis()  # Put the highest at the top
plt.grid(axis='x', linestyle='--', alpha=0.6)

# Format the X-axis for readability
plt.ticklabel_format(style='plain', axis='x')

# Save the chart
plt.tight_layout()
plt.savefig('genre_profitability.png')
print("Analysis Complete! Chart saved as 'genre_profitability.png'.")
