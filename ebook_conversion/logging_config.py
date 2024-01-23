import logging

def start_loggers():
  error_logger = logging.getLogger('error_logger')
  error_logger.setLevel(logging.ERROR)
  error_handler = logging.FileHandler('error.log')
  error_formatter = logging.Formatter('%(asctime)s - %(name)s - ERROR - %(message)s')
  error_handler.setFormatter(error_formatter)
  error_logger.addHandler(error_handler)

  info_logger = logging.getLogger('info_logger')
  info_logger.setLevel(logging.INFO)
  info_handler = logging.FileHandler('info.log')
  info_formatter = logging.Formatter('%(asctime)s - %(name)s - INFO - %(message)s')
  info_handler.setFormatter(info_formatter)
  info_logger.addHandler(info_handler)
