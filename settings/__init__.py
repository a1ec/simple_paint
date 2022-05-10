from loguru import logger
import sys
from pathlib import Path

# obsfuscate file path
p = Path(__file__)
serial_logloc = p.parent / "logs/serialized.log"
debug_logloc = p.parent / "logs/debug.log"


# logger configuration called from main
config = {
    "handlers": [
        {"sink": sys.stdout, "format": "<yellow>{time:YYYY-MM-DD at HH:mm:ss}</> | <level>{level}</level>    | <green>{module}</>:<green>{function}</>:<green>{line}</> - <blue>{message}</> | {elapsed.seconds}"},
        # {"sink": serial_logloc, "serialize": True},
        {"sink": debug_logloc, "format": "<yellow>{time:YYYY-MM-DD at HH:mm:ss}</> | <level>{level}</level>    | <green>{module}</>:<green>{function}</>:<green>{line}</> - <blue>{message}</> | {elapsed.seconds}"}
    ],
    "extra": {"user": "Don Huelo"},
}

# instantiate global logger configs
logger.configure(**config)

if __name__ == "__main__":
    logger.success(f"Logger setup from {p.resolve()}")
    logger.debug(f"serial_logloc: {serial_logloc}")
    logger.debug(f"debug_logloc: {serial_logloc}")

    