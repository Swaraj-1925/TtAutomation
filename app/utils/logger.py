import logging
import colorlog

logger = logging.getLogger("TtAutomation")

logger.setLevel(logging.DEBUG)
handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    '%(white)s%(asctime)s %(levelname_log_color)s%(levelname)s %(white)s%(funcName)s %(reset)s- %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',  # Logcat-style date-time
    reset=True,  # Reset color after each log line
    log_colors={
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    },
    secondary_log_colors={
        'levelname': {
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    },
    style='%'
)
handler.setFormatter(formatter)
logger.addHandler(handler)