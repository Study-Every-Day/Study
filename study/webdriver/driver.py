# -*- encoding: utf-8 -*-
# here put the import lib
import os
import os.path as osp
import json
import logging
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from study.utils.driver import check_webdriver


logger = logging.getLogger(__name__)

_LOGIN_URL = "https://pc.xuexi.cn/points/login.html"


class Driver(object):

    def __init__(self):
        pass

    def _init_driver(self, cfg, cookies=None):
        self.gui_enable = cfg.DRIVER.GUI
        self.proxy_enable = cfg.DRIVER.PROXY.ENABLE
        self.proxy_type = cfg.DRIVER.PROXY.TYPE
        self.proxy_ip = cfg.DRIVER.PROXY.IP
        self.proxy_port = cfg.DRIVER.PROXY.PORT
        self.cookies_path = osp.join(cfg.OUTPUT_PATH, "cookies.json")

        options = webdriver.chrome.options.Options()
        # GUI setting
        if not self.gui_enable:
            options.add_argument('--headless')
        # Proxy setting
        if self.proxy_enable:
            proxy = f"{self.proxy_type}://{self.proxy_ip}:{self.proxy_port}"
            logger.info(f"Use proxy: {proxy}")
            options.add_argument(f"--proxy-server={proxy}")
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')  # avoid some bugs
        options.add_argument('--no-sandbox')
        options.add_argument('--mute-audio')
        options.add_argument('--window-size=800,800')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver_path = check_webdriver()

        self.driver = webdriver.Chrome(
            options=options, executable_path=driver_path)
        self.wait = WebDriverWait(self.driver, 20)

        if cookies is not None:
            self._restore_cookies(cookies=cookies)

    def __del__(self):
        if hasattr(self, "driver"):
            try:
                self.driver.quit()
            except Exception as e:
                logger.info(f"退出时产生错误: {e}.")

    def _save_cookies(self, save_path=None):
        if save_path is None:
            save_path = self.cookies_path
        json_str = json.dumps(self.driver.get_cookies(), indent=4, ensure_ascii=False)
        with open(save_path, "w") as fp:
            fp.write(json_str)

    def _remove_saved_cookies(self):
        if osp.exists(self.cookies_path):
            os.remove(self.cookies_path)

    def _restore_cookies_from_file(self, cookies_path=None):
        if cookies_path is None:
            assert os.path.exists(self.cookies_path), "No cookies used to restore."
            cookies_path = self.cookies_path
        with open(cookies_path, 'r') as fp:
            cookies = json.load(fp)
        self._restore_cookies_from_list(cookies=cookies)

    def _restore_cookies_from_list(self, cookies):
        self.driver.get(_LOGIN_URL)
        time.sleep(1)

        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            self.driver.add_cookie(cookie)

        self.driver.get(_LOGIN_URL)

    def _restore_cookies(self, cookies):
        if isinstance(cookies, str):
            logger.info(f"从文件 ({cookies}) 中加载cookies ...")
            self._restore_cookies_from_file(cookies)
        elif isinstance(cookies, list):
            logger.info("从list中加载cookies ...")
            self._restore_cookies_from_list(cookies)
        else:
            logger.info(f"未知的cookies类型: {type(cookies)}")

    def _hiden_elements(self, class_name=[]):
        js = "".join([
            f"document.getElementsByClassName"
            f"('{class_name_i}')[0].style.display='none';"
            for class_name_i in class_name
        ])
        self.driver.execute_script(js)
