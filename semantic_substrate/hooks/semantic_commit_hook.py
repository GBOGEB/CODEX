import re
import sys

REQUIRED_PATTERNS = [
    r'INV-[0-9]{3}',
    r'DELTA-[0-9]{4}',
    r'TUP-[0-9]{4}',
]


def validate_commit_message(message: str):
    found = any(re.search(pattern, message) for pattern in REQUIRED_PATTERNS)
    return found


if __name__ == '__main__':
    commit_message = sys.argv[1] if len(sys.argv) > 1 else ''

    if not validate_commit_message(commit_message):
        print('Semantic commit validation failed.')
        print('Expected semantic references such as INV-001, DELTA-0001, or TUP-0001.')
        sys.exit(1)

    print('Semantic commit validation passed.')
    sys.exit(0)
