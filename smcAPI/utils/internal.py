import datetime
import string

#Types:
#   1. start/end date :                    Sun, 30th October to Thu, 3rd November DONE
#   2. start/end date with time start/end: Wed, 7th September to Fri, 9th September 9:00am to 4:00pm DONE
#   3. single day w/o time:                Tue, 1st November DONE
#   4. single day with time start:         Tue, 25th October 6:00pm
#   5. single day with time start/end:     Wed, 2nd November 10:30am to 11:30am

def detect_date_type(date_string):
    def remove(iter_):
        for i in iter_:
            try:
                possible_types.remove(i)
            except ValueError:
                pass
    possible_types = [1, 2, 3, 4, 5]
    if ' to ' in date_string:
        if len(date_string.split(' to ')) == 3:
            remove([1, 3, 4, 5])
        else:
            remove([2])
        remove([3, 4])
    else:
        remove([1, 2, 5])
    if ':' in date_string:
        remove([1, 3])
    else:
        remove([2, 4, 5])
    if len(possible_types) > 1:
        #TODO: Improve Exception
        raise BaseException('Failed To Find String Type: {}'.format(date_string))
    else:
        return possible_types[0]

def parse_date(date_string, year, assume_school_time=False):
    year = int(year)
    type_ = detect_date_type(date_string)
    if type_ == 1:
        #start/end date
        #E.G: Sun, 30th October to Thu, 3rd November
        data = date_string.split(' to ')
        start = data[0]
        end = data[1]
        type_ = 'start/end date'
        start = start.split(' ')
        end = end.split(' ')
        start_day = start[:2]
        end_day = start[:2]
        start_month = start[2]
        end_month = end[2]
        start_day[1] = start_day[1].strip(string.ascii_letters)
        end_day[1] = end_day[1].strip(string.ascii_letters)
        start_day[0] = start_day[0].strip(',')
        end_day[0] = end_day[0].strip(',')
        if len(start_day) == 1:
            start_day = '0' + start_day
        if len(end_day) == 1:
            end_day = '0' + end_day
        if assume_school_time:
            start_temp = '08/35'
            end_temp = '15/15'
        else:
            start_temp = '00/00'
            end_temp = '23/59'
        start_date = '{}/{}/{}/{}/{}'.format(start_day[0], start_day[1], start_month, year, start_temp)
        end_date = '{}/{}/{}/{}/{}'.format(end_day[0], end_day[1], end_month, year, end_temp)
        start_payload = datetime.datetime.strptime(start_date, '%a/%d/%B/%Y/%H/%M')
        end_payload = datetime.datetime.strptime(end_date, '%a/%d/%B/%Y/%H/%M')
    elif type_ == 2:
        #start/end date with time start/end
        #E.G: Wed, 7th September to Fri, 9th September 9:00am to 4:00pm
        data = date_string.split(' ')
        start = data[:3] + [data[7]]
        end = data[4:7] + [data[9]]
        start[0] = start[0].strip(',')
        end[0] = end[0].strip(',')
        start[1] = start[1].strip(string.ascii_letters)
        end[1] = end[1].strip(string.ascii_letters)
        start[3] = start[3].split(':')
        end[3] = end[3].split(':')
        if 'am' in start[3][1].lower():
            start[3].append('AM')
        else:
            start[3].append('PM')
        if 'am' in end[3][1].lower():
            end[3].append('AM')
        else:
            end[3].append('PM')
        start[3][1] = start[3][1].strip(string.ascii_letters)
        end[3][1] = end[3][1].strip(string.ascii_letters)
        if len(start[3][0]) == 1:
            start[3][0] = '0' + start[3][0]
        if len(end[3][0]) == 1:
            end[3][0] = '0' + end[3][0]
        start[3] = ':'.join(start[3])
        end[3] = ':'.join(end[3])
        if len(start[1]) == 1:
            start[1] = '0' + start[1]
        if len(end[1]) == 1:
            end[1] = '0' + end[1]
        start_date = '{}/{}/{}/{}/{}'.format(start[0], start[1], start[2], year, start[3])
        end_date = '{}/{}/{}/{}/{}'.format(end[0], end[1], end[2], year, end[3])
        start_payload = datetime.datetime.strptime(start_date, '%a/%d/%B/%Y/%I:%M:%p')
        end_payload = datetime.datetime.strptime(end_date, '%a/%d/%B/%Y/%I:%M:%p')
    elif type_ == 3:
        #single day w/o time
        #E.G: Tue, 1st November
        start_day = date_string.split(' ')
        start_day[0] = start_day[0].strip(',')
        start_day[1] = start_day[1].strip(string.ascii_letters)
        if len(start_day[1]) == 1:
            start_day[1] = '0' + start_day[1]
        if assume_school_time:
            start_temp = '08:35'
            end_temp = '15:15'
        else:
            start_temp = '00:00'
            end_temp = '23:59'
        start_date = '{}/{}/{}/{}/{}'.format(start_day[0], start_day[1], start_day[2], year, start_temp)
        end_date = '{}/{}/{}/{}/{}'.format(start_day[0], start_day[1], start_day[2], year, end_temp)
        start_payload = datetime.datetime.strptime(start_date, '%a/%d/%B/%Y/%H:%M')
        end_payload = datetime.datetime.strptime(end_date, '%a/%d/%B/%Y/%H:%M')
    elif type_ == 4:
        #single day with time start
        #E.G: Tue, 25th October 6:00pm
        start_day = date_string.split(' ')
        start_day[0] = start_day[0].strip(',')
        start_day[1] = start_day[1].strip(string.ascii_letters)
        if len(start_day[1]) == 1:
            start_day[1] = '0' + start_day[1]
        start_day[3] = start_day[3].split(':')
        if 'pm' in start_day[3][1]:
            start_day[3].append('PM')
        else:
            start_day[3].append('AM')
        start_day[3][1] = start_day[3][1].strip('apm')
        if len(start_day[3][0]) == 1:
            start_day[3][0] = '0' + start_day[3][0]
        start_date = '{}/{}/{}/{}/{}:{}:{}'.format(start_day[0], start_day[1], start_day[2], year, start_day[3][0], start_day[3][1], start_day[3][2], start_day[3][1])
        start_payload = datetime.datetime.strptime(start_date, '%a/%d/%B/%Y/%I:%M:%p')
        if assume_school_time:
            end_date = '{}/{}/{}/{}/3:15:PM'.format(start_day[0], start_day[1], start_day[2], year)
            end_payload = datetime.datetime.strptime(end_date, '%a/%d/%B/%Y/%I:%M:%p')
            if end_payload <= start_payload:
                end_date = '{}/{}/{}/{}/11:59:PM'.format(start_day[0], start_day[1], start_day[2], year)
                end_payload = datetime.datetime.strptime(end_date, '%a/%d/%B/%Y/%I:%M:%p')
        else:
            end_date = '{}/{}/{}/{}/11:59:PM'.format(start_day[0], start_day[1], start_day[2], year)
            end_payload = datetime.datetime.strptime(end_date, '%a/%d/%B/%Y/%I:%M:%p')
    elif type_ == 5:
        #single day with time start/end
        #E.G: Wed, 2nd November 10:30am to 11:30am
        data = date_string.split(' ')
        start = data[:4]
        end = data[-1]
        start[0] = start[0].strip(',')
        start[1] = start[1].strip(string.ascii_letters)
        start[3] = start[3].split(':')
        end = end.split(':')
        if 'pm' in start[3]:
            start[3].append('PM')
        else:
            start[3].append('AM')
        if 'pm' in end:
            end.append('PM')
        else:
            end.append('AM')
        if len(start[1]) == 1:
            start[1] = '0' + start[1]
        if len(start[3][0]) == 1:
            start[3][0] = '0' + start[0]
        if len(end[0]) == 1:
            end[0] = '0' + end[0]
        start[3][1] = start[3][1].strip('apm')
        end[1] = end[1].strip('apm')
        start_date = '{}/{}/{}/{}/{}:{}:{}'.format(start[0], start[1], start[2], year, *start[-1])
        end_date = '{}/{}/{}/{}/{}:{}:{}'.format(start[0], start[1], start[2], year, *end)
        start_payload = datetime.datetime.strptime(start_date, '%a/%d/%B/%Y/%I:%M:%p')
        end_payload = datetime.datetime.strptime(end_date, '%a/%d/%B/%Y/%I:%M:%p')
    return start_payload, end_payload


























