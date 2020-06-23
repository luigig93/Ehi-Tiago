import logging

# only one handler for all loggers
# create file handler
file_handler = logging.FileHandler('robot.log')
file_handler.setLevel(logging.DEBUG)

# create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s','%a %d/%b/%Y %H:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)


def create_logger(logger_name, log_level):
    # create logger
    logger = logging.getLogger(logger_name)

    # select log level
    if log_level == "debug":
        logger.setLevel(logging.DEBUG)
    elif log_level == "info":
        logger.setLevel(logging.INFO)
    elif log_level == "warning":
        logger.setLevel(logging.WARNING)
    elif log_level == "error":
        logger.setLevel(logging.ERROR)

    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

