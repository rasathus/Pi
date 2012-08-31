'''
Created on 21 Jul 2012

@author: Jeremy Blythe

screen - Manages the Textstar 16x2 4 button display

Read the blog entry at http://jeremyblythe.blogspot.com for more information
'''
import datetime
import time
import subprocess
import twitter
import urllib2
import json
import textStarSerialLCD

CLEAR = chr(12)
ESC = chr(254)
BLOCK = chr(154)

POLL_TICKS = 15
REFRESH_TICKS = 300

display = None
# Start twitter
twitter_api = twitter.Api()


def write_datetime():
    display.position_cursor(1, 1)
    dt=str(datetime.datetime.now())
    display.ser.write('   '+dt[:10]+'   '+'    '+dt[11:19]+'    ')

def get_addr(interface):
    try:
        s = subprocess.check_output(["ip","addr","show",interface])
        return s.split('\n')[2].strip().split(' ')[1].split('/')[0]
    except:
        return '?.?.?.?'

def write_ip_addresses():
    display.position_cursor(1, 1)
    display.ser.write('e'+get_addr('eth0').rjust(15)+'w'+get_addr('wlan0').rjust(15))

def write_twitter():
    display.position_cursor(1, 1)
    try:
        statuses = twitter_api.GetUserTimeline('Raspberry_Pi')
        twitter_out = BLOCK
        for s in statuses:
            twitter_out+=s.text.encode('ascii','ignore')+BLOCK
        display.ser.write(twitter_out[:256])
    except:
        display.ser.write('twitter failed'.ljust(256))

def write_recent_numbers():
    display.position_cursor(1, 1)
    try:
        result = urllib2.urlopen("http://jerbly.uk.to/get_recent_visitors").read()
        j = json.loads(result)
        if len(j) > 0:
            entry = str(j[0]['numbers'][-1:])+' '+j[0]['countryName']
            display.ser.write(entry.ljust(32))
        else:
            display.ser.write('No entries found'.ljust(32))
    except:
        display.ser.write('jerbly.uk.to    failed'.ljust(32))

# Callbacks
def on_page():
    display.clear()
    display.window_home()
    if display.page == 'a':
        write_datetime()
    elif display.page == 'b':
        write_recent_numbers()
    elif display.page == 'c':
        write_twitter()
    elif display.page == 'd':
        write_ip_addresses()
        
def on_poll():
    if display.page == 'c':
        display.scroll_down()

def on_tick():
    if display.page == 'a':
        write_datetime()

def on_refresh():
    if display.page == 'b':
        write_recent_numbers()
    elif display.page == 'c':
        write_twitter()
    elif display.page == 'd':
        write_ip_addresses()

display = textStarSerialLCD.Display(on_page, on_poll, on_tick, on_refresh)            
display.run()

