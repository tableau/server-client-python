ALLOWED_SPECIAL = (' ', '.', '_', '-')


def to_filename(string_to_sanitize):
    sanitized = (c for c in string_to_sanitize if c.isalnum() or c in ALLOWED_SPECIAL)
    return "".join(sanitized)
