# -*- encoding: utf-8 -*-
# here put the import lib
import os
import os.path as osp
import time
import threading
import logging

from functools import partial
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from study.task import build_tasks
from study.webdriver import Driver
from study.utils.upload import upload_image
from study.utils.pusher import push_wechat


_TASK_NAME = {
    "每日登录",
    "阅读文章",
    "视听学习",
    "文章学习时长",
    "视听学习时长",
}

_LOGIN_URL = "https://pc.xuexi.cn/points/login.html"


class Study(Driver):

    def __init__(self, cfg):
        '''
        You need to first download the corresponding webdriver.
        Download link:
            chromedriver: http://chromedriver.storage.googleapis.com/index.html
        '''
        super().__init__()
        self.cfg = cfg
        self._init_driver(cfg)

        self.logger = logging.getLogger(name=__name__)

        self.cookies_login_enable = cfg.LOGIN.COOKIES_LOGIN
        self.qrcode_path = osp.join(cfg.OUTPUT_PATH, "qrcode")
        os.makedirs(self.qrcode_path, exist_ok=True)
        self.qrcode_push_enable = cfg.LOGIN.QRCODE.PUSH_ENABLE
        self.base64_encode_enable = cfg.LOGIN.QRCODE.BASE64_ENCODE.ENABLE
        self.qiniu_enable = cfg.LOGIN.QRCODE.QINIU.ENABLE
        self._upload_image_to_qiniu = partial(
            upload_image,
            access_key=cfg.LOGIN.QRCODE.QINIU.ACCESS_KEY,
            secret_key=cfg.LOGIN.QRCODE.QINIU.SECRET_KEY,
            bucket_name=cfg.LOGIN.QRCODE.QINIU.BUCKET_NAME,
        )
        self.qiniu_url_prefix = cfg.LOGIN.QRCODE.QINIU.URL_PREFIX
        self.wxpusher_enable = cfg.PUSH.WXPUSHER.ENABLE
        self._push_wechat = partial(
            push_wechat,
            token=cfg.PUSH.WXPUSHER.APP_TOKEN,
            uids=cfg.PUSH.WXPUSHER.UIDS)
        self.output_path = cfg.OUTPUT_PATH
        time_str = time.strftime('%Y_%m_%d', time.localtime())
        self.log_path = osp.join(cfg.OUTPUT_PATH, f"runtime_{time_str}.log")

        self.cookies_cache_exists = False
        if self.cookies_login_enable:
            if os.path.exists(self.cookies_path):
                self.cookies_cache_exists = True
            else:
                self.logger.info(
                    f"未找到缓存的cookies文件 ({self.cookies_path}), 将使用【扫码登录】方式进行登录...")

        self.merged_tasks = build_tasks(cfg.STUDY.TASKS)

    def __del__(self):
        super().__del__()

    def run(self):
        self._login()
        self._run_merged_tasks()

    def _login(self, max_num_retries=3):
        num_retries = 0
        self.logger.info("开始登录 ...")

        # load cookies if have
        if self.cookies_login_enable and self.cookies_cache_exists:
            self.logger.info(f"尝试使用缓存的cookies登录 ({self.cookies_path}) ...")
            self._restore_cookies_from_file(self.cookies_path)
            self.driver.get(_LOGIN_URL)
            is_login = self._check_login(max_check_times=5)

            if not is_login:
                self._remove_saved_cookies()
                self.cookies_cache_exists = False
                self.logger.info("尝试使用缓存的cookies登录失败, 开始使用【扫码登录】方式进行登录 ...")
                self._login()
            else:
                self.logger.info("🥳 => 登陆成功 ...")
                self.logger.info(f"更新本地缓存的cookies, 保存至: {self.cookies_path}")
                self._save_cookies()
                if self.wxpusher_enable:
                    self._push_cookies_login()
        else:
            self.driver.get(_LOGIN_URL)
            time.sleep(1)
            if self.wxpusher_enable and self.qrcode_push_enable:
                self._push_qrcode()
                self.logger.info("已将登录二维码推送至微信, 请使用 [XXQG] APP 扫码登录 ...")
            else:
                qrcode_image_path = self._extract_qrcode(return_type="path")
                self.logger.info(f"请扫描二维码登录: {qrcode_image_path}")

            while True:
                is_login = self._check_login()
                if not is_login:
                    if num_retries < max_num_retries:
                        self.logger.info("登录二维码过期，尝试第{num_retries}/{max_num_retries}次重新登录 ...")
                        self._login()
                    else:
                        self.logger.info("登录超时!")
                else:
                    self.logger.info("🥳 => 登录成功 ...")
                    if self.cookies_login_enable:
                        self.logger.info(f"保存cookies至本地: {self.cookies_path}")
                        self._save_cookies()
                    break

    def _check_login(self, max_check_times=60, sleep_time=3):
        """
        The total waiting time is equal to max_check_times * sleep_time.

        Args:
            max_check_times (int):
            sleep_time (int): sleep time.
        """
        count = 0
        while count < max_check_times:
            count += 1
            try:
                assert self.driver.title == "我的学习"
                return True
            except AssertionError:
                self.logger.info(f"未检测到登录状态, 等待中 ({sleep_time}s) ... (当前标题: {self.driver.title})")
                if count == max_check_times - 1:
                    return False
                else:
                    time.sleep(sleep_time)

    def _get_points(self):
        """

        Returns:
            task_name_to_points (dict[str: str]):
        """
        my_points_url = "https://pc.xuexi.cn/points/my-points.html"
        self.driver.get(my_points_url)
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='my-points-card']/p")))
        task_name = self.driver.find_elements_by_xpath(
            "//div[@class='my-points-card']/p")
        task_points = self.driver.find_elements_by_xpath(
            "//div[@class='my-points-card-text']")
        task_name_and_points = {}
        for tn, tp in zip(task_name, task_points):
            tn = tn.text
            tp = tp.text.replace("分", "")
            task_name_and_points[tn] = tp
        return task_name_and_points

    def _get_gap_points_one_task(self, task_name: str):
        """

        Args:
            task_name (str): task name, like "阅读文章", "文章学习时长" ...

        Returns:
            gap_points (int): gap points
        """
        assert task_name in _TASK_NAME, f"task_name arg must be in [{_TASK_NAME}]"
        task_name_and_points = self._get_points()
        task_points = task_name_and_points.get(task_name)
        self.logger.info(f"【{task_name}】任务积分：{task_points}")
        points = task_points.split("/")
        got_points = eval(points[0])
        sum_points = eval(points[1])
        assert got_points <= sum_points
        if got_points == sum_points:
            self.logger.info(f"【{task_name}】任务已完成")
            return 0
        else:
            gap_points = sum_points - got_points
            self.logger.info(f"【{task_name}】任务还差{gap_points}分即可完成")
            return gap_points

    def _check_merged_task_done(self, subtask_names: list) -> tuple:
        """

        Args:
            subtask_names (list[str]): subtask names, like: ["阅读文章", "文章学习时长"] ...

        Returns:
            task_done (list[bool]):
            gap_points (int):
        """
        task_done = [False for tn in subtask_names]
        gap_points = []
        for idx, tn in enumerate(subtask_names):
            gap_points_i = self._get_gap_points_one_task(tn)
            gap_points.append(gap_points_i)
            if gap_points_i == 0:
                task_done[idx] = True
        return task_done, max(gap_points)

    def _run_merged_tasks(self):
        self.complete_flag = {str(t): False for t in self.merged_tasks}
        for merged_task in self.merged_tasks:
            self.logger.info(f"启动线程，开始执行任务: {merged_task} ...")
            thread = threading.Thread(
                target=self._run_merged_task,
                args=(merged_task, )
            )
            thread.daemon = False
            thread.start()

    def _run_merged_task(self, merged_task, max_num_retries=5):
        """

        Args:
            merged_task (Task): task instance, e.g. ArticleTask ...
        """
        num_retries = 0
        task_names = merged_task.get_task_names()
        merged_task_done, max_gap_points = self._check_merged_task_done(task_names)
        done_titles = []
        while False in set(merged_task_done) and num_retries <= max_num_retries:
            merged_task._init_driver(self.cfg, cookies=self.driver.get_cookies())
            done_titles.extend(
                merged_task.run_task(need_points=max_gap_points, filters=done_titles)
            )
            merged_task_done, max_gap_points = self._check_merged_task_done(task_names)
            done_list_str = "\n".join(done_titles)
            self.logger.info(f"任务【{merged_task}】目前已学习的内容有：\n{done_list_str}")
            num_retries += 1

        if False not in set(merged_task_done):
            self.logger.info(f"🥳 => 任务【{merged_task}】已完成")
            self.complete_flag[str(merged_task)] = True
        else:
            self.logger.info(f"🙈 => 任务【{merged_task}】未完成, 已到达最大重试次数")

        if hasattr(merged_task, "driver"):
            merged_task.driver.quit()

        if False not in set(self.complete_flag.values()):
            self._study_complete_do()

    def _extract_qrcode(self, return_type="base64"):
        assert return_type in ["base64", "path"]

        # self._hiden_elements(
        #     class_name=["layout-header", "layout-footer", "redflagbox"])
        qrcode_ele = self.wait.until(
            EC.element_to_be_clickable((By.ID, "qglogin")))

        if return_type == "base64":
            return qrcode_ele.screenshot_as_base64
        elif return_type == "path":
            time_str = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())
            qrcode_image_name = f"{time_str}.png"
            qrcode_image_path = os.path.join(self.qrcode_path, qrcode_image_name)
            qrcode_ele.screenshot(qrcode_image_path)
            return qrcode_image_path
        else:
            raise ValueError(f"Unkonw qrcode return type: {return_type}.")

    def _push_cookies_login(self):
        self.logger.info("正在将登录状态推送至微信 ...")
        push_content = "\n\n".join([
            "# 🧑‍🎓 XXQG登陆成功 🧑‍🎓\n\n",
            "本次登录使用历史cookies登录，现已开始学习相关内容。",
            "完成任务后会将学习记录推送至微信。",
        ])
        response = self._push_wechat(push_content=push_content)
        self.logger.info(f"推送结果: {response.get('msg')}")

    def _push_qrcode(self):
        self.logger.info("正在将登陆二维码推送至微信")
        if self.base64_encode_enable:
            base64_encode = self._extract_qrcode(return_type="base64")
            image_line = [
                "![qrcode](data:image/png;base64,{})".format(base64_encode)
            ]
            qrcode_url = None
        elif self.qiniu_enable:
            qrcode_image_path = self._extract_qrcode(return_type="path")
            qrcode_image_name = qrcode_image_path.split("/")[-1]
            self._upload_image_to_qiniu(
                local_file_path=qrcode_image_path,
                remote_file_name=qrcode_image_name)
            qrcode_url = f"{self.qiniu_url_prefix}{qrcode_image_name}"
            self.logger.info(f"云端二维码地址：{qrcode_url}")
            image_line = [
                f"![qrcode]({qrcode_url})",
                f"> 二维码地址：[link]({qrcode_url})。"
            ]
        else:
            raise ValueError("您已经打开了推送开关 (cfg.PUSH.WXPUSHER.ENABLE)，所以请至少打开一种二维码推送方式 "
                             "(cfg.LOGIN.QRCODE.BASE64_ENCODE 或 cfg.LOGIN.QRCODE.QINIU).")

        push_content = "\n\n".join([
            "# 🏞 XXQG扫码登录 🏞\n\n",
            "请打开【XXQG】手机客户端扫描下方二维码登录。",
            "登陆成功后会开始学习相关内容。",
            "完成任务后会将学习记录推送至微信。",
            *image_line
        ])
        response = self._push_wechat(push_content=push_content, url=qrcode_url)
        self.logger.info(f"Push results: {response.get('msg')}")

    def _push_study_log(self):
        self.logger.info("正在将学习日志推送至微信")
        with open(self.log_path, "r", encoding="utf8") as fp:
            content_lines = fp.readlines()
        push_content = "\n\n".join([
            "# 🥳 XXQG任务完成 🥳\n\n",
            "今日学习任务已完成，学习日志如下：",
            *content_lines
        ])
        response = self._push_wechat(push_content=push_content)
        self.logger.info(f"Push results: {response.get('msg')}")

    def _study_complete_do(self):
        if self.wxpusher_enable:
            self._push_study_log()
        # write complete flag to file ./log/complete
        file_path = os.path.join(self.output_path, "latest_complete.date")
        with open(file_path, "w") as fp:
            content = time.strftime("%Y-%m-%d", time.localtime())
            fp.write(content)
