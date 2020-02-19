import sensor, image, lcd, time

lcd.init()
sensor.reset()

sensor.set_contrast(1)
sensor.set_gainceiling(16)
sensor.set_framesize(sensor.QVGA)
sensor.set_pixformat(sensor.RGB565)
sensor.run(1)
sensor.skip_frames(30)

# Load Haar Cascade
# By default this will use all stages, lower satges is faster but less accurate.

face_cascade = image.HaarCascade("frontalface", stages=25)
eyes_cascade = image.HaarCascade("eye", stages=24)

while(True):
    img = sensor.snapshot()
    objects = img.find_features(face_cascade, threshold=0.4, scale_factor=1.5)
    for face in objects:
        img.draw_rectangle(face)
        eyes = img.find_features(eyes_cascade, threshold=0.35, scale_factor=1.2, roi=face)
        for e in eyes:
            img.draw_rectangle(e)
    lcd.display(img)
lcd.clear()
