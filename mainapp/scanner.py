#Code for Barcode Scanner
from time import sleep

import requests
import cv2
import subprocess #Allows us to run console commands
from pyzbar import pyzbar
import liquidcrystal_i2c 



cols = 20
rows = 4
lcd = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=rows)
lcd.clear()


cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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

def attempt_reconnection():
    #Nifty Pi CLI commands for connection

    # nmcli connection show - Shows all saved connections
    # sudo wpa_cli -i wlan0 scan/scan_results - Scan first, then show results. Shows all available wifi connections
    # nmcli device wifi connect "SSID_NAME" password "wifi_password" ifname wlan0 - Connect to a wifi with the specific SSID with password. wlan0 refers to the pis network card. 
    #nmcli device disconnect wlan0 - Disconnect from wifi
    #nmcli device connect wlan0 - Reconnects the most recently used saved Wi-Fi network that’s available, based on its priority list
    #nmcli connection modify "SSID" connection.priority 10 - Modifies the priority of connection with the given SSID

    #print("Attempting to reconnect...")
    lcd.printline(1, 'Reconnecting'.center(cols))
    lcd.printline(2, 'to Internet...'.center(cols))
    subprocess.check_call(["nmcli","device","disconnect","wlan0"], 
    stdout=subprocess.DEVNULL, # Hide output from printing to console.(Redirects stdout to DEVNULL)
    stderr=subprocess.DEVNULL # Hide error output
    )
    sleep(10) #Allows the connection to disconnect
    subprocess.check_call(["nmcli","device","connect","wlan0"], 
    stdout=subprocess.DEVNULL, # Hide output from printing to console.(Redirects stdout to DEVNULL)
    stderr=subprocess.DEVNULL # Hide error output
    )
    sleep(10) #Allows the connection to disconnect



lcd.printline(1, 'Initializing'.center(cols))
lcd.printline(2, 'Server...'.center(cols))

#Start Local Server
#subprocess.check_call(["npm","run","production"], 
#    stdout=subprocess.DEVNULL, # Hide output from printing to console.(Redirects stdout to DEVNULL)
#    stderr=subprocess.DEVNULL # Hide error output
#    )

#message = 0 #Boolean to denote that a message has been posted so we don't get repeats...
lcd.clear()

data = []
framenum = 0

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

        #{obj.data.decode('utf-8')}
        lcd.clear()
        lcd.printline(1, 'Scanning...'.center(cols))
        
        if has_internet(): #Check Internet...
            response = requests.post("http://localhost:8000/scan", json={"id": data})
            if not response.Success:
                lcd.printline(2, 'Error Inputing'.center(cols))
                lcd.printline(3, 'Restart'.center(cols))
                break
            lcd.printline(2, 'Scan Success'.center(cols))
            sleep(3)
            lcd.clear()
        else:
            lcd.clear()
            attempt_reconnection()
            lcd.clear()
except KeyboardInterrupt: #Handles CTRL+C when exiting
    print("Interrupt Recieved...")
finally:
    cap.release()
    print("Camera released. Exiting. ")
