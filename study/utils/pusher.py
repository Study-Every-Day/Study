# -*- encoding: utf-8 -*-
# here put the import lib
from wxpusher import WxPusher


def push_wechat(token, uids, push_content, url=None, content_type=3):
    response = WxPusher.send_message(
        content=push_content,
        token=token,
        content_type=content_type,
        topic_ids=[],
        uids=uids,
        url=url,
    )
    return response


if __name__ == "__main__":
    with open("../qrcode/qrcode.html", "r") as fp:
        content = fp.read()
    response = push_wechat(content, content_type=2)  # html
    print(response)
