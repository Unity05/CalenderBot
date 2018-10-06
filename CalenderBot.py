import discord
import time
import datetime
import json
import asyncio
import os


client = discord.Client()

currentVersion = "1.3"  # var to check if the version of the files is the latest

meetingDateSP = 0

helpEmbed = discord.Embed(title="Hilfe für CalenderBot",  # helpEmbed for help-message
                          url='https://github.com/Unity05/CalenderBot/blob/master/README.md',
                          field='Präfix', color=discord.Colour.blue())
helpEmbed.set_footer(text="bot by Unity5#2704 | special thanks to @Anorak#5830")
helpEmbed.set_author(name='Unity5   GitHub: https://github.com/Unity05',
                     url='https://github.com/Unity05',
                     icon_url='https://avatars2.githubusercontent.com/u/38768420')
helpEmbed.add_field(name='Präfix', value='``#``')
helpEmbed.add_field(name='\n\nBefehle',
                    value='``newMeeting [Meeting] [DD.MM.YYYY, HH:MM] [Zeitverschiebung] [Häufigkeit]`` '
                          'fügt ein neues Meeting hinzu \n\n'
                          '``newMeeting [Meeting] [DD.MM.YYYY, HH:MM] [Zeitverschiebung] [Häufigkeit] [role]`` '
                          'fügt ein neues Meeting für alle User die diese Rolle haben \n\n'
                          '``deleteMeeting [Meeting] [DD.MM.YYYY, HH:MM]`` '
                          'löscht alle Meetings mit dem Inhalt an dem Datum \n\n'
                          '``deleteMeeting [Meeting] [DD.MM.YYYY, HH:MM] [role]`` '
                          'löscht das Meeting mit dem Inhalt an dem Datum für alle User die diese Rolle haben \n\n'
                          '``myMeetings`` gibt alle deine Meetings aus \n\n'
                          '``help`` sendet diese Hilfe \n\n')
helpEmbed.add_field(name='\n\nHäufigkeit',
                    value='``unique`` einmalig\n\n'
                          '``daily`` täglich\n\n'
                          '``weekly`` wöchentlich\n\n'
                          '``monthly`` monatlich\n\n'
                          '``yearly`` jährlich')
myMeetingsEmbed = discord.Embed(title="MyMeetings",  # myMeetingsEmbed for command #myMeetings
                                color=discord.Colour.blue())

meetingsFile = {}
backendMeetingsFile = {}
meetings = {}  # dict for meetings (saves meeting-content and date in your time zone)
backendMeetings = {}  # dict for meetings (saves meeting-content and the to utc converted date)
meetingDateVar = 'lol'


def is_dts_now():
    time = '%Z'
    if time == 'Mitteleuropäische Sommerzeit':
        return True
    else:
        return False


def is_dst_date(date):
    day = date[ :2]
    month = date[3:5]
    year = date[6:10]
    date_number = month + day

    if int(date_number) > 325 and int(date_number) < 1028:
        return True
    else:
        return False


def updateMeetingSaveFiles():
    '''
    replaces the meeting files content by meeting dicts
    :return: None
    '''

    with open("meetingsFile", "w") as fout:
        fout.write(json.dumps(meetings))

    with open("backendMeetingsFile", "w") as fout2:
        fout2.write(json.dumps(backendMeetings))


def checkSchaltjahr(year):
    '''
    checks if the param (year) is a leapyear
    :param year: the year
    :return: boolean (True/False)
    '''

    if (int(year) - 2016) / 4 == int(int(year) - 2016) / 4:
        return True
    else:
        return False


def checkDate(content):
    '''
    checks if the param (content) is possible
    :param content: the date
    :return: boolean (True/False)
    '''

    try:
        d = int(content[0:2])
        m = content[3:5]
        y = content[6:10]
        H = int(content[12:14])
        M = int(content[15:17])

        if d == 0:
            return False

        if int(m) > 12 or int(m) < 0:
            return False

        if y < time.strftime('%Y'):
            return False

        if checkSchaltjahr(y) == False:
            if m == '02':
                if d > 28:
                    return False

        if m == '01' or m == '03' or m == '05' or m == '07' or m == '08' or m == '10' or m == '12':
            if d > 31 or d < 0:
                return False

        if m == '02' or m == '04' or m == '06' or m == '09' or m == '11':
            if d > 30 or d < 0:
                return False

        if H > 24 or H < 0:
            return False

        if M > 59 or M < 0:
            return False

        if y == time.strftime('%Y') and int(m) < int(time.strftime('%m')):
            return False

        if y == time.strftime('%Y') and int(m) == time.strftime('%m') and d < time.strftime('%d'):
            return False

        return True

    except ValueError:
        return False


async def sendPreMeetingsPN():
    '''
    sends PNs with meetings to the users
    every 60 sec
    :return: None
    '''

    await client.wait_until_ready()

    while not client.is_closed():
        date = time.strftime('%d.%m.%Y, %H:%M')
        date2 = newTime(0, mode="minute", realTime=False, content=date)

        for users in backendMeetings.keys():
            for dates, dates2 in zip(backendMeetings[users], meetings[users]):
                if str(dates) == date2 and str(backendMeetings[users][dates]) != '[]':
                    embedDescriptionContent = None

                    for value in backendMeetings[users][dates]:
                        if embedDescriptionContent != None:
                            embedDescriptionContent += '; ' + str(value[0]) + ' [' + str(value[1]) + ']'
                        else:
                            embedDescriptionContent = str(value[0]) + ' [' + str(value[1]) + ']'
                    meetingEmbed = discord.Embed(title="Erinnerung",
                                                 description="In 30 Minuten: " + embedDescriptionContent,
                                                 color=discord.Colour.blue())
                    updateMeetingSaveFiles()
                    await client.get_user(int(users)).send(embed=meetingEmbed)
                    break

        await asyncio.sleep(60)  # task runs every 60 seconds


async def sendMeetingsPN():
    '''
    sends PNs 30 min before the meeting to the users
    every 60 sec
    :return: None
    '''

    await client.wait_until_ready()

    while not client.is_closed():
        date = time.strftime('%d.%m.%Y, %H:%M')

        for users in backendMeetings.keys():
            for dates, dates2 in zip(backendMeetings[users], meetings[users]):
                if str(dates) == date and str(backendMeetings[users][dates]) != '[]':
                    embedDescriptionContent = None

                    for value in backendMeetings[users][dates]:
                        if embedDescriptionContent != None:
                            embedDescriptionContent += '; ' + str(value[0]) + ' [' + str(value[1]) + ']'
                        else:
                            embedDescriptionContent = str(value[0]) + ' [' + str(value[1]) + ']'
                        times = str(value[1])

                        if times == "daily":
                            newDate = newTime(0, mode='day', content=dates2)
                            newDateBackend = newTime(0, mode='day', content=dates)

                        if times == 'weekly':
                            newDate = newTime(0, mode='week', content=dates2)
                            newDateBackend = newTime(0, mode='week', content=dates)

                        if times == 'monthly':
                            newDate = newTime(0, mode='month', content=dates2)
                            newDateBackend = newTime(0, mode='month', content=dates)

                        if times == 'yearly':
                            newDate = newTime(0, mode='year', content=dates2)
                            newDateBackend = newTime(0, mode='year', content=dates)

                        currentDate = time.strftime('%d.%m.%y, %H:%M')
                        currentDateDST = is_dst_date(currentDate)
                        dateBackendDST = is_dst_date(newDateBackend)

                        if currentDateDST == True and dateBackendDST == False:
                            newDateBackend = newTime(1, 'hour', content=date)
                        elif currentDateDST == False and dateBackendDST == True:
                            newDateBackend = newTime(-1, 'hour', content=date)

                        if times != 'unique':
                            try:
                                meetings[str(users)][str(newDate)].append([str(value[0]), str(value[1])])
                                backendMeetings[str(users)][str(newDateBackend)].append([str(value[0]), str(value[1])])

                            except KeyError:
                                meetings[str(users)].update({str(newDate): [[str(value[0]), str(value[1])]]})
                                backendMeetings[str(users)].update({str(newDateBackend):
                                                                        [[str(value[0]), str(value[1])]]})

                    meetingEmbed = discord.Embed(title="Benachrichtigung",
                                                 description="Jetzt: " + embedDescriptionContent,
                                                 color=discord.Colour.blue())
                    await client.get_user(int(users)).send(embed=meetingEmbed)

                    v = backendMeetings[users][dates] = []
                    v2 = meetings[users][dates2] = []
                    updateMeetingSaveFiles()

                    break

        await asyncio.sleep(60)  # task runs every 60 seconds


def meetingContent(content):
    '''
    splits the meeting content
    :param content: meeting content
    :return: meeting content-part
    '''

    endPoint = list(content).index(']')
    return [str(content[1:endPoint]), endPoint + 3]


def meetingDate(content, startPoint):
    '''
    splits the meeting content
    :param content: meeting content
    :param startPoint: start point of new meeting content-part
    :return: meeting content-part
    '''

    newContent = content[startPoint:]
    endPoint = list(newContent).index(']')
    return tuple([str(newContent[:endPoint]), endPoint + 14])


def sTimeZone(content):
    '''
    filters the time zone-part from meeting content
    :param content: meeting content
    :return: meeting content-part
    '''

    newContent = content[20:]
    endPoint = list(newContent).index(']')
    return [str(newContent[:endPoint]), endPoint + 2, newContent]


def checkRole(content, startPoint):
    '''
    filters the role ID-part from role content
    :param content: role content
    :param startPoint: start point of role content-part
    :return: role ID
    '''

    return content[startPoint + 6: len(content) - 1]


def newTime(timeZone, mode: str, content="nothing", realTime=False, availableMinute=0):
    '''
    adds a minute / hour / day / week / month / year up to the date
    updates (if necessary) the hour / day / month / year
    :param timeZone: the time zone
    :param mode: the mode (minute / hour / day / week / month / year)
    :param content: date content
    :param realTime: use current time (utc) or date content
    :param availableMinute: minute content for real time
    :return: new date
    '''

    hour = content[12:14]

    if realTime == True:
        minute = availableMinute
        hour = time.strftime("%H")
        day = time.strftime("%d")
        month = time.strftime("%m")
        year = time.strftime("%Y")
    else:
        minute = content[15:17]
        hour = content[12:14]
        day = content[:2]
        month = content[3:5]
        year = content[6:10]

    if mode == "hour":
        try:
            time0 = int(hour) + int(timeZone)

            if time0 > 24:
                time0 = 0 + time0 % 24
                day = int(day) + 1

                if month == '02' and checkSchaltjahr(year) == False and int(day) > 28:
                    month == '03'
                    day = '01'
                elif month == '01' or month == '03' or month == '05' or month == '07' or \
                        month == '08' or month == '10' or month == '12' and int(day) > 31:
                    month = int(month) + 1
                    day = '01'
                elif month == '02' or month == '04' or month == '06' or \
                        month == '09' or month == '11' and int(day) > 30:
                    month = int(month) + 1
                    day = '01'

                if str(month) == '13':
                    year = int(year) + 1
                    month = '01'

            elif time0 < 0:
                time0 = 24 - (time0 * (-1))
                day = int(day) - 1

                if int(day) < 1:
                    month = int(month) - 1

                if int(month) < 1:
                    year = int(year) - 1
                    month = '12'
                    day = '01'

            if len(str(day)) == 1:
                day = '0' + str(day)

            if len(str(month)) == 1:
                month = '0' + str(month)

            if len(str(time0)) == 1:
                time0 = '0' + str(time0)

            date = str(day) + '.' + str(month) + '.' + str(year) + ', ' + str(time0) + ':' + str(minute)
            return date

        except ValueError:
            return 'wrongDate'

    if mode == "minute":
        minuteTime = int(minute) + 30

        if minuteTime > 59:
            minute = minuteTime - 60

            if len(str(minute)) == 1:
                minute = "0" + str(minute)

            date = newTime(1, "hour", realTime=True, availableMinute=minute)
            return date

        else:
            if len(str(minuteTime)) == 1:
                minuteTime = "0" + str(minuteTime)

            return time.strftime("%d") + '.' + time.strftime("%m") + '.' + \
                   time.strftime("%Y") + ', ' + time.strftime("%H") + ':' + str(minuteTime)

    if mode == 'day':
        day = int(day) + 1

        if month == '02' and checkSchaltjahr(year) == False and int(day) > 28:
            if int(day) > 28:
                month == '03'
                day = '01'
        elif month == '01' or month == '03' or month == '05' or month == '07' or \
                month == '08' or month == '10' or month == '12' and int(day) > 31:
            if int(day) > 31:
                month = int(month) + 1
                day = '01'
        elif month == '02' or month == '04' or month == '06' or month == '09' or month == '11' and int(day) > 30:
            if int(day) > 30:
                month = int(month) + 1
                day = '01'

        if str(month) == '13':
            year = int(year) + 1
            month = '01'

        if len(str(month)) == 1:
            month = '0' + str(month)

        if len(str(day)) == 1:
            day = '0' + str(day)

        return str(day) + '.' + str(month) + '.' + str(year) + ', ' + str(hour) + ':' + str(minute)

    if mode == 'month':
        month = int(month) + 1

        if str(month) == '13':
            year = int(year) + 1
            month = '01'

        if len(str(month)) == 1:
            month = '0' + str(month)

        return str(day) + '.' + str(month) + '.' + str(year) + ', ' + str(hour) + ':' + str(minute)

    if mode == 'year':
        year = int(year) + 1
        return str(day) + '.' + str(month) + '.' + str(year) + ', ' + str(hour) + ':' + str(minute)

    if mode == 'week':
        day = int(day) + 7

        if month == '02' and checkSchaltjahr(year) == False and int(day) > 28:
            if int(day) > 28:
                month == '03'
                day = '01'

        elif month == '01' or month == '03' or month == '05' or month == '07' or \
                month == '08' or month == '10' or month == '12' and int(day) > 31:
            if int(day) > 31:
                month = int(month) + 1
                day = '01'
        elif month == '02' or month == '04' or month == '06' or month == '09' or month == '11' and int(day) > 30:
            if int(day) > 30:
                month = int(month) + 1
                day = '01'

        if str(month) == '13':
            year = int(year) + 1
            month = '01'

        if len(str(month)) == 1:
            month = '0' + str(month)

        if len(str(day)) == 1:
            day = '0' + str(day)

        return str(day) + '.' + str(month) + '.' + str(year) + ', ' + str(hour) + ':' + str(minute)


def checkMemberAlreadyInList(memeber):
    '''
    checks if member is already in dict
    :param memeber: member ID
    :return: boolean (True/False)
    '''

    for i in meetings.keys():
        if i == str(memeber):
            return True
    return False


@client.event
async def on_ready():
    '''
    starts when client has started
    :return: None
    '''

    is_dst_date('15.08.2030, 18:02')
    print('We have logged in as {0.user}'.format(client))

    await client.change_presence(activity=discord.Game(name='#help'))

    try:
        with open('__version__', 'r') as version_file:
            version = version_file.read()

            if str(version) == '"' + str(currentVersion) + '"':
                pass
            else:
                updateFilesToNewVersion()

    except FileNotFoundError:
        updateFilesToNewVersion()

    with open("meetingsFile", "r") as file:
        global meetings
        meetings = json.load(file)

    with open("backendMeetingsFile", "r") as file2:
        global backendMeetings
        backendMeetings = json.load(file2)


def updateFilesToNewVersion():
    '''
    checks if the version of the meeting files is the latest
    updates (if necessary) the meeting files
    :return: None
    '''

    with open('meetingsFile', 'r') as mF_read:
        meetingsDict = json.load(mF_read)
        newMeetingsDict = {}

        for users in meetingsDict.keys():
            for dates in meetingsDict[users].keys():

                try:
                    newMeetingsDict[users].update({str(dates): []})

                except KeyError:
                    newMeetingsDict[users] = {str(dates): []}

                for contents in meetingsDict[users][dates]:
                    newMeetingsDict[users][dates].append([contents[0], contents[1], 'own'])

    with open('backendMeetingsFile', 'r') as bmF_read:
        backendMeetingsDict = json.load(bmF_read)
        newBackendMeetingsDict = {}

        for users in backendMeetingsDict.keys():
            for dates in backendMeetingsDict[users].keys():

                try:
                    newBackendMeetingsDict[users].update({str(dates): []})

                except KeyError:
                    newBackendMeetingsDict[users] = {str(dates): []}

                for contents in backendMeetingsDict[users][dates]:
                    newBackendMeetingsDict[users][dates].append([contents[0], contents[1], 'own'])

    with open('meetingsFile', 'w') as mF_write:
        mF_write.write(json.dumps(newMeetingsDict))

    with open('backendMeetingsFile', 'w') as bmF_write:
        bmF_write.write(json.dumps(newBackendMeetingsDict))

    with open('__version__', 'w') as version_file_3:
        version_file_done = str(currentVersion)
        version_file_3.write(json.dumps(version_file_done))


@client.event
async def on_message(message):
    '''
    is executed if a user sent a message
    :param message: message
    '''

    guild = message.guild

    if message.author == client.user:
        return

    if message.content.startswith('#newMeeting'):
        adminRole = discord.utils.get(guild.roles, name='CP')
        contentList = str(message.content)
        contentListSaver = contentList
        contentListForDate = contentList[12:]
        contentList = meetingContent(contentList[12:])[0]
        contentListSaver = meetingContent(contentListSaver[12:])[1]
        meetingDateVar = meetingDate(str(contentListForDate), int(contentListSaver))[0]
        dateEndpoint = meetingDate(str(contentListForDate), int(contentListSaver))[1]
        rightDate = checkDate(str(meetingDateVar))
        timeZone = sTimeZone(str(contentListForDate)[contentListSaver:])[0]
        timeZoneEndpoint = sTimeZone(str(contentListForDate)[contentListSaver:])[1]
        times = sTimeZone(str(contentListForDate)[contentListSaver + timeZoneEndpoint + 1:])[0]
        date = meetingDateVar
        dateBackendDST = is_dst_date(meetingDateVar)
        timesEndpoint = sTimeZone(str(contentListForDate)[contentListSaver + timeZoneEndpoint + 1:])[1]
        groupContent = str(contentListForDate)[contentListSaver + 18 + timeZoneEndpoint + timesEndpoint:]
        group = groupContent[4: len(groupContent)-1]

        try:
            group = discord.utils.get(guild.roles, name=str(group)).id

        except AttributeError:
            group = ''

        if dateBackendDST == False:
            date = newTime(int(timeZone) - 1, "hour", content=str(meetingDateVar))  # "int(timeZone) + 2" geändert
        elif dateBackendDST == True:
            date = newTime(int(timeZone) - 2, "hour", content=str(meetingDateVar))  # "int(timeZone) + 2" geändert

        if times != 'unique' and times != 'daily' and times != 'weekly' and times != 'monthly' and times != 'yearly':
            await message.channel.send('Sie haben eine ungültige Häufigkeit eingegeben!')
            return

        if rightDate == False:
            await message.channel.send("Sie haben ein ungültiges Datum eingegeben!")
        else:
            isEvenKey = False

            if str(group) == '' or str(group) == ' ':
                for i in meetings.keys():
                    if i == str(message.author.id):
                        isEvenKey = True

                if isEvenKey == False:
                    liste = {str(meetingDateVar): [[str(contentList), str(times), 'own']]}
                    meetings[str(message.author.id)] = liste
                    backendListe = {str(date): [[str(contentList), times, 'own']]}
                    backendMeetings[str(message.author.id)] = backendListe

                    await message.channel.send(str(message.author.display_name) + ' hat sich ``' + str(contentList) +
                                               '`` für den ``' + str(meetingDateVar) + '`` hinzugefügt!')
                else:

                    try:
                        meetings[str(message.author.id)][str(meetingDateVar)].append([str(contentList),
                                                                                      str(times), 'own'])
                        backendMeetings[str(message.author.id)][str(date)].append([str(contentList),
                                                                                   str(times), 'own'])

                    except KeyError:
                        meetings[str(message.author.id)][str(meetingDateVar)] = [[str(contentList), str(times), 'own']]
                        backendMeetings[str(message.author.id)][str(date)] = [[str(contentList), str(times), 'own']]

                    await message.channel.send(str(message.author.display_name) + ' hat sich ``' + str(contentList) +
                                               "`` für den ``" + str(meetingDateVar) + '`` hinzugefügt!')

            elif adminRole in message.author.roles:
                goif = str(newTime(str(meetingDateVar), timeZone, "hour"))

                if goif != 'wrongDate':
                    for member in guild.members:
                        for role in member.roles:
                            if str(role.id) == str(group):
                                isEvenKey = checkMemberAlreadyInList(member.id)

                                if isEvenKey == False:
                                    liste = {str(meetingDateVar): [[str(contentList), str(times),
                                                                    ('für alle mit der Rolle ' + str(role)),
                                                                    str(role)]]}
                                    meetings[str(member.id)] = liste
                                    backendListe = {str(date): [[str(contentList), str(times), str(role)]]}
                                    backendMeetings[str(member.id)] = backendListe  # BEFORE: MESSAGE:AUTHOR:ID
                                else:

                                    try:
                                        meetings[str(member.id)][str(meetingDateVar)].append([str(contentList),
                                                                                              str(times),
                                                                                              ('für alle mit der Rolle '
                                                                                               + str(role)),
                                                                                              str(role)])
                                        backendMeetings[str(member.id)][str(date)].append([str(contentList),
                                                                                           str(times), str(role)])

                                    except KeyError:
                                        meetings[str(member.id)].update({str(meetingDateVar): [[str(contentList),
                                                                                                str(times),
                                                                                                ('für alle mit der '
                                                                                                 'Rolle ' + str(role)),
                                                                                                str(role)]]})
                                        backendMeetings[str(member.id)].update({str(date): [[str(contentList),
                                                                                             str(times), str(role)]]})

                    await message.channel.send(str(message.author.display_name) + ' hat ``' + str(contentList) +
                                               '`` für den ``' + str(meetingDateVar) + '`` für alle mit der Rolle <@&'
                                               + str(group) + '> hinzugefügt!')

                else:
                    await message.channel.send('Sie haben ein ungültiges Datum eingegeben!')

            else:
                await message.channel.send('Sie gehören nicht zum Community Projekt!')

        updateMeetingSaveFiles()

    if message.content.startswith('#deleteMeeting'):
        contentList = str(message.content)
        contentListSaver = contentList
        contentListForDate = contentList[15:]
        contentList = meetingContent(contentList[15:])[0]
        contentListSaver = meetingContent(contentListSaver[15:])[1]
        meetingDateVar, meetingDateEP = meetingDate(str(contentListForDate), int(contentListSaver))
        role_text = contentListForDate[contentListSaver+20: len(contentListForDate)-1]
        role_id = None
        role_role = None

        try:
            role_id = discord.utils.get(guild.roles, name=str(role_text)).id
            role_role = discord.utils.get(guild.roles, name=str(role_text))
        except AttributeError:
            if role_text != '':
                await message.channel.send('Die angegebene Rolle ``' + role_text + '`` existiert nicht.')

        i = 0

        if role_id == None:
            try:
                print(str(meetings[str(message.author.id)][str(meetingDateVar)]))
                for content in meetings[str(message.author.id)][str(meetingDateVar)][0]:  # ``[0]`` 15.08.2018, 16:10
                    print(content)
                    if [str(content)] == [str(contentList)]:
                        datesForBackend = None
                        for dates, dates2 in zip(meetings[str(message.author.id)].keys(),
                                                backendMeetings[str(message.author.id)].keys()):
                            if str(dates) == str(meetingDateVar):
                                datesForBackend = dates2
                                break
                        v = meetings[str(message.author.id)][str(meetingDateVar)].pop(i)
                        v2 = backendMeetings[str(message.author.id)][datesForBackend].pop(i)
                        await message.channel.send("Dein Termin wurde erfolgreich gelöscht, " +
                                                   str(message.author.display_name) + "!")
                    i += 1

            except Exception:
                await message.channel.send("Sie haben an diesem Datum noch keine Termine, " +
                                           str(message.author.display_name) + "!")
            updateMeetingSaveFiles()

        else:
            for members in meetings.keys():
                i = 0
                member_member = None
                for guild_members in guild.members:
                    print('hi1 \n' + str(guild_members.id) + '\n' + str(members))
                    if str(guild_members.id) == members:
                        print('hi2')
                        member_member = guild_members
                        break
                print(str(member_member.roles))
                if role_role not in member_member.roles:
                    print('CONTINUE')
                    continue
                else:
                    try:
                        for content, role_delete in zip(meetings[members][meetingDateVar],
                                                    meetings[members][meetingDateVar]):
                            print('ROLE: ' + str(role_delete[3]) + ' | ' + str(role_role))
                            if str(content[0]) == str(contentList) and str(role_delete[3]) == str(role_role):
                                datesForBackend = None
                                print('IM IN IF')
                                for dates, dates2 in zip(meetings[str(members)].keys(),
                                                    backendMeetings[str(members)].keys()):
                                    if str(dates) == str(meetingDateVar):
                                        datesForBackend = dates2
                                        break
                                print('IIIIIIIIII ' + str(i))
                                v = meetings[str(members)][str(meetingDateVar)].pop(i)
                                v2 = backendMeetings[str(members)][datesForBackend].pop(i)
                            i += 1

                    except Exception:
                        pass
            await message.channel.send('Der Termin ``' + str(content[0]) +
                                       '`` wurde für alle Benutzer mit der Rolle <@&' + str(role_role.id) +
                                       '> erfolgreich gelöscht.')
            updateMeetingSaveFiles()

    if message.content.startswith('#myMeetings'):
        if str(message.author.id) in meetings.keys():
            min_one_field = False
            for date in meetings[str(message.author.id)].keys():
                #min_one_field = False
                valueStr = ''
                i = 0
                dayWord = date[:10]
                day = dayWord[:2]
                month = dayWord[3:5]
                year = dayWord[6:10]
                thisDate = datetime.date(year=int(year), month=int(month), day=int(day))
                thisDate = thisDate.strftime("%A")

                for value in meetings[str(message.author.id)][str(date)]:
                    if i < len(meetings[str(message.author.id)][str(date)]) - 1:
                        if value[2] == 'own':
                            valueStr += str(value[0]) + ' [' + str(value[1]) + '] \n '
                        else:
                            valueStr += str(value[0]) + ' [' + str(value[1]) + '] ' + str(value[2]) + '\n'
                    else:
                        if value[2] == 'own':
                            valueStr += str(value[0]) + ' [' + str(value[1]) + '] \n '
                        else:
                            valueStr += str(value[0]) + ' [' + str(value[1]) + '] ' + str(value[2]) + '\n'

                    i += 1

                if valueStr == '':
                    continue
                min_one_field = True
                myMeetingsEmbed.add_field(name=thisDate + " - " + str(date), value=valueStr, inline=False)

            if min_one_field == False:
                myMeetingsEmbed.add_field(name='Keine Meetings', value='Sie haben noch keine Meetings.')

            await message.add_reaction("✔")
            await message.author.send(embed=myMeetingsEmbed)
            myMeetingsEmbed.clear_fields()

        else:
            myMeetingsEmbed.add_field(name='Keine Meetings', value='Sie haben noch keine Meetings.')
            await message.author.send(embed=myMeetingsEmbed)
            await message.add_reaction("✔")
            myMeetingsEmbed.clear_fields()

    if message.content.startswith('#help'):
        await message.add_reaction("✔")
        await message.author.send(embed=helpEmbed)

    if message.content.startswith('#date'):
        dateSend = newTime(2, mode="hour", content=time.strftime('%d.%m.%Y, %H:%M'), realTime=False)
        await message.channel.send(dateSend)


client.loop.create_task(sendMeetingsPN())
client.loop.create_task(sendPreMeetingsPN())
client.run(os.environ['CALBOTTOKEN'])
