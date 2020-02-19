import sensor, time, lcd, math

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

sensor.set_gainceiling(16)
sensor.set_vflip(False)
sensor.set_hmirror(False)

sensor.run(1)

ALL_ROI = [0, 0, sensor.width(), sensor.height()]

RED_THRESHOLDS = [(0, 100, 127, 47, 127, -128)]
GREENE_THRESHOLDS = [(0, 100, -20, -128, -128, 127)]
BLUE_THRESHOLDS = [(0, 100, 127, -128, -10, -128)]

def getColoredObjects(img_, threshold_, pixelthreshold_, xstride_, ystride_, margin_, roi_):
    return img_.find_blobs(threshold_, x_stride = xstride_, y_stride = ystride_, pixels_threshold = pixelthreshold_, merge = True, margin = margin_, roi = roi_)

def getClosestToCenter(object_, xmiddle_, ymiddle_, xoffset_, yoffset_):
    if object_:
        l = [math.sqrt((obj.cx()-xmiddle_)**2 + (obj.cy()-ymiddle_)**2) for obj in object_]
        object = object_[l.index(min(l))]
        return (object.cx(), object.cy())

def outlineObjects(img_, objects_, color_, border_, fill_):
    for object in objects_:
        img_.draw_rectangle(object[0], object[1], object[2], object[3], color_, border_, fill_)

def markPoint(img_, xy_, radius_, color_, thickness_, fill_):
    if xy_:
        img_.draw_circle(xy_[0], xy_[1], radius_, color_, thickness_, fill_)

while True:
    img = sensor.snapshot()

    uraniumRods = getColoredObjects(img, GREENE_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
    redRods = getColoredObjects(img, RED_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
    blueRods = getColoredObjects(img, BLUE_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
    
    allObjects = uraniumRods + redRods + blueRods
    closestObject = getClosestToCenter(allObjects, img.width()/2, img.height()/2, 0, 0)

    outlineObjects(img, uraniumRods, (0, 255, 0), 2, False)
    outlineObjects(img, redRods, (255, 0, 0), 2, False)
    outlineObjects(img, blueRods, (0, 0, 255), 2, False)

    markPoint(img, closestObject, 3, (255, 255, 0), 1, True)

    lcd.display(img)
