import math
import pandas as pd
import isodate
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

def safe_int(val, default: int = 0) -> int:
    """Safely converts any value (including NaN, None, float, string) to integer."""
    try:
        if val is None or pd.isna(val):
            return default
        return int(float(val))
    except (ValueError, TypeError):
        return default


def parse_iso8601_duration(duration_str: str) -> dict:
    """
    Parses an ISO 8601 duration string (e.g. 'PT1H2M10S', 'PT15M30S', 'PT45S')
    and returns total seconds and formatted duration string.
    """
    if not duration_str:
        return {"duration_seconds": 0, "duration_formatted": "00:00"}
        
    try:
        duration = isodate.parse_duration(duration_str)
        total_seconds = int(duration.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            formatted = f"{minutes:02d}:{seconds:02d}"
            
        return {
            "duration_seconds": total_seconds,
            "duration_formatted": formatted
        }
    except Exception:
        return {"duration_seconds": 0, "duration_formatted": "00:00"}


def calculate_engagement_rate(likes, comments, shares, views) -> float:
    """Calculates engagement percentage relative to total views safely."""
    l = safe_int(likes)
    c = safe_int(comments)
    s = safe_int(shares)
    v = safe_int(views)
    if v <= 0:
        return 0.0
    return round(((l + c + s) / v) * 100, 2)


def resolve_upload_date_range(
    period: Optional[str] = None,
    uploaded_after: Optional[str] = None,
    uploaded_before: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Resolves upload date presets ('this-month', 'last-month', 'this-year', 'last-year', 'last-30d', etc.)
    and explicit date strings into ISO 8601 UTC timestamp strings, respecting the user's local timezone.
    """
    # Get user's local timezone
    local_tz = datetime.now().astimezone().tzinfo
    local_now = datetime.now(local_tz)
    after_str = None
    before_str = None

    if period:
        p = period.lower().strip()
        if p in ["this-month", "this_month"]:
            start_local = datetime(local_now.year, local_now.month, 1, 0, 0, 0, tzinfo=local_tz)
            after_str = start_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            before_str = local_now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif p in ["last-month", "last_month"]:
            first_of_this_month = datetime(local_now.year, local_now.month, 1, tzinfo=local_tz)
            last_day_prev_month = first_of_this_month - timedelta(days=1)
            start_prev_month = datetime(last_day_prev_month.year, last_day_prev_month.month, 1, 0, 0, 0, tzinfo=local_tz)
            end_prev_month = datetime(last_day_prev_month.year, last_day_prev_month.month, last_day_prev_month.day, 23, 59, 59, tzinfo=local_tz)
            after_str = start_prev_month.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            before_str = end_prev_month.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif p in ["this-year", "this_year"]:
            start_local = datetime(local_now.year, 1, 1, 0, 0, 0, tzinfo=local_tz)
            after_str = start_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            before_str = local_now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif p in ["last-year", "last_year"]:
            prev_year = local_now.year - 1
            start_prev = datetime(prev_year, 1, 1, 0, 0, 0, tzinfo=local_tz)
            end_prev = datetime(prev_year, 12, 31, 23, 59, 59, tzinfo=local_tz)
            after_str = start_prev.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            before_str = end_prev.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif p in ["last-7-days", "last-7d", "last_7d", "7d"]:
            start_local = local_now - timedelta(days=7)
            after_str = start_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            before_str = local_now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif p in ["last-30-days", "last-30d", "last_30d", "30d"]:
            start_local = local_now - timedelta(days=30)
            after_str = start_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            before_str = local_now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif p in ["last-90-days", "last-90d", "last_90d", "90d"]:
            start_local = local_now - timedelta(days=90)
            after_str = start_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            before_str = local_now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif p in ["last-365-days", "last-365d", "last_365d", "365d"]:
            start_local = local_now - timedelta(days=365)
            after_str = start_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            before_str = local_now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if uploaded_after:
        if len(uploaded_after) == 10:  # YYYY-MM-DD in local time
            parts = [int(x) for x in uploaded_after.split("-")]
            start_local = datetime(parts[0], parts[1], parts[2], 0, 0, 0, tzinfo=local_tz)
            after_str = start_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            after_str = uploaded_after

    if uploaded_before:
        if len(uploaded_before) == 10:  # YYYY-MM-DD in local time
            parts = [int(x) for x in uploaded_before.split("-")]
            end_local = datetime(parts[0], parts[1], parts[2], 23, 59, 59, tzinfo=local_tz)
            before_str = end_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            before_str = uploaded_before

    return after_str, before_str
