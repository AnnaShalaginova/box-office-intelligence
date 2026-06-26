import pandas as pd

# Load the dataset
df = pd.read_csv('box_office.csv')

# 1. Basic Info
print("--- Dataset Info ---")
print(df.info())

# 2. Check for missing values
print("\n--- Missing Values ---")
print(df.isnull().sum())

# 3. Preview first 5 rows
print("\n--- First 5 Rows ---")
print(df.head())

# 4. Clean 'Rating' column - convert "6.126/10" to float 6.126
df['Rating'] = df['Rating'].str.split('/').str[0].astype(float)

# 5. Clean Currency Columns - they seem to be floats already based on the preview, 
# but let's ensure they are numeric.
cols_to_fix = ['$Worldwide', '$Domestic', '$Foreign']
for col in cols_to_fix:
    df[col] = pd.to_numeric(df[col], errors='coerce')

print("\n--- Cleaned Info ---")
print(df[['Release Group', 'Rating', '$Worldwide']].head())
