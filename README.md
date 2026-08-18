# 📊 YouTube Analytics & Studio Intelligence CLI Extractor

A high-performance Python CLI tool designed to extract deep video metadata, YouTube Studio analytics, audience demographics, device types, traffic sources, playlist statistics, and historical trends directly from the official **YouTube Data API v3**, **YouTube Analytics API v2**, and **YouTube Reporting API v1**.

Includes a standalone zero-CORS **Interactive HTML Dashboard** (`dashboard.html`) featuring Chart.js visualizers and granular per-video inspection modals.

---

## 🚀 Key Features

* **Complete Video Metadata & Public Stats (Data API v3)**:
  * Video Title, Description, Duration (`MM:SS`), ISO 8601 formatting, Tags, Category, Topics, Privacy status (`public`, `unlisted`, `private`), Likes, Comments, View Counts.
  * Content format (`VOD`, `Shorts`, `Live`), Manual caption indicator (`has_captions`), Spoken/audio language (`default_audio_language`), and metadata language (`default_language`).
* **YouTube Studio Analytics & Retention (Analytics API v2)**:
  * Watch time (minutes & hours), Average watch time in minutes (`average_watch_time_minutes` & `MM:SS`), Average retention %, Engagement rate %, Like Ratio % (`like_ratio_pct`), Subscribers gained/lost per video.
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
* **Multi-Format Export**:
  * Exports to Multi-Tab Excel (`.xlsx`), individual CSVs, JSON records, SQLite (`.db`), and interactive HTML dashboard.

---

## 🛠️ Prerequisites & Google Cloud Setup

### 1. Google Cloud Console Setup
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `YouTube-Analytics-App`).
3. Enable the following APIs in **APIs & Services $\rightarrow$ Library**:
   * **YouTube Data API v3**
   * **YouTube Analytics API**
   * **YouTube Reporting API**
4. Configure the **OAuth Consent Screen**:
   * User Type: **External**.
   * Add your Google Account email under **Test Users**.
   * Add the following scopes:
     * `https://www.googleapis.com/auth/youtube.readonly`
     * `https://www.googleapis.com/auth/yt-analytics.readonly`
     * `https://www.googleapis.com/auth/yt-analytics-monetary.readonly` *(Optional: only if monetized)*
     * `https://www.googleapis.com/auth/yt-analytics-reporting.readonly`
5. Create Credentials:
   * Go to **Credentials $\rightarrow$ Create Credentials $\rightarrow$ OAuth client ID**.
   * Application type: **Desktop App**.
   * Download the JSON file, rename it to **`client_secret.json`**, and place it in the project root directory.

---

## 📦 Installation & Setup

```bash
# 1. Clone or extract the project directory
cd /path/to/YoutubeAnalyticsAPIApp

# 2. Create and activate a Python 3.10+ virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt
```

---

## 💻 CLI Usage Guide

### 1. Standard Run (Channel Metadata + Studio Analytics)
```bash
./venv/bin/python cli.py
```
*Prompts for one-time browser OAuth login on first run, saves tokens in `token.json`, and exports all metadata and Studio dimensions to `output/`.*

---

### 2. Deep Per-Video Breakdown (Devices, Traffic, Demographics, Subscribers, Countries per Video)
```bash
./venv/bin/python cli.py --per-video-breakdown
```
*Iterates through all individual videos on the channel to extract their individual device types, traffic sources, demographics, **watch time from subscribers vs non-subscribers**, and **top viewer countries**.*

---

### 3. Filter by Upload Date & Presets (Early-Exit Quota Saver)
```bash
# Preset period keywords
./venv/bin/python cli.py --period this-month
./venv/bin/python cli.py --period last-month
./venv/bin/python cli.py --period this-year
./venv/bin/python cli.py --period last-year
./venv/bin/python cli.py --period last-30d
./venv/bin/python cli.py --period last-90d
./venv/bin/python cli.py --period last-365d

# Custom upload date range
./venv/bin/python cli.py --uploaded-after 2024-01-01 --uploaded-before 2024-12-31
```

---

### 4. Target a Specific Playlist
```bash
./venv/bin/python cli.py --playlist-id PL3lcem0Q32bNOyu3AYWmyKq7iot-SoOX-
```
*Extracts videos and performance metrics specifically for videos in that playlist.*

---

### 5. Analytics Date Range (Measurement Window)
```bash
./venv/bin/python cli.py --start-date 2024-01-01 --end-date 2024-12-31
```
*Measures watch time, views, and demographics for activity that occurred in this window.*

---

### 6. Include Revenue / Monetization Metrics (YPP Channels)
```bash
./venv/bin/python cli.py --include-revenue
```

---

### 7. Multi-Channel Switching
Keep separate tokens and output folders for different channels:
```bash
# Channel A
./venv/bin/python cli.py -t token_channel_a.json -o output_channel_a

# Channel B
./venv/bin/python cli.py -t token_channel_b.json -o output_channel_b
```

---

## 📂 Exported Output Files

When running with `-f all` (default), all tables are exported into the `output/` directory:

| Format | File Path | Contents |
| :--- | :--- | :--- |
| **Excel** | `output/youtube_<CHANNEL_ID>_full.xlsx` | Multi-tab Excel file with dedicated sheets for each Studio dimension: <br> - `channel_summary`: Channel high-level metrics & subscriber totals. <br> - `playlists_summary`: Playlist starts, views per start, session watch time, and total playlist views. <br> - `videos_full_data`: Complete metadata (duration, format, captions/languages, topics, tags, privacy) + Studio performance metrics. <br> - `subscribed_status`: Watch time & views broken down by Subscribed vs Non-Subscribed viewers. <br> - `content_types`: Views and watch time broken down by Content Format (VOD, Shorts, Live Stream). <br> - `demographics_gender`: Official channel viewer gender percentage. <br> - `demographics_age`: Official channel viewer age group percentage. <br> - `demographics_age_gender`: Detailed 14-cell Age $\times$ Gender intersection matrix. <br> - `device_types`: Mobile, Desktop, Tablet, TV, Game Console. <br> - `operating_systems`: Android, iOS, Windows, Mac, Linux, etc. <br> - `traffic_sources`: YouTube Search, Suggested Videos, External, Playlists, etc. <br> - `geography_countries`: Country-by-country views, watch minutes, and subscribers gained. <br> - `playback_locations`: YouTube Watch Page vs Embedded on external websites. <br> - `sharing_services`: Sharing apps (WhatsApp, Facebook, Twitter, Copy-link, etc.). <br> - `daily_timeline`: Historical day-by-day views, watch time, and subscriber growth. <br> - `video_device_breakdown` *(if `--per-video-breakdown` passed)* <br> - `video_traffic_breakdown` *(if `--per-video-breakdown` passed)* <br> - `video_demographics_breakdown` *(if `--per-video-breakdown` passed)* <br> - `video_subscribed_breakdown` *(if `--per-video-breakdown` passed)* <br> - `video_geography_breakdown` *(if `--per-video-breakdown` passed)* |
| **CSV** | `output/youtube_<ID>_<DIMENSION>.csv` | Standalone CSV files for each table. |
| **JSON** | `output/youtube_<ID>_<DIMENSION>.json` | Structured JSON records for each dataset. |
| **SQLite** | `output/youtube_<ID>.db` | Relational SQLite database with all tables indexed. |
| **HTML** | `output/dashboard.html` *(and `dashboard.html` in root)* | Standalone interactive dashboard with Chart.js visualizers and inspection modals. |

---

## 📦 How to Move / Zip to Another Machine

To transfer the project to another computer without copying massive virtual environment or temporary cache files:

```bash
# Create a clean, lightweight zip archive (excludes venv, output, and cache)
zip -r YoutubeAnalyticsApp.zip . \
  -x "venv/*" \
  -x "output/*" \
  -x "__pycache__/*" \
  -x "*/__pycache__/*" \
  -x ".DS_Store" \
  -x "token*.json"
```

On the new machine:
1. Unzip `YoutubeAnalyticsApp.zip`.
2. Ensure `client_secret.json` is in the folder.
3. Run:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python cli.py
   ```
