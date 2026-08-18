import pandas as pd
from typing import Callable, Optional, Dict, Tuple
from utils.formatting import parse_iso8601_duration, calculate_engagement_rate

def fetch_channel_info(youtube_data) -> Dict:
    """Fetches overview details for the authorized channel."""
    res = youtube_data.channels().list(
        mine=True,
        part="snippet,contentDetails,statistics,topicDetails"
    ).execute()
    
    if not res.get("items"):
        raise ValueError("No YouTube channel found for the authenticated user.")
        
    item = res["items"][0]
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    content = item.get("contentDetails", {})
    uploads_playlist_id = content.get("relatedPlaylists", {}).get("uploads")
    
    return {
        "channel_id": item["id"],
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "custom_url": snippet.get("customUrl"),
        "published_at": snippet.get("publishedAt"),
        "country": snippet.get("country"),
        "views": int(stats.get("viewCount", 0)),
        "subscribers": int(stats.get("subscriberCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "uploads_playlist_id": uploads_playlist_id
    }


def fetch_all_video_ids(
    youtube_data,
    uploads_playlist_id: str,
    uploaded_after: Optional[str] = None,
    uploaded_before: Optional[str] = None,
    progress_callback: Optional[Callable] = None
) -> list:
    """
    Retrieves video IDs from the uploads playlist with optional upload date filtering.
    Leverages YouTube's reverse-chronological order to early-exit as soon as older videos are reached.
    """
    video_ids = []
    next_page_token = None
    stop_pagination = False
    
    while not stop_pagination:
        playlist_res = youtube_data.playlistItems().list(
            playlistId=uploads_playlist_id,
            part="contentDetails,snippet",
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        
        items = playlist_res.get("items", [])
        if not items:
            break

        for item in items:
            content_details = item.get("contentDetails", {})
            snippet = item.get("snippet", {})
            vid = content_details.get("videoId") or snippet.get("resourceId", {}).get("videoId")
            pub_time = content_details.get("videoPublishedAt") or snippet.get("publishedAt", "")
            
            if not vid:
                continue

            # If video is newer than uploaded_before, skip it and continue looking
            if uploaded_before and pub_time and pub_time > uploaded_before:
                continue

            # If video is older than uploaded_after, since playlist is sorted newest-first,
            # all subsequent videos will also be older -> Early Exit!
            if uploaded_after and pub_time and pub_time < uploaded_after:
                stop_pagination = True
                break

            video_ids.append(vid)
            
        if progress_callback:
            progress_callback(len(video_ids))
            
        next_page_token = playlist_res.get("nextPageToken")
        if not next_page_token:
            break
            
    return video_ids


def fetch_video_metadata(
    youtube_data,
    video_ids: list,
    progress_callback: Optional[Callable] = None
) -> pd.DataFrame:
    """
    Fetches rich metadata for a list of video IDs in batches of 50.
    """
    video_data = []
    total_ids = len(video_ids)
    
    for i in range(0, total_ids, 50):
        batch_ids = ",".join(video_ids[i:i+50])
        v_res = youtube_data.videos().list(
            id=batch_ids,
            part="snippet,contentDetails,statistics,status,topicDetails,liveStreamingDetails"
        ).execute()
        
        for item in v_res.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            status = item.get("status", {})
            topics = item.get("topicDetails", {})
            live = item.get("liveStreamingDetails", {})
            
            raw_duration = content.get("duration", "")
            duration_info = parse_iso8601_duration(raw_duration)
            
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
            
            tags = snippet.get("tags", [])
            tag_string = ", ".join(tags) if isinstance(tags, list) else ""
            
            topic_categories = topics.get("topicCategories", [])
            topic_str = ", ".join([t.split("/")[-1] for t in topic_categories]) if topic_categories else ""
            
            video_data.append({
                "video_id": item["id"],
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "published_at": snippet.get("publishedAt"),
                "duration_seconds": duration_info["duration_seconds"],
                "duration_formatted": duration_info["duration_formatted"],
                "definition": content.get("definition"),
                "caption": content.get("caption"),
                "has_captions": content.get("caption") == "true",
                "default_language": snippet.get("defaultLanguage", ""),
                "default_audio_language": snippet.get("defaultAudioLanguage", ""),
                "content_format": "Shorts" if (duration_info["duration_seconds"] > 0 and duration_info["duration_seconds"] <= 60) else ("Live" if bool(live) else "VOD"),
                "licensed_content": content.get("licensedContent", False),
                "privacy_status": status.get("privacyStatus"),
                "embeddable": status.get("embeddable", True),
                "made_for_kids": status.get("madeForKids", False),
                "category_id": snippet.get("categoryId"),
                "tags": tag_string,
                "topics": topic_str,
                "views": views,
                "likes": likes,
                "comments": comments,
                "is_live_content": bool(live),
                "live_actual_start": live.get("actualStartTime", ""),
                "live_actual_end": live.get("actualEndTime", "")
            })
            
        if progress_callback:
            progress_callback(min(i + 50, total_ids))
            
    return pd.DataFrame(video_data)


def fetch_playlists_info(youtube_data) -> pd.DataFrame:
    """Fetches all playlists created on the channel."""
    playlists = []
    next_page_token = None

    while True:
        res = youtube_data.playlists().list(
            mine=True,
            part="snippet,contentDetails,status",
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in res.get("items", []):
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})
            status = item.get("status", {})
            playlists.append({
                "playlist_id": item["id"],
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "published_at": snippet.get("publishedAt"),
                "item_count": int(content.get("itemCount", 0)),
                "privacy_status": status.get("privacyStatus"),
            })

        next_page_token = res.get("nextPageToken")
        if not next_page_token:
            break

    return pd.DataFrame(playlists)


def fetch_playlist_video_ids(
    youtube_data,
    playlist_id: str,
    uploaded_after: Optional[str] = None,
    uploaded_before: Optional[str] = None,
    progress_callback: Optional[Callable] = None
) -> list:
    """
    Retrieves video IDs from a specific playlist, respecting optional upload date filters.
    """
    video_ids = []
    next_page_token = None

    while True:
        res = youtube_data.playlistItems().list(
            playlistId=playlist_id,
            part="contentDetails,snippet",
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in res.get("items", []):
            content_details = item.get("contentDetails", {})
            snippet = item.get("snippet", {})
            vid = content_details.get("videoId") or snippet.get("resourceId", {}).get("videoId")
            pub_time = content_details.get("videoPublishedAt") or snippet.get("publishedAt", "")

            if not vid:
                continue

            if uploaded_after and pub_time and pub_time < uploaded_after:
                continue
            if uploaded_before and pub_time and pub_time > uploaded_before:
                continue

            video_ids.append(vid)

        if progress_callback:
            progress_callback(len(video_ids))

        next_page_token = res.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids


