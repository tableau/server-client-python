# TODO: check for env variables, else set default values

ALLOWED_FILE_EXTENSIONS = ["tds", "tdsx", "tde", "hyper", "parquet"]

BYTES_PER_MB = 1024 * 1024

# For when a datasource is over 64MB, break it into 5MB(standard chunk size) chunks
CHUNK_SIZE_MB = 5 * 10  # 5MB felt too slow, upped it to 50

DELAY_SLEEP_SECONDS = 0.1

# The maximum size of a file that can be published in a single request is 64MB
FILESIZE_LIMIT_MB = 64
