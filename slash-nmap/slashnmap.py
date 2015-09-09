#!/usr/bin/env python
import bottle   # pip install bottle
import nmap
import requests
import json
import threading
import socket
from datetime import datetime, timedelta
import config

# initializes cooldown variable
lastscan = datetime.now() - timedelta(hours=1)
app = application = bottle.Bottle()


@app.route('/', method='POST')
def slack_post():
    body = bottle.request.body.read()

    token = bottle.request.forms.get('token')
    team_id = bottle.request.forms.get('team_id')
    team_domain = bottle.request.forms.get('team_domain')
    service_id = bottle.request.forms.get('service_id')
    channel_id = bottle.request.forms.get('channel_id')
    channel_name = bottle.request.forms.get('channel_name')
    timestamp = bottle.request.forms.get('timestamp')
    user_id = bottle.request.forms.get('user_id')
    user_name = bottle.request.forms.get('user_name')
    victim = bottle.request.forms.get('text')
    trigger_words = bottle.request.forms.get('trigger_words')

    if token != config.slack_token:  # integration token
        print "INVALID REQUEST RECEIVED! --> %s" % body
        return "LOL NOPE"

    print lastscan
    thisscan = datetime.now()
    print thisscan
    if (thisscan - lastscan) > timedelta(minutes=config.cooldown_min):
        print "No cooldown present."
    else:
        print "Scanner cooling down! Please wait..."
        print (thisscan - lastscan)
        return "Scanner cooling down! Please wait..."

    print "Scan request received from user: %s, for target: %s" % (user_name, victim)

    # Make sure the target is valid by attempting a connection to it
    try:
        victim_ip = socket.gethostbyname(victim)
        socket.inet_aton(victim_ip)
        print "Target is valid: %s - %s" % (victim, victim_ip)
    except socket.error:
        print "Target is not valid"
        message = "Scan requested by %s contains an invalid target: %s !" % (
            user_name, victim)
        sendToSlack(message)
        return "Your target, %s, is not valid. Please try again with syntax `/nmap <ip_or_hostname>`" % victim

    print "Victim: " + victim
    thr = threading.Thread(target=runScan(
        victim, user_name, timestamp), args=(), kwargs={})
    thr.start()

    global lastscan
    lastscan = datetime.now()


def runScan(victim, user_name, timestamp):
    results = ""
    print "Starting scan on target: " + victim
    message = "Starting scan on target: `%s`, requested by: `%s`. Results will post here momentarily." % (
        victim, user_name)
    sendToSlack(message)
    nm = nmap.PortScanner()
    nm.scan(hosts=victim, arguments=nmap_arguments)
    print nm.command_line()
    print "Scan run, sending results." + "\n"
    for host in nm.all_hosts():
        results = "----------------------------------------------------" + "\n"
        results = results + 'Scan run by: %s' % user_name + "\n"
        results = results + 'Ran at: %s' % timestamp + "\n"
        results = results + \
            'Host : %s (%s)' % (host, nm[host].hostname()) + "\n"
        results = results + 'State : %s' % nm[host].state() + "\n"
        results = results + 'Command: `%s`' % nm.command_line() + "\n"

        for proto in nm[host].all_protocols():
            results = results + '----------' + "\n"
            results = results + 'Protocol : %s' % proto + "\n"

            lport = nm[host][proto].keys()
            lport.sort()
            for port in lport:
                results = results + \
                    'port : %s\tstate : %s' % (port, nm[host][proto][
                                               port]['state']) + "\n"

    results = results + '----------------------------------------------------'

    print results + "\n"
    sendToSlack(results)


def sendToSlack(message):
    url = config.slack_url
    data = {"username": botname, "text": message}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print r.status_code
    print r.content
    print "\n"

if __name__ == '__main__':
    bottle.run(app, host='0.0.0.0', port=config.listen_port)
