import logging
import coloredlogs

logger = logging.getLogger("DummyMessenger")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(" "message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
coloredlogs.install(
    level="INFO",
    logger=logger,
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    field_styles={
        "asctime": {"color": "white"},
        "name": {"color": "white"},
        "levelname": {"color": "white"},
        "message": {"color": "white"},
    },
    level_styles={
        "info": {"color": "green"},
        "warning": {"color": "yellow"},
        "error": {"color": "red"},
        "critical": {"color": "red", "bold": True},
    },
)