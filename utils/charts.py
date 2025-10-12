import plotly.express as px
import pandas as pd

def plot_progress(df):
    if df.empty:
        return {}
    df2 = df.copy()
    fig = px.line(df2, x='date', y='steps', title='Steps over time', markers=True)
    return fig

def plot_pie(df):
    if df.empty:
        return {}
    values = [df['steps'].sum(), df['calories'].sum()]
    labels = ['Steps','Calories']
    fig = px.pie(values=values, names=labels, title='Steps vs Calories (sum)')
    return fig

def plot_calendar_heatmap(df):
    if df.empty:
        return {}
    df2 = df.copy()
    df2['date'] = pd.to_datetime(df2['date']).dt.date
    heat = df2.groupby('date')['steps'].sum().reset_index()
    heat['date'] = pd.to_datetime(heat['date'])
    heat['dow'] = heat['date'].dt.weekday
    heat['week'] = (heat['date'] - heat['date'].min()).dt.days // 7
    pivot = heat.pivot(index='dow', columns='week', values='steps').fillna(0)
    fig = px.imshow(pivot, labels=dict(x='Week', y='Day of week', color='Steps'), title='Activity Heatmap (by week/dow)')
    return fig
