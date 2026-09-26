from .config import DATA_SOURCES
from .source_loader import load_source


def extract_all():
    extracted_data = {}

    for source, file_path in DATA_SOURCES.items():
        extracted_data[source] = load_source(
            source,
            file_path
        )

    return extracted_data