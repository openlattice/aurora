import os
from slackclient import SlackClient
from phue import Bridge
import datetime
import colorsys, time, re, random
import requests

#setup bridge
b = Bridge('Your Bridge IP Here')
b.connect()

desk = [1]
token = 'Your Token Here'


def huePoint(color):
        # Splits the spectrum up by the number of lights in the chandiler to get
            # an evenly spaced rainbow of colors
    hue = 4095 * color
    return hue

def disco(sleeptime):
   for i in range(16):
        b.set_light(1, {'hue': huePoint(i), 'sat': 254, 'bri': 254, 'transitiontime': 3,'on':True})
        time.sleep(sleeptime)
        b.set_light(1,{'on':False})
        time.sleep(sleeptime)




def parse_bot_commands(slack_events):
    slack_client = SlackClient(token)
    #if slack_client.rtm_connect(with_team_state=False):
    for event in slack_events:
        #only message from users
        if event['type'] == 'message' and not "subtype" in event:
            #get the  user_id and the text of the post
            user_id, text_received, channel = event['user'], event['text'], event['channel']
            #activate if 'client' or 'customer' is in the post
            if channel == 'The proper Slack channelID':
                b.set_light(1, {'hue':39000, 'on':True})
            if any([k in text_received for k in ['new client', 'new customer', 'new jurisdiction', 'New Customer', 'New Jurisdiction', 'New Client']]):
                disco(0.5)
                slack_client.api_call("chat.postMessage", channel = channel, text = "I turned on the light!")
            if any([k in text_received for k in ['wifi']]):
                slack_client.api_call("chat.postMessage", channel=channel, text="Your Wifi Password")
            if any([k in text_received for k in ['light off']]):
                b.set_light(1, {'on': False})
            if any([k in text_received for k in ['welcome']]):
                slack_client.api_call("chat.postMessage", channel=channel, text="Welcome to OpenLattice!")
                disco(0.1)
            if any([k in text_received for k in ['disco']]):
                disco(0.1)
                disco(0.1)
            if any([k in text_received for k in ['ping']]):
                response = requests.get('Stack Health API')
                if response.status_code == 200:
                    b.set_light(1, {'hue': 25574, 'sat': 255, 'bri': 150, 'transitiontime': 3, 'on': True})
                    slack_client.api_call("chat.postMessage", channel = channel, text = "Pong")
                elif response.status_code == 502:
                    b.set_light(1, {'hue': 60000,'on': True})
                    slack_client.api_call("chat.postMessage", channel = channel, text = "502! Time to wake up Matthew!")
                else:
                    b.set_light(1, {'hue': 16000, 'on': True})
                    slack_client.api_call("chat.postMessage", channel = channel, text = "Uh oh. Time to go home! ")



if __name__ == "__main__":
    slack_client = SlackClient(token)
    response = requests.get('Stack Health API')
    if b'pong' in response.content:
        b.set_light(1, {'hue': 25574, 'sat': 255, 'bri':150, 'transitiontime': 3, 'on': True})
    if slack_client.rtm_connect(with_team_state=False):
        lightbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            parse_bot_commands(slack_client.rtm_read())
            time.sleep(1)