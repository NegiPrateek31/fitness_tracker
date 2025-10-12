'''import plotly.express as px
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
    
    # 1. Prepare Date Columns and create a continuous week number for indexing
    df_cal['date'] = pd.to_datetime(df_cal['date'])
    df_cal['day_of_week'] = df_cal['date'].dt.dayofweek # 0=Mon, 6=Sun
    
    # Calculate continuous week number (Fix for cross-year ISO week issue)
    min_date = df_cal['date'].min()
    df_cal['week_number'] = ((df_cal['date'] - min_date).dt.days // 7).astype(int)
    
    # 2. Aggregate data (Steps per day)
    heat = df_cal.groupby(['date', 'day_of_week', 'week_number'])['steps'].sum().reset_index()
    
    # 3. Create pivot table for heatmap structure
    # Rows: Day of Week (0-6), Columns: Week Number
    pivot = heat.pivot_table(
        index='day_of_week', 
        columns='week_number', 
        values='steps', 
        fill_value=0
    )
    
    # 4. Create full matrix to handle sparse days (essential for calendar grid)
    min_week = pivot.columns.min()
    max_week = pivot.columns.max()

    num_weeks = max_week - min_week + 1
    
    # Rows: 7 days of week, Columns: contiguous weeks
    full_matrix = np.zeros((7, num_weeks))
    
    # Populate the full matrix with steps from the pivot table
    for i, week_num in enumerate(range(min_week, max_week + 1)):
        if week_num in pivot.columns:
            # pivot.index is day_of_week (0-6)
            full_matrix[pivot.index, i] = pivot[week_num]

    # 5. Create Heatmap
    fig = go.Figure(data=go.Heatmap(
            z=full_matrix,
            x=[f"Week {i+1}" for i in range(num_weeks)], # Display friendly Week 1, Week 2, etc.
            y=DOW_NAMES,
            colorscale='Viridis',
            # FIXED: 'titlesize' is correctly nested under 'title'
            colorbar={
                'title': {
                    'text': 'Total Steps', 
                    'font': {'size': 12}
                }
            }
    ))

    # 6. Customize Layout for Calendar Look
    fig.update_layout(
        title={'text': 'Activity Heatmap (Steps Logged)', 'x': 0.5, 'font': {'size': 16}},
        xaxis={'title': '', 'tickmode': 'array', 'tickvals': list(range(num_weeks)), 'ticktext': [f"Week {i+1}" for i in range(num_weeks)]},
        yaxis={'title': '', 'autorange': 'reversed', 'tickangle': 0},
        height=450, # Slightly increased height
        margin=dict(l=30, r=30, t=50, b=30),
    )
    
    # 7. Add Annotations (Steps value inside the box)
    annotations = []
    # Calculate the median step value for dynamic text coloring
    non_zero_steps = full_matrix[full_matrix > 0]
    median_steps = np.percentile(non_zero_steps, 50) if non_zero_steps.size > 0 else 0
    
    for week_idx in range(num_weeks):
        for day_idx in range(7):
            steps = full_matrix[day_idx, week_idx]
            if steps > 0:
                # Use white text for higher values (darker background) and black for lower values
                text_color = "white" if steps > median_steps else "black"
                
                annotations.append(
                    dict(
                        x=week_idx,
                        y=day_idx,
                        text=f"{int(steps)}",
                        font=dict(size=11, color=text_color),
                        showarrow=False
                    )
                )
    
    fig.update_layout(annotations=annotations)
    
    return fig'''
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
    # INCREASED HEADING SIZE
    fig.update_layout(title_font_size=20) 
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
    # INCREASED HEADING SIZE
    fig.update_layout(title_font_size=20) 
    return fig

def plot_calendar_heatmap(df):
    if df.empty:
        return _get_empty_figure('No Activity Data Logged')
    
    df_cal = df.copy()
    
    # 1. Prepare Date Columns and create a continuous week number for indexing
    df_cal['date'] = pd.to_datetime(df_cal['date'])
    df_cal['day_of_week'] = df_cal['date'].dt.dayofweek # 0=Mon, 6=Sun
    
    # Calculate continuous week number (Fix for cross-year ISO week issue)
    min_date = df_cal['date'].min()
    df_cal['week_number'] = ((df_cal['date'] - min_date).dt.days // 7).astype(int)
    
    # 2. Aggregate data (Steps per day)
    heat = df_cal.groupby(['date', 'day_of_week', 'week_number'])['steps'].sum().reset_index()
    
    # 3. Create pivot table for heatmap structure
    # Rows: Day of Week (0-6), Columns: Week Number
    pivot = heat.pivot_table(
        index='day_of_week', 
        columns='week_number', 
        values='steps', 
        fill_value=0
    )
    
    # 4. Create full matrix to handle sparse days (essential for calendar grid)
    min_week = pivot.columns.min()
    max_week = pivot.columns.max()

    num_weeks = max_week - min_week + 1
    
    # Rows: 7 days of week, Columns: contiguous weeks
    full_matrix = np.zeros((7, num_weeks))
    
    # Populate the full matrix with steps from the pivot table
    for i, week_num in enumerate(range(min_week, max_week + 1)):
        if week_num in pivot.columns:
            # pivot.index is day_of_week (0-6)
            full_matrix[pivot.index, i] = pivot[week_num]

    # 5. Create Heatmap
    fig = go.Figure(data=go.Heatmap(
            z=full_matrix,
            x=[f"Week {i+1}" for i in range(num_weeks)], # Display friendly Week 1, Week 2, etc.
            y=DOW_NAMES,
            # CHANGED COLORSCALE TO A LIGHTER GRADIENT (Blues)
            colorscale='Blues',
            colorbar={
                'title': {
                    'text': 'Total Steps', 
                    'font': {'size': 14} # Increased color bar title size
                }
            }
    ))

    # 6. Customize Layout for Calendar Look
    fig.update_layout(
        # INCREASED MAIN TITLE SIZE
        title={'text': 'Activity Heatmap (Steps Logged)', 'x': 0.5, 'font': {'size': 20}},
        # Increased X and Y axis label font size
        xaxis={'title': '', 'tickmode': 'array', 'tickvals': list(range(num_weeks)), 'ticktext': [f"Week {i+1}" for i in range(num_weeks)], 'tickfont': {'size': 12}},
        yaxis={'title': '', 'autorange': 'reversed', 'tickangle': 0, 'tickfont': {'size': 12}},
        height=450, 
        margin=dict(l=30, r=30, t=50, b=30),
    )
    
    # 7. Add Annotations (Steps value inside the box)
    annotations = []
    # Calculate the median step value for dynamic text coloring
    # The 'Blues' colorscale means darker colors are higher up, so we can stick to white text for high values.
    # I'll use a fixed threshold based on the minimum sample data to ensure legibility.
    threshold = 5500 # Slightly above the sample start value
    
    for week_idx in range(num_weeks):
        for day_idx in range(7):
            steps = full_matrix[day_idx, week_idx]
            if steps > 0:
                # Use white text for medium/high values, and black for very light (low) values
                text_color = "white" if steps > threshold else "black"
                
                annotations.append(
                    dict(
                        x=week_idx,
                        y=day_idx,
                        text=f"{int(steps)}",
                        font=dict(size=12, color=text_color), # Increased annotation font size
                        showarrow=False
                    )
                )
    
    fig.update_layout(annotations=annotations)
    
    return fig

