import os
import json

def generate_html_dashboard(
    channel_summary_path: str,
    videos_data_path: str,
    device_types_path: str,
    traffic_sources_path: str,
    operating_systems_path: str,
    geography_path: str,
    playback_locations_path: str,
    daily_timeline_path: str,
    video_device_path: str,
    video_traffic_path: str,
    output_html_path: str,
    playlists_path: str = "",
    demographics_path: str = "",
    video_demographics_path: str = "",
    gender_path: str = "",
    age_path: str = "",
    subscribed_status_path: str = "",
    content_types_path: str = "",
    video_subscribed_path: str = "",
    video_geography_path: str = ""
):
    """
    Generates a modern, standalone HTML dashboard with embedded JSON data.
    Includes Studio analytics, audience demographics, subscriber watch time %,
    content formats (Shorts/VOD/Live), subtitles & language tracking, country geography,
    and granular per-video inspection modals.
    """
    def load_json(path, default):
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    channel_data = load_json(channel_summary_path, [{}])
    channel = channel_data[0] if channel_data else {}
    videos = load_json(videos_data_path, [])
    playlists = load_json(playlists_path, [])
    demographics_data = load_json(demographics_path, [])
    video_demographics = load_json(video_demographics_path, [])
    gender_data = load_json(gender_path, [])
    age_data = load_json(age_path, [])
    subscribed_status = load_json(subscribed_status_path, [])
    content_types = load_json(content_types_path, [])
    devices = load_json(device_types_path, [])
    traffic = load_json(traffic_sources_path, [])
    os_data = load_json(operating_systems_path, [])
    geography = load_json(geography_path, [])
    playback = load_json(playback_locations_path, [])
    daily = load_json(daily_timeline_path, [])
    video_devices = load_json(video_device_path, [])
    video_traffic = load_json(video_traffic_path, [])
    video_subscribed = load_json(video_subscribed_path, [])
    video_geography = load_json(video_geography_path, [])

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{channel.get('title', 'YouTube Channel')} - Studio Analytics Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --bg-primary: #0a0e17;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.75);
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-red: #FF0033;
            --accent-gradient: linear-gradient(135deg, #FF0033 0%, #FF6B4A 100%);
            --accent-cyan: #00F2FE;
            --accent-purple: #7928CA;
            --text-primary: #F9FAFB;
            --text-secondary: #9CA3AF;
            --text-muted: #6B7280;
            --success: #10B981;
            --warning: #F59E0B;
            --info: #3B82F6;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }}

        h1, h2, h3, h4, .font-heading {{
            font-family: 'Outfit', sans-serif;
        }}

        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 24px;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(255, 0, 51, 0.07) 0%, transparent 35%),
                radial-gradient(circle at 90% 80%, rgba(0, 242, 254, 0.05) 0%, transparent 35%);
            background-attachment: fixed;
        }}

        .container {{
            max-width: 1440px;
            margin: 0 auto;
        }}

        /* Header */
        .header-card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }}

        .channel-info {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        .channel-avatar {{
            width: 64px;
            height: 64px;
            border-radius: 50%;
            background: var(--accent-gradient);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: 700;
            color: #fff;
            box-shadow: 0 4px 14px rgba(255, 0, 51, 0.35);
        }}

        .channel-details h1 {{
            font-size: 24px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-color);
        }}

        .badge-red {{
            background: rgba(255, 0, 51, 0.15);
            color: #FF6B4A;
            border-color: rgba(255, 0, 51, 0.3);
        }}

        .badge-success {{
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border-color: rgba(16, 185, 129, 0.3);
        }}

        .badge-info {{
            background: rgba(59, 130, 246, 0.15);
            color: #60A5FA;
            border-color: rgba(59, 130, 246, 0.3);
        }}

        .badge-purple {{
            background: rgba(121, 40, 202, 0.15);
            color: #A855F7;
            border-color: rgba(121, 40, 202, 0.3);
        }}

        /* KPI Metric Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, border-color 0.2s;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.18);
        }}

        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--card-accent, var(--accent-gradient));
        }}

        .kpi-title {{
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 26px;
            font-weight: 700;
            font-family: 'Outfit', sans-serif;
            color: var(--text-primary);
            line-height: 1.1;
            margin-bottom: 4px;
        }}

        .kpi-subtext {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        /* Navigation Tabs */
        .nav-tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 12px;
            overflow-x: auto;
        }}

        .tab-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-secondary);
            padding: 10px 18px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }}

        .tab-btn:hover {{
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.04);
        }}

        .tab-btn.active {{
            background: var(--accent-gradient);
            color: #fff;
            box-shadow: 0 4px 12px rgba(255, 0, 51, 0.25);
        }}

        /* Tab Panes */
        .tab-pane {{
            display: none;
        }}

        .tab-pane.active {{
            display: block;
        }}

        /* Grids & Cards */
        .charts-grid-3 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .charts-grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}

        .card-title {{
            font-size: 17px;
            font-weight: 700;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .chart-container {{
            position: relative;
            height: 280px;
            width: 100%;
        }}

        /* Table */
        .table-responsive {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            text-align: left;
        }}

        thead th {{
            background: rgba(255, 255, 255, 0.04);
            color: var(--text-secondary);
            font-weight: 600;
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }}

        tbody td {{
            padding: 14px 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            color: var(--text-primary);
            vertical-align: middle;
        }}

        tbody tr:hover {{
            background: rgba(255, 255, 255, 0.025);
        }}

        .video-cell {{
            display: flex;
            align-items: center;
            gap: 14px;
            min-width: 280px;
        }}

        .video-thumb {{
            width: 90px;
            height: 50px;
            border-radius: 8px;
            object-fit: cover;
            background: #1f2937;
            flex-shrink: 0;
        }}

        .video-meta h4 {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1.3;
            margin-bottom: 4px;
        }}

        .video-meta a {{
            color: inherit;
            text-decoration: none;
            transition: color 0.2s;
        }}

        .video-meta a:hover {{
            color: #FF6B4A;
        }}

        .video-sub {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .btn-inspect {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .btn-inspect:hover {{
            background: var(--accent-gradient);
            border-color: transparent;
        }}

        .search-bar {{
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }}

        .search-input {{
            flex: 1;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 10px 16px;
            color: #fff;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }}

        .search-input:focus {{
            border-color: #FF0033;
        }}

        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(8px);
            z-index: 999;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}

        .modal.active {{
            display: flex;
        }}

        .modal-content {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            max-width: 900px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            padding: 32px;
            position: relative;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
        }}

        .modal-close {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-color);
            color: #fff;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }}

        .modal-close:hover {{
            background: #FF0033;
            border-color: transparent;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Channel Header -->
        <header class="header-card">
            <div class="channel-info">
                <div class="channel-avatar">{channel.get('title', 'Y')[0]}</div>
                <div class="channel-details">
                    <h1>
                        {channel.get('title', 'Channel Analytics')}
                        <span class="badge badge-red">{channel.get('custom_url', '')}</span>
                    </h1>
                    <p style="color: var(--text-secondary); font-size: 14px; margin-top: 4px;">
                        Channel ID: <code>{channel.get('channel_id', '')}</code> • Created: {channel.get('published_at', '')[:10]}
                    </p>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 8px;">
                <span class="badge badge-success">● Connected to YouTube Analytics API</span>
                <span class="badge" style="background: rgba(0, 242, 254, 0.1); color: #00F2FE; border-color: rgba(0, 242, 254, 0.3);">
                    ⚡ Data Freshness: <span id="freshnessTimestamp">--</span>
                </span>
            </div>
        </header>

        <!-- KPI Metrics Grid -->
        <div class="kpi-grid">
            <div class="kpi-card" style="--card-accent: linear-gradient(135deg, #FF0033, #FF6B4A);">
                <div class="kpi-title">Total Channel Views</div>
                <div class="kpi-value" id="kpi-views">0</div>
                <div class="kpi-subtext">Lifetime Public & Unlisted Views</div>
            </div>
            <div class="kpi-card" style="--card-accent: linear-gradient(135deg, #00F2FE, #4FACFE);">
                <div class="kpi-title">Total Watch Time</div>
                <div class="kpi-value" id="kpi-watch-hours">0 hrs</div>
                <div class="kpi-subtext" id="kpi-watch-mins">0 mins</div>
            </div>
            <div class="kpi-card" style="--card-accent: linear-gradient(135deg, #10B981, #34D399);">
                <div class="kpi-title">Subscribers</div>
                <div class="kpi-value">{channel.get('subscribers', 0):,}</div>
                <div class="kpi-subtext">Channel Subscriber Count</div>
            </div>
            <div class="kpi-card" style="--card-accent: linear-gradient(135deg, #EC4899, #F43F5E);">
                <div class="kpi-title">Audience Gender</div>
                <div class="kpi-value" id="kpi-gender">--</div>
                <div class="kpi-subtext" id="kpi-gender-sub">Direct Channel Demographics</div>
            </div>
            <div class="kpi-card" style="--card-accent: linear-gradient(135deg, #7928CA, #B800FF);">
                <div class="kpi-title">Subscriber Watch Time</div>
                <div class="kpi-value" id="kpi-sub-status">--</div>
                <div class="kpi-subtext" id="kpi-sub-status-sub">Subscribed vs Non-Subscribed</div>
            </div>
            <div class="kpi-card" style="--card-accent: linear-gradient(135deg, #F59E0B, #FBBF24);">
                <div class="kpi-title">Avg. Audience Retention</div>
                <div class="kpi-value" id="kpi-avg-retention">0%</div>
                <div class="kpi-subtext">Across All Video Uploads</div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <nav class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('tab-overview')">📊 Overview & Studio</button>
            <button class="tab-btn" onclick="switchTab('tab-videos')">🎬 Videos Performance ({len(videos)})</button>
            <button class="tab-btn" onclick="switchTab('tab-playlists')">📑 Playlists ({len(playlists)})</button>
            <button class="tab-btn" onclick="switchTab('tab-demographics')">👥 Demographics & Subscribers</button>
            <button class="tab-btn" onclick="switchTab('tab-geography')">🌍 Geography & Countries ({len(geography)})</button>
            <button class="tab-btn" onclick="switchTab('tab-traffic')">🚀 Traffic Sources</button>
            <button class="tab-btn" onclick="switchTab('tab-devices')">📱 Devices & OS</button>
            <button class="tab-btn" onclick="switchTab('tab-timeline')">📈 Daily Timeline Trend</button>
        </nav>

        <!-- TAB 1: OVERVIEW -->
        <section id="tab-overview" class="tab-pane active">
            <div class="charts-grid-3">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">👥 Viewer Gender Share</div>
                        <span class="badge">Demographics</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="overviewGenderChart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">🔔 Watch Time from Subscribers</div>
                        <span class="badge badge-purple">Subscribed Status</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="overviewSubscribedChart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">🎞️ Content Format Breakdown</div>
                        <span class="badge badge-info">Format</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="overviewContentTypeChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="charts-grid-3">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">📱 Device Types</div>
                        <span class="badge">Views</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="deviceChart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">🚀 Top Traffic Sources</div>
                        <span class="badge">Discovery</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="trafficBarChart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">🌍 Top Geography (Countries)</div>
                        <span class="badge">Location</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="geoChart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 2: VIDEOS TABLE -->
        <section id="tab-videos" class="tab-pane">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">🎬 All Channel Videos & Analytics</div>
                </div>
                <div class="search-bar">
                    <input type="text" id="videoSearchInput" class="search-input" placeholder="🔍 Search video title, ID, topics, or language..." oninput="filterVideos()">
                </div>
                <div class="table-responsive">
                    <table id="videosTable">
                        <thead>
                            <tr>
                                <th>Video</th>
                                <th>Format</th>
                                <th>Subtitles / CC</th>
                                <th>Published</th>
                                <th>Duration</th>
                                <th>Views</th>
                                <th>Watch Time</th>
                                <th>Retention %</th>
                                <th>Like Ratio</th>
                                <th>Engagement</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="videosTableBody"></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB: PLAYLISTS PERFORMANCE -->
        <section id="tab-playlists" class="tab-pane">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">📑 Channel Playlists & Viewer Engagement</div>
                    <span class="badge badge-success">Playlists Analytics</span>
                </div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Playlist Title</th>
                                <th>Items</th>
                                <th>Status</th>
                                <th>Playlist Starts</th>
                                <th>Views / Start</th>
                                <th>Avg Time in Playlist</th>
                                <th>Watch Time (Mins)</th>
                            </tr>
                        </thead>
                        <tbody id="playlistsTableBody"></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 3: AUDIENCE DEMOGRAPHICS & SUBSCRIBERS -->
        <section id="tab-demographics" class="tab-pane">
            <!-- Subscriber vs Non-Subscriber Deep Dive -->
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-header">
                    <div class="card-title">🔔 Watch Time & Views by Subscriber Status</div>
                    <span class="badge badge-purple">YouTube Studio Core Metric</span>
                </div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Subscription Status</th>
                                <th>Views</th>
                                <th>Watch Time (Mins)</th>
                                <th>% of Total Watch Time</th>
                                <th>Avg. View Duration</th>
                            </tr>
                        </thead>
                        <tbody id="subscribedTableBody"></tbody>
                    </table>
                </div>
            </div>

            <div class="charts-grid-2">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">👥 Viewer Gender Distribution</div>
                        <span class="badge badge-success">Demographics Breakdown</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="genderDetailedChart"></canvas>
                    </div>
                    <div class="table-responsive" style="margin-top: 20px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>Gender</th>
                                    <th>Viewer Percentage</th>
                                </tr>
                            </thead>
                            <tbody id="genderTableBody"></tbody>
                        </table>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">🎂 Viewer Age Group Distribution</div>
                        <span class="badge badge-success">Demographics Breakdown</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="ageDetailedChart"></canvas>
                    </div>
                    <div class="table-responsive" style="margin-top: 20px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>Age Group</th>
                                    <th>Viewer Percentage</th>
                                </tr>
                            </thead>
                            <tbody id="ageTableBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Granular Matrix Table -->
            <div class="card" style="margin-top: 24px;">
                <div class="card-header">
                    <div class="card-title">📊 Granular Age × Gender Demographics Matrix</div>
                    <span class="badge">YouTube Studio Advanced View</span>
                </div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Age Group</th>
                                <th>Gender</th>
                                <th>Viewer Percentage</th>
                            </tr>
                        </thead>
                        <tbody id="matrixTableBody"></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 4: GEOGRAPHY & COUNTRIES -->
        <section id="tab-geography" class="tab-pane">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">🌍 Top Audience Countries & Regions</div>
                    <span class="badge badge-info">Geography Analytics</span>
                </div>
                <div class="chart-container" style="height: 320px; margin-bottom: 24px;">
                    <canvas id="geoDetailedChart"></canvas>
                </div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Country Code</th>
                                <th>Views</th>
                                <th>Watch Time (Mins)</th>
                                <th>% of Total Views</th>
                                <th>Avg View Duration</th>
                                <th>Subscribers Gained</th>
                            </tr>
                        </thead>
                        <tbody id="geographyTableBody"></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 5: TRAFFIC SOURCES -->
        <section id="tab-traffic" class="tab-pane">
            <div class="charts-grid-2">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Traffic Sources Distribution</div>
                    </div>
                    <div class="chart-container">
                        <canvas id="trafficPieChart"></canvas>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Traffic Details Table</div>
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>Traffic Source</th>
                                    <th>Views</th>
                                    <th>Watch Mins</th>
                                    <th>% of Total Views</th>
                                </tr>
                            </thead>
                            <tbody id="trafficTableBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 6: DEVICES & OS -->
        <section id="tab-devices" class="tab-pane">
            <div class="charts-grid-2">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Device Breakdown</div>
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>Device Type</th>
                                    <th>Views</th>
                                    <th>Watch Minutes</th>
                                </tr>
                            </thead>
                            <tbody id="devicesTableBody"></tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Operating System Breakdown</div>
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>Operating System</th>
                                    <th>Views</th>
                                    <th>Watch Minutes</th>
                                </tr>
                            </thead>
                            <tbody id="osTableBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 7: DAILY TIMELINE -->
        <section id="tab-timeline" class="tab-pane">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">📈 Daily Views & Watch Time Evolution</div>
                    <span class="badge">Channel History</span>
                </div>
                <div class="chart-container" style="height: 420px;">
                    <canvas id="timelineChart"></canvas>
                </div>
            </div>
        </section>
    </div>

    <!-- Modal for Video Breakdown -->
    <div id="videoModal" class="modal">
        <div class="modal-content">
            <button class="modal-close" onclick="closeModal()">✕</button>
            <div id="modalBody"></div>
        </div>
    </div>

    <!-- Embedded Datasets -->
    <script>
        const rawData = {{
            channel: {json.dumps(channel, ensure_ascii=False)},
            videos: {json.dumps(videos, ensure_ascii=False)},
            playlists: {json.dumps(playlists, ensure_ascii=False)},
            demographics: {json.dumps(demographics_data, ensure_ascii=False)},
            videoDemographics: {json.dumps(video_demographics, ensure_ascii=False)},
            gender: {json.dumps(gender_data, ensure_ascii=False)},
            age: {json.dumps(age_data, ensure_ascii=False)},
            subscribedStatus: {json.dumps(subscribed_status, ensure_ascii=False)},
            contentTypes: {json.dumps(content_types, ensure_ascii=False)},
            devices: {json.dumps(devices, ensure_ascii=False)},
            traffic: {json.dumps(traffic, ensure_ascii=False)},
            operatingSystems: {json.dumps(os_data, ensure_ascii=False)},
            geography: {json.dumps(geography, ensure_ascii=False)},
            playback: {json.dumps(playback, ensure_ascii=False)},
            daily: {json.dumps(daily, ensure_ascii=False)},
            videoDevices: {json.dumps(video_devices, ensure_ascii=False)},
            videoTraffic: {json.dumps(video_traffic, ensure_ascii=False)},
            videoSubscribed: {json.dumps(video_subscribed, ensure_ascii=False)},
            videoGeography: {json.dumps(video_geography, ensure_ascii=False)}
        }};

        // Compute Demographics: Prioritize direct single-dimension stats; fallback to normalized matrix
        function computeDemographics() {{
            let genderList = (rawData.gender && rawData.gender.length) ? rawData.gender : [];
            let ageList = (rawData.age && rawData.age.length) ? rawData.age : [];
            const demoList = (rawData.demographics && rawData.demographics.length) ? rawData.demographics : [];

            if (!genderList.length && demoList.length) {{
                const genderTotals = {{}};
                let totalGenderPct = 0;
                demoList.forEach(d => {{
                    const g = d.gender ? d.gender.toLowerCase() : 'other';
                    const pct = parseFloat(d.viewerPercentage) || 0;
                    genderTotals[g] = (genderTotals[g] || 0) + pct;
                    totalGenderPct += pct;
                }});

                genderList = Object.keys(genderTotals).map(k => ({{
                    gender: k,
                    viewerPercentage: totalGenderPct > 0 ? parseFloat(((genderTotals[k] / totalGenderPct) * 100).toFixed(1)) : parseFloat(genderTotals[k].toFixed(1))
                }}));
            }}

            if (!ageList.length && demoList.length) {{
                const ageTotals = {{}};
                let totalAgePct = 0;
                demoList.forEach(d => {{
                    const a = d.ageGroup || 'unknown';
                    const pct = parseFloat(d.viewerPercentage) || 0;
                    ageTotals[a] = (ageTotals[a] || 0) + pct;
                    totalAgePct += pct;
                }});

                ageList = Object.keys(ageTotals).map(k => ({{
                    ageGroup: k,
                    viewerPercentage: totalAgePct > 0 ? parseFloat(((ageTotals[k] / totalAgePct) * 100).toFixed(1)) : parseFloat(ageTotals[k].toFixed(1))
                }}));
            }}

            return {{
                gender: genderList,
                age: ageList,
                matrix: demoList
            }};
        }}

        const computedDemo = computeDemographics();

        function formatGenderName(g) {{
            if (!g) return '-';
            const lower = g.toLowerCase();
            if (lower.includes('user') || lower.includes('specified') || lower === 'other') return 'User Specified / Other';
            return lower.charAt(0).toUpperCase() + lower.slice(1);
        }}

        function formatLocalDateTime(isoStr, dateOnly = false) {{
            if (!isoStr) return '-';
            try {{
                const d = new Date(isoStr);
                if (isNaN(d.getTime())) return isoStr;
                if (dateOnly) {{
                    return d.toLocaleDateString(undefined, {{ year: 'numeric', month: 'short', day: 'numeric' }});
                }}
                return d.toLocaleString(undefined, {{ year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }});
            }} catch {{
                return isoStr;
            }}
        }}

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            const target = document.getElementById(tabId);
            if (target) target.classList.add('active');
            if (event && event.currentTarget) event.currentTarget.classList.add('active');

            setTimeout(() => {{
                window.dispatchEvent(new Event('resize'));
                if (window.chartInstances) {{
                    window.chartInstances.forEach(c => {{
                        if (c && typeof c.resize === 'function') c.resize();
                    }});
                }}
            }}, 50);
        }}

        function initDashboard() {{
            const totalViews = rawData.videos.reduce((sum, v) => sum + (parseInt(v.views) || 0), 0);
            const totalWatchMins = rawData.videos.reduce((sum, v) => sum + (parseInt(v.estimatedMinutesWatched) || 0), 0);
            const totalWatchHours = (totalWatchMins / 60).toFixed(1);
            
            const retentionValues = rawData.videos.filter(v => v.averageViewPercentage > 0).map(v => parseFloat(v.averageViewPercentage));
            const avgRetention = retentionValues.length ? (retentionValues.reduce((a, b) => a + b, 0) / retentionValues.length).toFixed(1) : "0.0";

            document.getElementById('kpi-views').innerText = Number(totalViews).toLocaleString();
            document.getElementById('kpi-watch-hours').innerText = Number(totalWatchHours).toLocaleString() + " hrs";
            document.getElementById('kpi-watch-mins').innerText = Number(totalWatchMins).toLocaleString() + " mins total";
            document.getElementById('kpi-avg-retention').innerText = avgRetention + "%";

            // Data Freshness
            const lastSync = rawData.channel.last_updated_at || rawData.channel.published_at;
            const freshEl = document.getElementById('freshnessTimestamp');
            if (freshEl) freshEl.innerText = formatLocalDateTime(lastSync);

            // Gender KPI
            if (computedDemo.gender && computedDemo.gender.length) {{
                const maleObj = computedDemo.gender.find(g => g.gender === 'male');
                const femaleObj = computedDemo.gender.find(g => g.gender === 'female');
                if (maleObj && femaleObj) {{
                    document.getElementById('kpi-gender').innerText = `M ${{maleObj.viewerPercentage}}% / F ${{femaleObj.viewerPercentage}}%`;
                }} else if (maleObj) {{
                    document.getElementById('kpi-gender').innerText = `Male ${{maleObj.viewerPercentage}}%`;
                }}
            }}

            // Subscribed Status KPI
            if (rawData.subscribedStatus && rawData.subscribedStatus.length) {{
                const totalSubMins = rawData.subscribedStatus.reduce((acc, s) => acc + (parseFloat(s.estimatedMinutesWatched) || 0), 0);
                const subItem = rawData.subscribedStatus.find(s => s.subscribedStatus === 'SUBSCRIBED');
                if (subItem && totalSubMins > 0) {{
                    const subPct = ((subItem.estimatedMinutesWatched / totalSubMins) * 100).toFixed(1);
                    document.getElementById('kpi-sub-status').innerText = `${{subPct}}% Subscribed`;
                }}
            }}

            renderVideosTable(rawData.videos);
            renderPlaylistsTable();
            renderCharts();
            renderTables();
        }}

        function renderVideosTable(videoList) {{
            const tbody = document.getElementById('videosTableBody');
            tbody.innerHTML = '';

            videoList.forEach(v => {{
                const tr = document.createElement('tr');
                const thumbUrl = `https://img.youtube.com/vi/${{v.video_id}}/mqdefault.jpg`;
                const privacyClass = v.privacy_status === 'public' ? 'badge-success' : 'badge';

                const formatClass = v.content_format === 'Shorts' ? 'badge-red' : (v.content_format === 'Live' ? 'badge-info' : 'badge');
                const ccBadge = v.has_captions 
                    ? `<span class="badge badge-success">CC: ${{v.default_language || 'Yes'}}</span>` 
                    : `<span class="badge" style="color: var(--text-muted);">None</span>`;

                const avgWatchFormatted = v.average_watch_time_formatted || (v.averageViewDuration ? (Math.floor(v.averageViewDuration/60)).toString().padStart(2, '0') + ':' + Math.round(v.averageViewDuration%60).toString().padStart(2, '0') : '00:00');
                const avgWatchMins = v.average_watch_time_minutes || (v.averageViewDuration ? (v.averageViewDuration / 60).toFixed(2) : 0);

                tr.innerHTML = `
                    <td>
                        <div class="video-cell">
                            <img src="${{thumbUrl}}" class="video-thumb" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'90\\' height=\\'50\\' fill=\\'%23222\\'><rect width=\\'100%\\' height=\\'100%\\'/></svg>'">
                            <div class="video-meta">
                                <h4><a href="https://www.youtube.com/watch?v=${{v.video_id}}" target="_blank">${{v.title || 'Untitled Video'}}</a></h4>
                                <div class="video-sub">ID: ${{v.video_id}} • ${{v.topics || 'No topics'}}${{v.last_updated_at ? ' • 🔄 Synced: ' + formatLocalDateTime(v.last_updated_at) : ''}}</div>
                            </div>
                        </div>
                    </td>
                    <td><span class="badge ${{formatClass}}">${{v.content_format || 'VOD'}}</span></td>
                    <td>${{ccBadge}}</td>
                    <td><strong>${{formatLocalDateTime(v.published_at, true)}}</strong></td>
                    <td><span class="badge">${{v.duration_formatted || '00:00'}}</span></td>
                    <td><strong>${{Number(v.views || 0).toLocaleString()}}</strong></td>
                    <td>${{v.estimated_watch_hours || 0}} hrs</td>
                    <td>
                        <span class="badge badge-red">${{v.averageViewPercentage || 0}}%</span>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">⏱️ ${{avgWatchFormatted}} (${{avgWatchMins}}m)</div>
                    </td>
                    <td><span class="badge badge-success">👍 ${{v.like_ratio_pct || 100}}%</span></td>
                    <td>${{v.engagement_rate_pct || 0}}%</td>
                    <td><span class="badge ${{privacyClass}}">${{v.privacy_status || 'unknown'}}</span></td>
                    <td>
                        <button class="btn-inspect" onclick="inspectVideo('${{v.video_id}}')">🔍 Breakdown</button>
                    </td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function renderPlaylistsTable() {{
            const pBody = document.getElementById('playlistsTableBody');
            if (rawData.playlists && rawData.playlists.length) {{
                pBody.innerHTML = rawData.playlists.map(p => `
                    <tr>
                        <td>
                            <strong><a href="https://www.youtube.com/playlist?list=${{p.playlist_id}}" target="_blank" style="color: inherit; text-decoration: none;">${{p.title || 'Untitled Playlist'}}</a></strong>
                            <div style="font-size: 12px; color: var(--text-muted);">ID: ${{p.playlist_id}}</div>
                        </td>
                        <td><span class="badge">${{p.item_count || 0}} videos</span></td>
                        <td><span class="badge ${{p.privacy_status === 'public' ? 'badge-success' : 'badge'}}">${{p.privacy_status || 'unlisted'}}</span></td>
                        <td><strong style="color: #00F2FE;">${{Number(p.playlistStarts || 0).toLocaleString()}}</strong></td>
                        <td><span class="badge badge-red">${{Number(p.viewsPerPlaylistStart || 0).toFixed(1)}}</span></td>
                        <td>${{Math.round(Number(p.averageTimeInPlaylist || 0))}} sec</td>
                        <td>${{Number(p.estimatedMinutesWatched || 0).toLocaleString()}}</td>
                    </tr>
                `).join('');
            }} else {{
                pBody.innerHTML = '<tr><td colspan="7" style="color: var(--text-muted)">No playlist data found on this channel</td></tr>';
            }}
        }}

        function filterVideos() {{
            const query = document.getElementById('videoSearchInput').value.toLowerCase();
            const filtered = rawData.videos.filter(v => 
                (v.title && v.title.toLowerCase().includes(query)) ||
                (v.video_id && v.video_id.toLowerCase().includes(query)) ||
                (v.topics && v.topics.toLowerCase().includes(query)) ||
                (v.default_language && v.default_language.toLowerCase().includes(query)) ||
                (v.content_format && v.content_format.toLowerCase().includes(query))
            );
            renderVideosTable(filtered);
        }}

        function inspectVideo(videoId) {{
            const video = rawData.videos.find(v => v.video_id === videoId);
            if (!video) return;

            const traffic = rawData.videoTraffic.filter(t => t.video_id === videoId);
            const devices = rawData.videoDevices.filter(d => d.video_id === videoId);
            const demo = rawData.videoDemographics.filter(d => d.video_id === videoId);
            const sub = rawData.videoSubscribed ? rawData.videoSubscribed.filter(s => s.video_id === videoId) : [];
            const geo = rawData.videoGeography ? rawData.videoGeography.filter(g => g.video_id === videoId) : [];

            const totalSubMins = sub.reduce((acc, s) => acc + (parseFloat(s.estimatedMinutesWatched) || 0), 0);
            const totalGeoViews = geo.reduce((acc, g) => acc + (parseInt(g.views) || 0), 0);
            const ccInfo = video.has_captions ? `Yes (${{video.default_language || 'Default'}})` : 'None';
            const avgWatchFormatted = video.average_watch_time_formatted || (video.averageViewDuration ? (Math.floor(video.averageViewDuration/60)).toString().padStart(2, '0') + ':' + Math.round(video.averageViewDuration%60).toString().padStart(2, '0') : '00:00');
            const avgWatchMins = video.average_watch_time_minutes || (video.averageViewDuration ? (video.averageViewDuration / 60).toFixed(2) : 0);

            let html = `
                <h2 style="font-size: 22px; margin-bottom: 8px;">${{video.title}}</h2>
                <p style="color: var(--text-secondary); margin-bottom: 20px; font-size: 14px;">
                    Video ID: <code>${{video.video_id}}</code> • Duration: ${{video.duration_formatted}} • Format: <strong>${{video.content_format || 'VOD'}}</strong> • CC: <strong>${{ccInfo}}</strong> • Views: ${{Number(video.views).toLocaleString()}} • Watch Time: ${{video.estimated_watch_hours}} hrs • ⏱️ Avg Watch Time: <strong style="color: #00F2FE;">${{avgWatchFormatted}} (${{avgWatchMins}} mins)</strong> • 👍 Like Ratio: <strong style="color: #34D399;">${{video.like_ratio_pct || 100}}%</strong> (${{video.likes || 0}} Likes / ${{video.dislikes || 0}} Dislikes)
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                    <!-- 1. Video Demographics -->
                    <div class="card" style="padding: 16px;">
                        <h3 style="font-size: 15px; margin-bottom: 12px; color: #EC4899;">👥 Video Demographics (Age × Gender)</h3>
                        <table style="font-size: 13px;">
                            <thead><tr><th>Age Group</th><th>Gender</th><th>Viewer %</th></tr></thead>
                            <tbody>
                                ${{demo.length ? demo.map(d => `<tr><td><strong>${{d.ageGroup.replace('age', '').replace('-', ' - ')}}</strong></td><td>${{formatGenderName(d.gender)}}</td><td><span class="badge badge-red">${{d.viewerPercentage}}%</span></td></tr>`).join('') : '<tr><td colspan="3" style="color: var(--text-muted)">Not enough video views for demographic threshold</td></tr>'}}
                            </tbody>
                        </table>
                    </div>

                    <!-- 2. Video Subscribed Status -->
                    <div class="card" style="padding: 16px;">
                        <h3 style="font-size: 15px; margin-bottom: 12px; color: #7928CA;">🔔 Watch Time from Subscribers</h3>
                        <table style="font-size: 13px;">
                            <thead><tr><th>Status</th><th>Views</th><th>Watch Mins</th><th>%</th></tr></thead>
                            <tbody>
                                ${{sub.length ? sub.map(s => `<tr><td><strong>${{s.subscribedStatus === 'SUBSCRIBED' ? 'Subscribed' : 'Not Subscribed'}}</strong></td><td>${{Number(s.views).toLocaleString()}}</td><td>${{s.estimatedMinutesWatched}}</td><td><span class="badge ${{s.subscribedStatus === 'SUBSCRIBED' ? 'badge-purple' : 'badge-info'}}">${{totalSubMins ? ((s.estimatedMinutesWatched / totalSubMins) * 100).toFixed(1) : 0}}%</span></td></tr>`).join('') : '<tr><td colspan="4" style="color: var(--text-muted)">No per-video subscriber data</td></tr>'}}
                            </tbody>
                        </table>
                    </div>

                    <!-- 3. Video Top Geography -->
                    <div class="card" style="padding: 16px;">
                        <h3 style="font-size: 15px; margin-bottom: 12px; color: #10B981;">🌍 Top Viewer Countries</h3>
                        <table style="font-size: 13px;">
                            <thead><tr><th>Country</th><th>Views</th><th>Watch Mins</th><th>%</th></tr></thead>
                            <tbody>
                                ${{geo.length ? geo.map(g => `<tr><td><strong>${{g.country}}</strong></td><td>${{Number(g.views).toLocaleString()}}</td><td>${{g.estimatedMinutesWatched}}</td><td><span class="badge badge-info">${{totalGeoViews ? ((g.views / totalGeoViews) * 100).toFixed(1) : 0}}%</span></td></tr>`).join('') : '<tr><td colspan="4" style="color: var(--text-muted)">No per-video geography data</td></tr>'}}
                            </tbody>
                        </table>
                    </div>

                    <!-- 4. Video Devices -->
                    <div class="card" style="padding: 16px;">
                        <h3 style="font-size: 15px; margin-bottom: 12px; color: #00F2FE;">📱 Video Device Types</h3>
                        <table style="font-size: 13px;">
                            <thead><tr><th>Device</th><th>Views</th><th>Watch Mins</th></tr></thead>
                            <tbody>
                                ${{devices.length ? devices.map(d => `<tr><td>${{d.deviceType}}</td><td><strong>${{Number(d.views).toLocaleString()}}</strong></td><td>${{d.estimatedMinutesWatched}}</td></tr>`).join('') : '<tr><td colspan="3" style="color: var(--text-muted)">No device breakdown data</td></tr>'}}
                            </tbody>
                        </table>
                    </div>

                    <!-- 5. Video Traffic -->
                    <div class="card" style="padding: 16px;">
                        <h3 style="font-size: 15px; margin-bottom: 12px; color: #FF6B4A;">🚀 Video Traffic Sources</h3>
                        <table style="font-size: 13px;">
                            <thead><tr><th>Source</th><th>Views</th><th>Watch Mins</th></tr></thead>
                            <tbody>
                                ${{traffic.length ? traffic.map(t => `<tr><td>${{t.insightTrafficSourceType}}</td><td><strong>${{Number(t.views).toLocaleString()}}</strong></td><td>${{t.estimatedMinutesWatched}}</td></tr>`).join('') : '<tr><td colspan="3" style="color: var(--text-muted)">No traffic breakdown data</td></tr>'}}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            document.getElementById('modalBody').innerHTML = html;
            document.getElementById('videoModal').classList.add('active');
        }}

        function closeModal() {{
            document.getElementById('videoModal').classList.remove('active');
        }}

        function renderTables() {{
            // Subscribed Status Table
            const subBody = document.getElementById('subscribedTableBody');
            if (rawData.subscribedStatus && rawData.subscribedStatus.length) {{
                const totalSubMins = rawData.subscribedStatus.reduce((acc, s) => acc + (parseFloat(s.estimatedMinutesWatched) || 0), 0);
                subBody.innerHTML = rawData.subscribedStatus.map(s => `
                    <tr>
                        <td><strong>${{s.subscribedStatus === 'SUBSCRIBED' ? '🔔 Subscribed' : '👤 Not Subscribed'}}</strong></td>
                        <td>${{Number(s.views).toLocaleString()}}</td>
                        <td>${{Number(s.estimatedMinutesWatched).toLocaleString()}}</td>
                        <td><span class="badge ${{s.subscribedStatus === 'SUBSCRIBED' ? 'badge-purple' : 'badge-info'}}">${{totalSubMins ? ((s.estimatedMinutesWatched / totalSubMins) * 100).toFixed(1) : 0}}%</span></td>
                        <td>${{s.averageViewDuration}} sec</td>
                    </tr>
                `).join('');
            }} else {{
                subBody.innerHTML = '<tr><td colspan="5" style="color: var(--text-muted)">No subscriber status data available</td></tr>';
            }}

            // Geography Table
            const geoBody = document.getElementById('geographyTableBody');
            if (rawData.geography && rawData.geography.length) {{
                const totalGeoViews = rawData.geography.reduce((acc, g) => acc + (parseInt(g.views) || 0), 0);
                geoBody.innerHTML = rawData.geography.map(g => `
                    <tr>
                        <td><strong>${{g.country}}</strong></td>
                        <td>${{Number(g.views).toLocaleString()}}</td>
                        <td>${{Number(g.estimatedMinutesWatched).toLocaleString()}}</td>
                        <td><span class="badge badge-info">${{totalGeoViews ? ((g.views / totalGeoViews) * 100).toFixed(1) : 0}}%</span></td>
                        <td>${{g.averageViewDuration || 0}} sec</td>
                        <td>${{g.subscribersGained || 0}}</td>
                    </tr>
                `).join('');
            }} else {{
                geoBody.innerHTML = '<tr><td colspan="6" style="color: var(--text-muted)">No geography data available</td></tr>';
            }}

            // Gender Table
            const genderBody = document.getElementById('genderTableBody');
            if (computedDemo.gender && computedDemo.gender.length) {{
                genderBody.innerHTML = computedDemo.gender.map(g => `
                    <tr>
                        <td><strong>${{formatGenderName(g.gender)}}</strong></td>
                        <td><span class="badge ${{g.gender === 'male' ? 'badge-red' : 'badge-success'}}">${{g.viewerPercentage}}%</span></td>
                    </tr>
                `).join('');
            }} else {{
                genderBody.innerHTML = '<tr><td colspan="2" style="color: var(--text-muted)">Not enough demographic data to meet privacy thresholds</td></tr>';
            }}

            // Age Table
            const ageBody = document.getElementById('ageTableBody');
            if (computedDemo.age && computedDemo.age.length) {{
                ageBody.innerHTML = computedDemo.age.map(a => `
                    <tr>
                        <td><strong>${{a.ageGroup.replace('age', '').replace('-', ' - ')}}</strong></td>
                        <td><span class="badge badge-red">${{a.viewerPercentage}}%</span></td>
                    </tr>
                `).join('');
            }} else {{
                ageBody.innerHTML = '<tr><td colspan="2" style="color: var(--text-muted)">Not enough demographic data to meet privacy thresholds</td></tr>';
            }}

            // Matrix Table
            const matrixBody = document.getElementById('matrixTableBody');
            if (computedDemo.matrix && computedDemo.matrix.length) {{
                matrixBody.innerHTML = computedDemo.matrix.map(m => `
                    <tr>
                        <td><strong>${{m.ageGroup.replace('age', '').replace('-', ' - ')}}</strong></td>
                        <td><span class="badge ${{m.gender === 'male' ? 'badge-red' : 'badge-success'}}">${{formatGenderName(m.gender).toUpperCase()}}</span></td>
                        <td><strong>${{m.viewerPercentage}}%</strong></td>
                    </tr>
                `).join('');
            }} else {{
                matrixBody.innerHTML = '<tr><td colspan="3" style="color: var(--text-muted)">No granular matrix data available</td></tr>';
            }}

            // Traffic Table
            const totalTrafficViews = rawData.traffic.reduce((sum, t) => sum + (parseInt(t.views) || 0), 0);
            const trBody = document.getElementById('trafficTableBody');
            trBody.innerHTML = rawData.traffic.map(t => `
                <tr>
                    <td><strong>${{t.insightTrafficSourceType}}</strong></td>
                    <td>${{Number(t.views).toLocaleString()}}</td>
                    <td>${{Number(t.estimatedMinutesWatched).toLocaleString()}}</td>
                    <td><span class="badge">${{totalTrafficViews ? ((t.views / totalTrafficViews) * 100).toFixed(1) : 0}}%</span></td>
                </tr>
            `).join('');

            // Devices Table
            const devBody = document.getElementById('devicesTableBody');
            devBody.innerHTML = rawData.devices.map(d => `
                <tr>
                    <td><strong>${{d.deviceType}}</strong></td>
                    <td>${{Number(d.views).toLocaleString()}}</td>
                    <td>${{Number(d.estimatedMinutesWatched).toLocaleString()}}</td>
                </tr>
            `).join('');

            // OS Table
            const osBody = document.getElementById('osTableBody');
            osBody.innerHTML = rawData.operatingSystems.map(o => `
                <tr>
                    <td><strong>${{o.operatingSystem}}</strong></td>
                    <td>${{Number(o.views).toLocaleString()}}</td>
                    <td>${{Number(o.estimatedMinutesWatched).toLocaleString()}}</td>
                </tr>
            `).join('');
        }}

        function renderCharts() {{
            Chart.defaults.color = '#9CA3AF';
            Chart.defaults.font.family = "'Inter', sans-serif";
            window.chartInstances = [];

            // 1. Gender Doughnut
            const genderLabels = (computedDemo.gender && computedDemo.gender.length) ? computedDemo.gender.map(g => formatGenderName(g.gender).toUpperCase()) : ['MALE', 'FEMALE'];
            const genderValues = (computedDemo.gender && computedDemo.gender.length) ? computedDemo.gender.map(g => g.viewerPercentage) : [50, 50];
            const genderColors = genderLabels.map(l => l.includes('MALE') && !l.includes('FE') ? '#00F2FE' : (l.includes('FEMALE') ? '#FF0033' : '#7928CA'));

            const cOverviewGender = new Chart(document.getElementById('overviewGenderChart'), {{
                type: 'doughnut',
                data: {{
                    labels: genderLabels,
                    datasets: [{{
                        data: genderValues,
                        backgroundColor: genderColors,
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ position: 'bottom' }} }}
                }}
            }});
            window.chartInstances.push(cOverviewGender);

            // 2. Subscribed Status Doughnut
            if (rawData.subscribedStatus && rawData.subscribedStatus.length) {{
                const subLabels = rawData.subscribedStatus.map(s => s.subscribedStatus === 'SUBSCRIBED' ? 'SUBSCRIBED' : 'NOT SUBSCRIBED');
                const subValues = rawData.subscribedStatus.map(s => s.estimatedMinutesWatched);
                const cSub = new Chart(document.getElementById('overviewSubscribedChart'), {{
                    type: 'doughnut',
                    data: {{
                        labels: subLabels,
                        datasets: [{{
                            data: subValues,
                            backgroundColor: ['#7928CA', '#00F2FE'],
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ 
                            legend: {{ position: 'bottom' }},
                            tooltip: {{
                                callbacks: {{
                                    label: ctx => ` ${{ctx.label}}: ${{Number(ctx.raw).toLocaleString()}} watch mins`
                                }}
                            }}
                        }}
                    }}
                }});
                window.chartInstances.push(cSub);
            }}

            // 3. Content Type Doughnut
            if (rawData.contentTypes && rawData.contentTypes.length) {{
                const ctLabels = rawData.contentTypes.map(c => c.creatorContentType.replace('creatorContentType', ''));
                const ctValues = rawData.contentTypes.map(c => c.views);
                const cCt = new Chart(document.getElementById('overviewContentTypeChart'), {{
                    type: 'doughnut',
                    data: {{
                        labels: ctLabels,
                        datasets: [{{
                            data: ctValues,
                            backgroundColor: ['#FF0033', '#00F2FE', '#F59E0B', '#10B981'],
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ position: 'bottom' }} }}
                    }}
                }});
                window.chartInstances.push(cCt);
            }}

            // 4. Detailed Gender Doughnut
            const cGenderDetailed = new Chart(document.getElementById('genderDetailedChart'), {{
                type: 'doughnut',
                data: {{
                    labels: genderLabels,
                    datasets: [{{
                        data: genderValues,
                        backgroundColor: genderColors,
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ 
                        legend: {{ position: 'right' }},
                        tooltip: {{
                            callbacks: {{
                                label: ctx => ` ${{ctx.label}}: ${{ctx.raw}}%`
                            }}
                        }}
                    }}
                }}
            }});
            window.chartInstances.push(cGenderDetailed);

            // 5. Age Bar Chart
            const ageLabels = (computedDemo.age && computedDemo.age.length) ? computedDemo.age.map(a => a.ageGroup.replace('age', '').replace('-', ' - ')) : ['18 - 24', '25 - 34', '35 - 44'];
            const ageValues = (computedDemo.age && computedDemo.age.length) ? computedDemo.age.map(a => a.viewerPercentage) : [0, 0, 0];

            const cAgeDetailed = new Chart(document.getElementById('ageDetailedChart'), {{
                type: 'bar',
                data: {{
                    labels: ageLabels,
                    datasets: [{{
                        label: 'Viewer %',
                        data: ageValues,
                        backgroundColor: 'rgba(255, 0, 51, 0.75)',
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ grid: {{ display: false }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ callback: v => v + '%' }} }}
                    }}
                }}
            }});
            window.chartInstances.push(cAgeDetailed);

            // 6. Device Chart
            const cDev = new Chart(document.getElementById('deviceChart'), {{
                type: 'doughnut',
                data: {{
                    labels: rawData.devices.map(d => d.deviceType),
                    datasets: [{{
                        data: rawData.devices.map(d => d.views),
                        backgroundColor: ['#FF0033', '#00F2FE', '#7928CA', '#F59E0B', '#10B981'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ position: 'bottom' }} }}
                }}
            }});
            window.chartInstances.push(cDev);

            // 7. Traffic Bar Chart
            const cTrBar = new Chart(document.getElementById('trafficBarChart'), {{
                type: 'bar',
                data: {{
                    labels: rawData.traffic.map(t => t.insightTrafficSourceType),
                    datasets: [{{
                        label: 'Views',
                        data: rawData.traffic.map(t => t.views),
                        backgroundColor: 'rgba(0, 242, 254, 0.75)',
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ grid: {{ display: false }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
                    }}
                }}
            }});
            window.chartInstances.push(cTrBar);

            // 8. Geography Overview Bar Chart
            const cGeo = new Chart(document.getElementById('geoChart'), {{
                type: 'bar',
                data: {{
                    labels: rawData.geography.slice(0, 5).map(g => g.country),
                    datasets: [{{
                        label: 'Views',
                        data: rawData.geography.slice(0, 5).map(g => g.views),
                        backgroundColor: 'rgba(121, 40, 202, 0.75)',
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ grid: {{ display: false }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
                    }}
                }}
            }});
            window.chartInstances.push(cGeo);

            // 9. Geography Detailed Bar Chart
            const cGeoDetailed = new Chart(document.getElementById('geoDetailedChart'), {{
                type: 'bar',
                data: {{
                    labels: rawData.geography.map(g => g.country),
                    datasets: [{{
                        label: 'Views',
                        data: rawData.geography.map(g => g.views),
                        backgroundColor: 'rgba(59, 130, 246, 0.75)',
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ grid: {{ display: false }} }},
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
                    }}
                }}
            }});
            window.chartInstances.push(cGeoDetailed);

            // 10. Traffic Pie Chart
            const cTrPie = new Chart(document.getElementById('trafficPieChart'), {{
                type: 'doughnut',
                data: {{
                    labels: rawData.traffic.map(t => t.insightTrafficSourceType),
                    datasets: [{{
                        data: rawData.traffic.map(t => t.views),
                        backgroundColor: ['#FF0033', '#00F2FE', '#7928CA', '#F59E0B', '#10B981', '#EC4899', '#3B82F6'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ position: 'right' }} }}
                }}
            }});
            window.chartInstances.push(cTrPie);

            // 11. Daily Timeline Line Chart
            if (rawData.daily && rawData.daily.length) {{
                const cTime = new Chart(document.getElementById('timelineChart'), {{
                    type: 'line',
                    data: {{
                        labels: rawData.daily.map(d => d.day),
                        datasets: [
                            {{
                                label: 'Views',
                                data: rawData.daily.map(d => d.views),
                                borderColor: '#FF0033',
                                backgroundColor: 'rgba(255, 0, 51, 0.1)',
                                fill: true,
                                tension: 0.3,
                                yAxisID: 'y'
                            }},
                            {{
                                label: 'Watch Time (Mins)',
                                data: rawData.daily.map(d => d.estimatedMinutesWatched),
                                borderColor: '#00F2FE',
                                backgroundColor: 'transparent',
                                borderDash: [4, 4],
                                tension: 0.3,
                                yAxisID: 'y1'
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{ mode: 'index', intersect: false }},
                        scales: {{
                            x: {{ grid: {{ display: false }} }},
                            y: {{ type: 'linear', display: true, position: 'left', grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
                            y1: {{ type: 'linear', display: true, position: 'right', grid: {{ drawOnChartArea: false }} }}
                        }}
                    }}
                }});
                window.chartInstances.push(cTime);
            }}
        }}

        window.onload = initDashboard;
    </script>
</body>
</html>
"""
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
