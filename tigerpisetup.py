"""
Tiger Pi Setup
With GUI
by Enny Jole
Occidental College
Information Technology Services
for Python <v3.5
"""
from subprocess import call
import os,crypt,random,sys

def main():
  password = input("Please enter the setup password: \n")
  pwd = "pass:" + password
  #func_01 = "openssl des3 -d -in /home/pi/dd_script/nopass4u.txt -out /home/pi/dd_script/pwdfile.txt -pass pass:" + password
  #func_01 = "openssl des3 -d -in /Users/ennyjole/Desktop/nopass4u.txt -out /Users/ennyjole/Desktop/pwdfile.txt -pass pass:" + password
  #print(func_01)
  call(['openssl', 'des3', '-d', '-in', '/Users/ennyjole/Desktop/nopass4u.txt', '-out', '/Users/ennyjole/Desktop/pwdfile.txt', '-pass', pwd])
  if os.stat("/Users/ennyjole/Desktop/pwdfile.txt").st_size == 0:
      call(['rm', '/Users/ennyjole/Desktop/pwdfile.txt'])
      print("Wrong password. Please try again.")
      exit
  else:
      file = open("/Users/ennyjole/Desktop/pwdfile.txt", "r")
      userpass = file.read()
      file.close()
      #h/t to David Ferguson from PiBakery and Filipe Pina on StackOverflow
      ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ./"
      salt = ''.join(random.choice(ALPHABET) for i in range(16))
      shadow_password = crypt.crypt(userpass,'$6$'+salt+'$')
      call(['usermod', '-p', shadow_password, 'pi'])
      certdir = "/home/pi/.certs/"
      def email_setup()
        call(['sudo', 'mkdir' certdir])
        call(['certutil', '-N', '-f', '/home/pi/dd_script/pwdfile.txt', '-d', '/home/pi/.certs/'])
        heading = "/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p"
        truehead = repr(heading)
        call(['echo', '-n', '|', 'openssl', 's_client', '-connect', 'smtp.gmail.com:465', '|', 'sed', '-ne', truehead, '>', '/home/pi/.certs/gmail.crt'])
        account = open(“/etc/nail.rc”,”w”)
        account.write("account helpdesk {")
        account.write("set smtp-use-starttls")
        account.write("set ssl-verify=ignore")
        account.write("set smtp-auth=login")
        account.write("set smtp=smtp://smtp.gmail.com:587")
        account.write("set from=" + repr(repr("helpdesk@oxy.edu")))
        account.write("set smtp-auth-user=helpdesk@oxy.edu")
        account.write("set smtp-auth-password=" + userpass)
        account.write("set ssl-verify=ignore")
        account.write("set nss-config-dir=/home/pi/.certs")
        account.write("}")
        account.close()
      if os.path.isdir(certdir) == True:
        do email_setup()
      else:
        call(['sudo', 'mkdir', certdir])
        do email_setup()
      
