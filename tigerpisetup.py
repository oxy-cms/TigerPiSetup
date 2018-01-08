"""
Tiger Pi Setup
With GUI
by Enny Jole '18
Occidental College
Information Technology Services
for Python <v3.5
"""
#Python 2.7 is the default installation on Raspbian OS. Rather than install v3.6, differentiate the system install and user install, and then run this program, I've opted to go with a pre-3.5 environment
#We lose out on the run() command for the shell, which is more efficeint, but otherwise there would be no difference between post-3.5 and pre-3.5 functionality
from subprocess import call #for shell commands
import os,crypt,random,sys,socket #for file manipulation, password encryption, and IP finding

def main(): #main function
  #Decryption and Authorization
  password = raw_input("Please enter the setup password: \n") #prompts for setup password, which decrypts user and email password and prevents unauthorized setup
  #call(['openssl', 'des3', '-d', '-in', '/home/pi/dd_script/nopass4u.txt', '-out', '/home/pi/dd_script/pwdfile.txt', '-pass', pwd])
  call(['gpg', '--output', '/home/pi/dd_script/pwdfile.txt','--passphrase', password, '--batch', '--decrypt', '/home/pi/dd_script/nopass4u.txt'])
  #Here GPG is called to decrypt the pre-encrypted password file. Naming the decryped file as "pwdfile.txt" is required for the email setup later on. When encrypting a new password file, it is imperative that the same name ("nopass4u.txt") and encryption method ("des3") be used.
  if os.stat("/home/pi/dd_script/pwdfile.txt").st_size == 0: #GPG won't create a file on a bad decryption. This if loop prevents the program from continuing in the event of a bad decryption
      print("Wrong password. Please try again.") #self-explanatory
      exit #closes the program
  else: #in the event of a successful decryption
      file = open("/home/pi/dd_script/pwdfile.txt", "r") #opens the password file as a variable
      userpass = file.read() #converts the contents of the file to a string
      file.close() #closes the password file to save resources. since it's already a string we don't need it anymore
      #Changing and Encrypting the User Password
      #h/t to David Ferguson from PiBakery and Filipe Pina on StackOverflow for this section
      ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ./" #alphabet as a string for entropy
      salt = ''.join(random.choice(ALPHABET) for i in range(16)) #picks 16 random characters to use as a salt
      shadow_password = crypt.crypt(userpass,'$6$'+salt+'$') #salts the password
      call(['usermod', '-p', shadow_password, 'pi']) #uses usermod to change the password for the user, storing it as a salted password
      #Changing the Hostname
      hostname = raw_input("Please enter the hostname: \n") #prompt to input host name
      call(['raspi-config', 'nonint', 'do_hostname', repr(repr(hostname))]) #uses the raspi-config script to change the hostname
      call(['hostname', '-b', repr(repr(hostname))]) #changes it in the system as well
      call(['systemctl', 'restart', 'avahi-daemon']) #restarts one of the networking services
      #Setting Up Web Content
      url = input("Please enter the web/slideshow URL: \n") #prompt for URL for slideshow or other web content
      def makescripts(): #easier to group this as one function to create the shell scripts used to launch, restart, etc the web content.
        launch = open("/home/pi/dd_script/launch_chrome.sh","w") #file path to write to
        launch.write("sleep 30") #pause so the Pi doesn't eat up all its resources on startup, and allows for network connection
        launch.write("chromium-browser --kiosk --incognito --no-first-run --disable-infobars --disable-session-crashed-bubble " + repr(url)) #launches Chrome. All the arguments are required to disable the ugly yellow bubble upon killing chrome during the refresh. the repr(url) part adds single quotes around the URL so Bash is happy (won't work otherwise.)
        launch.close() #closes the file to save resources
        relaunch = open("/home/pi/dd_script/chromium_launch_and_refresh.sh","w") #refresh script
        relaunch.write("PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin") #stuff for cron
        relaunch.write("killall chromium-browser;") #kills chrome
        relaunch.write("export DISPLAY=:0.0;") #sets the display. required to do this as a script/on command line
        relaunch.write("/bin/bash /home/pi/dd_script/launch_chrome.sh > /dev/null;") #runs the launch script, shoves the output to nowhereland so the cronjob isn't constantly running and eating up resources
        relaunch.close() #closes the file to save resources
        def makeshortcut(): #subscript to autolaunch chrome on startup
            shortcut = open("/home/pi/.config/autostart/launch_chrome.sh.desktop") #writing .desktop file directly to the proper path, no mv required
            shortcut.write("[Desktop Entry]") #this just says it's a shortcut
            shortcut.write("Name=Launch Chrome") #not needed, but good documentation
            shortcut.write("Comment=by Enny Jole (C/O 2018), Oxy ITS") #credit where credit is due (me)
            shortcut.write("Exec=/home/pi/dd_script/launch_chrome.sh") #path to script/program the shortcut runs
            shortcut.write("Type=Application") #I don't think this matters except when creating a shortcut for the command prompt. Good documentation practice anyway
            shortcut.write("Encoding=UTF8") #standard encoding
            shortcut.close() #closes the file to save resources
        if os.path.isdir("/home/pi/.config/autostart/") == True: #tests to see if the autostart directory exists or not
            makeshortcut() #if it does, then the shortcut function runs
        else: #if not--
            os.mkdir("/home/pi/.config/autostart/") #then we make it
            makeshortcut() #and then run the shortcut function
      makescripts() #actually runs the script making function
      #Email Setup
      print("Would you like to set-up email?\n") #prompts for email setup
      m_in = raw_input("Yes/No") #prompt again
      #we don't get a choice here. It'll do it anyway
      certdir = "/home/pi/.certs/" #sets the cert directory as a variable
      def email_setup(): #email setup function. just makes this easier
        call(['sudo', 'apt-get', 'install', 'heirloom-mailx', '-y']) #installs the mailx pacakage so PiBakery doesn't have to
        call(['sudo', 'apt-get', 'install', 'libnss3-tools', '-y']) #installs the certutil stuff so PiBakery doesn't have to
        call(['certutil', '-N', '-f', '/home/pi/dd_script/pwdfile.txt', '-d', '/home/pi/.certs/']) #runs certutil to start setting up the mail certificate so the Pi can send to outside addresses
        heading = "/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p" #heading of the cert as a string
        truehead = repr(heading) #heading with single quotes around it
        call(['echo', '-n', '|', 'openssl', 's_client', '-connect', 'smtp.gmail.com:465', '|', 'sed', '-ne', truehead, '>', '/home/pi/.certs/gmail.crt']) #pulls the SSL certificate from Gmail down and creates a certificate file for it
        account = open("/etc/nail.rc","w") #creates file for the account info
        account.write("account helpdesk {") #writes account info to file, line-by-line
        account.write("set smtp-use-starttls") #writes account info to file, line-by-line
        account.write("set ssl-verify=ignore") #writes account info to file, line-by-line
        account.write("set smtp-auth=login") #writes account info to file, line-by-line
        account.write("set smtp=smtp://smtp.gmail.com:587") #writes account info to file, line-by-line
        account.write("set from=" + repr(repr("helpdesk@oxy.edu"))) #writes account info to file, line-by-line
        account.write("set smtp-auth-user=helpdesk@oxy.edu") #writes account info to file, line-by-line
        account.write("set smtp-auth-password=" + userpass) #writes account info to file, line-by-line. uses the password pulled from the decrypted file earlier
        account.write("set ssl-verify=ignore") #writes account info to file, line-by-line
        account.write("set nss-config-dir=/home/pi/.certs") #writes account info to file, line-by-line
        account.write("}") #writes account info to file, line-by-line
        account.close() #closes the file to save resources
      #Email Logging (Dependent on Email Setup)
      def cronjobs(): #sets up cronjobs and autologging
        oneam = "0 1 " #variable so I don't have to repeat this
        sixam = "0 6 " #variable so I don't have to repeat this
        noon = "0 12 " #variable so I don't have to repeat this
        fourpm = "0 16 " #variable so I don't have to repeat this
        midnight = "0 0 " #variable so I don't have to repeat this
        everyday = "* * * " #variable so I don't have to repeat this
        sundays = "* * 0 " #variable so I don't have to repeat this
        call(['crontab', '-l', ';', 'echo', repr(repr(oneam + sundays + "/bin/bash cat /var/log/auth.log | mailx -A helpdesk -s 'SSH Log' helpdesk@oxy.edu"))]) #creates cronjob to email the SSH access log weekly on Sunday at 1am
        call(['crontab', '-l', ';', 'echo', repr(repr(oneam + sundays + "/bin/bash sudo apt-get upgrade -y"))]) #creates cronjob to upgrade packages on Sundays at 1am
        call(['crontab', '-l', ';', 'echo', repr(repr(sixam + everyday + "/bin/bash /home/pi/dd_script/chromium_launch_and_refresh.sh"))]) #creates cronjob to refresh the slideshow at 6am every day
        call(['crontab', '-l', ';', 'echo', repr(repr(noon + everyday + "/bin/bash /home/pi/dd_script/chromium_launch_and_refresh.sh"))]) #creates cronjob to refresh the slideshow at noon every day
        call(['crontab', '-l', ';', 'echo', repr(repr(fourpm + everyday + "/bin/bash /home/pi/dd_script/chromium_launch_and_refresh.sh"))]) #creates cronjob to refresh the slideshow at 4pm every day
      #IP Sending (Dependent on Email Setup)
      #h/t to Alexander from StackOverflow
      def ipmail(): #function for ip sending
        realip = ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
        #above line pulls IP as a string.
        subject = repr(repr("The IP address for " + hostname + "is " + realip)) #formatting for subject of the email
        call(['mailx', '-A', 'helpdesk' '-s', subject, 'helpdesk@oxy.edu']) #sends the email
      if os.path.isdir(certdir) == True: #if the cert directory exists--
        email_setup() #then the email setup goes through
      else: #otherwise
        call(['sudo', 'mkdir', certdir]) #we create it
        email_setup() #then do the email setup
      cronjobs() #then after do the cronjob
      ipmail() #then sends IP
      def timezone():
        timezone="America/Los_Angeles"
        call(['sudo', 'echo', timezone, '>', '/etc/timezone'])
        call(['sudo', 'cp', '/usr/share/zoneinfo/' + timezone, '/etc/localtime'])
      timezone()
