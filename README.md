# Metal Rates India

India's daily-updated reference for base and precious metal prices — built with plain HTML/CSS/JS, Chart.js, and a GitHub Actions data pipeline. No backend server required; runs entirely on GitHub Pages.

## 🚀 Deploy in 5 minutes

1. Push this folder's contents to the root of your GitHub repo (e.g. `MetalRatesIndia`).
2. In **Settings → Pages**, set the source to the `main` branch, `/ (root)` folder.
3. Your site goes live at `https://<your-username>.github.io/MetalRatesIndia/`.
4. Update every `https://akhairkar.github.io/MetalRatesIndia/` reference in the HTML/JSON/sitemap files (canonical tags, `sitemap.xml`, `robots.txt`) if your username or repo name is different.

That's it — the site works immediately with the seeded 365-day sample data in `/data`.

## 🔁 Making rates update automatically (no manual editing)

This is handled by `.github/workflows/update-rates.yml`, which runs `scripts/fetch_rates.py` once a day and commits the refreshed JSON straight to your repo.

**To turn on real live prices:**

1. Get a free API key from [MetalpriceAPI](https://metalpriceapi.com) (covers LME base metals + gold/silver). Free tier is enough for one call/day.
2. In your GitHub repo, go to **Settings → Secrets and variables → Actions → New repository secret**.
   - Name: `METAL_API_KEY`
   - Value: *(your API key)*
3. That's it. The workflow runs daily at 06:07 AM IST, or trigger it manually anytime from the **Actions** tab → "Update Metal Rates" → **Run workflow**.

**If you don't add a key:** the script still runs daily and applies a small, realistic random-walk adjustment to yesterday's rate, so the site never looks stale or broken — swap in a real key whenever you're ready.

**Want a different data source?** Edit `scripts/fetch_rates.py` — it's a single self-contained script. Any API that returns USD/ton (base metals) or USD/oz (gold/silver) can be dropped in; see the comments in `fetch_metalpriceapi()`.

## 🗂 Project structure

```
index.html                    Homepage
pages/                        One SEO page per metal + gold-silver + legal pages
data/metals.json              Base metals: current rate + 365-day history
data/goldsilver.json          Gold & Silver: 24K/22K/18K and 999/925 purities
css/styles.css                Full design system
js/script.js                  App logic (rendering, search, theme, PWA)
js/charts.js                  Chart.js sparkline + full-chart helpers
scripts/fetch_rates.py        Daily live-rate fetcher (run by GitHub Actions)
scripts/gen_data.py           One-time seed data generator (already run once)
scripts/generate_pages.py     Regenerates the 10 metal pages from the template
scripts/metal_template.html   Shared template used by generate_pages.py
.github/workflows/update-rates.yml   Daily automation
manifest.json / service-worker.js / offline.html   PWA support
admin.html                    Backup manual-override panel (client-side only)
robots.txt / sitemap.xml      SEO
```

## ✏️ Adding a new metal

1. Add an entry to `data/metals.json` (`metals.<id>`) following the existing shape, with at least 30 days of `history`.
2. Add a `GRADES["<id>"]` entry in `scripts/generate_pages.py`.
3. Run `python3 scripts/generate_pages.py` to regenerate `pages/<id>-rate-today.html`.
4. Add the metal to `LME_SYMBOLS_PER_TON` or `DERIVED_MULTIPLIERS` in `scripts/fetch_rates.py` so it keeps updating automatically.
5. Add its URL to `sitemap.xml`.

## 🔐 Admin panel

`admin.html` is a lightweight, client-side-only backup for manual overrides — GitHub Pages has no server, so it can't write to your repo directly. It generates an updated `metals.json` you copy and commit yourself. Change the hardcoded password in the `<script>` block before relying on it for anything sensitive — this is meant as an emergency fallback, not a real CMS.

## 📱 PWA

The site is installable (`manifest.json` + `service-worker.js`), caches the shell for offline use, and shows `offline.html` when there's no connection and no cached page available.

## ⚠️ Note on rate accuracy

Prices shown are indicative reference rates converted from international benchmarks, not official MCX/LME/bullion-association quotes. See `pages/disclaimer.html`.
