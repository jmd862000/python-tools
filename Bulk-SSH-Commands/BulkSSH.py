#!/usr/bin/env python3
import base64
import paramiko
from time import sleep
import getpass
from sys import argv
import datetime

#TODO:Convert to argv
Host_Path = 'hostlist.txt'
Command_Path = 'commandlist.txt'
Log_Path = 'logfile.txt'
username = input("Enter the username [" + getpass.getuser() + "]: ")
if(username == ''):
    username = getpass.getuser()
password = getpass.getpass("Enter the password: ")
results = {}

##Get list of hosts to connect to
try:
    host_file = open(Host_Path)
    hosts = [x for x in host_file.readlines()]
    host_file.close()
except Exception as ex:
    print("Error reading host file " + Host_Path + ". " + ex)
    raise ex

#Get list of commands to run
try:
    command_file = open(Command_Path)
    commands = [x for x in command_file.readlines()]
except Exception as ex:
    print("Error reading command file " + Command_Path + ". " + ex)
    raise ex

#open log file
try:
    log_file = open(Log_Path,mode='w')
    log_file.write('********* ' + datetime.datetime.now().isoformat() + ' **************\n')
except Exception as ex:
    print("Error opening log file " + Log_Path + ". " + ex)
    raise ex

def ConnectToShell(pClient,username,password):
    try:
        pClient.connect(host, username=username, password=password)
        shell = pClient.invoke_shell()
        sleep(1)
        shell.send("\n")
        return shell
    except paramiko.ssh_exception.AuthenticationException:
        print("Incorrect credentials. ")
        username = input("Enter the username [" + getpass.getuser() + "]: ")
        if(username == ''):
            username = getpass.getuser()
        password = getpass.getpass("Enter the password: ")
        ConnectToShell(pClient,username,password)

for host in hosts:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    try:
        shell = ConnectToShell(client,username,password)
        prompt = shell.recv(1000).decode("utf-8")
        if prompt is None:
            shell.send("\n")
    except Exception as ex:
        log_file.write(str(ex) + '\n')
        results[host] = "Error: " + str(ex)
        raise ex

    #Cisco Enable Prompt
    if prompt[-1]=='#':
        device = prompt[2:-1]
        results[host] = {}
        log_file.write('----- Starting:' + device + ' ------\n')
        #eliminate "more" scrolling
        shell.send("terminal length 0\n")
        sleep(1)
        prompt = shell.recv(1000).decode("utf-8")
        for command in commands:
            log_file.write('...Sending command: ' + command + '\n')
            try:
                shell.send(command + '\n')
                sleep(1)
                log_file.write('...' + shell.recv(1000).decode("utf-8").replace('\n','\n...') + '\n')
                results[host][command] = "Success"
            except Exception as ex:
                results[host][command] = "Error: " + ex
    #Otherwise just run the commands
    else:
        results[host] = {}
        log_file.write('----- Starting:' + host + ' ------\n')
        for command in commands:
            log_file.write('...Sending command: ' + command + '\n')
            try:
                shell.send(command + '\n')
                sleep(1)
                log_file.write('...' + shell.recv(1000).decode("utf-8").replace('\n','\n...') + '\n')
                results[host][command] = "Success"
            except Exception as ex:
                results[host][command] = "Error: " + ex
client.close()
