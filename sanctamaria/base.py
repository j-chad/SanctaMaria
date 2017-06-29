'''Placeholder'''

from . import BASE_URL
from ._utils import _parse, _parse_url_query


class Article:
    def __init__(self, link, title=None, text=None, image=None):
        '''Initialise News Article

        `link` is the only required parameter,
        all others can be populated automatically by calling self.update
        when the object is initialised

        :param link: The url where the article should be located
        :type link: string
        :param title: The title of the article, defaults to None
        :type title: string, optional
        :param text: The message in the article, defaults to None
        :type text: string, optional
        :param image: A link to the main image in the article if one exists, defaults to None
        :type image: string, optional
        '''
        self.link = link
        if title is not None:
            self.title = title
        if text is not None:
            self.text = text
        if image is not None:
            self.image = image
    def update(self):
        pass


def get_news(page=1, parse_text=False):
    '''Get A Page Of News From The Sancta Maria College Website

    :param page: page number, defaults to 1
    :type page: integer, optional
    :param parse_text: whether or not to get the limited text body available, defaults to False
    :type parse_text: bool, optional
    :raises: TypeError, ValueError
    '''
    if type(page) is not int:
        raise TypeError('`page` must be an integer')
    if page < 1:
        raise ValueError('`page` must be >= 1')
    start = page * 5
    news_page = _parse(BASE_URL + '/index.php?start={}'.format(start))
    max_obj = news_page.xpath("//ul[@class='pagination']/li/a[@title='End']")[0]
    max_page = int(_parse_url_query(max_obj.get('href')).get('start')) / 5
    if page > max_page:
        raise ValueError('`page` must be <= {} (subject to change)'.format(max_page))
    #articles=news_page.xpath("//div[@itemprop='blogPost']/article")
