import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np
from matplotlib.lines import Line2D

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("shots6.csv")

# Create team label
df['team'] = df['team_home'].apply(lambda x: 'Chelsea' if x else 'Manchester City')

# -----------------------------
# PLAYER STATS SUMMARY
# -----------------------------
player_stats = pd.DataFrame({
    "player": [
        "Antoine Semenyo","Erling Haaland","Cole Palmer","João Pedro",
        "Jérémy Doku","Marc Cucurella","Marc Guéhi","Nico O'Reilly",
        "Rayan Cherki","Bernardo Silva"
    ],
    "total_shots": [5,4,4,3,2,2,1,1,2,2],
    "goals": [0,0,0,0,1,0,1,1,0,0],
    "shooting_accuracy": [0.4,0.25,0.25,0.0,0.5,0.5,1.0,1.0,0.5,0.5],
    "avg_distance": [19.0,17.5,18.0,20.0,16.5,14.0,13.0,12.0,18.5,17.0]
})

# -----------------------------
# TITLE
# -----------------------------
st.title("⚽ Chelsea vs Manchester City - Shot Analysis Dashboard")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")
team_filter = st.sidebar.selectbox("Select Team", ["All", "Chelsea", "Manchester City"])
shot_filter = st.sidebar.selectbox("Shot Type", ["All"] + list(df['shot_type'].unique()))

# Apply filters
filtered_df = df.copy()
if team_filter != "All":
    filtered_df = filtered_df[filtered_df['team'] == team_filter]
if shot_filter != "All":
    filtered_df = filtered_df[filtered_df['shot_type'] == shot_filter]

# -----------------------------
# 1. KEY METRICS
# -----------------------------
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)
total_shots = len(filtered_df)
goals = len(filtered_df[filtered_df['shot_type'] == 'goal'])
on_target = len(filtered_df[filtered_df['shot_type'].isin(['goal', 'save'])])

col1.metric("Total Shots", total_shots)
col2.metric("Goals", goals)
col3.metric("On Target", on_target)

# -----------------------------
# 2. DATA TABLE
# -----------------------------
st.subheader("📋 Shot Data")
st.dataframe(filtered_df)

# -----------------------------
# 3. SHOT MAP
# -----------------------------
st.subheader("📍 Shot Map (With Distance)")
pitch = Pitch(pitch_type='statsbomb', pitch_color='#dbe2b0', line_color='white')
fig, ax = pitch.draw(figsize=(10, 6))
plot_df = filtered_df.copy()

# Flip Manchester City (away team)
if team_filter == "Manchester City":
    plot_df['x'] = 120 - plot_df['x']
    plot_df['y'] = 80 - plot_df['y']

# Distance to goal
plot_df['distance'] = np.sqrt((120 - plot_df['x'])**2 + (40 - plot_df['y'])**2).round(1)

# Colors
shot_colors = {"goal": "green", "miss": "red", "block": "orange", "save": "purple", "post": "blue"}

# Plot shots
for _, row in plot_df.iterrows():
    ax.scatter(row['x'], row['y'],
               color=shot_colors.get(row['shot_type'], "black"),
               s=140, edgecolors='black', alpha=0.9)
    ax.text(row['x'] + 1, row['y'] + 1, f"{row['distance']}m", fontsize=8, color='black')

# Legend
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Goal', markerfacecolor='green', markeredgecolor='black'),
    Line2D([0], [0], marker='o', color='w', label='Miss', markerfacecolor='red', markeredgecolor='black'),
    Line2D([0], [0], marker='o', color='w', label='Block', markerfacecolor='orange', markeredgecolor='black'),
    Line2D([0], [0], marker='o', color='w', label='Post', markerfacecolor='blue', markeredgecolor='black'),
    Line2D([0], [0], marker='o', color='w', label='Save', markerfacecolor='purple', markeredgecolor='black')
]
ax.legend(handles=legend_elements, title="Shot Outcome", loc="upper right")
ax.set_title("Shot Map with Distance to Goal")

st.pyplot(fig)

# -----------------------------
# 4. PLAYER SHOTS
# -----------------------------
st.subheader("👤 Player Shots")
player_shots = filtered_df['player'].value_counts().reset_index()
player_shots.columns = ['Player', 'Shots']
st.dataframe(player_shots)

# -----------------------------
# 5. SHOT SITUATIONS
# -----------------------------
st.subheader("⚙️ Shot Situations")
if 'situation' in filtered_df.columns:
    situation_counts = filtered_df['situation'].value_counts()
    st.bar_chart(situation_counts)
else:
    st.info("No 'situation' column found in dataset")

# -----------------------------
# 6. PLAYER STATS CHARTS
# -----------------------------
st.subheader("📈 Player Shot Analysis")

# Scatter chart
st.markdown("### Avg Distance vs Shooting Accuracy")
fig2, ax2 = plt.subplots(figsize=(8,6))
ax2.scatter(player_stats['avg_distance'], player_stats['shooting_accuracy'], s=100, edgecolor='black')
for i, row in player_stats.iterrows():
    ax2.text(row['avg_distance']+0.3, row['shooting_accuracy']+0.01, row['player'], fontsize=9)
ax2.set_xlabel("Average Distance to Goal (m)")
ax2.set_ylabel("Shooting Accuracy")
ax2.set_title("Avg Distance vs Shooting Accuracy per Player")

st.pyplot(fig2)

# Bar chart
st.markdown("### Goals per Player")
fig3, ax3 = plt.subplots(figsize=(10,5))
ax3.bar(player_stats['player'], player_stats['goals'], edgecolor='black')
ax3.set_ylabel("Goals")
ax3.set_xlabel("Player")
ax3.set_title("Goals per Player")
plt.xticks(rotation=45, ha='right')

st.pyplot(fig3)

# Table
st.subheader("👤 Player Stats Table")
st.dataframe(player_stats)

# -----------------------------
# 7. KEY INSIGHTS
# -----------------------------
st.subheader("🧠 Key Insights")

if total_shots > 0:
    conversion = (goals / total_shots) * 100

    st.markdown(f"""
- The team produced **{total_shots} shots** with a conversion rate of **{conversion:.1f}%**
- **{on_target} shots on target** reflect overall finishing performance
""")

    if conversion < 10:
        st.markdown("- ⚠️ Low conversion rate suggests poor finishing")

    blocks = len(filtered_df[filtered_df['shot_type'] == 'block'])
    if blocks > 0:
        st.markdown(f"- 🧱 {blocks} shots were blocked, showing defensive pressure")

    misses = len(filtered_df[filtered_df['shot_type'] == 'miss'])
    if misses > goals:
        st.markdown("- 🎯 High number of misses suggests poor shot selection")

else:
    st.warning("No data available for selected filters")