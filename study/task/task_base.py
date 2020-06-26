# -*- encoding: utf-8 -*-
# here put the import lib
import time
import random
import logging

from study.webdriver import Driver

logger = logging.getLogger(__name__)


class Task(Driver):

    def __init__(self, *args, **kwargs):
        super().__init__()
        sleep_time_range = kwargs.get("sleep_time_range", (200, 250))
        self.sleep_time_range = sleep_time_range

    def _init_driver(self, cfg, cookies):
        subtask = self.get_task_names()
        logger.info(f"⚽️ => 开始执行任务: {self}, 其中包含{len(subtask)}个子任务: {subtask}")

        super()._init_driver(cfg, cookies)
        assert self._check_login()

    def __del__(self):
        super().__del__()

    def _check_login(self, max_check_times=60, sleep_time=3):
        """
        The total waiting time is equal to max_check_times * sleep_time.

        Args:
            max_check_times (int):
            sleep_time (int): sleep time.
        """
        login_url = "https://pc.xuexi.cn/points/login.html"
        self.driver.get(login_url)
        time.sleep(1)

        count = 0
        while count < max_check_times:
            try:
                count += 1
                assert self.driver.title == "我的学习"
                return True
            except AssertionError:
                logger.info(f"未检测到登录状态, 等待中 ({sleep_time}s) ...\n"
                            f"Driver title is {self.driver.title} ...")
                if count == max_check_times - 1:
                    return False
                else:
                    time.sleep(sleep_time)

    def run(self):
        self._run_task()

    def _random_sleep_time(self):
        sleep_time = random.randint(*self.sleep_time_range)
        return sleep_time

    def _scroll_page(self,
                     scroll_time=random.uniform(2.0, 4.0),
                     scroll_times=100):
        scroll_time = scroll_time * 0.3
        back_scroll_time = 0.2

        clientHeight = "document.documentElement.clientHeight"

        # down
        sleep_time_i = scroll_time * (1.0 - back_scroll_time) / scroll_times
        scroll_pix_i = f"({clientHeight}/ {scroll_times})"
        for i in range(scroll_times):
            js = f"window.scrollTo({i}*{scroll_pix_i},({i}+1)*{scroll_pix_i});"
            if random.random() > 0.5:
                self.driver.execute_script(js)
            time.sleep(sleep_time_i)

        time.sleep(scroll_time * 0.4 / 0.3)
        # up
        sleep_time_i = scroll_time * back_scroll_time / scroll_times
        half_height = f"({clientHeight} / 2.0)"
        scroll_pix_i = f"({clientHeight} / 2.0 / {scroll_times})"
        for i in range(scroll_times - 1, 0, -1):
            js1 = f"window.scrollTo({half_height}+{i}*{scroll_pix_i}, "
            js2 = f"{half_height}+({i}+1)*{scroll_pix_i});"
            js = js1 + js2
            if random.random() > 0.5:
                self.driver.execute_script(js)
            time.sleep(sleep_time_i)

        time.sleep(scroll_time * 0.3 / 0.3)

    def run_task(self):
        raise NotImplementedError()

    @classmethod
    def get_task_names(cls):
        raise NotImplementedError()

    @classmethod
    def __repr__(cls):
        return cls.__name__
