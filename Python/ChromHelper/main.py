# code: utf8
import sys
import logging
from pathlib import Path
from datetime import datetime

from jnlib.general_utils import get_log_dir

from chrom_helper import launch

version = [1, 5, 1, 20230817]

ORG_NAME = "JnPrograms"
APP_NAME = "ChromHelper"


def init_logging() -> tuple[bool, str]:
    log_dir = get_log_dir(sys.platform)
    if log_dir is None:
        return False, f"未找到路径"

    app_log_dir = Path(log_dir, ORG_NAME, APP_NAME)
    app_log_dir.mkdir(parents=True, exist_ok=True)

    now_s = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ver_s = f"v{version[0]}.{version[1]}.{version[2]}"
    log_file = Path(app_log_dir, f"{APP_NAME}_{ver_s}_{now_s}.log")

    logging.basicConfig(filename=log_file, encoding="utf8", level=logging.INFO,
                        format="[%(asctime)s][%(funcName)s][%(levelname)s] %(message)s")
    return True, ""


def main():
    has_log, log_err = init_logging()
    launch(ORG_NAME, APP_NAME, has_log, log_err, version)


if __name__ == '__main__':
    main()
