#Code for Barcode Scanner
from time import sleep
import datetime
import threading
import requests
import cv2
import subprocess #Allows us to run console commands
from pyzbar import pyzbar
import liquidcrystal_i2c 

connected = 0

def attempt_reconnection():
    #Nifty Pi CLI commands for connection

    # nmcli connection show - Shows all saved connections
    # sudo wpa_cli -i wlan0 scan/scan_results - Scan first, then show results. Shows all available wifi connections
    # nmcli device wifi connect "SSID_NAME" password "wifi_password" ifname wlan0 - Connect to a wifi with the specific SSID with password. wlan0 refers to the pis network card. 
    #nmcli device disconnect wlan0 - Disconnect from wifi
    #nmcli device connect wlan0 - Reconnects the most recently used saved Wi-Fi network that’s available, based on its priority list
    #nmcli connection modify "SSID" connection.priority 10 - Modifies the priority of connection with the given SSID

    #print("Attempting to reconnect...")
    while True:
        if connected:
            sleep(300) #Recheck internet status every 5 minutes, if we are connected
        else:
            #Disconnect and reconnect
            subprocess.check_call(["nmcli","device","disconnect","wlan0"], 
            stdout=subprocess.DEVNULL, # Hide output from printing to console.(Redirects stdout to DEVNULL)
            stderr=subprocess.DEVNULL # Hide error output
            )
            sleep(20) #Allows the connection to disconnect
            subprocess.check_call(["nmcli","device","connect","wlan0"], 
            stdout=subprocess.DEVNULL, # Hide output from printing to console.(Redirects stdout to DEVNULL)
            stderr=subprocess.DEVNULL # Hide error output
            )
            sleep(20) #Allows the connection to disconnect
            if has_internet():
                connected = 1
            else: 
                connected = 0
   
def has_internet():
    try:
        subprocess.check_call(
            ["ping", "-c", "1", "8.8.8.8"],  # Command to run. (Send 1 ICMP packet to google dns server(8.8.8.8))
            stdout=subprocess.DEVNULL, # Hide output from printing to console.(Redirects stdout to DEVNULL)
            stderr=subprocess.DEVNULL # Hide error output
        )
        return True
    except subprocess.CalledProcessError: #If Error, return false
        return False

def submitscans(curr,h):
    c = []
    for i in curr.keys():
        c.append([i,curr[i]]) #C is an array of [ID, Time] pair for those currently checked in. H is a array of [ID, Time, Time] for people that have checked in & out. 
    response = requests.post("http://localhost:8000/batchscan", data = [c,h]) #Batch Append. This thread will block (won't be scheduled) until request is finished.
    response = response.json()

    '''Error Scanario:
    May require mutex lock for following scanario:
    1) Main thread scan triggers batch scan thread(There is internet). 
    2) Batch scan starts going
    3) Batch scan returns, but thread switches to main before clearing curr and history.
    4) Next scan has no internet, so it gets appended to curr/h
    5) On switch back to this thread, success condition(below) is evaluated, histories cleared, and the scan from main disappears

    Prob that this happens in this order is very low, but possible 
    '''
    if response["Success"]: #Clear both if we are successful -- TEST!!
        curr.clear() 
        h.clear() 

t = threading.Thread(target=attempt_reconnection) # Allocates thread. Target param is the function to execute and args is the arg passed.
t.start() #Start Thread. Multithreading helps as we don't have to wait scans caught offline to be uploaded before trying to scan new codes (We won't stall the main thread).

cols = 20
rows = 4
lcd = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=rows)
lcd.clear()

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

data = [] #
currcheck = {} #[ID] = Curr scan time
history = [] #Arr of Arr. [ID, first scan time, second scan time]
framenum = 0



lcd.printline(1, 'Initializing'.center(cols))
lcd.printline(2, 'Server...'.center(cols))

#Start Local Server. Popen command is non-blocking
proc = subprocess.Popen(
    ["npm", "run", "production"],
    cwd="/home/makerpi/Projects/makerspaceproj"
)

#message = 0 #Boolean to denote that a message has been posted so we don't get repeats...
lcd.clear()

try:
    while True:
        lcd.printline(1, 'Ready for Scan'.center(cols))
        while not data: #While we haven't had a code...
            ret, frame = cap.read() # Read a frame
            framenum += 1
            if framenum % 5 != 0: #Decode every 5th frame. FPS is ~25 for the camera and pi
                continue
            if not ret: #Error in reading frame
                lcd.printline(2,"Retry Scan".center(cols))
                sleep(1)
                lcd.clear() 
                lcd.printline(1, 'Ready for Scan'.center(cols))
                continue 
            data = pyzbar.decode(frame) #Decode the frame. Data will be populated if there is a QRcode in the frame
            framenum = 0

#-------Person Scans In-------
        lcd.clear()
        lcd.printline(1, 'Scanning...'.center(cols))
        ID = str(data[0].data)[2:-1] #ID from scan is parsed

        if has_internet(): #Check Internet...
            connected = 1
            if not currcheck or not history: #Because we have internet, we should upload local saved scans, if we have any
                t = threading.Thread(target=submitscans, args=[currcheck,history]) # Allocates thread. Target param is the function to execute and args is the arg passed.
                t.start() #Start Thread. Multithreading helps as we don't have to wait scans caught offline to be uploaded before trying to scan new codes (We won't stall the main thread).
            response = requests.post("http://localhost:8000/scan", json={"id":ID}) #Upload current scan
            response = response.json()
            if not response["Success"]: #If we get a failure
                print(response["Message"]) #Print Failure
                lcd.printline(2, 'Error Inputing'.center(cols))
                lcd.printline(3, 'Restart'.center(cols))
                raise Exception("Problem with Backend")
            lcd.printline(2, 'Scan Success'.center(cols))
            sleep(2)
            lcd.clear()
            ''' Error Scanario: 
                Check internet is evaluated, but right after, internet comes off, so following post will not go through.
                Checking the success status assist with catching it, but I may need to implement a more elegant solution
                to prevent lots of restarts if this happens often.
            '''
        else: #If we have no internet connection, we will save the scan locally
            connected = 0
            lcd.clear()
            if currcheck.get(ID): #If we have a scan for the ID already...
                history.push([ID, #Save the data (ID, first scan time, curr time) into the history array. This is for the history sheet
                              currcheck.pop(ID),#Also, Delete that entry from currcheck
                              datetime.datetime.now()])             
            else:
                currcheck[ID] = datetime.datetime.now() #Save just ID and Date pair 
            lcd.clear()
        data = [] #Clears Frame for next Scan/Reading
except KeyboardInterrupt: #Handles CTRL+C when exiting
    print("Interrupt Recieved...")

finally:
    lcd.clear()
    lcd.printline(1, 'Program Terminated'.center(cols))
    proc.terminate() #Terminate Server Process
    proc.wait() #Ensures server terminates by blocking until its done
    cap.release()
    print("Camera released. Exiting. ")


