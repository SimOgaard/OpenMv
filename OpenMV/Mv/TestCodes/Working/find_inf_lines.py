#find infinite lines
import sensor, image, lcd, time
enable_lens_corr = True
lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)
sensor.skip_frames(time = 2000)

min_degree = 0
max_degree = 179

while(True):
    img = sensor.snapshot()
    for l in img.find_lines(threshold = 2000, theta_margin = 25, rho_margin = 25):
        if (min_degree <= l.theta()) and (l.theta() <= max_degree):
            img.draw_line(l.line(), color = (255, 0, 0))
    lcd.display(img)
lcd.clear()
