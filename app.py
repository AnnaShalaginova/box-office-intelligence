import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import io

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Box Office Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. INJECT CUSTOM CSS FOR PREMIUM LOOK (Plus Jakarta Sans, Glassmorphism, Custom Tabs)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Apply font to everything */
html, body, [class*="css"], .stText, .stMarkdown, .stButton, .stTabs, label {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Gradient Title Container */
.header-container {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    border: 1px solid rgba(129, 140, 248, 0.2);
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    position: relative;
    overflow: hidden;
}

.header-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 60%);
    pointer-events: none;
}

.header-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #818CF8 0%, #C084FC 40%, #F472B6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    padding: 0;
    letter-spacing: -0.03em;
    line-height: 1.2;
}

.header-subtitle {
    font-size: 1.05rem;
    color: #94A3B8;
    font-weight: 400;
    margin-top: 0.5rem;
    margin-bottom: 0;
}

/* Glassmorphism Metric Cards */
.metric-card-container {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    width: 100%;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.metric-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #6366F1 0%, #EC4899 100%);
    border-radius: 4px 0 0 4px;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(99, 102, 241, 0.15);
    border-color: rgba(99, 102, 241, 0.4);
    background: rgba(30, 41, 59, 0.6);
}

.metric-title {
    font-size: 0.85rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 600;
    margin-bottom: 0.4rem;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #F8FAFC;
    line-height: 1.2;
    letter-spacing: -0.02em;
}

.metric-sub {
    font-size: 0.8rem;
    color: #64748B;
    margin-top: 0.3rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Custom spacing and styles for side panels */
.css-1542mo4 {
    padding: 2rem 1rem !important;
}

/* Modern styling for the sidebar header */
.sidebar-header {
    font-size: 1.2rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 0.5rem;
    background: linear-gradient(90deg, #818CF8 0%, #C084FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

# 3. DATA LOADING AND CACHING
@st.cache_data
def load_data():
    conn = sqlite3.connect('movies.db')
    # Load primary table
    df = pd.read_sql_query("SELECT * FROM box_office", conn)
    conn.close()
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Error loading database. Make sure you run setup_sql.py first! Details: {e}")
    st.stop()

# 4. SIDEBAR - CONTROLS & FILTERING
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎛️ Control Panel</div>', unsafe_allow_html=True)
    
    # Text Search Filter
    title_search = st.text_input("🔍 Search Movie Title", "", placeholder="Enter keyword...")
    
    # Year Filter
    min_year = int(df_raw['Year'].min())
    max_year = int(df_raw['Year'].max())
    selected_years = st.slider(
        "📅 Release Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )
    
    # IMDb Rating Filter
    selected_ratings = st.slider(
        "⭐ IMDb Rating Range",
        min_value=0.0,
        max_value=10.0,
        value=(0.0, 10.0),
        step=0.1
    )
    
    # Vote Count Filter
    max_votes = int(df_raw['Vote_Count'].max())
    min_votes = st.number_input(
        "🗳️ Min Vote Count",
        min_value=0,
        max_value=max_votes,
        value=500,
        step=100
    )
    
    # Extract unique genres (handling list strings)
    unique_genres = sorted(list(set(
        g.strip() for genres_str in df_raw['Genres'].dropna() 
        for g in genres_str.split(', ') if g.strip()
    )))
    selected_genres = st.multiselect(
        "🎭 Select Genres",
        options=unique_genres,
        placeholder="All Genres"
    )
    
    # Language Filter
    unique_languages = sorted(df_raw['Original_Language'].dropna().unique().tolist())
    selected_languages = st.multiselect(
        "🌐 Original Language",
        options=unique_languages,
        placeholder="All Languages"
    )

# 5. FILTER APPLICATION
filtered_df = df_raw.copy()

# Apply Filters
filtered_df = filtered_df[
    (filtered_df['Year'] >= selected_years[0]) & 
    (filtered_df['Year'] <= selected_years[1])
]
filtered_df = filtered_df[
    (filtered_df['Rating'] >= selected_ratings[0]) & 
    (filtered_df['Rating'] <= selected_ratings[1])
]
filtered_df = filtered_df[filtered_df['Vote_Count'] >= min_votes]

if title_search:
    filtered_df = filtered_df[filtered_df['Release_Group'].str.contains(title_search, case=False, na=False)]

if selected_genres:
    # Match movies containing at least one selected genre
    pattern = '|'.join([rf"\b{g}\b" for g in selected_genres])
    filtered_df = filtered_df[filtered_df['Genres'].str.contains(pattern, case=False, na=False)]

if selected_languages:
    filtered_df = filtered_df[filtered_df['Original_Language'].isin(selected_languages)]

# 6. HEADER RENDERING
st.markdown("""
<div class="header-container">
    <h1 class="header-title">Box Office Intelligence</h1>
    <p class="header-subtitle">Interactive analysis, trend visualization, and commercial performance insights for the movie industry (2000-2024).</p>
</div>
""", unsafe_allow_html=True)

# 7. METRIC CARDS CALCULATION & RENDERING
if filtered_df.empty:
    st.warning("⚠️ No movies match the current filters. Please adjust the sidebar settings.")
    st.stop()

# Calculations
total_movies = len(filtered_df)
total_gross = filtered_df['Worldwide_Gross'].sum()
avg_rating = filtered_df['Rating'].mean()

# Format gross helper
def format_currency(val):
    if val >= 1e9:
        return f"${val / 1e9:.2f} B"
    elif val >= 1e6:
        return f"${val / 1e6:.1f} M"
    else:
        return f"${val:,.0f}"

def apply_chart_style(fig, height=None):
    layout_updates = {
        "margin": dict(l=40, r=40, t=50, b=40),
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": dict(family="Plus Jakarta Sans", color="#F8FAFC"),
        "xaxis": dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        "yaxis": dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    }
    if height:
        layout_updates["height"] = height
    fig.update_layout(**layout_updates)
    return fig

def explode_multivalue_column(source_df, source_col, output_col):
    exploded = source_df.copy()
    exploded[output_col] = exploded[source_col].fillna("Unknown").str.split(", ")
    exploded = exploded.explode(output_col)
    exploded[output_col] = exploded[output_col].str.strip()
    return exploded[exploded[output_col].ne("")]

top_movie_row = filtered_df.loc[filtered_df['Worldwide_Gross'].idxmax()]
top_movie_title = top_movie_row['Release_Group']
top_movie_gross = format_currency(top_movie_row['Worldwide_Gross'])

# Render metrics in columns with custom HTML/CSS
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Revenue</div>
        <div class="metric-value">{format_currency(total_gross)}</div>
        <div class="metric-sub">Across {total_movies:,} movies</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Average Rating</div>
        <div class="metric-value">{avg_rating:.2f} / 10</div>
        <div class="metric-sub">IMDb audience average</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Top Grossing Movie</div>
        <div class="metric-value">{top_movie_gross}</div>
        <div class="metric-sub">{top_movie_title}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Average Gross</div>
        <div class="metric-value">{format_currency(total_gross / total_movies if total_movies > 0 else 0)}</div>
        <div class="metric-sub">Per release group</div>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacing

# 8. TABS LAYOUT
tab_financials, tab_genres, tab_market, tab_correlations, tab_builder, tab_search, tab_about = st.tabs([
    "📊 Financial Performance",
    "🎭 Genre Insights",
    "🗺️ Market Map",
    "📈 Ratings & Languages",
    "🧪 Chart Builder",
    "🔍 Search & Export",
    "ℹ️ About"
])

# COLOR PALETTES
PRIMARY_COLOR = '#6366F1' # Indigo
ACCENT_COLORS = ['#6366F1', '#8B5CF6', '#EC4899', '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#14B8A6']

# --- TAB 1: FINANCIAL PERFORMANCE ---
with tab_financials:
    st.subheader("Financial Performance & Historical Trends")
    
    # Row 1: Revenue Over Time Area Chart
    yearly_gross = filtered_df.groupby('Year')[['Worldwide_Gross', 'Domestic_Gross', 'Foreign_Gross']].sum().reset_index()
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=yearly_gross['Year'], y=yearly_gross['Worldwide_Gross'],
        mode='lines+markers',
        name='Worldwide Gross',
        line=dict(color='#818CF8', width=3),
        fill='tozeroy',
        fillcolor='rgba(129, 140, 248, 0.1)'
    ))
    fig_trend.add_trace(go.Scatter(
        x=yearly_gross['Year'], y=yearly_gross['Domestic_Gross'],
        mode='lines',
        name='Domestic Gross',
        line=dict(color='#34D399', width=2, dash='dash')
    ))
    fig_trend.add_trace(go.Scatter(
        x=yearly_gross['Year'], y=yearly_gross['Foreign_Gross'],
        mode='lines',
        name='Foreign Gross',
        line=dict(color='#F472B6', width=2, dash='dot')
    ))
    
    fig_trend.update_layout(
        title="Revenue Trends (2000 - 2024)",
        xaxis_title="Release Year",
        yaxis_title="Gross Earnings (in USD)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=50, b=40),
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickmode='linear'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Row 2: Columns (Top 10 Movies & Domestic vs Foreign Ratio)
    col_top, col_ratio = st.columns([2, 1])
    
    with col_top:
        st.write("")
        st.markdown("**Top 10 Highest Grossing Movies**")
        top10 = filtered_df.sort_values(by='Worldwide_Gross', ascending=False).head(10)
        
        fig_top = px.bar(
            top10,
            x='Worldwide_Gross',
            y='Release_Group',
            orientation='h',
            text='Worldwide_Gross',
            color='Worldwide_Gross',
            color_continuous_scale=['#4F46E5', '#8B5CF6', '#EC4899']
        )
        fig_top.update_traces(
            texttemplate='$%{text:.2s}', 
            textposition='inside',
            marker_line_color='rgba(0,0,0,0)'
        )
        fig_top.update_layout(
            xaxis_title="Worldwide Gross (USD)",
            yaxis_title="",
            coloraxis_showscale=False,
            margin=dict(l=40, r=20, t=20, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_top, use_container_width=True)
        
    with col_ratio:
        st.write("")
        st.markdown("**Domestic vs. Foreign Revenue Split**")
        total_dom = filtered_df['Domestic_Gross'].sum()
        total_for = filtered_df['Foreign_Gross'].sum()
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Domestic Gross', 'Foreign Gross'],
            values=[total_dom, total_for],
            hole=.4,
            marker=dict(colors=['#10B981', '#EC4899'])
        )])
        fig_pie.update_layout(
            margin=dict(l=20, r=20, t=20, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.write("")
    dist_col, rank_col = st.columns([1, 1])

    with dist_col:
        st.markdown("**Revenue Distribution**")
        distribution_metric = st.selectbox(
            "Distribution Metric",
            options=["Worldwide_Gross", "Domestic_Gross", "Foreign_Gross"],
            format_func=lambda col: col.replace("_", " "),
            key="distribution_metric"
        )
        use_log_scale = st.toggle("Log scale", value=True, key="distribution_log_scale")
        hist_df = filtered_df[[distribution_metric]].copy()
        hist_df = hist_df[hist_df[distribution_metric] > 0]
        hist_x = distribution_metric
        hist_labels = {distribution_metric: distribution_metric.replace("_", " ")}

        if use_log_scale:
            hist_x = "Log_Revenue"
            hist_df[hist_x] = np.log10(hist_df[distribution_metric])
            hist_labels[hist_x] = f"Log10 {distribution_metric.replace('_', ' ')}"

        fig_hist = px.histogram(
            hist_df,
            x=hist_x,
            nbins=45,
            color_discrete_sequence=["#14B8A6"],
            labels=hist_labels
        )
        if use_log_scale:
            log_ticks = np.arange(
                np.floor(hist_df[hist_x].min()),
                np.ceil(hist_df[hist_x].max()) + 1
            )
            fig_hist.update_xaxes(
                tickmode="array",
                tickvals=log_ticks,
                ticktext=[format_currency(10 ** tick) for tick in log_ticks]
            )
        fig_hist.update_layout(
            yaxis_title="Movie Count",
            bargap=0.05
        )
        st.plotly_chart(apply_chart_style(fig_hist), use_container_width=True)

    with rank_col:
        st.markdown("**Rank vs. Revenue Profile**")
        fig_rank = px.scatter(
            filtered_df,
            x="Rank",
            y="Worldwide_Gross",
            color="Rating",
            size="Vote_Count",
            hover_name="Release_Group",
            color_continuous_scale="Tealrose",
            labels={
                "Rank": "Annual Box Office Rank",
                "Worldwide_Gross": "Worldwide Gross",
                "Rating": "IMDb Rating",
                "Vote_Count": "Vote Count"
            }
        )
        fig_rank.update_layout(yaxis_type="log" if use_log_scale else "linear")
        st.plotly_chart(apply_chart_style(fig_rank), use_container_width=True)

# --- TAB 2: GENRE INSIGHTS ---
with tab_genres:
    st.subheader("Genre Performance & Popularity")
    
    # Process dynamic genre dataset from filtered movies
    exploded_genres = filtered_df.copy()
    exploded_genres['Genres_List'] = exploded_genres['Genres'].str.split(', ')
    exploded_genres = exploded_genres.explode('Genres_List')
    
    genre_stats = exploded_genres.groupby('Genres_List').agg(
        Avg_Revenue=('Worldwide_Gross', 'mean'),
        Movie_Count=('Worldwide_Gross', 'count'),
        Avg_Rating=('Rating', 'mean')
    ).reset_index().rename(columns={'Genres_List': 'Genre'})
    
    # Filter out genres with very low volume in current selection to avoid outliers
    genre_stats = genre_stats[genre_stats['Movie_Count'] > 0]
    
    # Double Column Layout
    col_gen_rev, col_gen_cnt = st.columns(2)
    
    with col_gen_rev:
        st.markdown("**Average Revenue by Genre (Profitability)**")
        genre_stats_sorted_rev = genre_stats.sort_values(by='Avg_Revenue', ascending=True)
        
        fig_gen_rev = px.bar(
            genre_stats_sorted_rev,
            y='Genre',
            x='Avg_Revenue',
            orientation='h',
            color='Avg_Revenue',
            color_continuous_scale='Viridis',
            labels={'Avg_Revenue': 'Average Worldwide Gross (USD)'}
        )
        fig_gen_rev.update_layout(
            coloraxis_showscale=False,
            margin=dict(l=40, r=20, t=20, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_gen_rev, use_container_width=True)
        
    with col_gen_cnt:
        st.markdown("**Volume of Movies by Genre (Market Density)**")
        genre_stats_sorted_cnt = genre_stats.sort_values(by='Movie_Count', ascending=True)
        
        fig_gen_cnt = px.bar(
            genre_stats_sorted_cnt,
            y='Genre',
            x='Movie_Count',
            orientation='h',
            color='Movie_Count',
            color_continuous_scale='Magma',
            labels={'Movie_Count': 'Number of Releases'}
        )
        fig_gen_cnt.update_layout(
            coloraxis_showscale=False,
            margin=dict(l=40, r=20, t=20, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_gen_cnt, use_container_width=True)
        
    # Extra scatter plot
    st.write("")
    st.markdown("**Genre Comparison: Market Volume vs. Average Gross Earnings**")
    
    fig_gen_bubble = px.scatter(
        genre_stats,
        x='Movie_Count',
        y='Avg_Revenue',
        size='Movie_Count',
        color='Avg_Rating',
        hover_name='Genre',
        text='Genre',
        labels={
            'Movie_Count': 'Number of Releases',
            'Avg_Revenue': 'Average Worldwide Revenue (USD)',
            'Avg_Rating': 'Average IMDb Rating'
        },
        color_continuous_scale='RdPu'
    )
    fig_gen_bubble.update_traces(textposition='top center')
    fig_gen_bubble.update_layout(
        margin=dict(l=40, r=40, t=30, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    )
    st.plotly_chart(fig_gen_bubble, use_container_width=True)

# --- TAB 3: MARKET MAP ---
with tab_market:
    st.subheader("Market Composition Explorer")

    map_col_1, map_col_2, map_col_3 = st.columns([1, 1, 1])
    with map_col_1:
        market_dimension = st.selectbox(
            "Segment By",
            options=["Genres", "Production_Countries", "Original_Language"],
            format_func=lambda col: {
                "Genres": "Genre",
                "Production_Countries": "Production Country",
                "Original_Language": "Original Language"
            }[col]
        )
    with map_col_2:
        market_metric = st.selectbox(
            "Measure",
            options=["Worldwide Gross", "Movie Count", "Average Rating", "Average Gross"],
            index=0
        )
    with map_col_3:
        market_chart_type = st.segmented_control(
            "Chart",
            options=["Treemap", "Sunburst", "Bar"],
            default="Treemap"
        )

    if market_dimension in ["Genres", "Production_Countries"]:
        segment_col = "Segment"
        market_source = explode_multivalue_column(filtered_df, market_dimension, segment_col)
    else:
        segment_col = "Original_Language"
        market_source = filtered_df.copy()
        market_source[segment_col] = market_source[segment_col].fillna("Unknown")

    market_stats = market_source.groupby(segment_col).agg(
        Worldwide_Gross=("Worldwide_Gross", "sum"),
        Movie_Count=("Release_Group", "count"),
        Average_Rating=("Rating", "mean"),
        Average_Gross=("Worldwide_Gross", "mean")
    ).reset_index()

    metric_column = market_metric.replace(" ", "_")
    market_stats = market_stats.sort_values(metric_column, ascending=False).head(25)
    market_stats["Revenue_Label"] = market_stats["Worldwide_Gross"].apply(format_currency)
    market_stats["Average_Gross_Label"] = market_stats["Average_Gross"].apply(format_currency)

    if market_chart_type == "Treemap":
        fig_market = go.Figure(
            go.Treemap(
                labels=market_stats[segment_col],
                parents=[""] * len(market_stats),
                values=market_stats[metric_column],
                marker=dict(
                    colors=market_stats["Average_Rating"],
                    colorscale="Tealrose",
                    colorbar=dict(title="Avg Rating")
                ),
                customdata=np.stack(
                    [
                        market_stats["Movie_Count"],
                        market_stats["Revenue_Label"],
                        market_stats["Average_Gross_Label"],
                        market_stats["Average_Rating"]
                    ],
                    axis=-1
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    f"{market_metric}: %{{value:,.2f}}<br>"
                    "Movies: %{customdata[0]:,}<br>"
                    "Total Gross: %{customdata[1]}<br>"
                    "Average Gross: %{customdata[2]}<br>"
                    "Average Rating: %{customdata[3]:.2f}<extra></extra>"
                )
            )
        )
    elif market_chart_type == "Sunburst":
        fig_market = go.Figure(
            go.Sunburst(
                labels=market_stats[segment_col],
                parents=[""] * len(market_stats),
                values=market_stats[metric_column],
                marker=dict(
                    colors=market_stats["Average_Rating"],
                    colorscale="Tealrose",
                    colorbar=dict(title="Avg Rating")
                ),
                customdata=np.stack(
                    [
                        market_stats["Movie_Count"],
                        market_stats["Revenue_Label"],
                        market_stats["Average_Gross_Label"],
                        market_stats["Average_Rating"]
                    ],
                    axis=-1
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    f"{market_metric}: %{{value:,.2f}}<br>"
                    "Movies: %{customdata[0]:,}<br>"
                    "Total Gross: %{customdata[1]}<br>"
                    "Average Gross: %{customdata[2]}<br>"
                    "Average Rating: %{customdata[3]:.2f}<extra></extra>"
                )
            )
        )
    else:
        fig_market = px.bar(
            market_stats.sort_values(metric_column, ascending=True),
            x=metric_column,
            y=segment_col,
            orientation="h",
            color="Average_Rating",
            color_continuous_scale="Tealrose",
            hover_data=["Movie_Count", "Revenue_Label", "Average_Gross_Label"],
            labels={segment_col: "", metric_column: market_metric}
        )

    fig_market.update_layout(coloraxis_colorbar=dict(title="Avg Rating"))
    st.plotly_chart(apply_chart_style(fig_market, height=620), use_container_width=True)

    table_col_1, table_col_2, table_col_3, table_col_4 = st.columns(4)
    table_col_1.metric("Segments", f"{len(market_stats):,}")
    table_col_2.metric("Largest Segment", str(market_stats.iloc[0][segment_col]))
    table_col_3.metric("Top Segment Gross", format_currency(market_stats.iloc[0]["Worldwide_Gross"]))
    table_col_4.metric("Top Segment Movies", f"{int(market_stats.iloc[0]['Movie_Count']):,}")

# --- TAB 4: RATINGS & LANGUAGES ---
with tab_correlations:
    st.subheader("Audience Ratings & Language Analysis")
    
    col_corr, col_lang = st.columns([1, 1])
    
    with col_corr:
        st.markdown("**Correlation: IMDb Rating vs. Worldwide Revenue**")
        
        # Build Scatter plot with Trendline manually
        x_data = filtered_df['Rating'].values
        y_data = filtered_df['Worldwide_Gross'].values
        
        fig_scatter = go.Figure()
        
        # Add primary scatter
        fig_scatter.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='markers',
            name='Movies',
            marker=dict(
                size=8,
                color=filtered_df['Vote_Count'],
                colorscale='Viridis',
                colorbar=dict(title='Vote Count', thickness=15),
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            text=filtered_df['Release_Group'],
            hovertemplate="<b>%{text}</b><br>Rating: %{x}<br>Revenue: $%{y:,.0f}<br><extra></extra>"
        ))
        
        # Compute Trend Line manually if possible
        if len(x_data) > 1:
            try:
                z = np.polyfit(x_data, y_data, 1)
                p = np.poly1d(z)
                x_range = np.linspace(x_data.min(), x_data.max(), 100)
                fig_scatter.add_trace(go.Scatter(
                    x=x_range,
                    y=p(x_range),
                    mode='lines',
                    name='Trend Line',
                    line=dict(color='red', width=2, dash='dash')
                ))
            except:
                pass
                
        # Calculate correlation coefficient
        corr_val = filtered_df['Rating'].corr(filtered_df['Worldwide_Gross'])
        
        fig_scatter.update_layout(
            xaxis_title="IMDb Rating (out of 10)",
            yaxis_title="Worldwide Gross (USD)",
            margin=dict(l=40, r=40, t=30, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption(f"**Statistical Note:** The Pearson correlation coefficient between rating and revenue is **{corr_val:.2f}**.")
        
    with col_lang:
        st.markdown("**Original Language Performance (Minimum 5 Releases)**")
        
        lang_stats = filtered_df.groupby('Original_Language').agg(
            Avg_Revenue=('Worldwide_Gross', 'mean'),
            Count=('Worldwide_Gross', 'count')
        ).reset_index()
        
        # Filter for languages with at least 5 releases
        lang_stats = lang_stats[lang_stats['Count'] >= 5].sort_values(by='Avg_Revenue', ascending=True)
        
        if not lang_stats.empty:
            fig_lang = px.bar(
                lang_stats,
                y='Original_Language',
                x='Avg_Revenue',
                orientation='h',
                color='Avg_Revenue',
                color_continuous_scale='Sunset',
                labels={'Avg_Revenue': 'Average Gross (USD)', 'Original_Language': 'Language Code'}
            )
            fig_lang.update_layout(
                coloraxis_showscale=False,
                margin=dict(l=40, r=20, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_lang, use_container_width=True)
        else:
            st.info("💡 Not enough data to display language comparisons with a minimum of 5 releases.")

# --- TAB 5: CUSTOM CHART BUILDER ---
with tab_builder:
    st.subheader("Custom Interactive Chart Builder")

    numeric_columns = [
        "Rank", "Worldwide_Gross", "Domestic_Gross", "Domestic_Pct",
        "Foreign_Gross", "Foreign_Pct", "Year", "Rating", "Vote_Count"
    ]
    categorical_columns = ["Genres", "Original_Language", "Production_Countries"]

    builder_col_1, builder_col_2, builder_col_3, builder_col_4 = st.columns([1, 1, 1, 1])
    with builder_col_1:
        builder_chart = st.selectbox("Chart Type", ["Scatter", "Bar", "Box"], key="builder_chart")
    with builder_col_2:
        builder_x = st.selectbox(
            "X Axis",
            categorical_columns + numeric_columns,
            index=(categorical_columns + numeric_columns).index("Year"),
            key="builder_x"
        )
    with builder_col_3:
        builder_y = st.selectbox(
            "Y Axis",
            numeric_columns,
            index=numeric_columns.index("Worldwide_Gross"),
            key="builder_y"
        )
    with builder_col_4:
        builder_color = st.selectbox(
            "Color",
            ["None", "Genres", "Original_Language", "Year", "Rating"],
            index=1,
            key="builder_color"
        )

    chart_df = filtered_df.copy()
    x_field = builder_x
    color_field = None if builder_color == "None" else builder_color

    if builder_x in ["Genres", "Production_Countries"]:
        x_field = "Segment"
        chart_df = explode_multivalue_column(chart_df, builder_x, x_field)

    if color_field in ["Genres"]:
        color_field = "Color_Segment"
        chart_df = explode_multivalue_column(chart_df, "Genres", color_field)

    if builder_chart == "Scatter":
        size_by_votes = st.toggle("Size points by vote count", value=True, key="builder_size_votes")
        fig_builder = px.scatter(
            chart_df,
            x=x_field,
            y=builder_y,
            color=color_field,
            size="Vote_Count" if size_by_votes else None,
            hover_name="Release_Group",
            hover_data=["Year", "Rating", "Worldwide_Gross"],
            color_continuous_scale="Tealrose",
            labels={x_field: builder_x.replace("_", " "), builder_y: builder_y.replace("_", " ")}
        )
    elif builder_chart == "Bar":
        aggregation = st.segmented_control(
            "Aggregation",
            options=["Sum", "Average", "Median", "Count"],
            default="Sum",
            key="builder_aggregation"
        )
        if aggregation == "Count":
            grouped = chart_df.groupby(x_field).size().reset_index(name="Movie_Count")
            y_field = "Movie_Count"
        else:
            agg_func = {"Sum": "sum", "Average": "mean", "Median": "median"}[aggregation]
            grouped = chart_df.groupby(x_field)[builder_y].agg(agg_func).reset_index()
            y_field = builder_y
        grouped = grouped.sort_values(y_field, ascending=False).head(30)
        fig_builder = px.bar(
            grouped.sort_values(y_field, ascending=True),
            x=y_field,
            y=x_field,
            orientation="h",
            color=y_field,
            color_continuous_scale="Tealrose",
            labels={x_field: builder_x.replace("_", " "), y_field: f"{aggregation} {builder_y.replace('_', ' ')}"}
        )
    else:
        fig_builder = px.box(
            chart_df,
            x=x_field,
            y=builder_y,
            color=color_field,
            hover_data=["Release_Group", "Year", "Rating"],
            points="outliers",
            labels={x_field: builder_x.replace("_", " "), builder_y: builder_y.replace("_", " ")}
        )

    st.plotly_chart(apply_chart_style(fig_builder, height=620), use_container_width=True)

# --- TAB 6: SEARCH & EXPORT ---
with tab_search:
    st.subheader("Explore and Export Dataset")
    st.write("Browse and filter the selected cohort. You can also download the custom sliced database table as a CSV.")
    
    # Formatted display columns
    display_df = filtered_df[[
        'Rank', 'Release_Group', 'Year', 'Genres', 'Rating', 'Vote_Count', 
        'Worldwide_Gross', 'Domestic_Gross', 'Foreign_Gross', 'Original_Language'
    ]].copy()
    
    # Capitalize columns for presentation
    display_df.columns = [col.replace('_', ' ') for col in display_df.columns]
    
    # Display table
    st.dataframe(
        display_df,
        column_config={
            "Worldwide Gross": st.column_config.NumberColumn("Worldwide Gross", format="$%,.0f"),
            "Domestic Gross": st.column_config.NumberColumn("Domestic Gross", format="$%,.0f"),
            "Foreign Gross": st.column_config.NumberColumn("Foreign Gross", format="$%,.0f"),
            "Vote Count": st.column_config.NumberColumn("Votes", format="%,.0f"),
            "Rating": st.column_config.NumberColumn("IMDb Rating", format="%.2f"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    # CSV Download Button
    csv_buffer = io.StringIO()
    display_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv_data,
        file_name="filtered_box_office_data.csv",
        mime="text/csv",
        use_container_width=True
    )

# --- TAB 7: ABOUT & DATA SOURCE ---
with tab_about:
    st.subheader("About This Dashboard")

    source_min_year = int(df_raw["Year"].min())
    source_max_year = int(df_raw["Year"].max())
    source_movie_count = len(df_raw)
    source_total_gross = df_raw["Worldwide_Gross"].sum()

    st.markdown(
        f"""
        Box Office Intelligence is an interactive dashboard for exploring movie revenue,
        audience ratings, genre performance, and market composition from
        **{source_min_year} through {source_max_year}**.

        The app is designed for exploratory analysis. Use the sidebar filters to narrow
        the dataset by year, rating, vote count, genre, language, or movie title; every
        chart updates from the filtered dataset.
        """
    )

    about_col_1, about_col_2, about_col_3 = st.columns(3)
    about_col_1.metric("Source Records", f"{source_movie_count:,}")
    about_col_2.metric("Year Range", f"{source_min_year}-{source_max_year}")
    about_col_3.metric("Worldwide Gross", format_currency(source_total_gross))

    st.markdown("### Data Source")
    st.markdown(
        """
        The dashboard reads from the local SQLite database file `movies.db`.
        That database was prepared from the project CSV data and contains one
        row per movie release group.

        The main table used by the app is `box_office`.
        """
    )

    st.markdown("### Key Fields")
    st.dataframe(
        pd.DataFrame(
            [
                {"Field": "Release_Group", "Meaning": "Movie or release group title"},
                {"Field": "Year", "Meaning": "Release year"},
                {"Field": "Worldwide_Gross", "Meaning": "Total worldwide box office revenue"},
                {"Field": "Domestic_Gross", "Meaning": "Domestic box office revenue"},
                {"Field": "Foreign_Gross", "Meaning": "International box office revenue"},
                {"Field": "Genres", "Meaning": "Comma-separated genre labels"},
                {"Field": "Rating", "Meaning": "Audience rating on a 10-point scale"},
                {"Field": "Vote_Count", "Meaning": "Number of audience rating votes"},
                {"Field": "Original_Language", "Meaning": "Original language code"},
                {"Field": "Production_Countries", "Meaning": "Comma-separated production country labels"},
            ]
        ),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Interpretation Notes")
    st.markdown(
        """
        - Revenue charts use gross box office revenue, not profit.
        - Genre and production country charts split comma-separated values, so one movie can count in multiple categories.
        - Ratings and vote counts are audience-signal fields and should be interpreted separately from financial performance.
        - The dashboard is best used for comparing patterns and segments, not as a final financial accounting system.
        """
    )
