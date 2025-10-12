import plotly.express as px
import plotly.graph_objects as go # <-- Added Plotly graph objects for handling empty states
import pandas as pd

def plot_progress(df):
    if df.empty:
        return go.Figure() # Returning an empty figure instead of {}
    df2 = df.copy()
    fig = px.line(df2, x='date', y='steps', title='Steps over time', markers=True)
    return fig

def plot_pie(df):
    if df.empty:
        return go.Figure() # Returning an empty figure instead of {}
    values = [df['steps'].sum(), df['calories'].sum()]
    labels = ['Steps','Calories']
    fig = px.pie(values=values, names=labels, title='Steps vs Calories (sum)')
    return fig

def plot_calendar_heatmap(df):
    if df.empty:
        return go.Figure() # Returning an empty figure instead of {}
    df2 = df.copy()
    
    # Ensure 'date' column is in the expected format before grouping/calculating dates
    # We use a try-except block here for safety against malformed date strings
    try:
        df2['date'] = pd.to_datetime(df2['date']).dt.date
    except Exception:
        return go.Figure().add_annotation(text="Error processing date data for heatmap.", showarrow=False)

    heat = df2.groupby('date')['steps'].sum().reset_index()
    
    if heat.empty:
        return go.Figure()

    heat['date'] = pd.to_datetime(heat['date'])
    heat['dow'] = heat['date'].dt.weekday
    heat['week'] = (heat['date'] - heat['date'].min()).dt.days // 7
    
    # Handle the edge case where there is not enough data for pivoting
    if heat['week'].max() < 0:
        return go.Figure()
        
    pivot = heat.pivot(index='dow', columns='week', values='steps').fillna(0)
    
    if pivot.empty:
        return go.Figure()
        
    fig = px.imshow(pivot, labels=dict(x='Week', y='Day of week', color='Steps'), title='Activity Heatmap (by week/dow)')
    return fig
