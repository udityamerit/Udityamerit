import os, re
from pathlib import Path
from datetime import datetime, timezone

import requests
import pandas as pd
import matplotlib.pyplot as plt

USERNAME = os.getenv("GH_USERNAME", "udityamerit")

DATA_DIR = Path("data")
ASSETS_DIR = Path("assets")
DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_DIR / "views_data.csv"
README_FILE = Path("README.md")

def fetch_total_views(username: str) -> int:
    url = f"https://komarev.com/ghpvc/?username={username}&style=flat"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    r.raise_for_status()
    svg = r.text
    # SVG ke andar last <text> me number hota hai
    matches = re.findall(r'>\s*([0-9,]+)\s*<', svg)
    if not matches:
        raise RuntimeError("Could not parse komarev svg for total views")
    return int(matches[-1].replace(",", ""))

def load_df() -> pd.DataFrame:
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            return df
    return pd.DataFrame(columns=["date", "total"])

def save_df(df: pd.DataFrame) -> None:
    df.to_csv(DATA_FILE, index=False)

def plot_series(series: pd.Series, title: str, outfile: Path, ylabel: str = "Views"):
    plt.figure(figsize=(10, 4))
    plt.plot(series.index, series.values, marker="o")
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(outfile)
    plt.close()

def update_readme(total: int):
    if not README_FILE.exists():
        return
    content = README_FILE.read_text(encoding="utf-8")
    start = "<!--PV_TOTAL-->"
    end = "<!--/PV_TOTAL-->"
    if start in content and end in content:
        import re as _re
        new_content = _re.sub(
            rf"{_re.escape(start)}.*?{_re.escape(end)}",
            f"{start}{total}{end}",
            content,
            flags=_re.S
        )
    else:
        # markers na milen to simple section append kar do
        extra = (
            "\n\n## 👀 Profile Views\n"
            f"Total: <!--PV_TOTAL-->{total}<!--/PV_TOTAL-->\n\n"
            "### Daily\n![Daily](assets/views_daily.png)\n"
        )
        new_content = content + extra
    if new_content != content:
        README_FILE.write_text(new_content, encoding="utf-8")

def main():
    total = fetch_total_views(USERNAME)
    today = pd.Timestamp(datetime.now(timezone.utc).date())

    df = load_df()

    if not df.empty and (df["date"] == today).any():
        prev = df.loc[df["date"] == today, "total"].iloc[0]
        if total < prev:
            total = prev
        df.loc[df["date"] == today, "total"] = total
    else:
        df = pd.concat([df, pd.DataFrame([{"date": today, "total": total}])], ignore_index=True)

    df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    save_df(df)

    s = df.set_index("date")["total"].astype(int)
    delta = s.diff().fillna(0).clip(lower=0)

    # Charts
    plot_series(delta,   "Daily Profile Views",   ASSETS_DIR / "views_daily.png")
    plot_series(delta.resample("W").sum(),  "Weekly Profile Views",  ASSETS_DIR / "views_weekly.png")
    plot_series(delta.resample("MS").sum(), "Monthly Profile Views", ASSETS_DIR / "views_monthly.png")
    plot_series(delta.resample("YS").sum(), "Yearly Profile Views",  ASSETS_DIR / "views_yearly.png")

    update_readme(int(s.iloc[-1]))

if __name__ == "__main__":
    main()
