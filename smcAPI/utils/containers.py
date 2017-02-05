import datetime
import requests
import string
import bs4

class _Report:
	def __init__(self, year, term, data):
		self.year = year
		self.term = term
		self.data = data
	def __repr__(self):
		return self.year + ' Report (Object)'
	def __str__(self):
		return self.year+' Report'
		
class _CalendarItem:
	def __init__(self, title, start, end):
		self.start = start
		self.end = end
		self.length = end - start
		self.title = title
	def __repr__(self):
		return 'calendaritem: '+self.title
	def __str__(self):
		return self.title
		
class _Member:
	def __init__(self, name, id, picture=None, email=None):
		self.email = email
		self.name = name
		self.picture = picture
		self.id = id
	def __repr__(self):
		return 'Member Object: '+self.name
	def __str__(self):
		return self.name
		
class _Course:
	def __init__(self, title, code, id, type):
		self.title = title
		self.code = code
		self.id = id
		self.type = type
		self.state = 'condensed'
	def __repr__(self):
		return 'Course Object: '+(self.code if self.code is not None else self.title)
	def __str__(self):
		return self.title
		
class _DayTimetable:
	def __init__(self, date, homeroom, p1, p2, p3, p4, p5):
		self.date = date  #TODO: convert str date to datetime object
		self.homeroom = homeroom
		self.p1 = p1
		self.p2 = p2
		self.p3 = p3
		self.p4 = p4
		self.p5 = p5
		self._current = 0
		#TODO: Implement __getitem__
	def __repr__(self):
		return 'Timetable Day Object: '+self.date
	def __str__(self):
		return self.date
	def __iter__(self):
		return iter([self.homeroom, self.p1, self.p2, self.p3, self.p4, self.p5])
	def now(self):
		now = datetime.datetime.now()
		now = datetime.time(now.hour, now.minute)
		if now > datetime.time(8, 35) and now < datetime.time(15, 15):
			if now < datetime.time(9):
				return 'homeroom'
			elif now < datetime.time(10):
				return 'p1'
			elif now < datetime.time(11):
				return 'p2'
			elif now < datetime.time(11, 25):
				return None
			elif now < datetime.time(12, 25):
				return 'p3'
			elif now < datetime.time(13, 25):
				return 'p4'
			elif now < datetime.time(14, 15):
				return None
			else:
				return 'p5'
		else:
			return None
			
class _LessonTimetable:
	def __init__(self, subject, teacher, location):
		self.subject = subject
		self.teacher = teacher
		self.location = location
	def __repr__(self):
		return 'Lesson Object: '+self.subject
	def __str__(self):
		return self.subject
		
class _Notices:
	def __init__(self, date, meetingNotices, generalNotices):
		date = date.split(' ')
		day = date[1].strip(string.ascii_letters)
		if len(day) < 2:
			day = '0' + day
		month = date[3][:-1]
		year = date[4]
		formatted_date = '{}.{}.{}'.format(day, month, year)
		self.date = datetime.datetime.strptime(formatted_date, '%d.%B.%Y')
		self.meetingNotices = meetingNotices
		self.generalNotices = generalNotices
		self.allNotices = meetingNotices+generalNotices
	def __repr__(self):
		return 'Notices Object: '+str(self.__len__)
	def __str__(self):
		return 'Notices'
	def __len__(self):
		return self.meetingNotices.__len__ + self.generalNotices.__len__
		
class _NoticeItem:
	def __init__(self, title, audience, description, teacher, location=None):
		self.title = title
		self.audience = audience
		self.description = description
		self.teacher = teacher
		if location:
			self.location = location
	def __repr__(self):
		return 'Notice Object: '+self.title
	def __str__(self):
		return self.title
		
class _Result:  #TODO: More detailed name
	def __init__(self, title, details, creds, result):
		self.title = title
		self.details = details
		self.credits = creds
		self.result = result
	def __repr__(self):
		return 'Result Object: '+self.title
	def __str__(self):
		return self.title
		
class _CreditsItem:
	def __init__(self, na, a, m, e):
		self.notAchieved = na
		self.achieved = a
		self.merit = m
		self.excellence = e
		self.total = na + a + m + e
	def __repr__(self):
		return 'Credits Object: '+str(self.total)
	def __str__(self):
		return str(self.total)
	def __len__(self):
		return self.total
	def percentage(self):
		na = self.notAchieved / self.total * 100
		a = self.achieved / self.total * 100
		m = self.merit / self.total * 100
		e = self.excellence / self.total * 100
		return {
			'notAchieved': na,
			'achieved': a,
			'merit': m,
			'excellence': e
		}
		
class _NewsletterItem:
	def __init__(self, title, link):
		self.title = title
		self.link = link
		self.extension = ''.join(link.split('.')[-1])
	def __repr__(self):
		return self.title+' (Newsletter Object)'
	def __str__(self):
		return self.title
	def getData(self):
		data = requests.get(self.link).content
		self.data = data
		return data
		
class _NewsItem:
	def __init__(self, title, link, text, image=None):
		self.image = image
		self.title = title
		self.link = link
		self.text = text
		self.state = 'condensed'
	def __str__(self):
		return self.title
	def __repr__(self):
		return 'NewsItem ({}): {}'.format(self.state, self.title)
	def readMore(self):
		source = bs4.BeautifulSoup(requests.get(self.link).text, 'html.parser')
		image = source.find(class_='article-image')
		if image is not None:
			image = 'http//sanctamaria.school.nz/'+image.find('img').get('src')
		self.image = image
		self.text = source.find(class_='article-content').text
		self.state = 'expanded'
