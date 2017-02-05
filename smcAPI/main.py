import bs4
import requests

from .utils.containers import _NewsItem
from .utils.exceptions import BadPage

class SanctaMaria (object):
	'''
	Contains Functions And Utilities Related To The Main Website
	
	Initialise The Class
	>>> school = SanctaMaria()
	
	Get The Number Of Pages Available
	>>> school.get_news()
	
	Get The First Page
	>>> school.get_news(1)
	'''
	def __init__(self):
		self.url = 'http://www.sanctamaria.school.nz/'
	def get_news(self, page=None):
		if page is not None:
			start = (-3 + page * 3)
			if start < 0:
				raise BadPage('{} Is Too Low A Number, Number Must Be >= 1')
			response = requests.get(self.url + 'index.php?start={}'.format(start)).text
			newsPage = bs4.BeautifulSoup(response, 'html.parser')
			#TODO: Raise BadPage For Any Invalid pages Too High
			articles = newsPage.find_all(itemprop="blogPost")
			temp = []
			for article in articles:
				title = article.find(class_='lndtitle').get('title')
				link = self.url[:-1] + article.find(class_='lndtitle').get('href')
				text = article.find('p')
				image = article.find(class_='article-image')
				if image is not None:
					image = self.url + image.find('img').get('src')
				if text is not None:
					text = text.text
				temp.append(_NewsItem(title, link, text, image))
			return temp
		else:
			source = bs4.BeautifulSoup(requests.get(self.url).text, 'html.parser')
			link = source.find(title='End').get('href')
			return int((int(link.strip('/index.php?start='))+3)/3)
