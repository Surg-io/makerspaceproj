#Code for Barcode Scanner
from time import sleep

import requests
import cv2
import subprocess #Allows us to run console commands
import liquidcrystal_i2c 



cols = 20
rows = 4

lcd = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=rows)

lcd.printline(0, 'Initializing'.center(cols))
lcd.printline(1, 'Backend...'.center(cols))
lcd.printline(2, 'python-')
lcd.printline(3, 'liquidcrystal_i2c'.rjust(cols))

cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

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

    print("Attempting to reconnect...")
    subprocess.check_call(["nmcli","device","disconnect","wlan0"], 
    stdout=subprocess.DEVNULL, # Hide output from printing to console.(Redirects stdout to DEVNULL)
    stderr=subprocess.DEVNULL # Hide error output
    )
    sleep(10) #Allows the connection to disconnect
    subprocess.check_call(["nmcli","device","connect","wlan0"], 
    stdout=subprocess.DEVNULL, # Hide output from printing to console.(Redirects stdout to DEVNULL)
    stderr=subprocess.DEVNULL # Hide error output
    )



#Start Local Server
#subprocess.check_call(["npm","run","production"], 
#    stdout=subprocess.DEVNULL, # Hide output from printing to console.(Redirects stdout to DEVNULL)
#    stderr=subprocess.DEVNULL # Hide error output
#    )

while True:
    #if has_internet(): #Ping Google
        while True: 
            _, img = cap.read()
            data, bbox, _ = detector.detectAndDecode(img)
            if data:
                print(data)
                response = requests.post("http://localhost:8000/scan", json={"id": data})
                print(response)
                #frequency = 900
                #duration = 500
                #winsound.Beep(frequency,duration)
                if not response.Success:
                    #print error message
                    break
                sleep(3)
            cv2.imshow("QRCODEscanner", img)
            
    #else:
        #attempt_reconnection() #Attempt Reconnection
cap.release()
cv2.destroyAllWindows()