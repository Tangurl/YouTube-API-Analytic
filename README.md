# 📊 YouTube Analytics & Studio Intelligence CLI Extractor

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Google Cloud APIs](https://img.shields.io/badge/Google%20Cloud-APIs%20Enabled-green.svg)](https://console.cloud.google.com/)
[![OAuth 2.0](https://img.shields.io/badge/Auth-OAuth%202.0%20Desktop-orange.svg)](https://developers.google.com/identity/protocols/oauth2)
[![Export Formats](https://img.shields.io/badge/Export-Excel%20%7C%20CSV%20%7C%20JSON%20%7C%20SQLite%20%7C%20HTML-purple.svg)](#-exported-output-files)

A professional-grade, high-performance Python CLI tool designed to extract deep video metadata, YouTube Studio private analytics, audience retention, demographics, device dimensions, traffic sources, playlist statistics, and historical trends directly from Google's official APIs:
* **YouTube Data API v3** (Public video metadata, snippets, content details, tags, topics, formats)
* **YouTube Analytics API v2** (Studio analytics, watch time, retention, subscriber splits, demographics, devices, geography, traffic)
* **YouTube Reporting API v1** (Bulk automated daily scheduled reporting jobs and report downloads)

It also generates a zero-CORS **Interactive HTML Dashboard** (`output/dashboard.html` / `dashboard.html`) powered by modern dark-mode CSS and Chart.js visualizers with granular per-video modal inspection.

---

## 🔒 Security & Privacy Notice

This application connects to private YouTube Studio analytics via Google OAuth 2.0. To protect your channel data and credentials:
* **Credentials & Tokens are Strictly Local**: Your `client_secret.json` and generated `token.json` contain sensitive OAuth keys and refresh tokens. They are excluded from version control via `.gitignore`.
* **Analytics Data is Private**: All generated reports, Excel sheets, CSVs, SQLite databases in `output/`, and the generated `dashboard.html` contain private channel metrics and are ignored by `.gitignore`.
* **Template Provided**: A sanitized template [client_secret.json.example](file:///Users/Tan/Uni/ThaiPBS/YoutubeAnalyticsAPIApp/client_secret.json.example) is provided as a reference.

---

## 🚀 Key Features

* **Complete Video Metadata & Public Stats (Data API v3)**:
  * Video Title, Description, Duration (`MM:SS`), ISO 8601 formatting, Tags, Category, Topics, Privacy status (`public`, `unlisted`, `private`), Likes, Comments, View Counts.
  * Content format classification (`VOD`, `Shorts`, `Live`), Manual caption indicator (`has_captions`), Spoken/audio language (`default_audio_language`), and metadata language (`default_language`).
* **YouTube Studio Analytics & Retention (Analytics API v2)**:
  * Watch time (minutes & hours), Average watch time (`average_watch_time_minutes` & `MM:SS`), Average retention %, Engagement rate %, Like Ratio % (`like_ratio_pct`), Subscribers gained/lost per video.
* **Watch Time from Subscribers (`subscribed_status`)**:
  * Exact watch time, views, and average view duration comparing **Subscribed vs. Non-Subscribed** viewers.
* **Content Format Breakdown (`content_types`)**:
  * Total views and watch time segmented by **VOD**, **Shorts**, and **Live Streams**.
* **Granular Audience Demographics & Geography**:
  * Viewer Gender distribution (Male, Female, User Specified) & Age Groups (`13-17`, `18-24`, `25-34`, `35-44`, `45-54`, `55-64`, `65+`).
  * Combined Age $\times$ Gender intersection matrix.
  * Country-by-country viewer breakdown with view counts, watch time %, and subscribers gained per nation.
* **Studio Discovery & Playback Dimensions**:
  * Device types (Mobile, Tablet, TV, Desktop), Operating Systems (Android, iOS, Windows, Mac), Traffic sources (Search, Suggested, External, Playlists, Notifications), Playback locations, and Daily historical timeline.
* **Channel & Playlist Performance Analytics**:
  * Playlist starts, Views per start (videos binged per session), Average session watch time, and total playlist views.
  * Option to target a specific playlist with `--playlist-id`.
* **Deep Per-Video Breakdowns (`--per-video-breakdown`)**:
  * Queries YouTube Analytics for *each individual video* to extract its specific device types, traffic sources, demographics, **subscriber watch time %, and top viewer countries**.
* **Upload Date Filtering & Early-Exit Quota Saver**:
  * Filter by upload presets (`--period this-month`, `this-year`, `last-month`, `last-year`, `last-30d`, etc.) or custom date ranges (`--uploaded-after`, `--uploaded-before`) with early-exit pagination to save 99%+ quota on massive channels.
* **YouTube Reporting API Scheduling & Downloads**:
  * Automate creation of official YouTube Reporting API daily batch jobs (`--setup-reporting-jobs`) and bulk download generated CSV reports (`--download-reports`).
* **Multi-Format Export**:
  * Exports to Multi-Tab Excel (`.xlsx`), individual CSVs, JSON records, SQLite (`.db`), and standalone interactive HTML dashboard.

---

## 🛠️ Prerequisites & Google Cloud Setup

### 1. Google Cloud Console Setup
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `YouTube-Analytics-App`).
3. Enable the following APIs under **APIs & Services $\rightarrow$ Library**:
   * **YouTube Data API v3**
   * **YouTube Analytics API**
   * **YouTube Reporting API**
4. Configure the **OAuth Consent Screen**:
   * User Type: **External**.
   * App name: e.g. `YouTube Analytics Extractor`.
   * Add your Google Account email under **Test Users**.
   * Add the following scopes:
     * `https://www.googleapis.com/auth/youtube.readonly`
     * `https://www.googleapis.com/auth/yt-analytics.readonly`
     * `https://www.googleapis.com/auth/yt-analytics-monetary.readonly` *(Optional: only required if your channel is monetized in YPP)*
     * `https://www.googleapis.com/auth/yt-analytics-reporting.readonly`
5. Create Credentials:
   * Navigate to **Credentials $\rightarrow$ Create Credentials $\rightarrow$ OAuth client ID**.
   * Application type: **Desktop App**.
   * Name: e.g. `YouTube Analytics Desktop Client`.
   * Click **Create**, then click **Download JSON**.
   * Rename the downloaded file to **`client_secret.json`** and place it in the project root directory (matching the structure in [client_secret.json.example](file:///Users/Tan/Uni/ThaiPBS/YoutubeAnalyticsAPIApp/client_secret.json.example)).

---

## 📦 Installation & Setup

```bash
# 1. Clone or extract the project directory
git clone https://github.com/Tangurl/Youtube-API-Analytics.git
cd Youtube-API-Analytics

# 2. Create and activate a Python 3.10+ virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Ensure client_secret.json is in project root
cp /path/to/downloaded/oauth_secret.json ./client_secret.json
```

---

## 💻 CLI Usage Guide

### 1. Standard Run (Channel Metadata + Studio Analytics)
```bash
python cli.py
```
*Prompts for a one-time browser OAuth login on the first run, securely caches tokens in `token.json`, and exports all metadata and Studio dimensions into `output/`.*

---

### 2. Deep Per-Video Breakdown
Extract specific device types, traffic sources, audience demographics, **subscriber watch time %**, and **top viewer countries** for every single video:
```bash
python cli.py --per-video-breakdown
```

---

### 3. Filter by Upload Date & Presets (Early-Exit Quota Saver)
For channels with hundreds or thousands of videos, date filters terminate API pagination early once older videos are encountered, saving quota:
```bash
# Relative preset periods
python cli.py --period this-month
python cli.py --period last-month
python cli.py --period this-year
python cli.py --period last-year
python cli.py --period last-7d
python cli.py --period last-30d
python cli.py --period last-90d
python cli.py --period last-365d

# Custom upload date range
python cli.py --uploaded-after 2024-01-01 --uploaded-before 2024-12-31
```

---

### 4. Target a Specific Playlist
Extract metadata and performance metrics exclusively for videos within a particular playlist:
```bash
python cli.py --playlist-id PL3lcem0Q32bNOyu3AYWmyKq7iot-SoOX-
```

---

### 5. Custom Analytics Measurement Window
Measure watch time, views, and demographic activity that occurred within a specific timeframe:
```bash
python cli.py --start-date 2024-01-01 --end-date 2024-12-31
```

---

### 6. Include Revenue / Monetization Metrics (YPP Channels)
If your channel is enrolled in the YouTube Partner Program (YPP), include estimated revenue, ad impressions, and CPM:
```bash
python cli.py --include-revenue
```

---

### 7. YouTube Reporting API (Bulk Batch Jobs)
Setup official daily bulk reporting jobs or download accumulated historical CSV reports:
```bash
# Setup daily scheduled reporting jobs
python cli.py --setup-reporting-jobs

# Download available generated CSV reports to reports/
python cli.py --download-reports
```

---

### 8. Choose Export File Formats
By default, all formats (`excel`, `csv`, `json`, `sqlite`, `html`) are exported. You can choose a specific format with `-f`:
```bash
# Multi-tab Excel workbook only
python cli.py -f excel

# CSV tables only
python cli.py -f csv

# SQLite relational database only
python cli.py -f sqlite

# JSON records only
python cli.py -f json
```

---

### 9. Multi-Channel Switching
Manage multiple YouTube channels seamlessly by using separate token files and output directories:
```bash
# Channel A
python cli.py -c client_secret.json -t token_channel_a.json -o output_channel_a

# Channel B
python cli.py -c client_secret.json -t token_channel_b.json -o output_channel_b
```

---

## 📂 Exported Output Files

When running with `-f all` (default), all tables are exported into the `output/` directory:

| Format | File Path | Contents |
| :--- | :--- | :--- |
| **Excel** | `output/youtube_<CHANNEL_ID>_full.xlsx` | Multi-tab Excel workbook containing dedicated sheets for each Studio dimension: <br> • `channel_summary`: Channel high-level metrics & subscriber totals. <br> • `playlists_summary`: Playlist starts, views per start, session watch time, and total playlist views. <br> • `videos_full_data`: Complete metadata (duration, format, captions/languages, topics, tags, privacy) + Studio performance metrics. <br> • `subscribed_status`: Watch time & views broken down by Subscribed vs Non-Subscribed viewers. <br> • `content_types`: Views and watch time broken down by Content Format (VOD, Shorts, Live Stream). <br> • `demographics_gender`: Official channel viewer gender percentage. <br> • `demographics_age`: Official channel viewer age group percentage. <br> • `demographics_age_gender`: Detailed Age $\times$ Gender intersection matrix. <br> • `device_types`: Mobile, Desktop, Tablet, TV, Game Console. <br> • `operating_systems`: Android, iOS, Windows, Mac, Linux, etc. <br> • `traffic_sources`: YouTube Search, Suggested Videos, External, Playlists, etc. <br> • `geography_countries`: Country-by-country views, watch minutes, and subscribers gained. <br> • `playback_locations`: YouTube Watch Page vs Embedded on external websites. <br> • `sharing_services`: Sharing apps (WhatsApp, Facebook, Twitter, Copy-link, etc.). <br> • `daily_timeline`: Historical day-by-day views, watch time, and subscriber growth. <br> • `video_device_breakdown` *(if `--per-video-breakdown` passed)* <br> • `video_traffic_breakdown` *(if `--per-video-breakdown` passed)* <br> • `video_demographics_breakdown` *(if `--per-video-breakdown` passed)* <br> • `video_subscribed_breakdown` *(if `--per-video-breakdown` passed)* <br> • `video_geography_breakdown` *(if `--per-video-breakdown` passed)* |
| **CSV** | `output/youtube_<ID>_<DIMENSION>.csv` | Standalone CSV files for each individual dimension table. |
| **JSON** | `output/youtube_<ID>_<DIMENSION>.json` | Structured JSON records for each dataset. |
| **SQLite** | `output/youtube_<ID>.db` | Relational SQLite database with all tables indexed and queryable via SQL. |
| **HTML** | `output/dashboard.html` *(and `dashboard.html`)* | Zero-CORS standalone interactive dashboard with Chart.js visualizers and inspection modals. |

---

## 🖥️ Interactive HTML Dashboard

The tool generates a standalone HTML file (`dashboard.html` and `output/dashboard.html`):
* **Zero External Dependencies / Zero CORS**: Simply double-click `dashboard.html` in your file browser (or open via Chrome / Safari / Edge / Firefox). It requires no local web server.
* **Modern Studio UI**: Dark theme aesthetic built with custom CSS variables and responsive typography.
* **Interactive Chart.js Visualizers**:
  * Views & Watch Time distribution by Content Type (VOD, Shorts, Live).
  * Subscribed vs. Non-Subscribed viewership comparison.
  * Age & Gender demographic pyramid.
  * Device & Operating System breakdowns.
  * Traffic Source acquisition donut charts.
  * Top viewer countries with interactive progress bars.
* **Granular Video Modal Inspector**: Click any video card or row to open a deep inspection modal displaying video retention, tags, topics, exact duration, and per-video metrics.

---

## 📁 Project Structure

```
YoutubeAnalyticsAPIApp/
├── auth.py                      # Google OAuth 2.0 flow & credential manager
├── cli.py                       # CLI argument parsing, workflow orchestrator & Rich output
├── client_secret.json.example   # Reference template for OAuth credentials (safe for Git)
├── requirements.txt             # Python dependencies
├── .gitignore                   # Comprehensive exclusions for credentials, tokens, data
├── extractors/
│   ├── __init__.py
│   ├── data_api.py              # YouTube Data API v3 (metadata, playlists, pagination)
│   ├── analytics_api.py         # YouTube Analytics API v2 (Studio dimensions & demographics)
│   └── reporting_api.py         # YouTube Reporting API v1 (bulk batch jobs & reports)
├── utils/
│   ├── __init__.py
│   ├── dashboard_generator.py   # Standalone HTML & Chart.js dashboard generator
│   ├── exporter.py              # Multi-format exporter (Excel, CSV, JSON, SQLite)
│   └── formatting.py            # Duration parsers, date helpers, number formatting
├── output/                      # [Git-ignored] Exported datasets and reports
└── reports/                     # [Git-ignored] Downloaded YouTube Reporting CSVs
```

---

## ❓ Troubleshooting & FAQs

### 1. "Google hasn't verified this app" during login
* **Cause**: Your Google Cloud project is in "Testing" mode.
* **Solution**: Click **Advanced** $\rightarrow$ **Go to YouTube Analytics Extractor (unsafe)** $\rightarrow$ **Continue**. Ensure your Google account email is added under **Test Users** on the Google Cloud OAuth Consent Screen.

### 2. "Access Not Configured" or `403 Forbidden`
* **Cause**: One of the required APIs has not been enabled in the Google Cloud Console.
* **Solution**: Ensure **YouTube Data API v3**, **YouTube Analytics API**, and **YouTube Reporting API** are enabled in [Google Cloud Console APIs & Services](https://console.cloud.google.com/apis/dashboard).

### 3. "The request is missing a valid API key or OAuth token"
* **Cause**: Invalid or expired `token.json`.
* **Solution**: Delete `token.json` and re-run `python cli.py`. It will open your browser for a fresh OAuth consent flow.

### 4. Quota Exceeded (Quota limits)
* YouTube Data API v3 provides 10,000 units per day by default.
* **Tip**: Use upload date filters (e.g. `--period this-month` or `--uploaded-after 2024-01-01`). The early-exit pagination automatically stops querying the Data API once it encounters older videos, saving over 99% of quota on large channels.

---

## 📦 How to Archive / Move to Another Machine

To transfer this project cleanly without bundling massive virtual environment or temporary cache files:

```bash
# Create a clean, lightweight zip archive (excludes venv, output, tokens, and cache)
zip -r YoutubeAnalyticsApp.zip . \
  -x "venv/*" \
  -x ".venv/*" \
  -x "output/*" \
  -x "reports/*" \
  -x "__pycache__/*" \
  -x "*/__pycache__/*" \
  -x ".DS_Store" \
  -x "token*.json" \
  -x "client_secret*.json" \
  -x "dashboard.html"
```

On the new machine:
1. Extract `YoutubeAnalyticsApp.zip`.
2. Place your `client_secret.json` in the root folder.
3. Run:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python cli.py
   ```
