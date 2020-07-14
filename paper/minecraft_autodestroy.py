#!/usr/bin/env python3

from os import system
from re import search
from time import sleep
from json import loads
from urllib.parse import urlencode
from urllib.request import Request, urlopen

api_url = 'https://api.vultr.com/v1'
api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
mega_email = 'email@gmail.com'
mega_password = 'password1234'

# Logs the connected players
system("""sudo -H -u minecraft bash -c 'screen -S minecraft -p 0 -X stuff "list^M"'""")
sleep(5) # Wait 5 seconds

def autodestroy_server(save):
  # Stops the minecraft service
  system("systemctl stop minecraft.service")
  # Saves the files on the cloud
  if (save):
    #
    # CAREFUL! THIS IS  THE WORST WAY TO DO IT
    #
    # Uploads the end to Mega
    system("megarm --username " + mega_email + " --password " + mega_password + " /Root/minecraft/paper/world_the_end")
    system("megamkdir --username " + mega_email + " --password " + mega_password + " /Root/minecraft/paper/world_the_end")
    system("megacopy --username " + mega_email + " --password " + mega_password + " --reload --local /home/minecraft/paper/world_the_end --remote /Root/minecraft/paper/world_the_end")
    # Uploads the nether to Mega
    system("megarm --username " + mega_email + " --password " + mega_password + " /Root/minecraft/paper/world_nether")
    system("megamkdir --username " + mega_email + " --password " + mega_password + " /Root/minecraft/paper/world_nether")
    system("megacopy --username " + mega_email + " --password " + mega_password + " --reload --local /home/minecraft/paper/world_nether --remote /Root/minecraft/paper/world_nether")
    # Uploads the world to Mega
    system("megarm --username " + mega_email + " --password " + mega_password + " /Root/minecraft/paper/world")
    system("megamkdir --username " + mega_email + " --password " + mega_password + " /Root/minecraft/paper/world")
    system("megacopy --username " + mega_email + " --password " + mega_password + " --reload --local /home/minecraft/paper/world --remote /Root/minecraft/paper/world")
  # Destroys the VPS (doesn't check wich server - assumes only one server with the tag 'minecraft' exists)
  servers_request = Request(api_url + '/server/list?tag=minecraft', headers={'API-Key' : api_key})
  servers = loads(urlopen(servers_request).read())
  for key in servers:
    destroy_request = Request(api_url + '/server/destroy', headers={'API-Key' : api_key}, data={'SUBID': key})
    destroy = loads(urlopen(destroy_request).read())
    print(destroy)

# Reads all the connected players from the minecraft server log
def list_players_finder(file):
    for line in file:
        if 'players online' in line:
             yield line

logfile = open('/home/minecraft/paper/logs/latest.log','r')
results = list_players_finder(logfile)
current = []
for match in results:
  players = search('There are (.*) of a', match).group(1)
  seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(match[1:9].split(':'))))
  current.append((int(players), seconds))
logfile.close()

# Checks if the server needs to be destroyed
if (len(current) > 0):
  first_check = current[0]
  last_check = current[len(current) - 1]
  online = len([n for n in current if n[0] > 0])
  if (online > 0):
    last_online = [n for n in current if n[0] > 0][online - 1]
    # More than 30min since the last player connected
    if (last_check[1] - last_online[1] > 1800):
      autodestroy_server(True) # Saves the world
  else:
    # More than 45min without any player connecting
    if (last_check[1] - first_check[1] > 2700):
      autodestroy_server(False)
