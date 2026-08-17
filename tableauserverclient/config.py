import os

ALLOWED_FILE_EXTENSIONS = ["tds", "tdsx", "tde", "hyper", "parquet"]

BYTES_PER_MB = 1024 * 1024

DELAY_SLEEP_SECONDS = 0.1


class Config:
    # The maximum size of a file that can be published in a single request is 64MB
    @property
    def FILESIZE_LIMIT_MB(self):
        return min(int(os.getenv("TSC_FILESIZE_LIMIT_MB", 64)), 64)

    # For when a datasource is over 64MB, break it into 5MB(standard chunk size) chunks
    # Applies to *upload* / chunked publish. Downloads use DOWNLOAD_CHUNK_SIZE_MB.
    @property
    def CHUNK_SIZE_MB(self):
        return int(os.getenv("TSC_CHUNK_SIZE_MB", 5 * 10))  # 5MB felt too slow, upped it to 50

    # Chunk size for streaming *downloads* (view CSV / Excel / PDF, workbook /
    # datasource / flow downloads). Kept separate from the upload knob because
    # a large read chunk delays the first-byte yield on slow connections --
    # requests.iter_content buffers up to chunk_size before yielding, so on a
    # 1 Mbps link a 50 MB chunk means ~7 minutes before the first yield.
    # 1 MB is empirically a reasonable balance between per-chunk overhead and
    # progressive-yield latency; callers who want a different tradeoff can
    # tune via TSC_DOWNLOAD_CHUNK_SIZE_MB.
    @property
    def DOWNLOAD_CHUNK_SIZE_MB(self):
        return int(os.getenv("TSC_DOWNLOAD_CHUNK_SIZE_MB", 1))

    # Default page size
    @property
    def PAGE_SIZE(self):
        return int(os.getenv("TSC_PAGE_SIZE", 100))


config = Config()
