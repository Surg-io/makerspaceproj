#Code for Barcode Scanner
from time import sleep

import requests
import cv2
import subprocess #Allows us to run console commands
import liquidcrystal_i2c 



cols = 20
rows = 4
lcd = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=rows)
lcd.clear()


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


while True: 
    lcd.printline(1, 'Ready for Scan'.center(cols))
    _, img = cap.read() # I believe this is interupt based, so it will record until it sees a QR code
    data, bbox, _ = detector.detectAndDecode(img) #Decode QR code
    if data: #After Scan...
        lcd.clear()
        lcd.printline(1, 'Scanning...'.center(cols))
        if has_internet(): #Check Internet...
            response = requests.post("http://localhost:8000/scan", json={"id": data})
            if not response.Success:
                lcd.printline(2, 'Error Scanning'.center(cols))
                lcd.printline(3, 'Restart'.center(cols))
                break
            lcd.printline(2, 'Scan Success'.center(cols))
            sleep(3)
            lcd.clear()
        else:
            lcd.clear()
            attempt_reconnection()
            lcd.clear()
    cv2.imshow("QRCODEscanner", img)    
    
cap.release()
cv2.destroyAllWindows()