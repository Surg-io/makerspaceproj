import datetime
from time import sleep
'''
import cv2
from pyzbar import pyzbar

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Starting QR code detection...")

intframe = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    intframe += 1

    if(intframe % 5 != 0): #Decode every 5th frame. Camera runs ~25 frames a sec, so about 5 times a sec
        continue
        
    decoded_objects = pyzbar.decode(frame)


    
    #for obj in decoded_objects:
    #   print(f"Detected QR code: {obj.data.decode('utf-8')}")
    
    print(decoded_objects) #This should print one thing, one string...
    
    

    # Break after first detection for testing
    if decoded_objects:
        break

cap.release()
print("Done")
'''

q = []

for i in range(3):
    q.append(str("100" + i),datetime.datetime.now() )
    sleep(3)
