import sensor, lcd, math

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

sensor.set_gainceiling(16)
sensor.set_vflip(False)
sensor.set_hmirror(False)
sensor.set_auto_exposure(True)

sensor.run(1)



RED_THRESHOLDS = [(0, 100, 127, 20, 127, -128)]
GREENE_THRESHOLDS = [(0, 100, -20, -128, -128, 127)]
BLUE_THRESHOLDS = [(0, 100, 127, -128, -10, -128)]
ROAD_JOINTS_THRESHOLDS = [(0, 100, 127, -128, -10, -128)]
GRAY_THRESHOLDS = [(200, 255)]

ALPHA_DARKEN = 57
ROADTYPE_THRESHOLDS = 0.5
THETA_TILT = 11
PEDESTRIAN_CROSSING_PIXELS = 2500
skipAmount = 4

LEFT_LANE_ROI = [0, 0, int(sensor.width()/3), sensor.height()]
RIGHT_LANE_ROI = [int(sensor.width()/1.5), 0, sensor.width(), sensor.height()]
MIDDLE_LANE_ROI = [0, int(sensor.height()/1.5), sensor.width(), sensor.height()]

LEFT_CROSS_ROI = [0, 0, int(sensor.width()/3), sensor.height()]
RIGHT_CROSS_ROI = [int(sensor.width()/1.5), 0, sensor.width(), sensor.height()]
MIDDLE_CROSS_ROI = [0, int(sensor.height()/1.5), sensor.width(), sensor.height()]




def getColoredObjects(img_, threshold_, pixelthreshold_, xstride_, ystride_, margin_, roi_):
    return img_.find_blobs(threshold_, x_stride = xstride_, y_stride = ystride_, pixels_threshold = pixelthreshold_, merge = True, margin = margin_, roi = roi_)

def getYoloObjects(img_):
    yoloObj = kpu.run_yolo2(task, img_.copy(roi=YOLO_ROI, copy_to_fb=False).to_rgb565(copy=False))
    return True if yoloObj else False

def laneAppropriateImg(img_, roi_):
    img_copy = img_.to_grayscale(copy = True, rgb_channel = (0/1/2))

    lights = getColoredObjects(img_copy, GRAY_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
    if lights:
        l = [obj.pixels() for obj in lights]
        light = lights[l.index(max(l))]
        img_copy_roi = img_copy.copy(roi=light.rect(), copy_to_fb=False).clear()
        img_copy = img_copy.draw_image(img_copy_roi, light.x(), light.y(), alpha=ALPHA_DARKEN)

    for roi in roi_:
        outlineObjects(img_copy, roi, (0, 0, 0), 1, True)
    return img_copy

def getPedestrianCrossing(img_, threshold_, xstride_, ystride_, roi_, margin_):
    pedestrianCrossings = getColoredObjects(img_, threshold_, 0, xstride_, ystride_, margin_, roi_)
    crossingArea = sum([obj.pixels() for obj in pedestrianCrossings])
    return True if crossingArea >= PEDESTRIAN_CROSSING_PIXELS else False

def getLaneLine(img_, threshold_, pixelthreshold_, robust_, xstride_, ystride_, roi_):
    laneLine = img_.get_regression((threshold_), pixels_threshold = pixelthreshold_, robust = robust_, x_stride = xstride_, y_stride = ystride_, roi = roi_)
    return laneLine

def getClosestToCenter(object_):
    if object_:
        l = [math.sqrt((obj.cx()-sensor.width()/2)**2 + (obj.cy()-sensor.height()/2)**2) for obj in object_]
        object = object_[l.index(min(l))]
        return (object.cx(), object.cy())

def getSteerValues(lines_, bothV, bothX):
    new = False
    if lines_[0] and lines_[1]:
        new = True
        leftV = lines_[0].theta()+90 if lines_[0].theta() < 90 else abs(lines_[0].theta()-90)
        rightV = lines_[1].theta()+90 if lines_[1].theta() < 90 else abs(lines_[1].theta()-90)
        bothV = (leftV+rightV) / 2
        bothX = (lines_[0].x2() + lines_[1].x2())/2 - sensor.width()/2
    return bothV, bothX, new

def getRoadType(img_, roadType_, bothV_, leftCrossing_, rightCrossing_, middleCrossing_, new_):
    roadType_[3] = 1
    if not leftCrossing_ and not rightCrossing_ and middleCrossing_:
        roadType_[0] = 1
        roadType_[1] = 1
    else:
        if leftCrossing_ or bothV_ <= 90-THETA_TILT:
            roadType_[0] = 1
        if rightCrossing_ or bothV_ >= 90+THETA_TILT:
            roadType_[1] = 1
        if bothV_ > 90-THETA_TILT and bothV_ < 90+THETA_TILT:
            roadType_[2] = 1
    matrix_ = [[0,roadType_[2],0],[roadType_[0],1,roadType_[1]],[0,roadType_[3],0]]
    return roadType_, matrix_

def outlineObjects(img_, objects_, color_, border_, fill_):
    for object in objects_:
        img_.draw_rectangle(object.rect(), color_, border_, fill_)

def markPoint(img_, xy_, radius_, color_, thickness_, fill_):
    if xy_:
        img_.draw_circle(xy_[0], xy_[1], radius_, color_, thickness_, fill_)

def drawLine(img_, line_, color_, thickness_):
    for lines in line_:
        if lines:
            img_.draw_line(lines.line(), color_, thickness_)

def drawMap(img_, matrix_, cords_, scale_):
    x, y = 0, 0
    for amount1, row in enumerate(matrix_):
        for amount2, col in enumerate(row):
            img_.draw_rectangle([x,y,scale_,scale_], (0,0,0) if col==0 else (255,255,255) if col==1 else (255,0,0), 1, True)
            x += scale_
        x = 0
        y += scale_

ALL_ROI = [0, 0, sensor.width(), sensor.height()]
YOLO_ROI = [48, 8, 224, 224]
coordinate = [0, 0]
roadType = [0, 0, 0, 0]
bothV = 90
bothX = sensor.width()/2
matrix = [[0,0,0],[0,0,0],[0,0,0]]
skipped = 0

def binaryThresholdImage(img_, threshold_):
    imgCopy = img_.copy(copy_to_fb=False)
    imgCopy.binary(threshold_)
    return imgCopy


def lineImage(img_, imgCopy):
    if rightLaneLine and leftLaneLine:
        imgCopy = img_.copy(copy_to_fb=False)
        imgCopy.draw_rectangle(LEFT_LANE_ROI, (0, 255, 255), 2, False)
        imgCopy.draw_rectangle(RIGHT_LANE_ROI, (0, 255, 255), 2, False)

        leftV = leftLaneLine.theta()+90 if leftLaneLine.theta() < 90 else abs(leftLaneLine.theta()-90)
        rightV = rightLaneLine.theta()+90 if rightLaneLine.theta() < 90 else abs(rightLaneLine.theta()-90)

        if leftV > 90-THETA_TILT and leftV < 90+THETA_TILT:
            color = (0,255,0)
        else:
            color = (255,0,0)

        imgCopy.draw_line(leftLaneLine.line(), color, 1)

        if rightV > 90-THETA_TILT and rightV < 90+THETA_TILT:
            color = (0,255,0)
        else:
            color = (255,0,0)

        imgCopy.draw_line(rightLaneLine.line(), color, 1)

    return imgCopy


def crosswalkImage(img_):
    imgCopy = img_.copy(copy_to_fb=False)

    imgCopy.draw_rectangle(LEFT_CROSS_ROI, (0, 255, 255), 2, False)
    imgCopy.draw_rectangle(RIGHT_CROSS_ROI, (0, 255, 255), 2, False)
    imgCopy.draw_rectangle(MIDDLE_CROSS_ROI, (0, 255, 255), 2, False)

    imgCopy.draw_string(int((LEFT_CROSS_ROI[0]+LEFT_CROSS_ROI[2])/2),int((LEFT_CROSS_ROI[1]+LEFT_CROSS_ROI[3])/2), str(leftCrossing), color =(255,0,0),mono_space=False, scale = 2)
    imgCopy.draw_string(int((RIGHT_CROSS_ROI[0]+RIGHT_CROSS_ROI[2])/2),int((RIGHT_CROSS_ROI[1]+RIGHT_CROSS_ROI[3])/2), str(rightCrossing), color =(255,0,0),mono_space=False, scale=2)
    imgCopy.draw_string(int((MIDDLE_CROSS_ROI[0]+MIDDLE_CROSS_ROI[2])/2),int((MIDDLE_CROSS_ROI[1]+MIDDLE_CROSS_ROI[3])/2), str(middleCrossing), color =(255,0,0),mono_space=False, scale=2)

    return imgCopy

imgur = sensor.snapshot()

while True:
    img = sensor.snapshot()

    uraniumRods = getColoredObjects(img, GREENE_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
    redRods = getColoredObjects(img, RED_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
    blueRods = getColoredObjects(img, BLUE_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)

    allObjects = uraniumRods + redRods + blueRods
    closestObject = getClosestToCenter(allObjects)

    laneAppropiate = laneAppropriateImg(img, [allObjects])
    # leftLaneLine = getLaneLine(laneAppropiate, GRAY_THRESHOLDS, 20, True, 4, 2, LEFT_LANE_ROI)
    # rightLaneLine = getLaneLine(laneAppropiate, GRAY_THRESHOLDS, 20, True, 4, 2, RIGHT_LANE_ROI)

    # leftCrossing = getPedestrianCrossing(laneAppropiate, GRAY_THRESHOLDS, 4, 2, LEFT_LANE_ROI, 50)
    # rightCrossing = getPedestrianCrossing(laneAppropiate, GRAY_THRESHOLDS, 4, 2, RIGHT_LANE_ROI, 50)
    # middleCrossing = getPedestrianCrossing(laneAppropiate, GRAY_THRESHOLDS, 4, 2, MIDDLE_LANE_ROI, 50)

    # bothV, bothX, new = getSteerValues([leftLaneLine, rightLaneLine], bothV, bothX)

    # roadType, matrix = getRoadType(img, [0,0,0,0], bothV, leftCrossing, rightCrossing, middleCrossing, new)




    imgur = binaryThresholdImage(laneAppropiate, GRAY_THRESHOLDS)
    # imgur = binaryThresholdImage(img, GREENE_THRESHOLDS)
    # imgur = binaryThresholdImage(img, RED_THRESHOLDS)
    # imgur = binaryThresholdImage(img, BLUE_THRESHOLDS)
    # imgur = binaryThresholdImage(img, ROAD_JOINTS_THRESHOLDS)
    # imgur = crosswalkImage(img)
    # imgur = lineImage(img, imgur)



    # outlineObjects(img, uraniumRods, (0, 255, 0), 2, False)
    # outlineObjects(img, redRods, (255, 0, 0), 2, False)
    # outlineObjects(img, blueRods, (0, 0, 255), 2, False)

    # markPoint(img, closestObject, 3, (255, 255, 0), 1, True)
    # drawLine(img, [leftLaneLine, rightLaneLine], (0, 0, 0), 2)
    # drawMap(img, matrix, (-1, -1), 5)

    lcd.display(imgur)


#make lines red when rotated enought

