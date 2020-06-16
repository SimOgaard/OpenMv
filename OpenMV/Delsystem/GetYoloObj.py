### When this is solved:
# multiple classes doesnt work but there is a "cleaner" way of utilising camera reset in classes which that takes time but is possible
# roi image copy of 320x240 converted to rgb yeilds low confidence; lower treshold work terrible but is possible
# change input nodes on yolo algorythm to 320x240 instead of 224x224

### Work on this:
# deficient maixpy ram; cant run kpu in serie with ex: regression

import sensor, time, lcd
import KPU as kpu

lcd.init()
# sensor.skip_frames(time = 500)

classes = ["Legogubbe"]
task = kpu.load(0x600000)
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
a = kpu.init_yolo2(task, 0.75, 0.3, 5, anchor)

YOLO_ROI = [48, 8, 224, 224]

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.color = (0, 255, 0)
        self.border = 2
        self.fill = False

        self.sensor = sensor

        self.sensor.reset()
        self.sensor.set_pixformat(sensor.RGB565)
        self.sensor.set_framesize(sensor.QVGA)

        self.sensor.set_contrast(-2)
        self.sensor.set_gainceiling(16)
        self.sensor.set_vflip(False)
        self.sensor.set_hmirror(False)

        self.sensor.set_windowing((width,height))

        self.sensor.run(1)
    
    def takepic(self):
        self.img = sensor.snapshot()
    
    def yolo(self):
        self.yoloObj = kpu.run_yolo2(task, self.img)
        if self.yoloObj:
            for object in self.yoloObj:
                self.img.draw_rectangle(object.rect(), self.color, self.border, self.fill)        # setCamera((320,240))
        # yoloObj = kpu.run_yolo2(task, img_.copy(roi=YOLO_ROI, copy_to_fb=False))
        # yoloObj = kpu.run_yolo2(task, img_.copy(roi=YOLO_ROI, copy_to_fb=False))#.to_rgb565(copy=False))
        # if yoloObj:
        #     print(yoloObj)
        # return yoloObj if yoloObj else []

    # def outlineObjects(img_, objects_, color_, border_, fill_):
    #     for object in objects_:
    #         img_.draw_rectangle(object.rect(), color_, border_, fill_)

    def displaypic(self):
        lcd.display(self.img)

    

# def setCamera(window_):
#     sensor.reset()
#     sensor.set_pixformat(sensor.RGB565)
#     sensor.set_framesize(sensor.QVGA)

#     sensor.set_contrast(-2)
#     sensor.set_gainceiling(16)
#     sensor.set_vflip(False)
#     sensor.set_hmirror(False)

#     sensor.set_windowing(window_)

#     sensor.run(1)

# def getYoloObjects(img_):
#     # setCamera((224,224))
#     # yoloObj = kpu.run_yolo2(task, img_)
#     # setCamera((320,240))
#     # yoloObj = kpu.run_yolo2(task, img_.copy(roi=YOLO_ROI, copy_to_fb=False))
#     yoloObj = kpu.run_yolo2(task, img_.copy(roi=YOLO_ROI, copy_to_fb=False))#.to_rgb565(copy=False))
#     if yoloObj:
#         print(yoloObj)
#     return yoloObj if yoloObj else []

# def outlineObjects(img_, objects_, color_, border_, fill_):
#     for object in objects_:
#         img_.draw_rectangle(object.rect(), color_, border_, fill_)

# # setCamera((224,224))
# setCamera((320,240))

Camera1 = Camera(224,224)
# Camera2 = Camera(320,240)
while True:
    Camera1.takepic()
    Camera1.yolo()

# print("sensor 1 done")

# for _ in range(100):
#     Camera2.takepic()

# while(True):
    # img = sensor.snapshot().copy(roi=YOLO_ROI, copy_to_fb=True).to_rgb565(copy=True)#.scale(x_scale = 0.5, y_scale=0.5, copy_to_fb=False)

    # # legoGubbar = getYoloObjects(img)

    # legoGubbar = kpu.run_yolo2(task, img)

    # if not legoGubbar: legoGubbar=[]

    # outlineObjects(img, legoGubbar, (0, 255, 0), 2, False)

    # lcd.display(img)
