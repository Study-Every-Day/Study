# -*- encoding: utf-8 -*-
# here put the import lib
import sys
sys.path.append(".")  # noqa
sys.path.append("..")  # noqa
import os.path as osp
import time
import random
import logging

from study.config import cfg
from study.study import Study
from study.utils import check_webdriver, setup_logger, push_wechat


def default_setup(cfg, sys_argv):
    cfg.parse_from_sys_argv(sys_argv)
    time_str = time.strftime('%Y_%m_%d', time.localtime())
    log_file = osp.join(cfg.OUTPUT_PATH, f"runtime_{time_str}.log")
    setup_logger(log_file, name="root")
    logger = setup_logger(log_file)
    if cfg.SHOW_CONFIG:
        logger.info("config: \n{}".format(cfg))
    logger.info("正在检查运行环境 ...")
    check_webdriver()


def push_error(error_info):
    logger = logging.getLogger("study")
    logger.info("正在将错误信息推送至微信 ...")
    push_content = "\n\n".join([
        "# 😔 XXQG错误通知 🙈",
        "产生错误如下:",
        error_info,
        "> 请联系管理员修复。",
    ])
    response = push_wechat(
        token=cfg.PUSH.WXPUSHER.APP_TOKEN,
        uids=cfg.PUSH.WXPUSHER.UIDS,
        push_content=push_content)
    logger.info(f"推送结果：{response.get('msg')}")


def random_sleep(min, max):
    logger = logging.getLogger("study")
    sleep_time = random.randint(min, max)
    logger.info(f"随机沉睡: {time.strftime('%H:%M:%S', time.gmtime(sleep_time))} ...")
    time.sleep(sleep_time)


def main():
    default_setup(cfg, sys.argv)

    # Debug mode
    if cfg.DEBUG_MODE:
        study = Study(cfg)
        study.run()
        return

    random_sleep(0, cfg.MAX_SLEEP_TIME_BEFORE_START)
    try:
        study = Study(cfg)
        study.run()
    except Exception as error_info:
        logger = logging.getLogger("study")
        logger.error(f"产生错误：{error_info}")
        if cfg.PUSH.WXPUSHER.ENABLE:
            push_error(str(error_info))


if __name__ == "__main__":
    main()
