import jetson.inference
import jetson.utils

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson.utils.videoSource("/dev/video0")      # '/dev/video0' for V4L2
display = jetson.utils.videoOutput("rtp://192.168.86.42:1234","--headless") # 'my_video.mp4' for file

de_history = ["nothing"]

# List possible detection areas:
kitchen = ["refrigerator", "sink", "bottle", "microwave"]
bath = ["toilet", "sink", "dispenser", "shower", "shelve"]
livingroom = ["tv", "couch", "lamp", "desk"]


print("Welcome to the inventory checker! What do you like to check?")
print("Currently, we support the following: Kitchen (type 'k'), Bath (type 'b') or Livingroom (type 'l')")
x = input()
if x == "k":
    inventory = kitchen
if x == "b":
    inventory = bath
if x == "l":
    inventory = livingroom

while True:
    if len(de_history) > 10000:
        de_history = []
        print("Cleared history to avoid buffer overflow!")
    img = camera.Capture()
    detections = net.Detect(img)
    new_object_detected = False
    new_objects = []
    for detection in detections:
        if detection not in de_history:
            de_history.append(net.GetClassDesc(detection.ClassID))
            new_objects.append(net.GetClassDesc(detection.ClassID))
            new_object_detected = True
    if [item for item in inventory if item not in de_history] == [] and new_object_detected:
        print("Successfully checked inventory of your room, congrats!")
        print("Restart the program to check the next room")
        break
    if new_object_detected:
        print("Congrats, you identified the following object: " + str(new_objects))
        print("The following items are remaining: " + str([item for item in inventory if item not in de_history]))
    
    display.Render(img)
    display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
    if not camera.IsStreaming() or not display.IsStreaming():
        break
