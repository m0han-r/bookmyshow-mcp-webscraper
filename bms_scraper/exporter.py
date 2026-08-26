"""
Data Export Utility for BookMyShow Web Scraper.
Supports exporting lists of models to JSON, CSV, and Excel.
"""

import json
import csv
from typing import List, Any
import pandas as pd
from pydantic import BaseModel


class DataExporter:

    @staticmethod
    def to_json(data: List[BaseModel], file_path: str, indent: int = 2) -> str:
        """Exports pydantic models list to a JSON file."""
        dicts = [item.model_dump() for item in data] if data and isinstance(data[0], BaseModel) else data
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dicts, f, indent=indent, default=str)
        return file_path

    @staticmethod
    def to_csv(data: List[BaseModel], file_path: str) -> str:
        """Exports pydantic models list to a CSV file."""
        if not data:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")
            return file_path

        dicts = [item.model_dump() for item in data] if isinstance(data[0], BaseModel) else data
        df = pd.DataFrame(dicts)
        df.to_csv(file_path, index=False, encoding="utf-8")
        return file_path

    @staticmethod
    def to_excel(data: List[BaseModel], file_path: str) -> str:
        """Exports pydantic models list to an Excel (.xlsx) file."""
        if not data:
            df = pd.DataFrame()
        else:
            dicts = [item.model_dump() for item in data] if isinstance(data[0], BaseModel) else data
            df = pd.DataFrame(dicts)

        df.to_excel(file_path, index=False)
        return file_path
