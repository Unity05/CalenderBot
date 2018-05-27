import discord
import time
import asyncio

client = discord.Client()
meetingDateSP = 0

helpEmbed = discord.Embed(title="Hilfe für CalenderBot", url = 'https://github.com/Unity05', description= '', field = 'Präfix',color = discord.Colour.blue())
myMeetingsEmbed = discord.Embed(title="MyMeetings", color=discord.Colour.blue())
helpEmbed.set_footer(text = "bot by Unity5#2704 | special thanks to @Anorak#5830")
helpEmbed.add_field(name = 'Präfix', value = '``#``')
helpEmbed.add_field(name = 'Befehle', value = '``newMeeting [Meeting] [DD.MM.YYYY, HH:MM] [Zeitverschiebung]`` fügt ein neues Meeting hinzu \n``newMeeting [Meeting] [DD.MM.YYYY, HH:MM] [Zeitverschiebung] @role`` fügt ein neues Meeting für alle mit dieser Rolle hinzu \n``deleteMeeting [Meeting] [DD.MM.YYYY, HH:MM]`` löscht alle Meetings mit dem Inhalt an dem Datum \n``myMeetings`` gibt alle deine Meetings aus \n``date``zeigt das datum \n``help`` sendet diese Hilfe')





def checkSchaltjahr(year):
    if (int(year)-2016)/4 == int(int(year)-2016)/4 :
        return True
    else:
        return False
#dd.mm.yyyy, hh:mm
def checkDate(content):
    try:
        d = int(content[0:2])
        m = content[3:5]
        print(content)
        y = content[6:10]
        print(content)
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

              
async def sendMeetingsPN():
    await client.wait_until_ready()
    while not client.is_closed():
        date = time.strftime('%d.%m.%Y, %H:%M')
        for users in backendMeetings.keys():
            for dates, dates2 in zip(backendMeetings[users], meetings[users]):
                if str(dates) == date and str(backendMeetings[users][dates]) != '[]':
                    meetingEmbed = discord.Embed(title="Benachrichtigung", description=str(backendMeetings[users][dates])[2:len(backendMeetings[users][dates])-3], color=discord.Colour.blue())               
                    await client.get_user(int(users)).send(embed = meetingEmbed)
                    v = backendMeetings[users][dates] = [] 
                    v2= meetings[users][dates2] = []
                    break
                 
        await asyncio.sleep(30) # task runs every 30 seconds


def meetingContent(content):                    
    endPoint = list(content).index(']')
    return [str(content[1:endPoint]), endPoint+3]
    
def meetingDate(content, startPoint):
    newContent = content[startPoint:]
    endPoint = list(newContent).index(']')
    return [str(newContent[ :endPoint]), endPoint+14]
    
def sTimeZone(content):
    newContent = content[20: ]
    endPoint = list(newContent).index(']')
    return [str(newContent[ :endPoint]), endPoint+2, newContent]
    
def checkRole(content, startPoint):
    return content[startPoint+3 : len(content)-1]
    
def newTime(content, timeZone):
    hour = content[12:14 ]
    minute = content[15:17]
    day = content[ :2]
    month = content[3:5]
    year = content[6:10]
    
    try:
        time = int(hour) + int(timeZone)
        if time > 24:
            time = 0 + time % 24        
            day = int(day) + 1
        
            if month == '02' and checkSchaltjahr(year) == False and int(day) > 28:
                month == '03'
                day = '01'
            elif month == '01' or month == '03' or month == '05' or month == '07' or month == '08' or month == '10' or month == '12' and int(day) > 31:
                month = int(month) + 1
                day = '01'
            elif month == '02' or month == '04' or month == '06' or month == '09' or month == '11' and int(day) >30:
                month = int(month) + 1
                day = '01'
            if str(month) == '13':
                year = int(year) + 1
                month = '01'           
        
        elif time < 0:
            time = 24 - (time * (-1))
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
        if len(str(time)) == 1:
            time = '0' + str(time)    
        
        date = str(day) + '.' + str(month) + '.' + str(year) + ', ' + str(time) + ':' + str(minute)
        
        return date
        
    except ValueError:
        return 'wrongDate'



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
  
meetings = {}
backendMeetings = {}
groupMeetings = {}
meetingDateVar = 'lol'
        
@client.event
async def on_message(message):
    if message.author == client.user:
        return
   
     
    if message.content.startswith('#newMeeting'):
        
        guild = message.guild
        adminRole = discord.utils.get(guild.roles, name='Admin')
        
        contentList = str(message.content)
        contentListSaver = contentList
        contentListForDate = contentList[12: ]
        contentList = meetingContent(contentList[12: ])[0]
        contentListSaver = meetingContent(contentListSaver[12: ])[1]
        meetingDateVar = meetingDate(str(contentListForDate), int(contentListSaver))[0]
        dateEndpoint = meetingDate(str(contentListForDate), int(contentListSaver))[1]
        rightDate = checkDate(str(meetingDateVar))
        timeZone = sTimeZone(str(contentListForDate)[contentListSaver:])[0]
        timeZoneEndpoint = sTimeZone(str(contentListForDate)[contentListSaver:])[1]
        groupContent = sTimeZone(str(contentListForDate)[contentListSaver:])[2]
        group = checkRole(str(groupContent), int(timeZoneEndpoint))
        date = newTime(str(meetingDateVar), timeZone)
        if rightDate == False:
            await message.channel.send("Sie haben ein ungültiges Datum eingegeben!")
        else:
        
            isEvenKey = False
            
            if str(group) == '' or str(group) == ' ':
                for i in meetings.keys():
                    if i == str(message.author.id):
                        isEvenKey = True
                    
                if isEvenKey == False:
                    liste = {str(meetingDateVar) : [str(contentList)]}
                    meetings[str(message.author.id)] = liste
                    backendListe = {str(newTime(str(meetingDateVar), timeZone)) : [str(contentList)]}
                    backendMeetings[str(message.author.id)] = backendListe
                    
                    await message.channel.send(str(message.author.display_name) + ' hat ``' + str(contentList) + '`` für den ' + str(meetingDateVar) + ' hinzugefügt!')
                else:
                    try:
                        meetings[str(message.author.id)][str(meetingDateVar)].append(str(contentList))
                        backendMeetings[str(message.author.id)][str(date)].append(str(contentList))
                    except KeyError:
                        meetings[str(message.author.id)][str(meetingDateVar)] = [str(contentList)]
                        backendMeetings[str(message.author.id)][str(date)] = [str(contentList)]
                        
                    await message.channel.send(str(message.author.display_name) + ' hat ``' + str(contentList) + "`` für den " + str(meetingDateVar) + ' hinzugefügt!')
                        
            elif adminRole in message.author.roles:
                 for i in meetings.keys():
                    if i == str(message.author.id):
                        isEvenKey = True
                 goif = str(newTime(str(meetingDateVar), timeZone))
                 if goif != 'wrongDate':  
                     for member in guild.members:
                         for role in member.roles:
                             if str(role.id) == group:

                                 if isEvenKey == False:
                                     liste = {str(meetingDateVar) : [str(contentList)]}
                                     meetings[str(member.id)] = liste
                                     backendListe = {str(newTime(str(meetingDateVar), timeZone)) : [str(contentList)]}
                                     backendMeetings[str(message.author.id)] = backendListe

                                 else:
                                     try:
                                         meetings[str(member.id)][str(meetingDateVar)].append(str(contentList))
                                         backendMeetings[str(message.author.id)][str(newTime(str(meetingDateVar), timeZone))].append(str(contentList))
                                     except KeyError:
                                         meetings[str(member.id)][str(meetingDateVar)] = [str(contentList)]
                                         backendMeetings[str(message.author.id)][str(newTime(str(meetingDateVar), timeZone))] = [str(contentList)]
           
                     await message.channel.send(str(message.author.display_name) + ' hat ``' + str(contentList) + '`` für den ' + str(meetingDateVar) + ' für alle mit der Rolle ' + str(group) + ' hinzugefügt!')
                     
                 else:
                     await message.channel.send('Sie haben ein ungültiges Datum eingegeben!')
                     
                        
              
                         
            else:
                await message.channel.send('Sie sind kein Admin!')
           
                              
            
        
        
        
    if message.content.startswith('#deleteMeeting'):
        
        contentList = str(message.content)
        contentListSaver = contentList
        contentListForDate = contentList[15: ]
        contentList = meetingContent(contentList[15: ])[0]
        contentListSaver = meetingContent(contentListSaver[15: ])[1]
        meetingDateVar = meetingDate(str(contentListForDate), int(contentListSaver))[0]
        
        
        i = 0
        try:
            for content in meetings[str(message.author.id)][str(meetingDateVar)]:
                if [str(content)] == [str(contentList)]:
                    datesForBackend = None
                    for dates, dates2 in zip(meetings[str(message.author.id)].keys(), backendMeetings[str(message.author.id)].keys()):
                        if str(dates) == str(meetingDateVar):
                            datesForBackend = dates2
                            break                           
                    v = meetings[str(message.author.id)][str(meetingDateVar)].pop(i)
                    v2 = backendMeetings[str(message.author.id)][datesForBackend].pop(i)
                    await message.channel.send("Dein Termin wurde erfolgreich gelöscht, " + str(message.author.display_name) + "!")      
                i += 1
        except KeyError:
            await message.channel.send("Sie haben an diesem Datum noch keine Termine, " + str(message.author.display_name) + "!")      
        
        
    if message.content.startswith('#myMeetings'):
        if str(message.author.id) in meetings.keys():
            for date in meetings[str(message.author.id)].keys():
                valueStr = ''
                i = 0
                for value in meetings[str(message.author.id)][str(date)]:
                    if i < len(meetings[str(message.author.id)][str(date)])-1:
                        valueStr += str(value) + '; '
                    else:
                        valueStr += str(value)
                    i += 1
                if valueStr == '':
                        continue
                myMeetingsEmbed.add_field(name = str(date), value = valueStr)
            await message.add_reaction( "✔")
            await message.author.send(embed = myMeetingsEmbed)
            myMeetingsEmbed.clear_fields()
        else: 
            await message.channel.send("Sie haben noch keine Meetings!")
            
            
    if message.content.startswith('#help'):
          await message.add_reaction( "✔")
          await message.author.send(embed = helpEmbed)
        
        
    if message.content.startswith('#date'):
        await message.channel.send(time.strftime('%d.%m.%Y, %H:%M'))
        

client.loop.create_task(sendMeetingsPN())
client.run('Bot-Token')
