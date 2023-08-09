# code: utf8
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

from chrom_helper import launch

version = [1, 3, 0, 20230809]

ORG_NAME = "JnPrograms"
APP_NAME = "ChromHelper"


def init_logging() -> tuple[bool, str]:
    match sys.platform:
        case "win32":
            config_path = os.path.expandvars("%appdata%")
        case "darwin":
            config_path = os.path.expanduser("~")
        case _:
            return False, "不支持的操作系统"
    config_path = Path(config_path)
    if not config_path.exists():
        return False, f"未找到路径 [{config_path}]"

    config_path = Path(config_path, ORG_NAME, APP_NAME)
    config_path.mkdir(parents=True, exist_ok=True)

    now_s = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ver_s = f"v{version[0]}.{version[1]}.{version[2]}"
    config_path = Path(config_path, f"{APP_NAME}_{ver_s}_{now_s}.log")

    logging.basicConfig(filename=config_path, encoding="utf8", level=logging.INFO,
                        format="[%(asctime)s][%(funcName)s][%(levelname)s] %(message)s")
    return True, ""


def main():
    has_log, log_err = init_logging()
    launch(ORG_NAME, APP_NAME, has_log, log_err, version)


if __name__ == '__main__':
    main()
