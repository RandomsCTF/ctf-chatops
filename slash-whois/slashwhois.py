#!/usr/bin/python
import bottle   # pip install bottle
import requests
import threading
import socket
import json
from datetime import datetime, timedelta
import whois
import config

app = application = bottle.Bottle()
lastquery = datetime.now() - timedelta(hours = 1)

@app.route('/whois', method='POST')
def slack_post():
    body = bottle.request.body.read()

    token           = bottle.request.forms.get('token')
    team_id         = bottle.request.forms.get('team_id')
    team_domain     = bottle.request.forms.get('team_domain')
    service_id      = bottle.request.forms.get('service_id')
    channel_id      = bottle.request.forms.get('channel_id')
    channel_name    = bottle.request.forms.get('channel_name')
    timestamp       = bottle.request.forms.get('timestamp')
    user_id         = bottle.request.forms.get('user_id')
    user_name       = bottle.request.forms.get('user_name')
    target          = bottle.request.forms.get('text')
    trigger_words   = bottle.request.forms.get('trigger_words')

    if token != config.slack_token:  # integration token
        print "INVALID REQUEST RECEIVED! --> %s" % body
        return "LOL NOPE"

    print lastquery
    thisquery = datetime.now()
    print thisquery
    if (thisquery - lastquery) > timedelta(minutes = config.cooldown_min):
        print "No cooldown present."
    else:
        print "Whois tool cooling down! Please wait..."
        print (thisquery - lastquery)
        return "Whois tool cooling down! Please wait..."


    print "Whois request received from user: %s, for target: %s" % (user_name, target)

    # Make sure the target is valid by attempting a connection to it
    try:
        target_ip = socket.gethostbyname(target)
        socket.inet_aton(target_ip)
        print "Target is valid: %s - %s" % (target, target_ip)
    except socket.error:
        print "Target is not valid"
        return "Your target, %s, is not valid. Please try again with syntax `/whois <ip_or_hostname>`" % target

    print "Target: " + target
    thr = threading.Thread(target=runQuery(target, user_name, timestamp), args=(), kwargs={})
    thr.start()

    global lastquery
    lastquery = datetime.now()

def runQuery(target, user_name, timestamp):
    results = ""
    print "Starting query on target: " + target
    domain = whois.query(target)

    message = "----------------------------------------------------" + "\n"
    message = "Whois query initiated by: %s, on target: %s \n" % (user_name, target)
    for k, v in domain.__dict__.items():
	    message = message + '%s\t"%s"' % (k, v) + "/n"
    print message
    sendToSlack(message)

def sendToSlack(message):
    url = config.slack_url
    data = {"username": "whois","text": message}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print r.status_code
    print r.content
    print "\n"

if __name__ == '__main__':
    bottle.run(app, host='0.0.0.0', port=config.listen_port)
