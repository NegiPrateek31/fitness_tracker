import plotly.express as px
import pandas as pd

def plot_progress(df):
    if df.empty:
        return None
    fig = px.line(df, x='date', y=['steps', 'calories', 'water', 'sleep'], markers=True)
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
    labels = ['Steps', 'Calories', 'Water', 'Sleep']
    fig = px.pie(values=values, names=labels, title="Total Activity Breakdown")
    return fig

def plot_calendar_heatmap(df):
    if df.empty:
        return None
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month_name()

    # Heatmap showing average steps per day by month
    fig = px.density_heatmap(
        df,
        x='day',
        y='month',
        z='steps',
        color_continuous_scale='Blues',
        title='Steps Activity Calendar Heatmap'
    )
    fig.update_layout(yaxis={'categoryorder': 'array', 'categoryarray': [
                      'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']})
    return fig
