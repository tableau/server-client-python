import logging

# TODO change: this defaults to logging *everything* to stdout
logger = logging.getLogger("TSC")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
