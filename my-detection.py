import jetson.inference
import jetson.utils

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson.utils.videoSource("/dev/video0")      # '/dev/video0' for V4L2
display = jetson.utils.videoOutput("rtp://192.168.86.42:1234","--headless") # 'my_video.mp4' for file

while True:
    img = camera.Capture()
    detections = net.Detect(img)
    objects = ["nothing"]
    for detection in detections:
        objects.append(net.GetClassDesc(detection.ClassID))
    if "person" in objects:
        print("Person detected!")
    print(objects)
    display.Render(img)
    display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
    if not camera.IsStreaming() or not display.IsStreaming():
        break
