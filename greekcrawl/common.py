import json
import logging
import os
import sys
import time
from datetime import datetime
from urllib import parse
import requests
from .cfg import options, parser, descriptions

account_url = 'https://account.geekbang.org/account/ticket/login'
base_url = 'https://time.geekbang.org/serv/v1/'

headers = {
    'Content-Type': "application/json",
    'Referer': "https://account.geekbang.org/dashboard/buy",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0",
    'Accept': "*/*",
    'Host': "time.geekbang.org",
}

log = logging.getLogger(__name__)
session = requests.session()
error_articles = []


class Throttle:
    """
     为了避免造成服务器过载，对同一域名的下载之间添加时延，从而降低爬虫下载速度
    """

    def __init__(self, delay):
        # 每个域名的下载延时时间
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        """
        请求延时
        :param url: 请求的网址
        :return:
        """
        domain = parse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()


throttle = None


def init():
    """
    初始化方法
    :return:
    """
    # 初始化日志系统
    global log
    formatter = logging.Formatter('%(levelname)s: - %(message)s')
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    log.addHandler(console)
    log.setLevel(logging.INFO)

    # 初始化throttle
    global throttle
    throttle = Throttle(options.download_interval)

    # 命令行参数校验
    for k, v in descriptions.items():
        _, _, default = v
        if default is None:
            value = getattr(options, k.replace('-', '_'))
            if value is None:
                parser.print_help()
                sys.exit(1)


def post(url, data=None, hs=headers, retry=3):
    """
    发送请求
    :param url: 请求网址
    :param data: 表单数据
    :param hs: 请求头
    :param retry: 失败重试次数
    :return: 响应体
    """
    throttle.wait(url)
    log.info("post %s" % url)
    payload = json.dumps(data) if data else "{}"
    res = session.request("POST", url, data=payload, headers=hs)
    if res.status_code != 200:
        if retry > 0:
            login(options.cell_phone, options.password)
            return post(url, data, hs, retry=retry-1)
        else:
            raise Exception("request err, code: %d, content: %s" % (res.status_code, res.text))
    return res


def login(cell_phone, password):
    """
    极客时间登陆
    :param cell_phone: 手机号
    :param password: 密码
    :return:
    """
    login_headers = {
        'Content-Type': "application/json",
        'Referer': "https://account.geekbang.org",
        'Host': "account.geekbang.org",
    }
    data = {
        "country": 86,
        "cellphone": cell_phone,
        "password": password,
        "captcha": "",
        "remember": 1,
        "platform": 3,
        "appid": 1
    }
    assert cell_phone is not None and password is not None
    response = post(account_url, data, hs=login_headers)
    res = response.json()
    if res['code'] != 0:
        # {"code": -1, "data": [], "error": {"code": -3011, "msg": "电话错误"},
        #  "extra": {"cost": 0.02108621597290039, "request-id": "132ac9b6d99a9aec8ea08207444c6ba0@2@account"}}
        msg = res['error']['msg']
        log.error("login failed, error: %s" % str(msg))
        sys.exit(1)
    log.info("login success")
    log.info("cookies: ")
    for cookie in response.cookies:
        log.info("%s=%s" % (cookie.name, cookie.value))
    session.cookies = response.cookies


def create_dir(path):
    """
    幂等的创建文件夹
    :param path: 要创建的文件夹路径
    :return:
    """
    if os.path.exists(path):
        return
    os.makedirs(path, 0o0755)

