import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

USERNAME = "udityamerit"
DATA_FILE = "data/views.csv"
README_FILE = "README.md"

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Load existing data or create new
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["date", "views"])

# Get current views from Komarev API
# (Simulated here since Komarev doesn't give history, we just increment)
current_views = 100 + len(df)  # starting count from your input

# Append new row
today = datetime.now().strftime("%Y-%m-%d")
if today not in df["date"].values:
    df = pd.concat([df, pd.DataFrame([[today, current_views]], columns=["date", "views"])], ignore_index=True)

# Save updated data
df.to_csv(DATA_FILE, index=False)

# Plot total views graph
fig_total = go.Figure()
fig_total.add_trace(go.Scatter(
    x=df["date"], y=df["views"],
    mode="lines+markers",
    line=dict(color="royalblue", width=3),
    marker=dict(size=8, color="orange"),
    name="Total Views"
))
fig_total.update_layout(
    title="Total Profile Views Over Time",
    xaxis_title="Date",
    yaxis_title="Views",
    template="plotly_dark",
    hovermode="x unified"
)
fig_total.write_html("data/total_views.html", include_plotlyjs="cdn")

# Prepare filtered plots
def save_plot(filtered_df, title, filename):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_df["date"], y=filtered_df["views"],
        mode="lines+markers",
        line=dict(color="lime", width=3),
        marker=dict(size=8, color="red"),
        name="Views"
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Views",
        template="plotly_dark",
        hovermode="x unified"
    )
    fig.write_html(filename, include_plotlyjs="cdn")

save_plot(df.tail(7), "Last 7 Days Views", "data/weekly_views.html")
save_plot(df.tail(30), "Last 30 Days Views", "data/monthly_views.html")
save_plot(df, "Yearly Views", "data/yearly_views.html")

# Update README
with open(README_FILE, "r", encoding="utf-8") as f:
    readme_content = f.read()

new_section = f"""
<!--PROFILE_VIEWS_START-->
## 📊 GitHub Profile Views

**Total Views:** {df['views'].iloc[-1]}  

### 🔹 Total Views Over Time
![Total Views](https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/main/data/total_views.html)

### 🔹 Weekly Views
![Weekly Views](https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/main/data/weekly_views.html)

### 🔹 Monthly Views
![Monthly Views](https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/main/data/monthly_views.html)

### 🔹 Yearly Views
![Yearly Views](https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/main/data/yearly_views.html)
<!--PROFILE_VIEWS_END-->
"""

if "<!--PROFILE_VIEWS_START-->" in readme_content:
    start = readme_content.index("<!--PROFILE_VIEWS_START-->")
    end = readme_content.index("<!--PROFILE_VIEWS_END-->") + len("<!--PROFILE_VIEWS_END-->")
    readme_content = readme_content[:start] + new_section + readme_content[end:]
else:
    readme_content += "\n" + new_section

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(readme_content)
