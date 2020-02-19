import sensor, time, lcd #, image

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

THRESHOLD = [(175, 255)]
ROI = [0,0,sensor.width(),sensor.height()]

def getLine(img_, threshold_, pxlthreshold_, robust_, xstride_, ystride_, roi_):
    return img_.get_regression((threshold_), pixels_threshold = pxlthreshold_, robust = robust_, x_stride = xstride_, y_stride = ystride_, roi=roi_)

while True:
    img = sensor.snapshot()

    line = getLine(img.to_grayscale(copy=True, rgb_channel=(0/1/2)), THRESHOLD, 20, True, 4, 2, ROI)

    if line:
        img.draw_line(line.line(), color = (0, 255, 0), thickness = 2)

    lcd.display(img)
