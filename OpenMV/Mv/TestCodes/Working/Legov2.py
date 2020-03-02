import sensor,image,lcd
import KPU as kpu

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

sensor.set_gainceiling(16)
sensor.set_vflip(False)
sensor.set_hmirror(False)

sensor.run(1)

YOLO_ROI = [48, 8, 224, 224]

classes = ["Legogubbe"]
task = kpu.load(0x600000)
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
a = kpu.init_yolo2(task, 0.3, 0.3, 5, anchor)

def getYoloObjects(img_):
    # img = img_.copy(roi=YOLO_ROI)
    img = img_.copy(roi=YOLO_ROI, copy_to_fb=False).to_rgb565(copy=False)
    # img = img_.resize(224,224)

    yoloObj = kpu.run_yolo2(task, img)

    # yoloObj = kpu.run_yolo2(task, img_.copy(roi=YOLO_ROI))

    # yoloObj = kpu.run_yolo2(task, img_.copy(roi=YOLO_ROI, copy_to_fb=False).to_rgb565(copy=False))

    # yoloObj = kpu.run_yolo2(task, img_.resize(224,224))

    return yoloObj if yoloObj else []

def getClosestToCenter(object_, xmiddle_, ymiddle_, xoffset_, yoffset_):
    if object_:
        l = [(abs(obj.x()+int(obj.w()/2)+xoffset_-xmiddle_) + abs(obj.y()+int(obj.h()/2)+yoffset_-ymiddle_)) for obj in object_]
        object = object_[l.index(min(l))]
        return (int(object.x()+object.w()/2), int(object.y()+object.h()/2))

def outlineObjects(img_, objects_, color_, border_):
    for object in objects_:
        img_.draw_rectangle(object.rect(), color_, border_)

def markPoint(img_, xy_, radius_, color_, thickness_, fill_):
    if xy_:
        img_.draw_circle(xy_[0], xy_[1], radius_, color_, thickness_, fill_)

while(True):
    img = sensor.snapshot()
    legoGubbar = getYoloObjects(img)
    closestLegoGubbe = getClosestToCenter(legoGubbar, img.width()/2, img.height()/2, 48, 8)

    print(legoGubbar)
    print(closestLegoGubbe)

    outlineObjects(img, legoGubbar, (255, 0, 0), 2)
    markPoint(img, closestLegoGubbe, 3, (255, 0, 0), 1, True)

    lcd.display(img)