#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import print as rprint

from auth import get_credentials, get_api_services
from extractors.data_api import (
    fetch_channel_info,
    fetch_all_video_ids,
    fetch_video_metadata,
    fetch_playlists_info,
    fetch_playlist_video_ids
)
from extractors.analytics_api import (
    fetch_video_analytics,
    fetch_all_channel_studio_analytics,
    fetch_per_video_studio_analytics,
    fetch_playlists_analytics
)
from extractors.reporting_api import create_standard_reporting_jobs, download_reporting_jobs_data
from utils.formatting import calculate_engagement_rate, resolve_upload_date_range
from utils.exporter import export_data
from utils.dashboard_generator import generate_html_dashboard

console = Console()

def parse_args():
    parser = argparse.ArgumentParser(
        description="YouTube Analytics & Reporting API CLI Extractor - Extract all video metadata & Studio analytics data."
    )
    parser.add_argument(
        "-c", "--credentials",
        default="client_secret.json",
        help="Path to Google Cloud OAuth client_secret.json file (default: client_secret.json)"
    )
    parser.add_argument(
        "-t", "--token",
        default="token.json",
        help="Path to store authorized OAuth token (default: token.json)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Output directory path for exported files (default: output)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["csv", "excel", "json", "sqlite", "all"],
        default="all",
        help="Export file format (default: all)"
    )
    parser.add_argument(
        "--playlist-id",
        help="Extract analytics for videos within a specific Playlist ID (or all playlists summary if omitted)"
    )
    parser.add_argument(
        "--period", "--uploaded-period",
        dest="uploaded_period",
        choices=["this-month", "last-month", "this-year", "last-year", "last-7d", "last-30d", "last-90d", "last-365d"],
        help="Filter videos by upload preset period (e.g. this-month, last-month, this-year, last-year, last-30d)"
    )
    parser.add_argument(
        "--uploaded-after",
        help="Only extract videos uploaded ON or AFTER this date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--uploaded-before",
        help="Only extract videos uploaded ON or BEFORE this date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--start-date",
        default="2000-01-01",
        help="Start date for Analytics API metrics (YYYY-MM-DD, default: 2000-01-01)"
    )
    parser.add_argument(
        "--end-date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date for Analytics API metrics (YYYY-MM-DD, default: today)"
    )
    parser.add_argument(
        "--include-revenue",
        action="store_true",
        help="Include monetary & revenue metrics (requires yt-analytics-monetary.readonly permission)"
    )
    parser.add_argument(
        "--per-video-breakdown",
        action="store_true",
        help="Extract detailed per-video device, traffic, and demographic breakdowns"
    )
    parser.add_argument(
        "--setup-reporting-jobs",
        action="store_true",
        help="Automatically setup bulk YouTube Reporting API scheduled daily jobs"
    )
    parser.add_argument(
        "--download-reports",
        action="store_true",
        help="Download available generated CSV reports from YouTube Reporting API"
    )
    return parser.parse_args()


def display_studio_previews(studio_dfs: dict):
    """Prints neat preview tables for major Studio metrics."""
    # 1. Demographics (Gender & Age)
    df_gender = studio_dfs.get("demographics_gender")
    df_demo = studio_dfs.get("demographics_age_gender")
    if df_gender is not None and not df_gender.empty:
        t = Table(title="Audience Gender Distribution", header_style="bold magenta")
        t.add_column("Gender", style="cyan")
        t.add_column("Viewer %", style="bold green")
        for _, row in df_gender.iterrows():
            t.add_row(str(row.get("gender")).capitalize(), f"{float(row.get('viewerPercentage', 0)):.1f}%")
        console.print(t)
        console.print()
    elif df_demo is not None and not df_demo.empty:
        t = Table(title="Audience Demographics (Age & Gender)", header_style="bold magenta")
        t.add_column("Age Group", style="cyan")
        t.add_column("Gender", style="yellow")
        t.add_column("Viewer %", style="bold green")
        for _, row in df_demo.iterrows():
            t.add_row(str(row.get("ageGroup")), str(row.get("gender")), f"{float(row.get('viewerPercentage', 0)):.1f}%")
        console.print(t)
        console.print()

    # 2. Device Types
    df_dev = studio_dfs.get("device_types")
    if df_dev is not None and not df_dev.empty:
        t = Table(title="Device Types Breakdown", header_style="bold blue")
        t.add_column("Device Type", style="cyan")
        t.add_column("Views", style="bold green")
        t.add_column("Watch Time (Mins)", style="yellow")
        for _, row in df_dev.iterrows():
            t.add_row(str(row.get("deviceType")), f"{int(row.get('views', 0)):,}", f"{int(row.get('estimatedMinutesWatched', 0)):,}")
        console.print(t)
        console.print()

    # 3. Traffic Sources
    df_tr = studio_dfs.get("traffic_sources")
    if df_tr is not None and not df_tr.empty:
        t = Table(title="Top Traffic Sources", header_style="bold green")
        t.add_column("Source Type", style="cyan")
        t.add_column("Views", style="bold green")
        t.add_column("Watch Time (Mins)", style="yellow")
        for _, row in df_tr.head(6).iterrows():
            t.add_row(str(row.get("insightTrafficSourceType")), f"{int(row.get('views', 0)):,}", f"{int(row.get('estimatedMinutesWatched', 0)):,}")
        console.print(t)
        console.print()

    # 4. Top Countries
    df_geo = studio_dfs.get("geography_countries")
    if df_geo is not None and not df_geo.empty:
        t = Table(title="Top Audience Countries", header_style="bold cyan")
        t.add_column("Country", style="cyan")
        t.add_column("Views", style="bold green")
        t.add_column("Watch Time (Mins)", style="yellow")
        t.add_column("Subs Gained", style="magenta")
        for _, row in df_geo.head(5).iterrows():
            t.add_row(
                str(row.get("country")),
                f"{int(row.get('views', 0)):,}",
                f"{int(row.get('estimatedMinutesWatched', 0)):,}",
                f"{int(row.get('subscribersGained', 0)):,}"
            )
    # 5. Subscribed Status
    df_sub = studio_dfs.get("subscribed_status")
    if df_sub is not None and not df_sub.empty:
        total_sub_mins = df_sub["estimatedMinutesWatched"].sum()
        t = Table(title="Watch Time from Subscribers", header_style="bold purple")
        t.add_column("Status", style="cyan")
        t.add_column("Views", style="bold green")
        t.add_column("Watch Time (Mins)", style="yellow")
        t.add_column("Watch Time %", style="bold magenta")
        for _, row in df_sub.iterrows():
            mins = float(row.get("estimatedMinutesWatched", 0))
            pct = f"{(mins / total_sub_mins) * 100:.1f}%" if total_sub_mins > 0 else "0.0%"
            t.add_row(
                "Subscribed" if row.get("subscribedStatus") == "SUBSCRIBED" else "Not Subscribed",
                f"{int(row.get('views', 0)):,}",
                f"{int(mins):,}",
                pct
            )
        console.print(t)
        console.print()


def main():
    args = parse_args()
    
    console.print(Panel.fit(
        "[bold cyan]YouTube Analytics & Reporting API CLI Extractor[/bold cyan]\n"
        "[dim]Extract comprehensive channel, video, and YouTube Studio intelligence[/dim]",
        border_style="cyan"
    ))

    # 1. Authenticate
    console.print("[bold yellow]1. Authenticating with Google OAuth 2.0...[/bold yellow]")
    try:
        credentials = get_credentials(
            credentials_file=args.credentials,
            token_file=args.token,
            include_monetary=args.include_revenue
        )
        youtube_data, youtube_analytics, youtube_reporting = get_api_services(
            credentials_file=args.credentials,
            token_file=args.token,
            include_monetary=args.include_revenue
        )
        console.print("[bold green]✔ OAuth Authentication Successful![/bold green]\n")
    except Exception as e:
        console.print(f"[bold red]❌ Authentication Error:[/bold red] {e}")
        sys.exit(1)

    # 2. Fetch Channel Info
    console.print("[bold yellow]2. Retrieving Channel Information...[/bold yellow]")
    try:
        channel_info = fetch_channel_info(youtube_data)
        
        table = Table(title="Channel Overview", show_header=True, header_style="bold magenta")
        table.add_column("Property", style="dim")
        table.add_column("Value", style="bold green")
        
        table.add_row("Channel Name", channel_info["title"])
        table.add_row("Channel ID", channel_info["channel_id"])
        table.add_row("Total Subscribers", f"{channel_info['subscribers']:,}")
        table.add_row("Total Public Views", f"{channel_info['views']:,}")
        table.add_row("Total Videos Count", f"{channel_info['video_count']:,}")
        console.print(table)
        console.print()
    except Exception as e:
        console.print(f"[bold red]❌ Failed to fetch channel info:[/bold red] {e}")
        sys.exit(1)

    # 3. Retrieve Video IDs (with optional playlist and upload date filtering)
    upload_after, upload_before = resolve_upload_date_range(
        period=args.uploaded_period,
        uploaded_after=args.uploaded_after,
        uploaded_before=args.uploaded_before
    )

    video_ids = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        if args.playlist_id:
            console.print(f"[bold yellow]3. Discovering Video IDs from Playlist '{args.playlist_id}'...[/bold yellow]")
            task = progress.add_task("Fetching Playlist Video IDs...", total=None)
            def p_cb(current_count):
                progress.update(task, completed=current_count)
            video_ids = fetch_playlist_video_ids(
                youtube_data,
                args.playlist_id,
                uploaded_after=upload_after,
                uploaded_before=upload_before,
                progress_callback=p_cb
            )
        else:
            if upload_after or upload_before:
                filter_desc = []
                if upload_after:
                    filter_desc.append(f"after {upload_after[:10]}")
                if upload_before:
                    filter_desc.append(f"before {upload_before[:10]}")
                console.print(f"[bold yellow]3. Discovering Video IDs (Upload Filter: {' & '.join(filter_desc)})...[/bold yellow]")
            else:
                console.print("[bold yellow]3. Discovering Video IDs from Uploads Playlist (All-Time)...[/bold yellow]")

            task = progress.add_task("Fetching Video IDs...", total=channel_info["video_count"] or None)
            def id_cb(current_count):
                progress.update(task, completed=current_count)
            video_ids = fetch_all_video_ids(
                youtube_data,
                channel_info["uploads_playlist_id"],
                uploaded_after=upload_after,
                uploaded_before=upload_before,
                progress_callback=id_cb
            )

    console.print(f"[bold green]✔ Discovered {len(video_ids)} matching videos to analyze![/bold green]\n")

    if not video_ids:
        console.print("[bold yellow]No videos found matching the criteria. Exiting.[/bold yellow]")
        sys.exit(0)

    # 4. Fetch Detailed Video Metadata (Data API v3)
    console.print("[bold yellow]4. Fetching Metadata & Public Statistics (Data API v3)...[/bold yellow]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Extracting Video Metadata...", total=len(video_ids))
        def meta_cb(current_count):
            progress.update(task, completed=current_count)
        df_metadata = fetch_video_metadata(youtube_data, video_ids, progress_callback=meta_cb)

    console.print(f"[bold green]✔ Fetched metadata for {len(df_metadata)} videos![/bold green]\n")

    # 5. Query Video-Level Analytics API v2
    console.print(f"[bold yellow]5. Querying Video Analytics ({args.start_date} to {args.end_date})...[/bold yellow]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Processing Video Analytics...", total=len(video_ids))
        def analytics_cb(current_count):
            progress.update(task, completed=current_count)
        df_analytics = fetch_video_analytics(
            youtube_analytics,
            video_ids,
            start_date=args.start_date,
            end_date=args.end_date,
            include_monetary=args.include_revenue,
            progress_callback=analytics_cb
        )

    console.print(f"[bold green]✔ Analytics retrieved for {len(df_analytics)} video entries![/bold green]\n")

    # 6. Fetch Studio Analytics (Demographics, Devices, Traffic Sources, Geography, OS, Playback, Timeline)
    console.print("[bold yellow]6. Extracting Channel YouTube Studio Analytics Dimensions...[/bold yellow]")
    studio_dfs = fetch_all_channel_studio_analytics(
        youtube_analytics,
        start_date=args.start_date,
        end_date=args.end_date
    )
    console.print("[bold green]✔ Studio Analytics Dimensions Extracted![/bold green]\n")
    display_studio_previews(studio_dfs)

    # Optional: Per-Video Studio Breakdown
    per_video_dfs = {}
    if args.per_video_breakdown:
        console.print("[bold yellow]Extracting Per-Video Studio Breakdown (Devices, Traffic, Demographics)...[/bold yellow]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Processing Per-Video Details...", total=len(video_ids))
            def per_vid_cb(current_count):
                progress.update(task, completed=current_count)
            per_video_dfs = fetch_per_video_studio_analytics(
                youtube_analytics,
                video_ids,
                start_date=args.start_date,
                end_date=args.end_date,
                progress_callback=per_vid_cb
            )
        console.print("[bold green]✔ Per-Video Details Extracted![/bold green]\n")

    # 7. Extract Channel Playlists & Analytics
    console.print("[bold yellow]7. Extracting Channel Playlists & Engagement Analytics...[/bold yellow]")
    try:
        df_playlists_raw = fetch_playlists_info(youtube_data)
        if not df_playlists_raw.empty:
            df_playlists = fetch_playlists_analytics(
                youtube_analytics,
                df_playlists_raw,
                start_date=args.start_date,
                end_date=args.end_date
            )
            
            p_table = Table(title="Channel Playlists Analytics", show_header=True, header_style="bold green")
            p_table.add_column("Playlist Title", style="cyan")
            p_table.add_column("Items", justify="right")
            p_table.add_column("Starts", justify="right", style="magenta")
            p_table.add_column("Views / Start", justify="right")
            p_table.add_column("Avg Time (Sec)", justify="right")
            for _, r in df_playlists.iterrows():
                p_table.add_row(
                    str(r.get("title", ""))[:30],
                    str(r.get("item_count", 0)),
                    str(r.get("playlistStarts", 0)),
                    f"{float(r.get('viewsPerPlaylistStart', 0)):.1f}",
                    str(int(float(r.get("averageTimeInPlaylist", 0))))
                )
            console.print(p_table)
            console.print()
        else:
            df_playlists = pd.DataFrame()
    except Exception as e:
        console.print(f"[dim]Playlist analytics query skipped: {e}[/dim]")
        df_playlists = pd.DataFrame()

    # 8. Merge & Calculate Extra Video Performance Metrics
    if not df_analytics.empty and "video_id" in df_analytics.columns:
        df_merged = pd.merge(df_metadata, df_analytics, on="video_id", how="left", suffixes=("", "_analytics"))
    else:
        df_merged = df_metadata

    def calculate_like_ratio(likes, dislikes):
        try:
            l = float(likes) if pd.notnull(likes) else 0.0
            d = float(dislikes) if pd.notnull(dislikes) else 0.0
            if (l + d) > 0:
                return round((l / (l + d)) * 100.0, 1)
            elif l > 0:
                return 100.0
            return 0.0
        except Exception:
            return 0.0

    df_merged["engagement_rate_pct"] = df_merged.apply(
        lambda r: calculate_engagement_rate(
            r.get("likes"),
            r.get("comments"),
            r.get("shares"),
            r.get("views")
        ), axis=1
    )
    df_merged["like_ratio_pct"] = df_merged.apply(
        lambda r: calculate_like_ratio(r.get("likes_analytics", r.get("likes")), r.get("dislikes")),
        axis=1
    )
    if "estimatedMinutesWatched" in df_merged.columns:
        df_merged["estimated_watch_hours"] = (df_merged["estimatedMinutesWatched"].fillna(0).astype(float) / 60.0).round(2)
    if "averageViewDuration" in df_merged.columns:
        df_merged["average_watch_time_seconds"] = df_merged["averageViewDuration"].fillna(0).astype(int)
        df_merged["average_watch_time_minutes"] = (df_merged["averageViewDuration"].fillna(0).astype(float) / 60.0).round(2)
        df_merged["average_watch_time_formatted"] = df_merged["average_watch_time_seconds"].apply(
            lambda sec: f"{int(sec // 60):02d}:{int(sec % 60):02d}"
        )

    df_channel = pd.DataFrame([channel_info])

    # Assemble all tables for export
    dfs_to_export = {
        "channel_summary": df_channel,
        "playlists_summary": df_playlists,
        "videos_full_data": df_merged,
        "demographics_gender": studio_dfs.get("demographics_gender"),
        "demographics_age": studio_dfs.get("demographics_age"),
        "demographics_age_gender": studio_dfs.get("demographics_age_gender"),
        "device_types": studio_dfs.get("device_types"),
        "operating_systems": studio_dfs.get("operating_systems"),
        "traffic_sources": studio_dfs.get("traffic_sources"),
        "geography_countries": studio_dfs.get("geography_countries"),
        "playback_locations": studio_dfs.get("playback_locations"),
        "sharing_services": studio_dfs.get("sharing_services"),
        "daily_timeline": studio_dfs.get("daily_timeline")
    }

    if per_video_dfs:
        for k, v in per_video_dfs.items():
            if v is not None and not v.empty:
                dfs_to_export[k] = v

    # 9. Setup / Download Reporting API Jobs
    if args.setup_reporting_jobs:
        console.print("[bold yellow]8. Setting up YouTube Reporting API Daily Scheduled Jobs...[/bold yellow]")
        created = create_standard_reporting_jobs(youtube_reporting)
        console.print(f"[bold green]✔ Created/verified {len(created)} reporting jobs![/bold green]\n")

    if args.download_reports:
        console.print("[bold yellow]9. Downloading Bulk CSV Reports (Reporting API v1)...[/bold yellow]")
        downloaded = download_reporting_jobs_data(youtube_reporting, credentials, os.path.join(args.output_dir, "reports"))
        console.print(f"[bold green]✔ Downloaded {len(downloaded)} bulk CSV reports![/bold green]\n")

    # 10. Export Data
    console.print(f"[bold yellow]Exporting datasets (format: {args.format})...[/bold yellow]")
    exported_files = export_data(
        dfs=dfs_to_export,
        output_dir=args.output_dir,
        export_format=args.format,
        file_prefix=f"youtube_{channel_info['channel_id']}"
    )

    # 11. Generate Interactive HTML Dashboard
    dash_path = os.path.join(args.output_dir, "dashboard.html")
    generate_html_dashboard(
        channel_summary_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_channel_summary.json"),
        videos_data_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_videos_full_data.json"),
        playlists_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_playlists_summary.json"),
        demographics_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_demographics_age_gender.json"),
        video_demographics_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_video_demographics_breakdown.json"),
        gender_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_demographics_gender.json"),
        age_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_demographics_age.json"),
        device_types_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_device_types.json"),
        traffic_sources_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_traffic_sources.json"),
        operating_systems_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_operating_systems.json"),
        geography_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_geography_countries.json"),
        playback_locations_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_playback_locations.json"),
        daily_timeline_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_daily_timeline.json"),
        video_device_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_video_device_breakdown.json"),
        video_traffic_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_video_traffic_breakdown.json"),
        video_subscribed_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_video_subscribed_breakdown.json"),
        video_geography_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_video_geography_breakdown.json"),
        subscribed_status_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_subscribed_status.json"),
        content_types_path=os.path.join(args.output_dir, f"youtube_{channel_info['channel_id']}_content_types.json"),
        output_html_path=dash_path
    )
    # Also sync to root dashboard.html if output_dir is 'output' for convenient opening
    if args.output_dir == "output":
        try:
            import shutil
            shutil.copyfile(dash_path, "dashboard.html")
        except Exception:
            pass
    exported_files['html_dashboard'] = dash_path

    console.print("\n[bold green]🎉 Extraction & Export Completed Successfully![/bold green]")
    export_table = Table(title="Exported Artifacts", show_header=True, header_style="bold blue")
    export_table.add_column("Format", style="cyan")
    export_table.add_column("File Path", style="yellow")
    
    for fmt, path in exported_files.items():
        export_table.add_row(fmt.upper(), path)
        
    console.print(export_table)

if __name__ == "__main__":
    main()
