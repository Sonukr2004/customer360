const API_BASE_URL = "http://127.0.0.1:8000";

export async function getQualityData() {
  const response = await fetch(
    `${API_BASE_URL}/api/quality`
  );

  let data = null;

  try {
    data = await response.json();
  } catch {
    // Backend did not return JSON.
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        `Failed to load data quality: ${response.status}`
    );
  }

  return data;
}