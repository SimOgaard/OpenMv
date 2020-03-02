#find non-infinite lines
import sensor, image, lcd, time
lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)
sensor.skip_frames(30)

while(True):
    img = sensor.snapshot()
    for l in img.find_line_segments(merge_distance = 10, max_theta_diff = 25, roi=(80,60,160,120)):
        img.draw_line(l.line(), color = (255, 0, 0))
    lcd.display(img)
lcd.clear()
