# Web App Build Steps

This document outlines the main steps used to create the interactive Box Office Intelligence web app.

## 1. Locate the Project Files

The project lives in:

```text
/Users/annashalaginova/box_office_project
```

Important files:

```text
app.py                  Streamlit web app
movies.db               SQLite database used by the app
box_office.csv          Original CSV dataset
setup_sql.py            Script that creates the database from CSV data
update_database.py      Script for refreshing the database
```

## 2. Inspect the Data Source

Before building charts, the first step was to understand where the data comes from and what fields are available.

The app loads data from SQLite:

```python
conn = sqlite3.connect("movies.db")
df = pd.read_sql_query("SELECT * FROM box_office", conn)
conn.close()
```

The database table includes these core columns:

```text
Rank
Release_Group
Worldwide_Gross
Domestic_Gross
Domestic_Pct
Foreign_Gross
Foreign_Pct
Year
Genres
Rating
Vote_Count
Original_Language
Production_Countries
```

This step matters because chart choices should come from the data shape. For example, `Year` supports trend charts, `Genres` supports category comparisons, and `Worldwide_Gross` supports revenue analysis.

## 3. Confirm the Data Is Usable

The next step was checking that important numeric fields were populated and useful for visualization.

Examples of checks:

```sql
SELECT COUNT(*), MIN(Year), MAX(Year), AVG(Rating), MAX(Worldwide_Gross)
FROM box_office;
```

The database contains 5,000 movie records covering 2000 through 2024.

## 4. Load and Cache the Data

The app uses Streamlit caching so the database is not reloaded from scratch every time a widget changes.

```python
@st.cache_data
def load_data():
    conn = sqlite3.connect("movies.db")
    df = pd.read_sql_query("SELECT * FROM box_office", conn)
    conn.close()
    return df
```

This keeps the app responsive while users interact with filters and charts.

## 5. Add Sidebar Filters

The sidebar controls define the current slice of data.

Current filters include:

```text
Movie title search
Release year range
IMDb rating range
Minimum vote count
Genre selection
Original language selection
```

Each chart uses `filtered_df`, so all visualizations respond to the same controls.

## 6. Create Summary Metrics

Before showing detailed charts, the app calculates high-level metrics from the filtered data:

```text
Total revenue
Average rating
Top grossing movie
Average gross per movie
```

These give users a quick overview before they explore deeper charts.

## 7. Build Financial Performance Charts

The first chart group focuses on revenue.

Charts added:

```text
Revenue trend by year
Top 10 highest grossing movies
Domestic vs. foreign revenue split
Revenue distribution
Rank vs. revenue profile
```

The yearly revenue chart groups data by `Year`:

```python
yearly_gross = filtered_df.groupby("Year")[
    ["Worldwide_Gross", "Domestic_Gross", "Foreign_Gross"]
].sum().reset_index()
```

## 8. Build Genre Analysis

Genres are stored as comma-separated values, so they need to be split before grouping.

Example:

```python
exploded_genres = filtered_df.copy()
exploded_genres["Genres_List"] = exploded_genres["Genres"].str.split(", ")
exploded_genres = exploded_genres.explode("Genres_List")
```

This allows one movie to count toward multiple genre categories.

Genre charts include:

```text
Average revenue by genre
Movie count by genre
Genre bubble chart comparing volume, revenue, and rating
```

## 9. Add Market Map Exploration

The Market Map tab lets users compare larger market segments.

Users can segment by:

```text
Genre
Production country
Original language
```

Users can measure:

```text
Worldwide gross
Movie count
Average rating
Average gross
```

The tab supports treemap, sunburst, and bar chart views.

## 10. Add a Custom Chart Builder

The Chart Builder tab lets users create their own visualizations without editing code.

Users can choose:

```text
Chart type
X axis
Y axis
Color grouping
Aggregation method for bar charts
```

This turns the app from a fixed dashboard into an exploratory analysis tool.

## 11. Handle Chart Edge Cases

One issue found during testing was that a `Worldwide_Gross` histogram could appear empty when rendered with a log-scaled axis.

The fix was to create a log-transformed helper column for the histogram instead of relying directly on Plotly's log-axis histogram behavior:

```python
hist_df["Log_Revenue"] = np.log10(hist_df[distribution_metric])
```

Then the x-axis labels were converted back to readable dollar amounts.

## 12. Validate the App

Validation steps included:

```bash
/opt/anaconda3/bin/python -m py_compile app.py
```

And running Streamlit's app test harness to check for runtime exceptions.

The app was also launched locally:

```bash
/opt/anaconda3/bin/streamlit run app.py --server.port 8502 --server.headless true --server.fileWatcherType poll
```

Local app URL:

```text
http://localhost:8502
```

## 13. Main Development Pattern

The general workflow was:

```text
1. Inspect the data.
2. Confirm column types and values.
3. Choose chart types that match the data.
4. Build filters first.
5. Make every chart use the filtered dataset.
6. Add charts in focused tabs.
7. Test for syntax and runtime errors.
8. Fix rendering issues discovered during testing.
```

