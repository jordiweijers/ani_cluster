import os
import sys
import logging
from datetime import datetime

def setup_logging(output_dir, log_name="script.log"):
	"""
	Set up logging to file and console.
	Args:
		output_dir (str): Directory where to log file will be created.
		log_name (str): Name of the log file (default: script.log).
	Returns:
		logger (logging.Logger): Configured logger instance.
	"""
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	log_file = os.path.join(output_dir, f"{log_name}_{timestamp}")
	logger = logging.getLogger("main_logger")
	logger.setLevel(logging.DEBUG)
	if logger.hasHandlers():
		logger.handlers.clear()
	# Console handler
	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)
	console_formatter = logging.Formatter("%(message)s")
	console_handler.setFormatter(console_formatter)
	logger.addHandler(console_handler)
	# File handler
	file_handler = logging.FileHandler(log_file, mode="w")
	file_handler.setLevel(logging.DEBUG)
	file_formatter = logging.Formatter(
		"[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S"
	)
	file_handler.setFormatter(file_formatter)
	logger.addHandler(file_handler)
	return logger
