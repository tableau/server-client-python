
# TODO: check for env variables, else set default values


# For when a datasource is over 64MB, break it into 5MB(standard chunk size) chunks
CHUNK_SIZE = 1024 * 1024 * 5 * 10  # 5MB felt too slow, upped it to 50

DELAY_SLEEP_SECONDS = 10
