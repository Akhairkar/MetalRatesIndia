#!/usr/bin/env python3
"""
Seed data generator for Metal Rates India.
Produces data/metals.json and data/goldsilver.json with 365 days of
synthetic-but-realistic per-kg INR history for every tracked metal.

This is run ONCE to seed the repo. After deployment, the GitHub Action
(.github/workflows/update-rates.yml -> scripts/fetch_rates.py) takes over
and appends real, live-fetched rates every day.
"""
import json, random, datetime, math, os

random.seed(7)
TODAY = datetime.date(2026, 7, 3)
DAYS = 365

BASE_METALS = {
    "copper":          {"name": "Copper",          "hi": "तांबा",   "symbol": "CU", "start": 780,   "vol": 0.006, "color": "#c87137"},
    "brass":           {"name": "Brass",            "hi": "पीतल",    "symbol": "BR", "start": 545,   "vol": 0.005, "color": "#c9a24b"},
    "aluminium":       {"name": "Aluminium",         "hi": "एल्युमिनियम","symbol": "AL", "start": 255, "vol": 0.005, "color": "#b8c2c9"},
    "iron":            {"name": "Iron",              "hi": "लोहा",    "symbol": "FE", "start": 60,    "vol": 0.004, "color": "#8a5a3b"},
    "steel":           {"name": "Steel",             "hi": "इस्पात",  "symbol": "ST", "start": 79,    "vol": 0.004, "color": "#6e7b85"},
    "stainless-steel": {"name": "Stainless Steel",   "hi": "स्टेनलेस स्टील", "symbol": "SS", "start": 200, "vol": 0.004, "color": "#a9b4bc"},
    "zinc":            {"name": "Zinc",              "hi": "जस्ता",   "symbol": "ZN", "start": 272, "vol": 0.006, "color": "#7d8a94"},
    "lead":            {"name": "Lead",              "hi": "सीसा",    "symbol": "PB", "start": 210, "vol": 0.005, "color": "#5b5f66"},
    "nickel":          {"name": "Nickel",            "hi": "निकल",    "symbol": "NI", "start": 1640,"vol": 0.008, "color": "#9fa8ad"},
    "tin":             {"name": "Tin",               "hi": "टिन",     "symbol": "SN", "start": 2760,"vol": 0.007, "color": "#c7c9cc"},
}

PRECIOUS = {
    "gold": {
        "name": "Gold", "hi": "सोना", "symbol": "AU",
        "purities": {"24k": {"label": "24K (999)", "start": 7250}, "22k": {"label": "22K (916)", "start": 6644}, "18k": {"label": "18K (750)", "start": 5438}},
        "vol": 0.004, "color": "#d4af37"
    },
    "silver": {
        "name": "Silver", "hi": "चांदी", "symbol": "AG",
        "purities": {"999": {"label": "Fine (999)", "start": 92}, "925": {"label": "Sterling (925)", "start": 85}},
        "vol": 0.006, "color": "#c7c9cc"
    }
}

def walk(start, vol, days):
    """Generate a mean-reverting random walk of `days` closes ending near `start`."""
    vals = [start]
    drift = random.uniform(-0.00015, 0.00015)
    for _ in range(days - 1):
        shock = random.gauss(0, vol)
        mean_revert = (start - vals[-1]) * 0.01
        nxt = vals[-1] * (1 + drift + shock) + mean_revert
        vals.append(max(nxt, start * 0.5))
    # force the series to end exactly at `start` (today's real rate) with a smooth taper
    end_val = vals[-1]
    for i in range(days):
        t = i / (days - 1)
        vals[i] += (start - end_val) * t
    return [round(v, 2) for v in vals]

def date_series(days):
    return [(TODAY - datetime.timedelta(days=days - 1 - i)).isoformat() for i in range(days)]

dates = date_series(DAYS)

metals_out = {}
for key, m in BASE_METALS.items():
    per_kg_start = m["start"]
    history = walk(per_kg_start, m["vol"], DAYS)
    today_rate = history[-1]
    yest_rate = history[-2]
    metals_out[key] = {
        "id": key,
        "name": m["name"],
        "nameHi": m["hi"],
        "symbol": m["symbol"],
        "color": m["color"],
        "unit": "per kg",
        "rate": today_rate,
        "yesterday": yest_rate,
        "change": round(today_rate - yest_rate, 2),
        "changePct": round((today_rate - yest_rate) / yest_rate * 100, 2),
        "high52w": round(max(history), 2),
        "low52w": round(min(history), 2),
        "avg52w": round(sum(history) / len(history), 2),
        "lastUpdated": f"{TODAY.isoformat()}T00:37:00+05:30",
        "history": [{"date": d, "rate": r} for d, r in zip(dates, history)]
    }

precious_out = {}
for key, m in PRECIOUS.items():
    purities_out = {}
    for pkey, p in m["purities"].items():
        history = walk(p["start"], m["vol"], DAYS)
        today_rate = history[-1]
        yest_rate = history[-2]
        purities_out[pkey] = {
            "label": p["label"],
            "perGram": round(today_rate, 2),
            "per10Gram": round(today_rate * 10, 2),
            "perKg": round(today_rate * 1000, 2),
            "yesterday": round(yest_rate, 2),
            "change": round(today_rate - yest_rate, 2),
            "changePct": round((today_rate - yest_rate) / yest_rate * 100, 2),
            "history": [{"date": d, "rate": r} for d, r in zip(dates, history)]
        }
    precious_out[key] = {
        "id": key,
        "name": m["name"],
        "nameHi": m["hi"],
        "symbol": m["symbol"],
        "color": m["color"],
        "lastUpdated": f"{TODAY.isoformat()}T00:37:00+05:30",
        "purities": purities_out
    }

os.makedirs("/home/claude/mri/data", exist_ok=True)
with open("/home/claude/mri/data/metals.json", "w", encoding="utf-8") as f:
    json.dump({"updated": f"{TODAY.isoformat()}T00:37:00+05:30", "metals": metals_out}, f, ensure_ascii=False, indent=2)

with open("/home/claude/mri/data/goldsilver.json", "w", encoding="utf-8") as f:
    json.dump({"updated": f"{TODAY.isoformat()}T00:37:00+05:30", "precious": precious_out}, f, ensure_ascii=False, indent=2)

print("Generated data/metals.json and data/goldsilver.json")
for k, v in metals_out.items():
    print(f"  {k}: ₹{v['rate']}/kg ({v['changePct']}%)")
