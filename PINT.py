r"""PINT.py: the Public IP Notification Tool (PINT) automaticaly alerts a list of recipients about changes to a system's public-facing IP address via email."""

import sys
import smtplib
from requests import get
from time import time, sleep
from datetime import datetime, timedelta


emailAct = "sendFromThisAddress@bogus.dom" ## Outbound email address
emailPsw = "passWord123"                   ## Outbound email address password
smtpServ = "smtp.bogus.dom"                ## Outbound email smtp server
smtpPort = 587                             ## SMTP Port for outbound email server

recipientList = {"Foo":"recipient1@hotmail.com", "Bar":"recipient2@gmail.com"}           ## Dictionary of name:address pairs to be notified of IP changes
initialRecipient = "Bar"                                                                 ## Name of person who will receive the optional email upon script start
formSubject = "Server IP Update"                                                         ## Subject line of notification email
formMessage = "Hello {0}! \nMy public-facing IP address is now: {1} \nTime since " + \
                "last IP change: {2} \n\nCheers! \n-the server"                          ## Skeleton of notification email (with explicit line continuation for clarity)
repeatInterval = 6                                                                       ## The number of hours to wait before checking the IP again

ip = '0.0.0.0'
lastChange = 0
timeSinceLastChange = "0 days, 0 hours, 0 minutes, 0 seconds"
server = None

def main(): 
    init()
    if (len(sys.argv) > 1):       ## If the script is called with a flag of some sort, parse the flag
        if (sys.argv[1] == "-i"): ## If called with the "-i" flag, the initialRecipient will receive an email alerting them to the server state at script startup
            composeAlerts(True)   ## Let composeAlerts() know this is just the initial email
    while(True):
        loopLogic()
        sleep(repeatInterval * 3600)        


def init():
    global ip
    global lastChange
    
    lastChange = time()
    ip = checkIP()
    
    
def loopLogic():
    global ip
    
    currentIP = checkIP()
    if (ip != currentIP):
        composeAlerts()
       
       
def checkIP():
    ip = get('https://api.ipify.org').text ## Million thanks to the good folks over at https://www.ipify.org/ 
    return ip
    
    
def composeAlerts(initialEmail = False): ## If initialEmail is True then composeAlerts only sends email to initialRecipient
    global lastChange
    
    curTime = time()
    timeSince = timedelta(seconds = (curTime - lastChange))
    hours = (timeSince.seconds // 3600)
    minutes = (timeSince.seconds // 60) % 60
    seconds = (timeSince.seconds % 60)        
    timeSinceLastChange = "{0} days, {1} hours, {2} minutes, {3} seconds".format(timeSince.days, hours, minutes, seconds)
    lastChange = curTime

    if (not initialEmail): ## If this isn't the optional on-startup email, send to all recipients
        for addressee in recipientList:
            sendAlert(recipientList[addressee], formMessage.format(addressee, ip, timeSinceLastChange))
    else: ## Else this is merely an email to alert the initialRecipient
        sendAlert(recipientList[initialRecipient], formMessage.format(initialRecipient, ip, timeSinceLastChange))
    
    
def sendAlert(recipient, msg):
    global server

    ## REVIEW: After a month of real-world testing, consider the neccessity of a try-catch around sending the email.
    email = "Subject: {0}\n\n{1}".format(formSubject, msg)
    
    server = smtplib.SMTP(smtpServ, smtpPort)
    server.ehlo()
    server.starttls()
    server.login(emailAct, emailPsw)
    server.sendmail(emailAct, recipient, email)
    server.quit()


main()