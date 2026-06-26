import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
# 1. Connect to the database
conn = sqlite3.connect('movies.db')
# 2. Get Total Revenue per Year
query = """
SELECT Year, SUM(Worldwide_Gross) as Total_Revenue
FROM box_office
WHERE Year BETWEEN 2000 AND 2024
GROUP BY Year
ORDER BY Year;
"""
df = pd.read_sql_query(query, conn)
conn.close()
# 3. Create the Visualization
plt.figure(figsize=(12, 6))
plt.plot(df['Year'].values, df['Total_Revenue'].values, marker='o', color='royalblue', linewidth=2)
# Format the chart
plt.title('Total Worldwide Box Office Revenue (2000-2024)', fontsize=14, pad=20)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Total Revenue', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
# This makes the Y-axis easier to read (no scientific notation)
plt.ticklabel_format(style='plain', axis='y')
# Save the chart as an image
plt.savefig('revenue_trend.png')
print("Analysis Complete! Chart saved as 'revenue_trend.png'.")
