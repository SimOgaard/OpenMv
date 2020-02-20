### TODO:
    # getSteerValues()
    # transferValues()

    # laneAppropiateImage               Copy binary version of image, invertera (not), använd som mask för mörkning. Tanken är att bara det ljusa ska bli mörkare. Fler itterationer? så att det ljusaste blir mörare än det lite ljusa
    #                                   Testa även multipy add subtract divide images, kolla om de gör som ovan om inte bättre
    # Snabbare funktioner               Tex image.clear() "verry fast" till skillnad från drawsquare. Även hur du använder numpy "vertecees" kunde adderas ihop tusen ggr snabbare än for loopar
    # Värden på:
    #           tresholds,
    #           osv
    # Yolo                              Få den att funka med copy och lite ram
    # Yolo dataset                      Fixa Yolo dataset
    # light sensor to find threshold    Kanske lyckas utan light sensor utan kollar på bilden överlag hur ljus är den?
    # Publice roadtype when roadtypechanging is false only once

### Biblotek ###
import sensor, lcd, math

### Sensor ###
lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

sensor.set_gainceiling(16)
sensor.set_vflip(False)
sensor.set_hmirror(False)
sensor.set_auto_exposure(True)

sensor.run(1)

### Konstanter ###
ALL_ROI = [0, 0, sensor.width(), sensor.height()]
YOLO_ROI = [48, 8, 224, 224]
LEFT_LANE_ROI = [0, 0, int(sensor.width()/3), sensor.height()]
RIGHT_LANE_ROI = [int(sensor.width()/1.5), 0, sensor.width(), sensor.height()]
coordinate = [0, 0]
roadType = [0, 0, 0, 0]
bothV = 90
bothX = sensor.width()/2
matrix = [[0,0,0],[0,0,0],[0,0,0]]
rotation = 0
oldRoadTypeChanging = False

### Variabler ###
RED_THRESHOLDS = [(0, 100, 127, 47, 127, -128)]
GREENE_THRESHOLDS = [(0, 100, -20, -128, -128, 127)]
BLUE_THRESHOLDS = [(0, 100, 127, -128, -10, -128)]
ROAD_JOINTS_THRESHOLDS = [(0, 100, 127, -128, -10, -128)]
GRAY_THRESHOLDS = [(165, 255)]
ALPHA_DARKEN = 90
ROADTYPE_THRESHOLDS = 0.5

THETA_TILT = 11
PEDESTRIAN_CROSSING_PIXELS = 2500

### Yolo2 ###
# import KPU as kpu
# classes = ["Legogubbe"]
# task = kpu.load(0x600000)
# a = kpu.init_yolo2(task, 0.3, 0.3, 5, (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828))

### Funktioner ###

### Beräkningar ###
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

def getLaneLine(img_, threshold_, pixelthreshold_, robust_, xstride_, ystride_, roi_, margin_):
    pedestrianCrossings = getColoredObjects(img_, threshold_, 0, xstride_, ystride_, margin_, roi_)
    crossingArea = sum([obj.pixels() for obj in pedestrianCrossings])
    laneLine = img_.get_regression((threshold_), pixels_threshold = pixelthreshold_, robust = robust_, x_stride = xstride_, y_stride = ystride_, roi = roi_)
    return laneLine, True if crossingArea >= PEDESTRIAN_CROSSING_PIXELS else False

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

def getRoadTypeWhen(img_, new_):
    roadJoints = getColoredObjects(img_, ROAD_JOINTS_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
    return True if len(roadJoints) >= 4 and new_ else False

def getRoadType(roadType_, bothV_, leftCrossing_, rightCrossing_):
    roadType_[3] = roadType_[3]+1

    if leftCrossing_ or bothV_ <= 90-THETA_TILT:
        roadType_[0] = roadType_[0]+1
    if rightCrossing_ or bothV_ >= 90+THETA_TILT:
        roadType_[1] = roadType_[1]+1
    if bothV_ > 90-THETA_TILT and bothV_ < 90+THETA_TILT:
        roadType_[2] = roadType_[2]+1

    return roadType_

# def 

def transferValues(*values_):
    print(values_)

# def useClaw():

# def drive():

# def Turtle():
#     if legoGubbar:


### Visuellt ###
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

while True:
    img = sensor.snapshot()

    # Objekt
    uraniumRods = getColoredObjects(img, GREENE_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
    redRods = getColoredObjects(img, RED_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
    blueRods = getColoredObjects(img, BLUE_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)

    allObjects = uraniumRods + redRods + blueRods
    closestObject = getClosestToCenter(allObjects)

    # # Yolo
    # legoGubbar = getYoloObjects(img)

    # Väg
    laneAppropiate = laneAppropriateImg(img, [allObjects])
    leftLaneLine, leftCrossing = getLaneLine(laneAppropiate, GRAY_THRESHOLDS, 20, True, 4, 2, LEFT_LANE_ROI, 50)
    rightLaneLine, rightCrossing = getLaneLine(laneAppropiate, GRAY_THRESHOLDS, 20, True, 4, 2, RIGHT_LANE_ROI, 50)

    bothV, bothX, new = getSteerValues([leftLaneLine, rightLaneLine], bothV, bothX)

    # Create two classes one that is: Turtle:
        # Om en legogubbe syns stanna och blinka
        # Om fyra vägMarkers syns stanna bilen och regristera vägen sedan skicka
        # Om det närmsta objektet är mellan y1 och y2 stanna bilen och plocka upp biten
        # Kör bilen mellan linjerna

    # Rabbit:
        # Om en legogubbe syns blinka
        # Om fyra vägMarkers syns skicka när de inte längre syns med ett interval av säkerhet
        # Om det närmsta objektet är mellan y1 och y2 stanna bilen och plocka upp biten
        # Kör bilen mellan linjerna
        # Vid preplanned route checka av om hur du kör stämmer med väg markörernas roadtype
        # Vid nytt territorium 

    # Ta fram väg typen och skicka värden. När är det tilfälligt att köra getRoadType?
    # När fyra blåa objekt syns, när linjerna är nya värden
    # När är det tilfälligt att hugga vägen i sten?
    # När De fyra objekten inte längre syns i x antal frames
    # Då ska den köra transferValues 1 gång
    


    roadTypeChanging = getRoadTypeWhen(img, new)
    if roadTypeChanging:
        oldRoadTypeChanging = roadTypeChanging
        roadType = getRoadType(roadType, bothV, leftCrossing, rightCrossing)
    if roadTypeChanging != oldRoadTypeChanging: # if roadtype[3] >= ItterationsNeccesary, så att om den 1 frame ser 3 objekt och nästa ser 4 räkna som 1 frame
        oldRoadTypeChanging = roadTypeChanging
        transferValues(roadType, coordinate, bothV, bothX)
        roadType = [True if x/roadType[3] >= ROADTYPE_THRESHOLDS else False for x in roadType]
        matrix = [[0,roadType[2],0],[roadType[0],1,roadType[1]],[0,roadType[3],0]]
        transferValues(roadType, coordinate, bothV, bothX)
        # Publice roadtype when roadtypechanging is false only once
        roadType = [0, 0, 0, 0]


    # Visuellt
    outlineObjects(img, uraniumRods, (0, 255, 0), 2, False)
    outlineObjects(img, redRods, (255, 0, 0), 2, False)
    outlineObjects(img, blueRods, (0, 0, 255), 2, False)

    markPoint(img, closestObject, 3, (255, 255, 0), 1, True)

    drawLine(img, [leftLaneLine, rightLaneLine], (0, 0, 0), 2)

    drawMap(img, matrix, (-1, -1), 5)

    lcd.display(img)