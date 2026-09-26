from pathlib import Path
import json

import pandas as pd

from .csv_loader import load_csv


def load_source(source: str, file_path: str) -> dict[str, pd.DataFrame]:
	path = Path(file_path)
	if not path.is_absolute():
		path = Path(__file__).resolve().parents[1] / path

	if not path.is_file():
		raise FileNotFoundError(
			f"Input file for source '{source}' was not found: {path}"
		)

	if path.suffix.lower() == ".csv":
		data = load_csv(str(path))
	elif path.suffix.lower() == ".jsonl":
		data = pd.read_json(path, lines=True)
	elif path.suffix.lower() == ".json":
		content = path.read_text(encoding="utf-8")
		json_start = next(
			(index for index in (content.find("{"), content.find("[")) if index >= 0),
			-1,
		)
		if json_start == -1:
			raise ValueError(f"No JSON object or array found for source '{source}': {path}")
		parsed_json, _ = json.JSONDecoder().raw_decode(content, json_start)
		data = pd.json_normalize(parsed_json)
	else:
		raise ValueError(
			f"Unsupported file type for source '{source}': {path.suffix}"
		)

	return {"data": data}
