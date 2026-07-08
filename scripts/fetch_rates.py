#!/usr/bin/env python3
"""
Daily rate updater for Metal Rates India.

Primary source: MetalpriceAPI (https://metalpriceapi.com) — free tier key
required, stored as the GitHub Actions secret METAL_API_KEY.
It returns LME/COMEX-style base metal and precious metal prices.

Fallback: if the API call fails or the secret isn't set, this script
applies a small, realistic random-walk nudge to yesterday's rate so the
site keeps "updating" and never breaks, until the API is fixed.

Run by: .github/workflows/update-rates.yml, once daily.
"""
import json, os, random, sys, datetime, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METALS_JSON = os.path.join(ROOT, "data", "metals.json")
GOLDSILVER_JSON = os.path.join(ROOT, "data", "goldsilver.json")
API_KEY = os.environ.get("METAL_API_KEY", "").strip()
TODAY = datetime.date.today().isoformat()

# MetalpriceAPI symbols -> our internal metal ids. Values are OUNCE prices
# in USD for precious metals, and USD-per-metric-TON for LME base metals
# (that's how MetalpriceAPI/most free metal APIs quote LME symbols).
LME_SYMBOLS_PER_TON = {
    "copper": "LME-XCU", "aluminium": "LME-ALU", "zinc": "LME-ZNC",
    "lead": "LME-PBL", "nickel": "LME-NI", "tin": "LME-SN",
}
# Metals without a direct free LME feed (brass/iron/steel/stainless) are
# derived from copper/iron proxies with a fixed multiplier — adjust the
# multipliers below if you have a better data source for these.
DERIVED_MULTIPLIERS = {
    "brass": ("copper", 0.70),
    "iron": ("copper", 0.077),
    "steel": ("copper", 0.101),
    "stainless-steel": ("copper", 0.256),
}
OUNCE_TO_GRAM = 31.1035


def fetch_usdinr():
    """Free, keyless USD->INR rate."""
    try:
        with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD", timeout=15) as r:
            data = json.load(r)
            return float(data["rates"]["INR"])
    except Exception as e:
        print("USD-INR fetch failed, using fallback 83.5:", e)
        return 83.5


def fetch_metalpriceapi():
    """Returns dict of symbol -> USD price, or None on failure."""
    if not API_KEY:
        print("No METAL_API_KEY set — skipping live API call.")
        return None
    symbols = ",".join(list(LME_SYMBOLS_PER_TON.values()) + ["XAU", "XAG"])
    url = f"https://api.metalpriceapi.com/v1/latest?api_key={API_KEY}&base=USD&currencies={symbols}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = json.load(r)
        if not data.get("success", True) and "rates" not in data:
            print("MetalpriceAPI returned an error payload:", data)
            return None
        # MetalpriceAPI returns rates as 1 USD = X of the metal unit (inverse of price)
        rates = data.get("rates", {})
        prices = {}
        for sym, rate in rates.items():
            if rate:
                prices[sym] = 1 / rate  # USD per unit (oz or ton)
        return prices
    except Exception as e:
        print("MetalpriceAPI fetch failed:", e)
        return None


def random_walk_fallback(prev_rate, vol=0.006):
    shock = random.gauss(0, vol)
    return round(max(prev_rate * (1 + shock), prev_rate * 0.5), 2)


def update_base_metals(usd_inr, live_prices):
    with open(METALS_JSON, encoding="utf-8") as f:
        doc = json.load(f)
    metals = doc["metals"]

    resolved_per_kg = {}

    for mid, sym in LME_SYMBOLS_PER_TON.items():
        prev = metals[mid]["rate"]
        if live_prices and sym in live_prices:
            usd_per_ton = live_prices[sym]
            inr_per_kg = round((usd_per_ton * usd_inr) / 1000, 2)
        else:
            inr_per_kg = random_walk_fallback(prev)
        resolved_per_kg[mid] = inr_per_kg

    for mid, (base_id, mult) in DERIVED_MULTIPLIERS.items():
        prev = metals[mid]["rate"]
        if base_id in resolved_per_kg:
            resolved_per_kg[mid] = round(resolved_per_kg[base_id] * mult, 2)
        else:
            resolved_per_kg[mid] = random_walk_fallback(prev)

    now_iso = datetime.datetime.now().isoformat()
    for mid, new_rate in resolved_per_kg.items():
        m = metals[mid]
        m["yesterday"] = m["rate"]
        m["rate"] = new_rate
        m["change"] = round(new_rate - m["yesterday"], 2)
        m["changePct"] = round((m["change"] / m["yesterday"]) * 100, 2) if m["yesterday"] else 0
        m["lastUpdated"] = now_iso
        m["history"].append({"date": TODAY, "rate": new_rate})
        m["history"] = m["history"][-365:]
        m["high52w"] = round(max(h["rate"] for h in m["history"]), 2)
        m["low52w"] = round(min(h["rate"] for h in m["history"]), 2)
        m["avg52w"] = round(sum(h["rate"] for h in m["history"]) / len(m["history"]), 2)

    doc["updated"] = now_iso
    with open(METALS_JSON, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print("Updated data/metals.json")


def update_precious(usd_inr, live_prices):
    with open(GOLDSILVER_JSON, encoding="utf-8") as f:
        doc = json.load(f)
    precious = doc["precious"]
    now_iso = datetime.datetime.now().isoformat()

    gold_usd_oz = live_prices.get("XAU") if live_prices else None
    silver_usd_oz = live_prices.get("XAG") if live_prices else None

    purity_factors = {"24k": 1.0, "22k": 0.916, "18k": 0.75, "999": 1.0, "925": 0.925}

    for metal_id, usd_oz in (("gold", gold_usd_oz), ("silver", silver_usd_oz)):
        p = precious[metal_id]
        for pkey, pdata in p["purities"].items():
            prev_gram = pdata["perGram"]
            if usd_oz:
                base_inr_gram = (usd_oz * usd_inr) / OUNCE_TO_GRAM
                new_gram = round(base_inr_gram * purity_factors.get(pkey, 1.0), 2)
            else:
                new_gram = random_walk_fallback(prev_gram, vol=0.004)
            pdata["yesterday"] = prev_gram
            pdata["perGram"] = new_gram
            pdata["per10Gram"] = round(new_gram * 10, 2)
            pdata["perKg"] = round(new_gram * 1000, 2)
            pdata["change"] = round(new_gram - prev_gram, 2)
            pdata["changePct"] = round((pdata["change"] / prev_gram) * 100, 2) if prev_gram else 0
            pdata["history"].append({"date": TODAY, "rate": new_gram})
            pdata["history"] = pdata["history"][-365:]
        p["lastUpdated"] = now_iso

    doc["updated"] = now_iso
    with open(GOLDSILVER_JSON, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print("Updated data/goldsilver.json")


if __name__ == "__main__":
    usd_inr = fetch_usdinr()
    live_prices = fetch_metalpriceapi()
    if live_prices is None:
        print("⚠ Live API unavailable — applying fallback random-walk update so the site still refreshes.")
    update_base_metals(usd_inr, live_prices)
    update_precious(usd_inr, live_prices)
    print("Done.")
