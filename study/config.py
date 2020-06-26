# -*- encoding: utf-8 -*-
# here put the import lib
import os
import os.path as osp

from .utils.config import Config


_config_dict = dict(
    DRIVER=dict(
        # 是否打开浏览器的图形用户界面
        GUI=False,
        # 代理配置
        PROXY=dict(
            ENABLE=False,
            TYPE="http",  # http/https
            IP="39.105.24.xx",
            port=8080,
        ),
    ),
    # 配置推送工具
    PUSH=dict(
        # 需要自己注册账号: http://wxpusher.zjiecode.com/
        WXPUSHER=dict(
            ENABLE=False,
            APP_TOKEN=os.getenv("APP_TOKEN"),
            UIDS=os.getenv("UIDS").split(","),  # Note: must be a list
        ),
    ),
    # 登录设置
    LOGIN=dict(
        # - `False` 时，不保存cookies，每次登陆都需要扫码登录
        # - `True` 时，第一次登录时需扫码登录，同时会保存cookies至log路径
        #   待下次运行程序时，程序会先检查能否用上次的cookies直接登陆(跳过扫码)
        #   若使用历史cookies登录失败时，则会使用扫码登录的方式登录
        #   (程序挂在服务器上每天自动运行时比较实用，不必每次都要扫码了，只需偶尔扫码)
        COOKIES_LOGIN=True,
        QRCODE=dict(
            # 是否将二维码推送至手机
            PUSH_ENABLE=False,
            # 配置二维码以何种形式图送至手机, 可选的两种二维码推送方式:
            # (只用配置一个即可，都打开则使用 BASE64_ENCODE)
            # - BASE64_ENCODE: 将二维码保存为base64编码格式，直接传至手机
            # - QINIU: 将二维码图片先传至七牛云的对象存储空间(OSS), 再将链接发送至手机
            # 推荐使用第一种方式，可以免去配置七牛云，若第一种方式失效可尝试第二种方式
            BASE64_ENCODE=dict(
                ENABLE=False,  # 目前存在一个小bug，先用第2种吧...
            ),
            QINIU=dict(
                # See: https://www.qiniu.com/ for more details
                # 建议把这种隐私信息设置在环境变量中，避免push代码时泄露
                ENABLE=False,
                ACCESS_KEY=os.getenv("QINIU_ACCESS_KEY"),
                SECRET_KEY=os.getenv("QINIU_SECRET_KEY"),
                BUCKET_NAME=os.getenv("QINIU_BUCKET_NAME"),
                URL_PREFIX=os.getenv("URL_PREFIX"),
            ),
        ),
    ),
    STUDY=dict(
        # 学习任务，"文章"和"视听", 默认设置即可，不用修改
        TASKS=[
            ("ArticleTask", dict(sleep_time_range=(130, 140),)),
            ("VideoTask", dict(sleep_time_range=(200, 210),)),
        ]
    ),
    # random sleep time before start
    # 程序执行前先随机睡眠一段时间(0~设置的值，单位秒)，程序挂在服务器上每天自动运行时比较实用
    # 这样每天的学习时间就不会是一个固定的时间了
    # 设为 0 时就不会在程序执行前执行睡眠操作了
    MAX_SLEEP_TIME_BEFORE_START=0 * 60,
    OUTPUT_PATH=osp.join(osp.dirname(osp.abspath(__file__)), "log"),
    # 程序运行时是否打印config.py中的配置细节
    SHOW_CONFIG=True,
)

cfg = Config(_config_dict)
