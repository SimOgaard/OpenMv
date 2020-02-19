import sensor, time, lcd
import KPU as kpu

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

sensor.set_contrast(-2)
sensor.set_gainceiling(16)
sensor.set_vflip(False)
sensor.set_hmirror(False)

sensor.run(1)
sensor.skip_frames(time = 500)

classes = ["Legogubbe"]
task = kpu.load(0x600000)
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
a = kpu.init_yolo2(task, 0.3, 0.3, 5, anchor)

YOLO_ROI = [48, 8, 224, 224]

def getYoloObjects(img_):
    yoloObj = kpu.run_yolo2(task, img_.copy(roi=YOLO_ROI, copy_to_fb=False).to_rgb565(copy=False))
    return yoloObj if yoloObj else []

def outlineObjects(img_, objects_, color_, border_, fill_):
    for object in objects_:
        img_.draw_rectangle(object.rect(), color_, border_, fill_)

while(True):
    img = sensor.snapshot()

    legoGubbar = getYoloObjects(img)

    outlineObjects(img, legoGubbar, (0, 255, 0), 2, False)

    lcd.display(img)
