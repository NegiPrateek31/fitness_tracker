import plotly.express as px
import pandas as pd

def plot_progress(df):
    if df.empty:
        return None
    fig = px.line(df, x='date', y=['steps','calories','water','sleep'], markers=True)
    fig.update_layout(title="Activity Progress", xaxis_title="Date", yaxis_title="Values")
    return fig

def plot_pie(df):
    if df.empty:
        return None
    total_steps = df['steps'].sum()
    total_calories = df['calories'].sum()
    total_water = df['water'].sum()
    total_sleep = df['sleep'].sum()
    values = [total_steps, total_calories, total_water, total_sleep]
    labels = ['Steps','Calories','Water','Sleep']
    fig = px.pie(values=values, names=labels, title="Total Activity Breakdown")
    return fig

def plot_calendar_heatmap(df):
    if df.empty:
        return None
    df = df.copy()
    df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
    fig = px.density_heatmap(df, x='date_str', y=['steps','calories'], title='Activity Heatmap')
    return fig
