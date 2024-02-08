import requests, os, json, csv, datetime

from ical.calendar import Calendar
from ical.event import Event
from ical.types import cal_address
from ical.types.cal_address import CalAddress

import datetime, calendar

from pathlib import Path
from ical.calendar_stream import IcsCalendarStream

calendar = Calendar()

url = "https://multi.univ-lorraine.fr/graphql"

with open('<TOKEN FILE PATH>', 'r') as f:
  tokens = f.readlines()

refresh_token = tokens[0][:-1] # Obtenir les tokens
token = tokens[1][:-1]


# Request header
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Accept": "*/*",
    "Accept-Language": "fr-FR,en-US;q=0.7,en;q=0.3",
    "Content-Type": "application/json",
    "x-refresh-token": refresh_token,
    "x-token": token,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

graphql_query = """
query timetable($uid: String!, $from: Float, $to: Float) {
  timetable(uid: $uid, from: $from, to: $to) {
    id
    messages {
      text
      level
    }
    plannings {
      id
      type
      label
      default
      messages {
        text
        level
      }
      events {
        id
        startDateTime
        endDateTime
        day
        duration
        urls
        course {
          id
          label
          color
          url
          type
        }
        teachers {
          name
          email
        }
        rooms {
          label
        }
        groups {
          label
        }
      }
    }
  }
}
"""

payload = {
    "operationName": "timetable",
    "variables": {"uid": "<NOM D'UTILISATEUR UL>", "from": 1696111200000, "to": 1719828000000}, # from : Timestamp début    to : Timestamp fin
    "query": graphql_query,  
}


# Envoi reqûete POST
response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    graphql_data = response.json()

    for i in range(0, len(graphql_data["data"]["timetable"]["plannings"][0]["events"])):
        data = graphql_data["data"]["timetable"]["plannings"][0]["events"][i]


        courseid = data["id"]
        startDateTime = data["startDateTime"]
        endDateTime = data["endDateTime"]
        duration = data["duration"]
        courseLabel = data["course"]["label"]

        weekday = (startDateTime[:4], startDateTime[5:7], startDateTime[8:10])
        weekday = datetime.date(int(weekday[0]), int(weekday[1]), int(weekday[2]))
        weekday = weekday.weekday() # Emploi du temps différent pour Vendredi

        try:
            teachers = data["teachers"][0]["name"]
        except:
            teachers = ""

        try:
            email = data["teachers"][0]["email"]
        except:
            email = ""

        try:
            room = data["rooms"][0]["label"]
        except:
            room = ""
        

        date = startDateTime.split('T')[0]
        year = int(date.split('-')[0])
        month = int(date.split('-')[1])
        day = int(date.split('-')[2])

        timeStart = startDateTime.split('T')[1].split('+')[0]
        hoursStart = int(timeStart.split(':')[0])
        minutesStart = int(timeStart.split(':')[1])
        secondsStart = int(timeStart.split(':')[2])


        timeEnd = endDateTime.split('T')[1].split('+')[0]
        hoursEnd = int(timeEnd.split(':')[0])
        minutesEnd = int(timeEnd.split(':')[1])
        secondsEnd = int(timeEnd.split(':')[2])

        # Fixer les pauses dans l'emploi du temps original

        if (hoursStart == 10 and minutesStart == 15): # matin tous les jours
          minutesStart = 25
        if (hoursEnd == 10 and minutesEnd == 15):
          minutesEnd = 5

        if (weekday != 4): # aprem tous les jours sauf le vendredi
          if (hoursEnd == 16 and minutesEnd == 0):
            hoursEnd = 15
            minutesEnd = 50
          elif (hoursStart == 16 and minutesStart == 0):
            minutesStart = 10

        else: # Vendredi
          if (hoursEnd == 15 and minutesEnd == 30):
            minutesEnd = 20
          elif (hoursStart == 15 and minutesStart == 30):
            minutesStart = 40

        organizers = {
            "CN" : teachers,
            "value" : "mailto:"+email
        }
        attendee = CalAddress(value = f"mailto:{email}", CN = teachers, CUTYPE = "INDIVIDUAL", ROLE = "REQUIRED-PARTICIPANT", PARTSTAT = "ACCEPTED")

        calendar.events.append(Event(summary=courseLabel, dtstart=datetime.datetime(year, month, day, hoursStart, minutesStart, secondsStart), dtend=datetime.datetime(year, month, day, hoursEnd, minutesEnd, secondsEnd), location=room, organizer=organizers, attendees=[attendee]))

    outputCalendar = "<OUTPUT FILE PATH>"


    filename = Path(outputCalendar)
    with filename.open(mode="w", encoding="utf-8") as ics_file:
        ics_file.write(IcsCalendarStream.calendar_to_ics(calendar))












elif response.status_code == 400:
    print("GraphQL Request Failed. Response Content:")
    print(response.text)
else:
    print("Failed to retrieve data from GraphQL endpoint. Status code:", response.status_code)
