import sqlite3
import pandas as pd

def run_query(query):
    conn = sqlite3.connect('movies.db')
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

# --- PRACTICE AREA ---
# Try your SQL query here!
query = """
SELECT Release_Group, Year, Rating, Vote_Count, Worldwide_Gross
FROM box_office
WHERE Vote_Count > 5000
ORDER BY Rating DESC
LIMIT 10;
"""

print(run_query(query))
