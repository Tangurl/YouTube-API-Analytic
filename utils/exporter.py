import os
import json
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict

def export_data(
    dfs: Dict[str, pd.DataFrame],
    output_dir: str,
    export_format: str = "all",
    file_prefix: str = "youtube_channel_data"
) -> Dict[str, str]:
    """
    Exports a dictionary of DataFrames to specified formats.
    Each run cleanly writes the exact dataset queried in that run with data freshness timestamps.
    
    Args:
        dfs: Dictionary of table names to DataFrames (e.g. {'videos_full_data': df})
        output_dir: Target directory path
        export_format: 'csv', 'excel', 'json', 'sqlite', or 'all'
        file_prefix: Base prefix for exported files
        
    Returns:
        Dictionary mapping export format to exported file path(s).
    """
    os.makedirs(output_dir, exist_ok=True)
    current_time_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    exported_files = {}

    final_dfs = {}
    for name, df in dfs.items():
        if df is not None and not df.empty:
            df_to_save = df.copy()
            if "last_updated_at" not in df_to_save.columns:
                df_to_save["last_updated_at"] = current_time_iso
            final_dfs[name] = df_to_save

    formats = ['csv', 'excel', 'json', 'sqlite'] if export_format == 'all' else [export_format]

    # 1. CSV Export
    if 'csv' in formats:
        csv_files = []
        for name, df in final_dfs.items():
            path = os.path.join(output_dir, f"{file_prefix}_{name}.csv")
            df.to_csv(path, index=False, encoding="utf-8-sig")
            csv_files.append(path)
        if csv_files:
            exported_files['csv'] = ", ".join(csv_files)

    # 2. Excel Export (Multi-tab)
    if 'excel' in formats:
        excel_path = os.path.join(output_dir, f"{file_prefix}_full.xlsx")
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            for name, df in final_dfs.items():
                sheet_name = name[:30]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        exported_files['excel'] = excel_path

    # 3. JSON Export
    if 'json' in formats:
        json_files = []
        for name, df in final_dfs.items():
            path = os.path.join(output_dir, f"{file_prefix}_{name}.json")
            df.to_json(path, orient="records", indent=2, force_ascii=False)
            json_files.append(path)
        if json_files:
            exported_files['json'] = ", ".join(json_files)

    # 4. SQLite Export
    if 'sqlite' in formats:
        sqlite_path = os.path.join(output_dir, f"{file_prefix}.db")
        conn = sqlite3.connect(sqlite_path)
        for name, df in final_dfs.items():
            table_name = name.replace(" ", "_").lower()
            df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        exported_files['sqlite'] = sqlite_path

    return exported_files
