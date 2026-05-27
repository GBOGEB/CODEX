"""Shared utilities for metric display name normalization across visualization scripts."""

# Maximum length for abbreviated metric names
MAX_ABBREVIATION_LENGTH = 6


def normalize_metric_name(key: str) -> str:
    """
    Convert a metric key to a human-readable display name.
    
    Args:
        key: Metric key from PROGRAM_METRICS.yaml (e.g., 'ci_cd', 'publication_readiness')
    
    Returns:
        Human-readable display name (e.g., 'CI/CD', 'Publication')
    """
    display_name = key.replace('_', ' ').title()
    
    # Special case mappings
    if display_name == 'Ci Cd':
        display_name = 'CI/CD'
    elif display_name == 'Publication Readiness':
        display_name = 'Publication'
    
    return display_name


def abbreviate_metric_name(display_name: str) -> str:
    """
    Create an abbreviated version of a metric display name for compact visualizations.
    
    Args:
        display_name: Full display name (e.g., 'Governance', 'Orchestration')
    
    Returns:
        Abbreviated name (e.g., 'Gov', 'Orch')
    """
    # Special case abbreviations
    abbreviations = {
        'Governance': 'Gov',
        'Orchestration': 'Orch',
        'Visualization': 'Visual',
        'Thermodynamics': 'Thermo',
        'Validation': 'Valid',
        'Publication': 'Pub',
    }
    
    if display_name in abbreviations:
        return abbreviations[display_name]
    
    # Default: truncate to MAX_ABBREVIATION_LENGTH characters
    return display_name[:MAX_ABBREVIATION_LENGTH]
