import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Connect to the database
conn = sqlite3.connect('movies.db')

# 2. Get Rating and Revenue (ignore missing values)
query = """
SELECT Rating, Worldwide_Gross 
FROM box_office 
WHERE Rating > 0 AND Worldwide_Gross > 0;
"""
df = pd.read_sql_query(query, conn)
conn.close()

# 3. Create the Visualization
plt.figure(figsize=(10, 6))

# Scatter plot
plt.scatter(df['Rating'].values, df['Worldwide_Gross'].values, 
            alpha=0.4, color='purple', edgecolors='white', linewidth=0.5)

# 4. Add a "Trend Line" (Intro to Linear Regression)
# This calculates the line of best fit
z = np.polyfit(df['Rating'].values, df['Worldwide_Gross'].values, 1)
p = np.poly1d(z)
plt.plot(df['Rating'].values, p(df['Rating'].values), "r--", alpha=0.8, label='Trend Line')

# Format the chart
plt.title('Correlation: Movie Rating vs. Worldwide Revenue', fontsize=14)
plt.xlabel('Rating (out of 10)', fontsize=12)
plt.ylabel('Worldwide Revenue', fontsize=12)
plt.ticklabel_format(style='plain', axis='y')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()

# Save the chart
plt.tight_layout()
plt.savefig('rating_correlation.png')
print("Analysis Complete! Chart saved as 'rating_correlation.png'.")

# Calculate Correlation Coefficient
correlation = df['Rating'].corr(df['Worldwide_Gross'])
print(f"Correlation Coefficient: {correlation:.2f}")
