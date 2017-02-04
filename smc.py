# -*- coding: utf-8 -*-
"""Sancta Maria College API.

This module contains a python API for Sancta Maria College.
As of this version this module has support for the following services:
    -Main Webpage (http://www.sanctamaria.school.nz)
    -Sancta Maria Portal (https://portal.sanctamaria.school.nz/student/index.php)
    -Sancta Maria Schoology (http://schoology.sanctamaria.school.nz)

Todo:
    * Remove function writeTo
    * Convert text dates into datetime dates

Author: Jackson Chadfield
Email : ibjacksonc@hotmail.com
"""

import os
import sys
sys.path.append(os.sep.join(__file__.split(os.sep)[:-1])+os.sep+"Modules")

import requests
import bs4
import string
import datetime
import re

#DEV
def writeTo(url,session):
    open('test.html','w').write(str(bs4.BeautifulSoup(session.get(url).text,'html.parser')))

def writeToBinary(url,session,extension):
    open('test.'+extension,'wb').write(session.get(url).content)
#DEV END

class SanctaMaria:
    def __init__(self):
        self.url='http://www.sanctamaria.school.nz/'
        self.portal=_portal()
        self.schoology=_schoology()
    def getNews(self,page=None):
        if page!=None:
            start=-3+page*3
            newsPage=bs4.BeautifulSoup(requests.get(self.url+'index.php?start=%s'%start).text,'html.parser')
            articles=newsPage.find_all(itemprop="blogPost")
            temp=[]
            for article in articles:
                title=article.find(class_='lndtitle').get('title')
                link=self.url[:-1]+article.find(class_='lndtitle').get('href')
                text=article.find('p')
                image=article.find(class_='article-image')
                if image != None:
                    image=self.url+image.find('img').get('src')
                if text != None:
                    text=text.text
                temp.append(_newsItem(title,link,text,image))
            return temp
        else:
            source=bs4.BeautifulSoup(requests.get(self.url).text,'html.parser')
            link=source.find(title='End').get('href')
            return int((int(link.strip('/index.php?start='))+3)/3)
    def searchNews(self,query,limit=0):
        query=str(query)
        if len(query)<3 or len(query)>200:
            raise BaseException('Query must be a minimum of 3 characters and a maximum of 200')
        url=self.url+'index.php/component/search/'
        url+='?searchword='+str(query)
        url+='&ordering=newest'
        url+='&searchphrase=all'
        url+='&limit='+str(limit)
        url+='&areas[1]=content'
        source=bs4.BeautifulSoup(requests.get(url).text,'html.parser')
        results=source.find(class_='search-results')
        temp=[]
        for x in results.find_all('li'):
            title=x.h3.a.text.strip(' \n\t\r')
            link=self.url[:-1]+x.h3.a.get('href')
            text=x.find(class_='result-text').text.strip(' \n\t\r')
            temp.append(_NewsItem(title,link,text))
        return temp
    def getNewsletters(self):
        response=bs4.BeautifulSoup(requests.get(self.url+'index.php/newsletter').text,'html.parser')
        temp=[]
        for link in response.find(class_='article-content').findAll('a'):
            temp.append(_newsletterItem(link.text,self.url+link.get('href')[1:]))
        self.newsletters=temp
        return temp

class _portal:
    def __init__(self):
        self._state=0
        self.url='https://portal.sanctamaria.school.nz/student/index.php/'
        self._userindependentdata=[]
    def login(self,userid,password):
        if self._state:
            raise BaseException('Already Logged In - Log Out First')
        else:
            self._session=requests.session()
            response=self._session.post(self.url+'process-login',{'username':str(userid),'password':str(password)})
            authenticated=(bs4.BeautifulSoup(response.text,'html.parser').find(class_='error')==None)
            if authenticated:
                self._state=1
                source=bs4.BeautifulSoup(response.text,'html.parser')
                self.name=source.find(id='auth').find('strong').text
                self.userType=source.find(id='auth').find('em').text.lower()
            else:
                self._session.close()
                raise AuthenticationError('Incorrect Authorisation')
    def logout(self):
        if not self._state:
            raise BaseException('Already Logged Out - Log In First')
        else:
            self._session.close()
            self._state=0
            for x in list(set(self._userindependentdata)):
                exec('del self.'+x)
    def getCalendar(self,daterange='month',date=None):
        if date==None:
            date=datetime.datetime.now()
        if not daterange.lower() in ['month','day','week']:
            raise BaseException('Not A Valid Range') #TODO: change to a more descriptive exception
        temp=[]
        response=bs4.BeautifulSoup(requests.get(self.url+'calendar/{}-{}/{}/{}'.format(date.year,date.month,date.day,daterange)).text,'html.parser')
        data=response.find(id='wrapper')
        table=data.find(id='calendar_table')
        year=table.find(class_='result_subject').text.split(' ')[1]
        dates=table.findAll(class_='result_increase')
        for event in dates:
            eventDate=event.text.strip('\n\t\r ')
            #parse date
            if 'to' in eventDate:
                data=eventDate.split(' to ')
                start=data[0]
                end=data[1]
                if ',' in end:
                    #start/end date
                    start=datetime.datetime(int(year),datetime.datetime.strptime(start.split(' ')[2],'%B').month,int(start.strip(string.ascii_letters+', ')),8,35)
                    end=datetime.datetime(int(year),datetime.datetime.strptime(end.split(' ')[2],'%B').month,int(end.strip(string.ascii_letters+', ')),15,15)
                else:
                    #start/end time
                    date=start.split(' ')[1:-1]
                    start=start.split(' ')[-1]
                    start=datetime.datetime.strptime(('' if len(start)>6 else '0')+start.upper(),'%I:%M%p')
                    end=datetime.datetime.strptime(('' if len(end)>6 else '0')+end.upper(),'%I:%M%p')
                    start=datetime.datetime(int(year),datetime.datetime.strptime(date[1],'%B').month,int(date[0].strip(string.ascii_letters+', ')),start.hour,start.minute)
                    end=datetime.datetime(int(year),datetime.datetime.strptime(date[1],'%B').month,int(date[0].strip(string.ascii_letters+', ')),end.hour,end.minute)
            elif 'am' in eventDate or 'pm' in eventDate:
                #single day w/ time
                eventDate=eventDate.split(', ')[1:]
                eventDate=''.join(eventDate).split(' ')
                time=datetime.datetime.strptime(('' if len(eventDate[2])>6 else '0')+eventDate[2].upper(),'%I:%M%p')
                start=datetime.datetime(int(year),datetime.datetime.strptime(eventDate[1],'%B').month,int(eventDate[0].strip(string.ascii_letters+', ')),time.hour,time.minute)
                endHour=time.hour+1
                if endHour>24:
                    endHour=0
                end=datetime.datetime(int(year),datetime.datetime.strptime(eventDate[1],'%B').month,int(eventDate[0].strip(string.ascii_letters+', ')),endHour,time.minute)
            else:
                #single day w/o time
                eventDate=eventDate.split(', ')[1:]
                eventDate=''.join(eventDate).split(' ')
                start=datetime.datetime(int(year),datetime.datetime.strptime(eventDate[1],'%B').month,int(eventDate[0].strip(string.ascii_letters+', ')),8,35)
                end=datetime.datetime(int(year),datetime.datetime.strptime(eventDate[1],'%B').month,int(eventDate[0].strip(string.ascii_letters+', ')),15,15)
            #finish parsing date
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

class _schoology:
    def __init__(self):
        self._state=0
        self.url='https://schoology.sanctamaria.school.nz/'
        self._userindependentdata=[]
    def login(self,userid,password):
        if self._state:
            raise BaseException('Already Logged In - Log Out First')
        else:
            self._session=requests.session()
            response=self._session.post(self.url+'/login?&school=457814129',{'mail':userid,'pass':password,'form_id':'s_user_login_form','school_nid':'457814129'})
            authenticated=(bs4.BeautifulSoup(response.text,'html.parser').find(class_='login-content')==None)
            if authenticated:
                self._state=1
                source=bs4.BeautifulSoup(response.text,'html.parser')
                self.name=source.find(id='profile').text
                self.id=source.find(id='profile').a.get('href').strip('/user')
                self.schoolID=source.find(class_='school').find('a').get('href').strip('school/')
            else:
                self._session.close()
                raise AuthenticationError('Incorrect Authorisation')
    def logout(self):
        if not self._state:
            raise BaseException('Already Logged Out - Log In First')
        else:
            self._session.close()
            self._state=0
            for x in list(set(self._userindependentdata)):
                exec('del self.'+x)
    def getCourses(self,memberid=None):
        if not self._state:
            raise BaseException('Must Be Logged In')
        else:
            temp=[]
            if memberid==None:
                response=bs4.BeautifulSoup(self._session.get(self.url+'courses').text,'html.parser')
                courses=response.findAll('li',class_='course-item')
                for course in courses:
                    id=course.findNext(class_='section-item').a.get('href').strip('/course')
                    title=course.p.find(class_='course-title').text
                    code=course.p.find(class_='course-code').text
                    temp.append(_course(title,code,id,'course'))
                self.courses=temp
            else:
                response=bs4.BeautifulSoup(self._session.get(self.url+'user/%s/courses/list'%(memberid)).text,'html.parser')
                courses=response.findAll(class_='course-item')
                for course in courses:
                    id=course.find(class_='course-item-left').a.get('href').strip('/course')
                    title=course.find(class_='course-item-right').a.text.split(':')[0]
                    code=None
                    temp.append(_course(title,code,id,'course'))
            return temp
    def getGroups(self,memberid=None):
        if not self._state:
            raise BaseException('Must Be Logged In')
        else:
            temp=[]
            if memberid==None:
                response=bs4.BeautifulSoup(self._session.get(self.url+'groups').text,'html.parser')
                groups=response.findAll(class_='mygroups-list-item')
                for group in groups:
                    id=group.find(class_='group-title').get('href').strip('/group')
                    title=group.find(class_='group-title').text
                    temp.append(_course(title,None,id,'group'))
                self.groups=temp
            else:
                response=bs4.BeautifulSoup(self._session.get(self.url+'user/%s/groups/list'%(memberid)).text,'html.parser')
                groups=response.findAll(class_='group-item')
                for course in courses:
                    id=course.find(class_='course-item-right').find('a')
                    if id != None:
                        id=id.get('href').strip('/group')
                    else:
                        id=None
                        title=course.find(class_='course-item-right').a.text.split(':')[0]
                    code=None
                    temp.append(_course(title,code,id,'course'))
            return temp
    def getMembers(self,course):
        if not self._state:
            raise BaseException('Must Be Logged In')
        else:
            temp=[]
            response=bs4.BeautifulSoup(self._session.get(self.url+course.type+'/'+course.id+'/members').text,'html.parser')
            table=response.find(class_='enrollment-user-list').table.tbody
            for member in table.findAll('tr'):
                name=member.find(class_='user-name').a.text
                picture='https://cdn3-1.cdn.schoology.com/system/files/imagecache/profile_reg/pictures/'+member.find(class_='profile-picture').img.get('src').split('/')[-1]
                id=member.find(class_='user-name').a.get('href').strip('/user')
                temp.append(_member(name,id,picture))
            course.members=temp
            return temp
    def getInfo(self,member=None):
        if not self._state:
            raise BaseException('Must Be Logged In')
        else:
            if member==None:
                response=bs4.BeautifulSoup(self._session.get(self.url+'user/'+self.id+'/info').text,'html.parser')
                posts,classmates=response.findAll(class_='social-counter-number',limit=2)
                self.email=response.find(class_='email').text
                self.picture=response.findAll(class_='profile-picture')[1].img.get('src')
                self.posts=int(posts.text)
                self.classmates=int(classmates.text)
            else:
                response=bs4.BeautifulSoup(self._session.get(self.url+'user/'+member.id+'/info').text,'html.parser')
                posts,classmates=response.findAll(class_='social-counter-number',limit=2)
                member.email=response.find(class_='email').text
                member.picture=response.findAll(class_='profile-picture')[1].img.get('src')
                member.posts=int(posts.text)
                member.classmates=int(classmates.text)
    def getStaff(self,page=None):
        if not self._state:
            raise BaseException('Must Be Logged In')
        else:
            if page!=None:
                response=bs4.BeautifulSoup(self._session.get(self.url+'school/'+self.schoolID+'/faculty?page=%s'%str(int(page)-1)).text,'html.parser')
                temp=[]
                for person in response.find(class_='faculty-listing').findAll('li'):
                    name=person.find(class_='faculty-name').text
                    id=person.find(class_='faculty-name').a.get('href').strip('/user')
                    picture='https://cdn3-1.cdn.schoology.com/system/files/imagecache/profile_reg/pictures/'+person.find(class_='profile-picture').img.get('src').split('/')[-1]
                    try:
                        email=person.find(class_='faculty-item-container-right').findAll('a')[1].get('href').split(':')[1]
                    except IndexError:
                        email=None
                    temp.append(_member(name,id,picture,email))
                self.staff=temp
                return temp
            else:
                response=bs4.BeautifulSoup(self._session.get(self.url+'school/'+self.schoolID+'/faculty?page=0').text,'html.parser')
                return int(response.find(class_='pager-last').a.get('href').split('=')[-1])+1               
            
#Exceptions
class AuthenticationError(Exception):
    pass

#Holder Classes
class _report:
    def __init__(self,year,term,data):
        self.year=year
        self.term=term
        self.data=data
    def __repr__(self):
        return self.year+' Report (Object)'
    def __str__(self):
        return self.year+' Report'

class _calendaritem:
    def __init__(self,title,start,end):
        self.start=start
        self.end=end
        self.length=end-start
        self.title=title
    def __repr__(self):
        return 'calendaritem: '+self.title
    def __str__(self):
        return self.title

class _member:
    def __init__(self,name,id,picture=None,email=None):
        self.email=email
        self.name=name
        self.picture=picture
        self.id=id
    def __repr__(self):
        return 'Member Object: '+self.name
    def __str__(self):
        return self.name

class _course:
    def __init__(self,title,code,id,type):
        self.title=title
        self.code=code
        self.id=id
        self.type=type
        self.state='condensed'
    def __repr__(self):
        return 'Course Object: '+(self.code if not self.code==None else self.title)
    def __str__(self):
        return self.title

class _dayTimetable:
    def __init__(self,date,homeroom,p1,p2,p3,p4,p5):
        self.date=date #TODO: convert str date to datetime object
        self.homeroom=homeroom
        self.p1=p1
        self.p2=p2
        self.p3=p3
        self.p4=p4
        self.p5=p5
        self._current=0
        self.dict={'homeroom':homeroom,'p1':p1,'p2':p2,'p3':p3,'p4':p4,'p5':p5} #TODO: More appropriate name here
    def __repr__(self):
        return 'Timetable Day Object: '+self.date
    def __str__(self):
        return self.date
    def __iter__(self):
        return self
    def __next__(self):
        if self._current>5:
            self._current=0
            raise StopIteration
        else:
            self._current += 1
            if self._current==1:
                return self.homeroom
            elif self._current==2:
                return self.p1
            elif self._current==3:
                return self.p2
            elif self._current==4:
                return self.p3
            elif self._current==5:
                return self.p4
            elif self._current==6:
                return self.p5
    def now(self):
        now=datetime.datetime.now()
        now=datetime.time(now.hour,now.minute)
        if now > datetime.time(8,35) and now < datetime.time(15,15):
            if now < datetime.time(9):
                return 'homeroom'
            elif now < datetime.time(10):
                return 'p1'
            elif now < datetime.time(11):
                return 'p2'
            elif now < datetime.time(11,25):
                return None
            elif now < datetime.time(12,25):
                return 'p3'
            elif now < datetime.time(13,25):
                return 'p4'
            elif now < datetime.time(14,15):
                return None
            else:
                return 'p5'
        else:
            return None

class _lessonTimetable:
    def __init__(self,subject,teacher,location):
        self.subject=subject
        self.teacher=teacher
        self.location=location
    def __repr__(self):
        return 'Lesson Object: '+self.subject
    def __str__(self):
        return self.subject

class _notices:
    def __init__(self,date,meetingNotices,generalNotices):
        date=date.split(' ')
        day=date[1].strip(string.ascii_letters)
        if len(day) < 2:
            day='0'+day
        month=date[3][:-1]
        year=date[4]
        self.date=datetime.datetime.strptime('%s %s %s'%(day,month,year),'%d %B %Y')
        self.meetingNotices=meetingNotices
        self.generalNotices=generalNotices
        self.allNotices=meetingNotices+generalNotices
    def __repr__(self):
        return 'Notices Object: '+str(len(self.meetingNotices)+len(self.generalNotices))
    def __str__(self):
        return 'Notices'

class _notice:
    def __init__(self,title,audience,description,teacher,location=None):
        self.title=title
        self.audience=audience
        self.description=description
        self.teacher=teacher
        if location:
            self.location=location
    def __repr__(self):
        return 'Notice Object: '+self.title
    def __str__(self):
        return self.title

class _result:
    def __init__(self,title,details,creds,result):
        self.title=title
        self.details=details
        self.credits=creds
        self.result=result
    def __repr__(self):
        return 'Result Object: '+self.title
    def __str__(self):
        return self.title

class _credits:
    def __init__(self,na,a,m,e):
        self.notAchieved=na
        self.achieved=a
        self.merit=m
        self.excellence=e
        self.total=na+a+m+e
    def __repr__(self):
        return 'Credits Object: '+str(self.total)
    def __str__(self):
        return str(self.total)
    def percentage(self):
        na=self.notAchieved/self.total*100
        a=self.achieved/self.total*100
        m=self.merit/self.total*100
        e=self.excellence/self.total*100
        return {'notAchieved':na,'achieved':a,'merit':m,'excellence':e}

class _newsletterItem:
    def __init__(self,title,link):
        self.title=title
        self.link=link
        self.extension=''.join(link.split('.')[-1])
    def __repr__(self):
        return self.title+' (Newsletter Object)'
    def __str__(self):
        return self.title
    def getData(self):
        data=requests.get(self.link).content
        self.data=data
        return data

class _newsItem:
    def __init__(self,title,link,text,image=None):
        self.image=image
        self.title=title
        self.link=link
        self.text=text
        self.state='condensed'
    def __str__(self):
        return self.title
    def __repr__(self):
        return 'NewsItem (%s): %s'%(self.state,self.title)
    def readMore(self):
        source=bs4.BeautifulSoup(requests.get(self.link).text,'html.parser')
        image=source.find(class_='article-image')
        if image != None:
            image='http://sanctamaria.school.nz/'+image.find('img').get('src')
        self.image=image
        self.text=source.find(class_='article-content').text
        self.state='expanded'
