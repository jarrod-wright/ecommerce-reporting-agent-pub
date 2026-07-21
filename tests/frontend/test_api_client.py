from unittest.mock import Mock, patch

from streamlit_app.api_client import trigger_report_generation


def test_trigger_report_generation_success():
    mock_response = Mock()
    mock_response.content = b'{"report_id": "12345", "status": "success"}'
    mock_response.status_code = 200

    with patch('requests.post', return_value=mock_response) as mock_post:
        sample_data = {
            "store_name": "Example Store",
            "date_range": "last_30_days"
        }

        result = trigger_report_generation(sample_data)

        mock_post.assert_called_once_with(
            "http://localhost:8000/generate-report",
            json=sample_data
        )
        assert result == mock_response.content
