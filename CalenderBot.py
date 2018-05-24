import discord
import time
import asyncio

client = discord.Client()
meetingDateSP = 0

helpEmbed = discord.Embed(title="Hilfe für CalenderBot", url = 'https://github.com/Unity05', description= '', field = 'Präfix',color = discord.Colour.blue())
myMeetingsEmbed = discord.Embed(title="MyMeetings", color=discord.Colour.blue())
helpEmbed.set_footer(text = "bot by Unity5#2704")
helpEmbed.add_field(name = 'Präfix', value = '``#``')
helpEmbed.add_field(name = 'Befehle', value = '``#newMeeting [Meeting] [DD.MM.YYYY, HH:MM]`` fügt ein neues Meeting hinzu \n``#deleteMeeting [Meeting] [DD.MM.YYYY, HH:MM]`` löscht alle Meetings mit dem Inhalt an dem Datum \n``#myMeetings`` gibt alle deine Meetings aus')
#helpEmbed.set_footer('shit')


def checkSchaltjahr(year):
    if (int(year)-2016)/4 == int(int(year)-2016)/4 :
        return True
    else:
        return False
#dd.mm.yyyy, hh:mm
def checkDate(content):
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

              
async def sendMeetingsPN():
    await client.wait_until_ready()
    while not client.is_closed():
        date = time.strftime('%d.%m.%Y, %H:%M')
        for users in meetings.keys():
            i = 0
            for dates in meetings[users]:
                if str(dates) == date and meetings[users][dates] != []:
                    await client.get_user(int(users)).send(str(meetings[users][dates])[2:len(meetings[users][dates])-3])
                    v = meetings[users][dates].pop(i)
                    break
                i += 1
        await asyncio.sleep(30) # task runs every 60 seconds


def meetingContent(content):                    #gibt Meeting Grund und Start Punkt für Date zurück
    endPoint = list(content).index(']')
    #meetingDateSP = endPoint 
    return [str(content[1:endPoint]), endPoint+3]
    
def meetingDate(content, startPoint):
    newContent = content[startPoint:]
    endPoint = list(newContent).index(']')
    return [str(newContent[ :endPoint]), endPoint+14]
    
def checkRole(content, startPoint):
    return content[22: len(content)-1]
    

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
  
meetings = {}
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
        #if adminRole in message.author.roles:
        group = checkRole(str(contentListForDate)[contentListSaver:], int(dateEndpoint))
            #dawait message.channel.send("Sie sind Admin!")
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
                    
                    await message.channel.send(str(message.author.display_name) + ' hat ' + str(contentList) + " für den " + str(meetingDateVar) + ' hinzugefügt!')
                else:
                    try:
                        meetings[str(message.author.id)][str(meetingDateVar)].append(str(contentList))
                    except KeyError:
                        meetings[str(message.author.id)][str(meetingDateVar)] = [str(contentList)]
                        
                    await message.channel.send(str(message.author.display_name) + ' hat ' + str(contentList) + " für den " + str(meetingDateVar) + ' hinzugefügt!')
                        
            elif adminRole in message.author.roles:
                 for i in meetings.keys():
                    if i == str(message.author.id):
                        isEvenKey = True
                
                 for member in guild.members:
                     for role in member.roles:
                         if str(role.id) == group:

                             if isEvenKey == False:
                                 liste = {str(meetingDateVar) : [str(contentList)]}
                                 meetings[str(member.id)] = liste

                             else:
                                 try:
                                     meetings[str(member.id)][str(meetingDateVar)].append(str(contentList))
                                 except KeyError:
                                     meetings[str(member.id)][str(meetingDateVar)] = [str(contentList)]
           
                 await message.channel.send(str(message.author.display_name) + ' hat ' + str(contentList) + " für den " + str(meetingDateVar) + ' für alle mit der Rolle ' + str(group) + ' hinzugefügt!')
                     
                        
              
                         
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
            await message.channel.send('meetingDateVar: ' + str(meetingDateVar))
            for content in meetings[str(message.author.id)][str(meetingDateVar)]:
                print("content: " + str(content))
                print("contentList: " + str(contentList))
                if [str(content)] == [str(contentList)]:
                    #print(meetings[str(message.author.id)][str(meetingDateVar)].pop(i))
                    v = meetings[str(message.author.id)][str(meetingDateVar)].pop(i)
                    await message.channel.send("Dein Termin wurde erfolgreich gelöscht, " + str(message.author.display_name) + "!")      
                i += 1
        except KeyError:
            await message.channel.send("Sie haben an diesem Datum noch keine Termine, " + str(message.author.display_name) + "!")      
        
        
    if message.content.startswith('#myMeetings'):
        #await message.channel.send(meetings[str(message.author.id)])
        if str(message.author.id) in meetings.keys():
            #await message.channel.send(meetings[str(message.author.id)])
            for date in meetings[str(message.author.id)].keys():
                valueStr = ''
                i = 0
                for value in meetings[str(message.author.id)][str(date)]:
                    print(str(value))
                    if i < len(meetings[str(message.author.id)][str(date)])-1:
                        valueStr += str(value) + '; '
                    else:
                        valueStr += str(value)
                    i += 1
                print('lulululu')
                if valueStr == '':
                        print('ok')
                        #meetings[str(message.author.id)].pop(str(date))
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
          

    if message.content.startswith('#myTimezone'):
        await message.channel.send(time.strftime('%Z'))
        
    if message.content.startswith('#date'):
        await message.channel.send(time.strftime('%d.%m.%Y, %H:%M'))
        

client.loop.create_task(sendMeetingsPN())
client.run('NDM5NTMzNDg0MDAwODA0ODY2.DcUjZQ.F39WfnwM9z9K4PJJqfsBX6vc1d0')
