'''Utility Functions'''


import requests


def _parse_url_query(url):
    return {i.split('=')[0]: i.split('=')[1] for i in requests.utils.urlparse(url).query.split('&')}
