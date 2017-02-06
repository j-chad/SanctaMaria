from .utils.exceptions import AuthenticationError
from .utils.internal import parse_date

import datetime
import requests
import bs4

class Portal:
	def __init__(self):
		self._state = 0
		self.url = 'https://portal.sanctamaria.school.nz/student/index.php/'
		self._userindependentdata = []
	def login(self, userid, password):
		if self._state:
			raise BaseException('Already Logged In - Log Out First')
		else:
			self._session = requests.session()
			response = self._session.post(self.url + 'process-login', {
				'username': str(userid),
				'password': str(password)
			})
			error = bs4.BeautifulSoup(response.text, 'html.parser').find(class_='error')
			authenticated = error is None
			if authenticated:
				self._state = 1
				source = bs4.BeautifulSoup(response.text, 'html.parser')
				self.name = source.find(id='auth').find('strong').text
				self.userType = source.find(id='auth').find('em').text.lower()
			else:
				self._session.close()
				msg = 'Authorisation Denied With Message: {}'.format(error.text)
				raise AuthenticationError(msg)
	def logout(self):
		if not self._state:
			raise BaseException('Already Logged Out - Log In First')
		else:
			self._session.close()
			self._state = 0
			for x in list(set(self._userindependentdata)):
				exec('del self.'+x)
	def getCalendar(self, daterange='month', date=None):
		if date is None:
			date = datetime.datetime.now()
		if not daterange.lower() in ['month', 'day', 'week']:
			msg = 'Daterange Must be One Of: \'month\', \'day\' or \'week\''
			raise BaseException(msg)  #TODO: change to a more descriptive exception
		temp = []
		url = self.url + 'calendar/{}-{}/{}/{}'
		url = url.format(date.year, date.month, date.day, daterange)
		response = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
		data = response.find(id='wrapper')
		table = data.find(id='calendar_table')
		year = table.find(class_='result_subject').text.split(' ')[1]
		dates = table.findAll(class_='result_increase')
		for event in dates:
			eventDate = event.text.strip('\n\t\r ')
			eventDate = parse_date(eventDate, year)
			eventTitle=event.parent.findNextSibling().text.strip('\n\t\r ')
			temp.append(_calendaritem(eventTitle,start,end))
		self.calendar=temp
		return temp
	def getNotices(self):
		response=bs4.BeautifulSoup(requests.get(self.url+'notices').text,'html.parser')
		data=response.find('div', id='notices')
		date=data.find(class_='notices-header').text
		meetingNotices=[]
		for notice in data.findAll(class_='meeting-notice'):
			title=notice.find(class_='subject').text
			audience=notice.find(class_='level').text
			description=notice.find(class_='body').text
			if description in string.whitespace:
				description=None
			teacher=notice.find(class_='teacher').text
			location=notice.find(class_='meet').text
			meetingNotices.append(_notice(title,audience,description,teacher,location))
		generalNotices=[]
		for notice in data.findAll(class_='general-notice'):
			title=notice.find(class_='subject').text
			audience=notice.find(class_='level').text
			description=notice.find(class_='body').text
			if description in string.whitespace:
				description=None
			teacher=notice.find(class_='teacher').text
			generalNotices.append(_notice(title,audience,description,teacher))
		self.notices=_notices(date,meetingNotices,generalNotices)
		return self.notices
	def getTimetable(self,alternate=False):
		if not self._state:
			raise BaseException('Must Be Logged In')
		else:
			response=bs4.BeautifulSoup(self._session.get(self.url+'timetable').text,'html.parser')
			table=response.find(id='timetable_table')
			self.week=int(table.find(id='week').get('value'))
			if alternate:
				response=bs4.BeautifulSoup(self._session.get(self.url+'timetable/'+str(self.week+1)).text,'html.parser')
				table=response.find(id='timetable_table')
			rows=table.findAll('tr')
			week={'monday':[],'tuesday':[],'wednesday':[],'thursday':[],'friday':[]}
			order=('monday','tuesday','wednesday','thursday','friday')
			for column in rows[0].findAll('th')[1:]:
				day=column.text
				date=column.div.text
				day=day[0:len(day)-len(date)].lower()
				week[day].append(date)
			dayiterator=0
			perioditerator=0
			for row in rows[2:-1]:
				if perioditerator==3 or perioditerator==6:
					perioditerator+=1
					continue
				perioditerator+=1
				for column in row.findAll('td')[1:]:
					day=order[dayiterator]
					title=column.strong.text
					text=column.div.text.replace('\n',' ').replace('\t',' ').split(' ')
					text=[char for char in text if char != '']
					if len(text)==0:
						teacher=''
						location=''
					else:
						teacher,location=text
					week[day].append(_lessonTimetable(title,teacher,location))
					dayiterator+=1
					if dayiterator>4:
						dayiterator=0
			monday=_dayTimetable(*week['monday'])
			tuesday=_dayTimetable(*week['tuesday'])
			wednesday=_dayTimetable(*week['wednesday'])
			thursday=_dayTimetable(*week['thursday'])
			friday=_dayTimetable(*week['friday'])
			week={'monday':monday,'tuesday':tuesday,'wednesday':wednesday,'thursday':thursday,'friday':friday}
			self._userindependentdata.append('timetable')
			if not alternate:
				self.timetable=week
			else:
				self.alternateTimetable=week
			return week
	def getNCEA(self):
		if not self._state:
			raise BaseException('Must Be Logged In')
		else:
			response=bs4.BeautifulSoup(self._session.get(self.url+'ncea-summary').text,'html.parser')
			na=int(response.find(class_='notachieved').text)
			a=int(response.find(class_='achieved').text)
			m=int(response.find(class_='merit').text)
			e=int(response.find(class_='excellence').text)
			self._userindependentdata.append('credits')
			self.credits=_credits(na,a,m,e)
			return {'notAchieved':na,'achieved':a,'merit':m,'excellence':e}
	def getCurrentYearResults(self):
		if not self._state:
			raise BaseException('Must Be Logged In')
		else:
			response=bs4.BeautifulSoup(self._session.get(self.url+'current-year-results').text,'html.parser')
			temp={}
			data=response.find(id='wrapper')
			for x in data.find_all('div'):
				if x.get('id') != None:
					if 'tab_' in x.get('id'):
						subject=x.h2.text
						temp[subject]=[]
						for i in x.findAll('tr'):
							title=i.find(class_='result_title').text
							if ' - ' in title:
								title,details=title.split(' - ',1)
							else:
								details=None
							creds=i.find(class_='result-credits').text.strip(string.ascii_letters+string.whitespace+string.punctuation)
							if creds=='':
								creds=0
							else:
								creds=int(creds)
							result=i.find(class_='result-value').text
							temp[subject].append(_result(title,details,creds,result))
			self._userindependentdata.append('currentYearResults')
			self.currentYearResults=temp
			return temp
	def getAllResults(self):
		if not self._state:
			raise BaseException('Must Be Logged In')
		else:
			response=bs4.BeautifulSoup(self._session.get(self.url+'all-results').text,'html.parser')
			table=response.find(id='results_table')
			temp={}
			subject=None
			for x in table.findAll('tr'):
				if x != '':
					if x.get('class') != None and 'result-subject' in x.get('class'):
						subject=x.text.lower()
						temp[subject]=[]
					elif x.td.get('class') != None and 'result_subject' in x.td.get('class'):
						continue
					elif subject != None:
						title=x.find(class_='result_title').text
						if ' - ' in title:
							title,details=title.split(' - ',1)
						else:
							details=None
						creds=x.find(class_='result-credits').text.strip(string.ascii_letters+string.whitespace+string.punctuation)
						if creds=='':
							creds=0
						else:
							creds=int(creds)
						result=x.find(class_='result-value').text
						temp[subject].append(_result(title,details,creds,result))
			self._userindependentdata.append('allResults')
			self.allResults=temp
			return temp
	def getReports(self):
		if not self._state:
			raise BaseException('Must Be Logged In')
		else:
			response=bs4.BeautifulSoup(self._session.get(self.url+'reports').text,'html.parser')
			temp={}
			for report in response.findAll('a',text=re.compile('Report')):
				if report.get('href')==self.url+'reports':
					continue
				else:
					reportPartitions=report.get('href').split('/')[6:8]
					year=reportPartitions[0]
					term=reportPartitions[1].strip(string.ascii_letters+string.whitespace)
					data=self._session.get(report.get('href')).content
					try:
						temp[year].append(_report(year,term,data))
					except KeyError:
						temp[year]=[_report(year,term,data)]
			self.reports=temp
			return temp
