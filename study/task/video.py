# -*- encoding: utf-8 -*-
# here put the import lib
import random
import requests
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .task_base import Task

logger = logging.getLogger(__name__)


class VideoTask(Task):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __del__(self):
        super().__del__()

    def run_task(self, need_points=6, filters=[], max_num_retries=10):
        """
        Args:
            need_points (int):

        Returns:
            article_title (str):
        """
        num_retries = 0
        done_titles = []
        source_url = "https://www.xuexi.cn/lgdata/17th9fq5c7l.json"
        while len(done_titles) < need_points and num_retries <= max_num_retries:
            try:
                video_news_list = requests.get(source_url).json()
                if len(video_news_list) <= 0:
                    logger.info("视频源未找到，请联系作者更新此软件")
                    return
                else:
                    logger.info(f"共找到新闻联播 {len(video_news_list)} 部 ...")
                logger.info(f"=> 本次任务共需观看{need_points}部视频，现在开始随机观看 ...")
                video_idx = random.sample(
                    range(0, len(video_news_list)),
                    need_points - len(done_titles),
                )
                logger.info(f"随机结果：「{video_idx}」")
                # previous_vide_handle = None
                for i, idx in enumerate(video_idx, 1):
                    video_url = video_news_list[idx]["url"]
                    video_title = video_news_list[idx].get("title", "新闻联播")
                    if video_title in filters:
                        logger.info(f"第【{i}】个视频【{video_title}】已阅观看过，跳过 ...")
                        continue
                    self.driver.get(video_url)
                    button_play = self.wait.until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "outter")))
                    button_play.click()
                    duration = self.wait.until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "duration"))
                    ).text
                    sleep_time = self._random_sleep_time()
                    logger.info(
                        f"开始观看第【{i}】个视频【{video_title}】，"
                        f"总时长：{duration}，观看时间：{sleep_time}s")
                    # watch video
                    scroll_times = 3
                    for _ in range(scroll_times):
                        self._scroll_page(sleep_time * 1.0 / scroll_times)
                    logger.info(f"第【{i}】个视频【{video_title}】观看时长已满（{sleep_time}s），结束观看.")
                    done_titles.append(video_title)
            except Exception as e:
                logger.info(f"产生错误：{e}")
                num = need_points - len(done_titles)
                logger.info(f"产生本次错误前已观看{len(done_titles)}部视频, "
                            f"尝试重新选择{num}部视频观看(第{num_retries}/{max_num_retries}次)")
                num_retries += 1

        logger.info(f"=> 本次任务共观看{need_points}部视频")
        return done_titles

    @classmethod
    def get_task_names(cls) -> list:
        return ["视听学习", "视听学习时长"]
