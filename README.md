# CalenderBot
A simple Discord Bot with meetings. 


# Commands:
#newMeeting [Meeting] [DD.MM.YYYY, HH:MM] [time zone] [frequency]

#newMeeting [Meeting] [DD.MM.YYYY, HH:MM] [time zone] [frequency] @role

#deleteMeeting [Meeting] [DD.MM.YYYY, HH:MM]

#myMeetings

#help


# Run Bot

1) add a system variable (variable: CALBOTTOKEN, value: your token)
2) run command in docker: docker run -it -e "CALBOTTOKEN=your token" unity5/calendarbot:1.0
