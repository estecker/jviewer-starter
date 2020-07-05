# jviewer-starter
Auto download Java Web Start jars for remote console access rather than deal with javaws security warnings and making java work in your web browser. This has saved me a lot of time, hopefull it helps other folks. Works on all American Megatrends Incorporated BIOS systems that I have used.  90% of the time, you need to reboot the BMC before there's any chance of Java app to work. If the Java app does start, but the screen is blank, you might just need to wait a minute. Hit enter a few times and wait a minute, the console will hopefully appear.

## Usage

You can either use the shell script "jviewer" which tries to be smart and reboot the BMC if needed before connecting. Or just use the main program: "jviewer-starter.py".

````
jviewer <ipmi-ip-address> 

````
Assumes that you did not change default admin password of "admin". 


If the java program starts up, but then immeditally says 'Connection Failed' the BMC is in a bad state. To fix it either power cycle the whole server or just reset the BMC card with:

````
bmc-reset.sh <ipmi-hostname>
````

## Requirements
* Java 8. Version 10 has issues for some BMC versions. OpenJDK OK.
* python3: brew install python
  * requests: pip3 install requests
* FreeIPMI: brew install freeipmi
* nc: Installed in base OS
* Mac only
  * brew tap caskroom/versions
  * brew cask install java8
  * brew cask install xquartz
  * brew install coreutils
