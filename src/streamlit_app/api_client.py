import logging

import requests

BACKEND_URL = "http://localhost:8000/generate-report"


def trigger_report_generation(data: dict) -> bytes | None:
    """
    Communicate with the backend to trigger report generation.

    Args:
        data: Dictionary containing report parameters

    Returns:
        Response content as bytes if successful, None otherwise
    """
    payload = data

    try:
        response = requests.post(BACKEND_URL, json=payload)

        if response.status_code == 200:
            return response.content
        else:
            logging.error(f"Backend returned status code {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None
