"""
Tiger Pi Setup
With GUI
by Enny Jole
Occidental College
Information Technology Services
for Python <v3.5
"""
from subprocess import call
import os

def main():
  password = input("Please enter the setup password: \n")
  pwd = "pass:" + password
  #func_01 = "openssl des3 -d -in /home/pi/dd_script/nopass4u.txt -out /home/pi/dd_script/pwdfile.txt -pass pass:" + password
  #func_01 = "openssl des3 -d -in /Users/ennyjole/Desktop/nopass4u.txt -out /Users/ennyjole/Desktop/pwdfile.txt -pass pass:" + password
  #print(func_01)
  call(['openssl', 'des3', '-d', '-in', '/Users/ennyjole/Desktop/nopass4u.txt', '-out', '/Users/ennyjole/Desktop/pwdfile.txt', '-pass', _pwd])
  if os.stat("file").st_size == 0:
      call(['rm', '/Users/ennyjole/Desktop/pwdfile.txt'])
      print("Wrong password. Please try again.")
      exit
  else:
      file = open("/Users/ennyjole/Desktop/pwdfile.txt", "r")
      userpass = file.read()
      file.close()
      print(userpass)
