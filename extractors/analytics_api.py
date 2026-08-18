import pandas as pd
from typing import Callable, Optional, List, Dict

BASE_METRICS = [
    "views",
    "estimatedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
    "subscribersGained",
    "subscribersLost",
    "likes",
    "dislikes",
    "shares",
    "comments"
]

MONETARY_METRICS = [
    "estimatedRevenue",
    "estimatedAdRevenue",
    "cpm",
    "grossRevenue"
]

def _execute_query(youtube_analytics, **kwargs) -> pd.DataFrame:
    """Helper to safely execute an Analytics API query and return a DataFrame."""
    try:
        res = youtube_analytics.reports().query(**kwargs).execute()
        headers = [col["name"] for col in res.get("columnHeaders", [])]
        rows = res.get("rows", [])
        if not rows or not headers:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=headers)
    except Exception as e:
        # Silent fallback or minimal log to handle data thresholds (e.g. low-view demographics)
        return pd.DataFrame()


def fetch_video_analytics(
    youtube_analytics,
    video_ids: List[str],
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01",
    include_monetary: bool = False,
    progress_callback: Optional[Callable] = None
) -> pd.DataFrame:
    """
    Queries YouTube Analytics API v2 for video-level performance metrics.
    Splits video IDs into batches of 200 to respect URL length and API filters.
    """
    metrics = list(BASE_METRICS)
    if include_monetary:
        metrics.extend(MONETARY_METRICS)
        
    metrics_str = ",".join(metrics)
    all_rows = []
    headers = []
    
    total_ids = len(video_ids)
    batch_size = 200
    
    for i in range(0, total_ids, batch_size):
        chunk_ids = video_ids[i:i+batch_size]
        video_filter = f"video=={','.join(chunk_ids)}"
        
        try:
            res = youtube_analytics.reports().query(
                ids="channel==MINE",
                startDate=start_date,
                endDate=end_date,
                metrics=metrics_str,
                dimensions="video",
                filters=video_filter,
                maxResults=batch_size
            ).execute()
            
            if not headers:
                headers = [col["name"] for col in res.get("columnHeaders", [])]
                
            rows = res.get("rows", [])
            all_rows.extend(rows)
            
        except Exception as e:
            if include_monetary and "monetary" in str(e).lower():
                res = youtube_analytics.reports().query(
                    ids="channel==MINE",
                    startDate=start_date,
                    endDate=end_date,
                    metrics=",".join(BASE_METRICS),
                    dimensions="video",
                    filters=video_filter,
                    maxResults=batch_size
                ).execute()
                if not headers:
                    headers = [col["name"] for col in res.get("columnHeaders", [])]
                all_rows.extend(res.get("rows", []))
            else:
                print(f"Warning: Analytics batch query error: {e}")
                
        if progress_callback:
            progress_callback(min(i + batch_size, total_ids))
            
    if not all_rows or not headers:
        return pd.DataFrame()
        
    df = pd.DataFrame(all_rows, columns=headers)
    if "video" in df.columns:
        df.rename(columns={"video": "video_id"}, inplace=True)
        
    return df


def fetch_gender_demographics(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """Fetches viewer percentage breakdown by gender (male, female, user_specified)."""
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "viewerPercentage",
        "dimensions": "gender",
        "sort": "-viewerPercentage"
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_age_demographics(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """Fetches viewer percentage breakdown by age group (e.g. age18-24, age25-34)."""
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "viewerPercentage",
        "dimensions": "ageGroup",
        "sort": "ageGroup"
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_demographics(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """
    Fetches viewer percentage breakdown by combined age group and gender.
    """
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "viewerPercentage",
        "dimensions": "ageGroup,gender",
        "sort": "gender,ageGroup"
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_device_types(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """
    Fetches views and watch time broken down by Device Type (Mobile, Desktop, Tablet, TV, etc.).
    """
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "views,estimatedMinutesWatched",
        "dimensions": "deviceType",
        "sort": "-views"
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_operating_systems(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """
    Fetches views and watch time broken down by Operating System (Android, iOS, Windows, Mac, etc.).
    """
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "views,estimatedMinutesWatched",
        "dimensions": "operatingSystem",
        "sort": "-views"
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_traffic_sources(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """
    Fetches views and watch time by Traffic Source (YouTube Search, Suggested Videos, External, etc.).
    """
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "views,estimatedMinutesWatched",
        "dimensions": "insightTrafficSourceType",
        "sort": "-views"
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_geography(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01",
    max_results: int = 200
) -> pd.DataFrame:
    """
    Fetches top audience countries with views, watch time, avg duration, and subscribers gained.
    """
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "views,estimatedMinutesWatched,averageViewDuration,subscribersGained",
        "dimensions": "country",
        "sort": "-views",
        "maxResults": max_results
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_playback_locations(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """
    Fetches views by playback location (YouTube Watch Page, Embedded on external sites, Channel page).
    """
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "views,estimatedMinutesWatched",
        "dimensions": "insightPlaybackLocationType",
        "sort": "-views"
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_sharing_services(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """
    Fetches share counts broken down by service (WhatsApp, Facebook, Twitter, Copy-link, etc.).
    """
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "shares",
        "dimensions": "sharingService",
        "sort": "-shares"
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_daily_timeline(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """
    Fetches day-by-day historical timeline metrics.
    """
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost,likes,comments,shares",
        "dimensions": "day",
        "sort": "day"
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_subscribed_status(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """
    Fetches views, watch time, and retention broken down by Subscriber Status (SUBSCRIBED vs UNSUBSCRIBED).
    """
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "views,estimatedMinutesWatched,averageViewDuration",
        "dimensions": "subscribedStatus",
        "sort": "-views"
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_content_types(
    youtube_analytics,
    video_id: Optional[str] = None,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """
    Fetches performance metrics broken down by Content Type (Shorts, VOD, Live Stream).
    """
    kwargs = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "views,estimatedMinutesWatched",
        "dimensions": "creatorContentType",
        "sort": "-views"
    }
    if video_id:
        kwargs["filters"] = f"video=={video_id}"
    return _execute_query(youtube_analytics, **kwargs)


def fetch_all_channel_studio_analytics(
    youtube_analytics,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> Dict[str, pd.DataFrame]:
    """
    Fetches all Studio-level dimensions for the channel.
    """
    return {
        "demographics_gender": fetch_gender_demographics(youtube_analytics, start_date=start_date, end_date=end_date),
        "demographics_age": fetch_age_demographics(youtube_analytics, start_date=start_date, end_date=end_date),
        "demographics_age_gender": fetch_demographics(youtube_analytics, start_date=start_date, end_date=end_date),
        "subscribed_status": fetch_subscribed_status(youtube_analytics, start_date=start_date, end_date=end_date),
        "content_types": fetch_content_types(youtube_analytics, start_date=start_date, end_date=end_date),
        "device_types": fetch_device_types(youtube_analytics, start_date=start_date, end_date=end_date),
        "operating_systems": fetch_operating_systems(youtube_analytics, start_date=start_date, end_date=end_date),
        "traffic_sources": fetch_traffic_sources(youtube_analytics, start_date=start_date, end_date=end_date),
        "geography_countries": fetch_geography(youtube_analytics, start_date=start_date, end_date=end_date),
        "playback_locations": fetch_playback_locations(youtube_analytics, start_date=start_date, end_date=end_date),
        "sharing_services": fetch_sharing_services(youtube_analytics, start_date=start_date, end_date=end_date),
        "daily_timeline": fetch_daily_timeline(youtube_analytics, start_date=start_date, end_date=end_date)
    }


def fetch_per_video_studio_analytics(
    youtube_analytics,
    video_ids: List[str],
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01",
    progress_callback: Optional[Callable] = None
) -> Dict[str, pd.DataFrame]:
    """
    Fetches per-video breakdowns for device types, traffic sources, and demographics (where available).
    """
    all_devices = []
    all_traffic = []
    all_demographics = []
    all_gender = []
    all_age = []
    all_subscribed = []
    all_geography = []
    
    total = len(video_ids)
    for idx, vid in enumerate(video_ids):
        # 1. Video Device Breakdown
        df_dev = fetch_device_types(youtube_analytics, video_id=vid, start_date=start_date, end_date=end_date)
        if not df_dev.empty:
            df_dev["video_id"] = vid
            all_devices.append(df_dev)
            
        # 2. Video Traffic Sources
        df_tr = fetch_traffic_sources(youtube_analytics, video_id=vid, start_date=start_date, end_date=end_date)
        if not df_tr.empty:
            df_tr["video_id"] = vid
            all_traffic.append(df_tr)
            
        # 3. Video Demographics (Combined Age & Gender)
        df_demo = fetch_demographics(youtube_analytics, video_id=vid, start_date=start_date, end_date=end_date)
        if not df_demo.empty:
            df_demo["video_id"] = vid
            all_demographics.append(df_demo)
            
        # 4. Video Gender Demographics (Standalone)
        df_g = fetch_gender_demographics(youtube_analytics, video_id=vid, start_date=start_date, end_date=end_date)
        if not df_g.empty:
            df_g["video_id"] = vid
            all_gender.append(df_g)

        # 5. Video Age Demographics (Standalone)
        df_a = fetch_age_demographics(youtube_analytics, video_id=vid, start_date=start_date, end_date=end_date)
        if not df_a.empty:
            df_a["video_id"] = vid
            all_age.append(df_a)

        # 6. Video Subscribed Status Breakdown
        df_s = fetch_subscribed_status(youtube_analytics, video_id=vid, start_date=start_date, end_date=end_date)
        if not df_s.empty:
            df_s["video_id"] = vid
            all_subscribed.append(df_s)

        # 7. Video Top Geography (Countries)
        df_geo = fetch_geography(youtube_analytics, video_id=vid, start_date=start_date, end_date=end_date, max_results=5)
        if not df_geo.empty:
            df_geo["video_id"] = vid
            all_geography.append(df_geo)
            
        if progress_callback:
            progress_callback(idx + 1)
            
    return {
        "video_device_breakdown": pd.concat(all_devices, ignore_index=True) if all_devices else pd.DataFrame(),
        "video_traffic_breakdown": pd.concat(all_traffic, ignore_index=True) if all_traffic else pd.DataFrame(),
        "video_demographics_breakdown": pd.concat(all_demographics, ignore_index=True) if all_demographics else pd.DataFrame(),
        "video_gender_breakdown": pd.concat(all_gender, ignore_index=True) if all_gender else pd.DataFrame(),
        "video_age_breakdown": pd.concat(all_age, ignore_index=True) if all_age else pd.DataFrame(),
        "video_subscribed_breakdown": pd.concat(all_subscribed, ignore_index=True) if all_subscribed else pd.DataFrame(),
        "video_geography_breakdown": pd.concat(all_geography, ignore_index=True) if all_geography else pd.DataFrame()
    }


def fetch_playlists_analytics(
    youtube_analytics,
    playlists_df: pd.DataFrame,
    start_date: str = "2000-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """
    Queries YouTube Analytics API v2 for playlist performance metrics:
    playlistStarts, viewsPerPlaylistStart, averageTimeInPlaylist, estimatedMinutesWatched, views
    """
    if playlists_df.empty:
        return pd.DataFrame()

    results = []
    for _, row in playlists_df.iterrows():
        p_id = row.get("playlist_id")
        if not p_id:
            continue
        try:
            df = _execute_query(
                youtube_analytics,
                ids="channel==MINE",
                startDate=start_date,
                endDate=end_date,
                metrics="views,estimatedMinutesWatched,playlistStarts,viewsPerPlaylistStart,averageTimeInPlaylist",
                filters=f"playlist=={p_id}"
            )
            if not df.empty:
                r = df.iloc[0].to_dict()
                r["playlist_id"] = p_id
                starts = float(r.get("playlistStarts", 0) or 0)
                v_per_start = float(r.get("viewsPerPlaylistStart", 0) or 0)
                avg_time = float(r.get("averageTimeInPlaylist", 0) or 0)
                cur_views = float(r.get("views", 0) or 0)
                cur_mins = float(r.get("estimatedMinutesWatched", 0) or 0)

                if cur_views == 0 and starts > 0:
                    r["views"] = int(round(starts * v_per_start))
                if cur_mins == 0 and starts > 0:
                    r["estimatedMinutesWatched"] = round((starts * avg_time) / 60.0, 1)

                results.append(r)
            else:
                results.append({
                    "playlist_id": p_id,
                    "views": 0,
                    "estimatedMinutesWatched": 0,
                    "playlistStarts": 0,
                    "viewsPerPlaylistStart": 0.0,
                    "averageTimeInPlaylist": 0.0
                })
        except Exception:
            results.append({
                "playlist_id": p_id,
                "views": 0,
                "estimatedMinutesWatched": 0,
                "playlistStarts": 0,
                "viewsPerPlaylistStart": 0.0,
                "averageTimeInPlaylist": 0.0
            })

    df_analytics = pd.DataFrame(results)
    if not df_analytics.empty:
        merged = pd.merge(playlists_df, df_analytics, on="playlist_id", how="left")
        return merged
    return playlists_df

