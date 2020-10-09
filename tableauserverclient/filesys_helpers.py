import os
ALLOWED_SPECIAL = (' ', '.', '_', '-')


def to_filename(string_to_sanitize):
    sanitized = (c for c in string_to_sanitize if c.isalnum() or c in ALLOWED_SPECIAL)
    return "".join(sanitized)


def make_download_path(filepath, filename):
    download_path = None

    if filepath is None:
        download_path = filename

    elif os.path.isdir(filepath):
        download_path = os.path.join(filepath, filename)

    else:
        download_path = filepath + os.path.splitext(filename)[1]

    return download_path


def file_is_compressed(file):
    # Determine if file is a zip file or not
    # This reference lists magic file signatures: https://www.garykessler.net/library/file_sigs.html

    zip_file_signature = b'PK\x03\x04'

    is_zip_file = file.read(len(zip_file_signature)) == zip_file_signature
    file.seek(0)

    return is_zip_file
