# -*- encoding: utf-8 -*-
# here put the import lib
import random
import requests
import logging

from study.task.task_base import Task

logger = logging.getLogger(__name__)


class ArticleTask(Task):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __del__(self):
        super().__del__()

    def run_task(self, need_points=6, filters=[], max_num_retries=10):
        """
        Args:

        Returns:
            article_title (str):
        """
        if need_points % 2 == 0:
            need_points //= 2

        num_retries = 0
        done_titles = []
        source_url = "https://www.xuexi.cn/lgdata/1crqb964p71.json"
        while len(done_titles) < need_points and num_retries <= max_num_retries:
            try:
                article_list = requests.get(source_url).json()
                if len(article_list) <= 0:
                    logger.info("文章源未找到，请联系作者更新此软件.")
                    return
                else:
                    logger.info(f"共找到文章 {len(article_list)} 篇 ...")
                logger.info(f"=> 本次任务共需阅读{need_points}篇文章，现在开始随机阅读 ...")
                article_idx = random.sample(
                    range(0, len(article_list)),
                    need_points - len(done_titles)
                )
                logger.info(f"随机结果：「{article_idx}」")
                for i, idx in enumerate(article_idx, 1):
                    article_url = article_list[idx]["url"]
                    article_title = article_list[idx].get("title")
                    if article_title in filters:
                        logger.info(f"第【{i}】文章【{article_title}】已阅读过，跳过 ...")
                        continue
                    self.driver.get(article_url)
                    sleep_time = self._random_sleep_time()
                    logger.info(
                        f"开始阅读第【{i}】篇文章【{article_title}】，阅读时间：{sleep_time}s")
                    # read article
                    scroll_times = 3
                    for _ in range(scroll_times):
                        self._scroll_page(sleep_time * 1.0 / scroll_times)
                    logger.info(f"第【{i}】篇文章【{article_title}】阅读完毕.")
                    done_titles.append(article_title)
            except Exception as e:
                logger.info(f"产生错误：{e}")
                num = need_points - len(done_titles)
                logger.info(f"产生本次错误前已阅读{len(done_titles)}篇文章"
                            f"尝试重新选择{num}篇文章阅读(第{num_retries}/{max_num_retries}次)")
                num_retries += 1

        logger.info(f"=> 本次任务共阅读{need_points}篇文章")
        return done_titles

    @classmethod
    def get_task_names(cls) -> list:
        return ["我要选读文章"]
