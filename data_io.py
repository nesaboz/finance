from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "data.json"


def ensure_data_file_exists() -> None:
	"""
	Ensure data.json exists; stop execution if missing.
	"""
	if not DATA_PATH.exists():
		st.error(f"Missing data file: {DATA_PATH}. Please create it and retry.")
		st.stop()


def load_data() -> Dict[str, Any]:
	"""
	Load persisted app data from data.json; no in-code defaults.
	"""
	ensure_data_file_exists()
	try:
		with DATA_PATH.open("r") as f:
			data: Dict[str, Any] = json.load(f)
	except json.JSONDecodeError:
		st.error("Invalid JSON in data.json. Please fix the file contents.")
		st.stop()
	return data


def save_data(data: Dict[str, Any]) -> None:
	"""
	Persist the given data back to data.json.
	"""
	with DATA_PATH.open("w") as f:
		json.dump(data, f, indent=2)


