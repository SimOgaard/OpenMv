import sensor, image, time, lcd
import KPU as kpu

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_vflip(False)
sensor.set_hmirror(False)

sensor.set_windowing((224, 224))
classes = ["Legogubbe"]
task = kpu.load(0x600000)
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
a = kpu.init_yolo2(task, 0.3, 0.3, 5, anchor)

sensor.run(1)
sensor.skip_frames(30)
sensor.set_auto_gain(True)
sensor.set_auto_whitebal(False)
sensor.set_contrast(-2)
sensor.set_gainceiling(16)

clock = time.clock()

# COLOR_THRESHOLDS = [(90, 100, -128, 127, -128, 127)]               # contrast 2
# COLOR_HIGH_LIGHT_THRESHOLDS = [(90, 100, -128, 127, -128, 127)]

COLOR_THRESHOLDS = [(80, 100, -128, 127, -128, 127)]                # contrast -2
COLOR_HIGH_LIGHT_THRESHOLDS = [(80, 100, -128, 127, -128, 127)]     # sänk 80 plz plox

AREA_THRESHOLD = 40
PIXELS_THRESHOLD = 40

BINARY_VIEW = False
DO_NOTHING = False
# REMOVE_LENS_FLARE = True

# hitta cirklar och gör de röda, ta bort de från binary view

while True:
    clock.tick()
    img = sensor.snapshot()

    if BINARY_VIEW:
        img = img.binary(COLOR_THRESHOLDS)
        # if REMOVE_LENS_FLARE:
        #     for c in img.find_circles(y_stride = 5, x_stride = 5, x_margin = 25, y_margin = 25, r_margin = 25, r_min = 15, r_max = 200, r_step = 2):
        #         img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))

    if DO_NOTHING:
        lcd.display(img)
        continue

    if BINARY_VIEW:
        line = img.get_regression(([(50, 100, -128, 127, -128, 127)]), robust = False, pixels_threshold = PIXELS_THRESHOLD, area_threshold = AREA_THRESHOLD)
    # elif REMOVE_LENS_FLARE:
        # line = img.get_regression((COLOR_THRESHOLDS), robust = False, pixels_threshold = PIXELS_THRESHOLD, area_threshold = AREA_THRESHOLD) # 123
    else:
        line = img.get_regression((COLOR_THRESHOLDS), robust = False, pixels_threshold = PIXELS_THRESHOLD, area_threshold = AREA_THRESHOLD)
    if line:
        string = ("FPS %f, mag = %s" % (clock.fps(), str(line.magnitude())))
        print(string)
        img.draw_string(2, 2, string, color=(0, 255, 0), scale=1.5)
        img.draw_line(line.line(), color=(0, 255, 0), thickness=2)
    else:
        string = ("FPS %f, mag = N/A" % (clock.fps()))
        print(string)
        img.draw_string(2, 2, (string), color=(255, 0, 0), scale=1.5)

    code = kpu.run_yolo2(task, img)
    if code:
        for i in code:
            img.draw_rectangle(i.rect(), color = (255, 255, 0))
            img.draw_string(i.x(), i.y(), classes[i.classid()], color=(255, 0, 0), scale=3)
            print("NAME= " + classes[i.classid()])

    lcd.display(img)
lcd.clear()
