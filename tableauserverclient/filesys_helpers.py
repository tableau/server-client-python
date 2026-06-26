import os

ALLOWED_SPECIAL = (" ", ".", "_", "-")


def to_filename(string_to_sanitize):
    """Strip characters from a string that are not safe for use in a filename."""
    sanitized = (c for c in string_to_sanitize if c.isalnum() or c in ALLOWED_SPECIAL)
    return "".join(sanitized)


def make_download_path(filepath, filename):
    """Resolve a download destination path from an optional target filepath and the server-provided filename."""
    download_path = None

    if filepath is None:
        download_path = filename

    elif os.path.isdir(filepath):
        download_path = os.path.join(filepath, filename)

    else:
        download_path = filepath + os.path.splitext(filename)[1]

    return download_path


def get_file_object_size(file):
    """Return the size in bytes of an open binary file object."""
    # Returns the size of a file object
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    return file_size


def get_file_type(file):
    """Detect the type of an open binary file by inspecting its magic bytes, returning one of 'zip', 'tde', 'xml', or 'hyper'."""
    # Tableau workbooks (twb) and data sources (tds) are both stored as xml files.
    # Packaged workbooks (twbx) and data sources (tdsx) are zip files
    # containing original files accompanied with supporting local files.

    # This reference lists magic file signatures: https://www.garykessler.net/library/file_sigs.html
    MAGIC_BYTES = {
        "zip": bytes.fromhex("504b0304"),
        "tde": bytes.fromhex("20020162"),
        "xml": bytes.fromhex("3c3f786d6c20"),
        "hyper": bytes.fromhex("487970657208000001000000"),
    }

    # Peek first bytes of a file
    first_bytes = file.read(32)

    file_type = None
    for ft, signature in MAGIC_BYTES.items():
        if first_bytes.startswith(signature):
            file_type = ft
            break

    # Return pointer back to start
    file.seek(0)

    if file_type is None:
        error = "Unknown file type!"
        raise ValueError(error)

    return file_type
