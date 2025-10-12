import plotly.express as px
import plotly.graph_objects as go # Importing go for advanced plotting
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
    return fig

def plot_pie(df):
    if df.empty:
        return _get_empty_figure('No Activity Data Logged')
    # Use mean of daily steps/calories instead of sum to make it representative per day
    df_mean = df[['steps', 'calories']].mean().reset_index()
    df_mean.columns = ['metric', 'value']
    
    fig = px.pie(
        df_mean, 
        values='value', 
        names='metric', 
        title='Average Daily Steps vs. Calories',
        hole=0.3
    )
    fig.update_traces(textinfo='percent+label', marker=dict(colors=['#4E79A7', '#F28E2B']))
    return fig

def plot_calendar_heatmap(df):
    if df.empty:
        return _get_empty_figure('No Activity Data Logged')
    
    df_cal = df.copy()
    
    # 1. Prepare Date Columns (Use ISO Weekday: 1=Mon, 7=Sun)
    df_cal['date'] = pd.to_datetime(df_cal['date']).dt.date
    df_cal['day_of_week'] = pd.to_datetime(df_cal['date']).dt.dayofweek # 0=Mon, 6=Sun
    df_cal['week_of_year'] = pd.to_datetime(df_cal['date']).dt.isocalendar().week.astype(int)
    
    # 2. Aggregate data (Steps per day)
    heat = df_cal.groupby(['date', 'day_of_week', 'week_of_year'])['steps'].sum().reset_index()
    
    # 3. Create pivot table for heatmap structure
    # Rows: Day of Week (0-6), Columns: Week of Year
    pivot = heat.pivot_table(
        index='day_of_week', 
        columns='week_of_year', 
        values='steps', 
        fill_value=0
    )
    
    # 4. Handle sparse data (if data doesn't start on a Monday, pad the first column)
    min_week = pivot.columns.min()
    max_week = pivot.columns.max()

    # Create full matrix with zero steps for missing days
    full_matrix = np.zeros((7, max_week - min_week + 1))
    
    # Populate the full matrix with steps from the pivot table
    for i, week in enumerate(range(min_week, max_week + 1)):
        if week in pivot.columns:
            full_matrix[pivot.index, i] = pivot[week]

    # 5. Create Heatmap
    fig = go.Figure(data=go.Heatmap(
            z=full_matrix,
            x=[f"Week {i}" for i in range(min_week, max_week + 1)],
            y=DOW_NAMES,
            colorscale='YlGnBu',
            colorbar={'title': 'Total Steps', 'titleside': 'right'}
    ))

    # 6. Customize Layout for Calendar Look
    fig.update_layout(
        title={'text': 'Activity Heatmap (Steps Logged)', 'x': 0.5},
        xaxis={'title': 'Week of Year'},
        yaxis={'title': 'Day of Week', 'autorange': 'reversed'}, # Sunday is traditionally at the bottom
        height=400, # Calendar heatmaps look better when constrained vertically
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # 7. Add Annotations (Optional, but makes it look more polished)
    annotations = []
    for week_idx, week in enumerate(range(min_week, max_week + 1)):
        for day_idx in range(7):
            steps = full_matrix[day_idx, week_idx]
            if steps > 0:
                annotations.append(
                    dict(
                        x=week_idx,
                        y=day_idx,
                        text=f"{int(steps)}",
                        font=dict(size=10, color="black"),
                        showarrow=False
                    )
                )
    
    fig.update_layout(annotations=annotations)
    
    return fig
