import plotly.express as px
import pandas as pd
import streamlit as st

def plot_progress(df):
    if df.empty:
        return None
    fig = px.line(
        df,
        x='date',
        y=['steps', 'calories', 'water', 'sleep'],
        markers=True,
        title="Activity Progress Over Time"
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Values")
    return fig


def plot_pie(df):
    if df.empty:
        return None
    totals = {
        "Steps": df["steps"].sum(),
        "Calories": df["calories"].sum(),
        "Water (L)": df["water"].sum(),
        "Sleep (hrs)": df["sleep"].sum(),
    }
    fig = px.pie(
        names=list(totals.keys()),
        values=list(totals.values()),
        title="Total Activity Breakdown"
    )
    return fig


def plot_calendar_heatmap(df):
    if df.empty:
        return None

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month_name()

    # Create tabs for two metrics
    tab1, tab2 = st.tabs(["🔥 Steps Heatmap", "🔥 Calories Heatmap"])

    with tab1:
        fig_steps = px.density_heatmap(
            df,
            x="day",
            y="month",
            z="steps",
            color_continuous_scale="Blues",
            title="Steps Activity Calendar Heatmap"
        )
        fig_steps.update_layout(
            yaxis={"categoryorder": "array", "categoryarray": [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]}
        )
        st.plotly_chart(fig_steps, use_container_width=True)

    with tab2:
        fig_calories = px.density_heatmap(
            df,
            x="day",
            y="month",
            z="calories",
            color_continuous_scale="Oranges",
            title="Calories Burned Calendar Heatmap"
        )
        fig_calories.update_layout(
            yaxis={"categoryorder": "array", "categoryarray": [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]}
        )
        st.plotly_chart(fig_calories, use_container_width=True)

    return True  # to confirm rendering success
