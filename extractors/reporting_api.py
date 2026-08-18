import os
import requests
import pandas as pd
from typing import List, Dict, Optional

STANDARD_REPORT_TYPES = [
    "channel_basic_a2",
    "channel_playback_location_a2",
    "channel_traffic_source_a2",
    "channel_device_os_a2",
    "channel_demographics_a1",
    "channel_combined_a2"
]

def list_reporting_jobs(youtube_reporting) -> List[Dict]:
    """Lists existing reporting jobs."""
    res = youtube_reporting.jobs().list().execute()
    return res.get("jobs", [])


def create_standard_reporting_jobs(youtube_reporting) -> List[Dict]:
    """
    Creates standard bulk reporting jobs if they do not exist yet.
    YouTube generates daily CSV reports for active jobs.
    """
    existing_jobs = list_reporting_jobs(youtube_reporting)
    existing_types = {j.get("reportTypeId") for j in existing_jobs}
    
    created_jobs = []
    for rtype in STANDARD_REPORT_TYPES:
        if rtype not in existing_types:
            job_body = {
                "reportTypeId": rtype,
                "name": f"CLI Job - {rtype}"
            }
            try:
                job = youtube_reporting.jobs().create(body=job_body).execute()
                created_jobs.append(job)
            except Exception as e:
                print(f"Warning: Failed to create reporting job for '{rtype}': {e}")
                
    return created_jobs


def download_reporting_jobs_data(
    youtube_reporting,
    credentials,
    output_dir: str = "output/reports"
) -> List[str]:
    """
    Checks all active reporting jobs and downloads available report CSV files.
    """
    os.makedirs(output_dir, exist_ok=True)
    jobs = list_reporting_jobs(youtube_reporting)
    downloaded_files = []
    
    headers = {"Authorization": f"Bearer {credentials.token}"}
    
    for job in jobs:
        job_id = job.get("id")
        report_type = job.get("reportTypeId", "report")
        
        try:
            reports_res = youtube_reporting.jobs().reports().list(jobId=job_id).execute()
            reports = reports_res.get("reports", [])
            
            for rep in reports:
                download_url = rep.get("downloadUrl")
                create_time = rep.get("createTime", "unknown").replace(":", "-")
                
                if download_url:
                    filename = f"{report_type}_{create_time}.csv"
                    filepath = os.path.join(output_dir, filename)
                    
                    if not os.path.exists(filepath):
                        r = requests.get(download_url, headers=headers)
                        if r.status_code == 200:
                            with open(filepath, "wb") as f:
                                f.write(r.content)
                            downloaded_files.append(filepath)
        except Exception as e:
            print(f"Warning: Could not fetch reports for job {job_id}: {e}")
            
    return downloaded_files
