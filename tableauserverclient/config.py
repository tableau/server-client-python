import os

ALLOWED_FILE_EXTENSIONS = ["tds", "tdsx", "tde", "hyper", "parquet"]

BYTES_PER_MB = 1024 * 1024

DELAY_SLEEP_SECONDS = 0.1


class Config:
    """Runtime configuration for TSC, controllable via environment variables."""

    # The maximum size of a file that can be published in a single request is 64MB
    @property
    def FILESIZE_LIMIT_MB(self):
        """Maximum single-request publish size in MB (env: TSC_FILESIZE_LIMIT_MB, capped at 64)."""
        return min(int(os.getenv("TSC_FILESIZE_LIMIT_MB", 64)), 64)

    # For when a datasource is over 64MB, break it into 5MB(standard chunk size) chunks
    @property
    def CHUNK_SIZE_MB(self):
        """Chunk size in MB for multipart publish requests (env: TSC_CHUNK_SIZE_MB)."""
        return int(os.getenv("TSC_CHUNK_SIZE_MB", 5 * 10))  # 5MB felt too slow, upped it to 50

    # Default page size
    @property
    def PAGE_SIZE(self):
        """Default page size for paginated API requests (env: TSC_PAGE_SIZE)."""
        return int(os.getenv("TSC_PAGE_SIZE", 100))


config = Config()
