class BadPage (Exception):
	'''For When The Page Requested Is Less Than 0 In SanctaMaria().get_news()'''
	pass
	
class AuthenticationError (Exception):
	'''For When An Attempted Login Is Denied'''
	pass
