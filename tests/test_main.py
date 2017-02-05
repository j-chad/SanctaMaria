'''
Tests Related To SanctaMaria Class
'''

import unittest
from context import smcAPI

class TestMainAPI(unittest.TestCase):
	def setUp(self):
		self.school = smcAPI.SanctaMaria()
	def test_news_pages(self):
		self.assertIsInstance(self.school.get_news(), int)
	def test_first_page(self):
		page = self.school.get_news(1)
		self.assertIsInstance(page, list)
		for news_item in page:
			with self.subTest(news_item=news_item):
				self.assertIsInstance(news_item, smcAPI.utils.containers._NewsItem)
	def test_last_page(self):
		page_num = self.school.get_news()
		page = self.school.get_news(page_num)
		self.assertIsInstance(page, list)
		for news_item in page:
			with self.subTest(news_item=news_item):
				self.assertIsInstance(news_item, smcAPI.utils.containers._NewsItem)
	def test_invalid_page_negative(self):
		page_num = -1
		self.assertRaises(smcAPI.utils.exceptions.BadPage, self.school.get_news, page_num)
	@unittest.expectedFailure
	def test_invalid_page_too_big(self):
		page_num = self.school.get_news() + 1
		self.assertRaises(smcAPI.utils.exceptions.BadPage, self.school.get_news, page_num)
		
unittest.main()
