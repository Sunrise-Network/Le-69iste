import logging
import re

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def extract_number_and_sum(message: str):
    numbers = list(map(int, re.findall(r'\b\d+\b', message)))
    total = sum(numbers)
    return numbers, total

