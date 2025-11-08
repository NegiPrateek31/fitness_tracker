import plotly.express as px
import plotly.graph_objects as go 
import pandas as pd
import numpy as np

# Map weekday numbers (0=Mon, 6=Sun) to common names for display
DOW_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

def _get_empty_figure(title="No data available"):
    """Returns a valid empty Plotly figure to prevent Streamlit errors."""
    fig = go.Figure()
    fig.update_layout(
        title={'text': title, 'x': 0.5},
        xaxis={'visible': False},
        yaxis={'visible': False},
        annotations=[
            dict(text=title, xref="paper", yref="paper", showarrow=False, font={'size': 20})
        ]
    )
    return fig

def plot_progress(df):
    if df.empty:
        return _get_empty_figure('No Activity Data Logged')
    df2 = df.copy()
    fig = px.line(df2, x='date', y='steps', title='Steps Over Time', markers=True)
    fig.update_layout(title_font_size=20) 
    return fig

# REMOVED PLOT_PIE (Misleading comparison between Steps and Calories average)

def plot_correlation(df):
    """Plots the correlation between Steps and Calories Burned."""
    if df.empty:
        return _get_empty_figure('No Correlation Data Available')
    
    df2 = df.copy()
    
    # Calculate R-squared for context
    corr = df2['steps'].corr(df2['calories'])
    title = f'Steps vs. Calories Burned (R={corr:.2f})'
    
    fig = px.scatter(
        df2, 
        x='steps', 
        y='calories', 
        color='date', 
        hover_data=['water', 'sleep'],
        title=title,
        trendline='ols' # Add Ordinary Least Squares regression line
    )
    
    fig.update_layout(
        title_font_size=20,
        xaxis_title="Steps",
        yaxis_title="Calories Burned",
    )
    fig.update_traces(marker=dict(size=10, opacity=0.8))
    
    return fig

def plot_calendar_heatmap(df):
    if df.empty:
        return _get_empty_figure('No Activity Data Logged')
    
    df_cal = df.copy()
    
    # 1. Prepare Date Columns and create a continuous week number for indexing
    df_cal['date'] = pd.to_datetime(df_cal['date'])
    df_cal['day_of_week'] = df_cal['date'].dt.dayofweek # 0=Mon, 6=Sun
    
    # Calculate continuous week number 
    min_date = df_cal['date'].min()
    df_cal['week_number'] = ((df_cal['date'] - min_date).dt.days // 7).astype(int)
    
    # 2. Aggregate data (Steps per day)
    heat = df_cal.groupby(['date', 'day_of_week', 'week_number'])['steps'].sum().reset_index()
    
    # 3. Create pivot table for heatmap structure
    pivot = heat.pivot_table(
        index='day_of_week', 
        columns='week_number', 
        values='steps', 
        fill_value=0
    )
    
    # 4. Create full matrix to handle sparse days 
    min_week = pivot.columns.min()
    max_week = pivot.columns.max()

    num_weeks = max_week - min_week + 1
    
    # Rows: 7 days of week, Columns: contiguous weeks
    full_matrix = np.zeros((7, num_weeks))
    
    # Populate the full matrix with steps from the pivot table
    for i, week_num in enumerate(range(min_week, max_week + 1)):
        if week_num in pivot.columns:
            full_matrix[pivot.index, i] = pivot[week_num]

    # 5. Create Heatmap
    fig = go.Figure(data=go.Heatmap(
            z=full_matrix,
            x=[f"Week {i+1}" for i in range(num_weeks)], 
            y=DOW_NAMES,
            colorscale='Blues',
            colorbar={
                'title': {
                    'text': 'Total Steps', 
                    'font': {'size': 14} 
                }
            }
    ))

    # 6. Customize Layout for Calendar Look
    fig.update_layout(
        title={'text': 'Activity Heatmap (Steps Logged)', 'x': 0.5, 'font': {'size': 20}},
        xaxis={'title': '', 'tickmode': 'array', 'tickvals': list(range(num_weeks)), 'ticktext': [f"Week {i+1}" for i in range(num_weeks)], 'tickfont': {'size': 12}},
        yaxis={'title': '', 'autorange': 'reversed', 'tickangle': 0, 'tickfont': {'size': 12}},
        height=450, 
        margin=dict(l=30, r=30, t=50, b=30),
    )
    
    # 7. Add Annotations (Steps value inside the box)
    annotations = []
    threshold = 5500 
    
    for week_idx in range(num_weeks):
        for day_idx in range(7):
            steps = full_matrix[day_idx, week_idx]
            if steps > 0:
                text_color = "white" if steps > threshold else "black"
                
                annotations.append(
                    dict(
                        x=week_idx,
                        y=day_idx,
                        text=f"{int(steps)}",
                        font=dict(size=12, color=text_color), 
                        showarrow=False
                    )
                )
    
    fig.update_layout(annotations=annotations)
    
    return fig
