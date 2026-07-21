from agent.utils.pii_scrubber import scrub_text_for_pii


def test_scrub_text_for_pii_redacts_common_entities():
    """Test that PII scrubbing function redacts common PII entities."""
    input_text = "Contact John Doe at john.doe@email.com or 555-123-4567."

    result = scrub_text_for_pii(input_text)

    expected = "Contact [PERSON] at [EMAIL_ADDRESS] or [PHONE_NUMBER]."
    assert result == expected
