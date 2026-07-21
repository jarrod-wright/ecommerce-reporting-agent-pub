from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


def scrub_text_for_pii(text: str) -> str:
    """
    Scrub PII from text using Presidio analyzer and anonymizer.

    Args:
        text: Input text that may contain PII

    Returns:
        Text with PII replaced by entity type placeholders
    """
    # Initialize engines
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    # Find PII entities in the text
    results = analyzer.analyze(text=text, language='en')

    # Configure anonymization to replace with entity type in square brackets
    operators = {}
    for entity_type in {result.entity_type for result in results}:
        operators[entity_type] = OperatorConfig(
            "replace", {"new_value": f"[{entity_type}]"}
        )

    # Anonymize the text
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=operators
    )

    return anonymized_result.text
