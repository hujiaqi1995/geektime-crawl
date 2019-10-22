# encoding: utf-8
import os
import json
import sys
from urllib.parse import urljoin
import pdfkit
from greekcrawl.cfg import options
from greekcrawl.common import post, log, base_url, error_articles, create_dir, login, init
from greekcrawl.models import Product, Article


def get_all_products():
    """
    获取已购买的所有产品(专栏)
    :return: 专栏id和专栏标题的字典
    """
    response = post(urljoin(base_url, 'my/products/all'))
    data = response.json(encoding='utf-8')['data']
    if len(data) == 0 or len(data[0]['list']) == 0:
        raise Exception("没有购买的专栏")
    log.info("get products success")
    return [Product(d['extra']['column_id'], d['title']) for d in data[0]['list']]


def get_all_products_callback(products):
    """
    对爬取的产品进行处理的回调(这里并没有使用异步线程池, 主动调用的)
    :param products: get_all_products返回的产品字典
    :return:
    """
    for product in products:
        get_all_articles_callback(get_all_articles(product), product)


def get_all_articles(product):
    """
    获取专栏下的所有文章
    :param product: 单个产品(专栏)
    :return: 文章id和文章标题的字典
    """
    payload = {
        "cid": product.id,
        "size": 500,
        "prev": 0,
        "order": "earliest",
        "sample": False
    }
    response = post(urljoin(base_url, 'column/articles'), payload)
    log.info("gat all articles success for product(id=%s, title=%s)" % (product.id, product.title))
    data = response.json(encoding='utf-8')['data']
    return [Article(str(d['id']), d['article_title']) for d in data['list']]


def get_all_articles_callback(articles, product):
    """
    对爬取的文章进行处理的回调(这里并没有使用异步线程池, 主动调用的)
    :param articles: get_all_articles返回的文章字典
    :param product: 文章所属于的产品(专栏)
    :return:
    """
    path = options.save_dir
    product_path = os.path.join(path, product.title)
    create_dir(product_path)
    for article in articles:
        title = article.title.replace(' ', '_').replace('|', '').replace('：', '').replace('?', '').replace('（', '')\
            .replace('）', '').replace('/', '').replace('*', '')
        article_path = os.path.join(
            product_path,
            '{}_{}.pdf'.format(article.id, title))
        article_id_path = os.path.join(product_path, '{}.pdf'.format(article.id))
        if os.path.exists(article_path) or os.path.exists(article_id_path):
            continue
        try:
            content = get_article_content(article)
            article.content = content
        except Exception as e:
            log.error(str(e))
            error_articles.append(article)
            continue
        write_pdf(article, article_path, article_id_path)


def write_pdf(article, article_path, article_id_path):
    """
    将文章内容写入本地pdf文件中, 首次尝试以文章标题为文件名, 若写入失败(标题中有特殊字符), 则使用文章id为文件名
    :param article: 要写入的文章
    :param article_path: 以标题命名的文章绝对路径
    :param article_id_path: 以id命名的文章绝对路径
    :return:
    """
    try:
        log.info('write %s' % article_path)
        pdfkit.from_string(article.content, article_path)
    except OSError:
        try:
            log.info('write %s' % article_id_path)
            pdfkit.from_string(article.content, article_id_path)
        except Exception as e:
            log.error(str(e))
            error_articles.append(article)
    except Exception as e:
        log.error(str(e))
        error_articles.append(article)


def get_article_content(article):
    """
    获取文章内容
    :param article: 目标文章
    :return: 文章内容的html
    """
    payload = {
        "id": article.id,
        "include_neighbors": False,
        "is_freelyread": False
    }
    log.info("prepare to get article(%s)" % article)
    response = post(urljoin(base_url, 'article'), payload)
    log.info("gat article success for article(id=%s, title=%s)" % (article.id, article.title))
    data = response.json(encoding='utf-8')['data']
    if 'article_content' not in data:
        raise Exception("no article content, data is: %s" % json.dumps(data, indent=4))
    return '<meta charset="utf-8">%s' % data['article_content']


def main():
    """
    主函数
    :return:
    """
    init()
    log.info("start--------------")
    try:
        login(options.cell_phone, options.password)
        get_all_products_callback(get_all_products())
    except KeyboardInterrupt:
        log.info("exit...")
    except Exception as e:
        log.error(e)
        sys.exit(1)
    if len(error_articles) > 0:
        log.error("%d article save error, please retry" % len(error_articles))
    else:
        log.info("save success")


if __name__ == '__main__':
    main()
