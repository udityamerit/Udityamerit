# import os, re, json
# from pathlib import Path
# from datetime import datetime, timezone, date, timedelta

# import requests
# import plotly.graph_objects as go

# USERNAME = "udityamerit"
# DATA_DIR = Path("docs/data")
# DATA_DIR.mkdir(parents=True, exist_ok=True)
# JSON_FILE = DATA_DIR / "views.json"
# THUMBNAIL = Path("docs/thumbnail.png")
# README = Path("README.md")

# SEED_TOTAL = 100  # first-run seed (last 2 days total you mentioned)

# def fetch_total_from_komarev(username: str) -> int | None:
#     url = f"https://komarev.com/ghpvc/?username={username}&style=flat"
#     r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
#     if r.status_code != 200:
#         return None
#     svg = r.text
#     nums = re.findall(r'>\s*([\d,]+)\s*<', svg)
#     if not nums:
#         return None
#     return int(nums[-1].replace(",", ""))

# def load_series():
#     if JSON_FILE.exists():
#         with open(JSON_FILE, "r", encoding="utf-8") as f:
#             return json.load(f)
#     # first run: create with yesterday & today seed
#     today = date.today()
#     points = [
#         {"date": (today - timedelta(days=1)).isoformat(), "total": SEED_TOTAL//2},
#         {"date": today.isoformat(), "total": SEED_TOTAL},
#     ]
#     return {"generated_at": datetime.now(timezone.utc).isoformat(),
#             "points": points}

# def save_series(data):
#     data["generated_at"] = datetime.now(timezone.utc).isoformat()
#     with open(JSON_FILE, "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)

# def ensure_today_point(data, current_total: int):
#     today = date.today().isoformat()
#     points = data["points"]
#     # keep unique by date
#     idx = next((i for i,p in enumerate(points) if p["date"]==today), None)
#     if idx is None:
#         points.append({"date": today, "total": current_total})
#     else:
#         # never go backwards
#         points[idx]["total"] = max(points[idx]["total"], current_total)
#     # sort & de-dupe
#     points.sort(key=lambda p: p["date"])
#     # drop duplicates keeping last
#     seen=set(); out=[]
#     for p in points:
#         if p["date"] in seen: 
#             out[-1]=p
#         else:
#             out.append(p); seen.add(p["date"])
#     data["points"]=out

# def make_thumbnail(data):
#     x = [p["date"] for p in data["points"]]
#     y = [p["total"] for p in data["points"]]
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=x,y=y, mode="lines+markers",
#         line=dict(width=4, shape="spline"),
#         marker=dict(size=8)))
#     fig.update_layout(
#         title="Profile Views (Cumulative)",
#         paper_bgcolor="#0b1020", plot_bgcolor="#0b1020",
#         font=dict(color="#eaeefb"),
#         xaxis=dict(gridcolor="#1b2340"),
#         yaxis=dict(gridcolor="#1b2340"),
#         margin=dict(l=50,r=20,t=50,b=50), width=900, height=420
#     )
#     # Use kaleido engine for static image
#     fig.write_image(str(THUMBNAIL), scale=2)

# def update_readme_total(total: int):
#     if not README.exists(): return
#     txt = README.read_text(encoding="utf-8")
#     new = re.sub(r"(<!--PV_TOTAL-->)(.*?)(<!--/PV_TOTAL-->)",
#                  rf"\1{total}\3", txt, flags=re.S)
#     if new != txt:
#         README.write_text(new, encoding="utf-8")

# def main():
#     data = load_series()
#     total = fetch_total_from_komarev(USERNAME)
#     if total is None:
#         # fallback to last known total
#         total = data["points"][-1]["total"] if data["points"] else SEED_TOTAL
#     ensure_today_point(data, total)
#     save_series(data)
#     make_thumbnail(data)
#     update_readme_total(data["points"][-1]["total"])

# if __name__ == "__main__":
#     main()
