# encoding: utf-8


class Model(object):

    def __init__(self, cid, title):
        self.id = cid
        self.title = title

    def __repr__(self):
        return 'id={}, title={}'.format(self.id, self.title)


class Product(Model):
    """
    产品(专栏)model
    """
    pass


class Article(Model):
    """
    产品(专栏)下的文章model
    """

    def __init__(self, cid, title, content=''):
        super(Article, self).__init__(cid, title)
        self.content = content
