'''
Tests Related To Portal Class
=============================

if you wish to not be prompted about user id/password you may:
	*create a file next to the test named 'test_auth' or 'portal_test_auth'
	 formatted with:
	 	<User ID>
	 	<Password>
	*set the environment variables 'portal_test_id' and 'portal_test_pass'
	
The Priority Will Be:
	1. Environment Variables
	2. 'portal_test_auth' file
	3. 'test_auth' file
'''

import os
import unittest
from context import smcAPI

class TestPortal (unittest.TestCase):
	id = os.environ.get('portal_test_id')
	pass_ = os.environ.get('portal_test_pass')
	if not (id and pass_):
		if os.path.isfile('test_auth'):
			id,pass_ = open('test_auth', 'r').readlines()[:2]
			id = id.strip('\n')
		else:
			print('Input Portal User ID And Password For Testing')
			print('='*45)
			id = input('User ID: ')
			pass_ = input('Password: ')
			print('='*45)
	def setUp(self):
		self.portal = smcAPI.Portal()
	def test_true_login(self):
		self.portal.login(self.id, self.pass_)
	def test_false_login(self):
		username = 'CompletelyStupidUsernameThatWillNeverBeAccepted'
		password = 'ReallySillyPasswordWithNumbersForGoodMeasure3324832'
		self.assertRaises(
			smcAPI.utils.exceptions.AuthenticationError,
			self.portal.login,
			username,
			password
		)
				
unittest.main()
