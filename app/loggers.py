import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(filename="logs/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("app_logger")