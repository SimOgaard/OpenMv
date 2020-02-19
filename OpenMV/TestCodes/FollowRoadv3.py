import sensor, image, time, lcd, math
import numpy as np

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

sensor.set_contrast(-2)
sensor.set_gainceiling(16)
sensor.set_vflip(False)
sensor.set_hmirror(False)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
IMG_HEIGHT = 224
IMG_WIDTH = 224
sensor.set_windowing((IMG_HEIGHT, IMG_WIDTH))

sensor.run(1)
sensor.skip_frames(time = 500)
clock= time.clock()

COLOR_THRESHOLD = [(96, 100, -128, 127, -128, 127)]
GRAYSCALE_THRESHOLDS = [(240, 255)]
AREA_THRESHOLD = 20
PIXELS_THRESHOLD = 20
LANE_ROI = (0, IMG_HEIGHT/2, IMG_WIDTH, IMG_HEIGHT/2)
MAG_THRESHOLD = 5
printString = " "
steer = 90

REGRESSION_COLOR = False
REGRESSION_GRAY = False
REGRESSION_SEGMENTED = True
# Setting upp thresholds function

# find_line_segments instead of get_line_regression?

while True:
    clock.tick()
    fps = clock.fps()

    img = sensor.snapshot().histeq()

    if REGRESSION_COLOR:
        line = img.get_regression((COLOR_THRESHOLD), pixels_threshold = PIXELS_THRESHOLD, area_threshold = AREA_THRESHOLD, robust = True, roi = LANE_ROI)
    elif REGRESSION_GRAY:
        line = image.rgb_to_grayscale(img).get_regression((GRAYSCALE_THRESHOLDS), pixels_threshold = PIXELS_THRESHOLD, area_threshold = AREA_THRESHOLD, robust = True, roi = LANE_ROI)
    elif REGRESSION_SEGMENTED:
        Lines = []
        for l in img.find_line_segments(merge_distance=0 max_theta_difference=15):
            img.draw_line(l.line(), color=(255, 0, 0), thickness=2)
            parameters = np.polyfit((l.line(x1),l.line(x2)), (l.line(y1),l.line(y2)), 1)
            slope = parameters[0]
            intercept = parameters[1]
            Lines.append((slope, intercept))
        LinesAverage = np.average(Lines, axis=0)

        # slope, intercept = l.line()
        # # y1 = IMG_HEIGHT
        # # y2 = int(IMG_HEIGHT*(3.25/5))
        # x1 = int((IMG_HEIGHT-intercept)/slope)
        # x2 = int((0-intercept)/slope)

    if line and line.magnitude() >= MAG_THRESHOLD:
        steer = (line.theta() - 90) + (line.x2() - IMG_WIDTH/2) + 90 # (line.theta() - 90) + (line.x2() - IMG_WIDTH/2) + 90 => line.theta() + line.x2() - 112

        img.draw_line(line.line(), color=(0, 255, 0), thickness=2)
        printString = "fps:%d, S:%d t:%d, x:%d" % (fps, steer, (line.theta() - 90), (line.x2() - IMG_WIDTH/2))
    else:
        printString = "fps:%d, S:%d" % (fps, steer)

    img.draw_string(2, 2, printString, color=(0, 255, 0), scale=1)
    print(printString)

    lcd.display(img)
