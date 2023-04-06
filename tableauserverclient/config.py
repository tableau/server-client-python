
# TODO: check for env variables, else set default values


# For when a datasource is over 64MB, break it into 5MB(standard chunk size) chunks
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB
CHUNK_SIZE = CHUNK_SIZE * 12  # that's so sloooooow

DELAY_SLEEP_SECONDS = 60
