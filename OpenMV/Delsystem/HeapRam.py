import sensor, time, lcd, gc
import KPU as kpu

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

sensor.set_gainceiling(16)
sensor.set_vflip(False)
sensor.set_hmirror(False)
sensor.set_auto_exposure(True)

sensor.run(1)

lcd.init()

lul = []

print(gc.mem_alloc())
print(gc.mem_free())
print(gc.mem_alloc()+gc.mem_free())


for x in range(20):
    print(x,"images:",gc.mem_alloc()-4096)
    lul.append(sensor.snapshot())

print(gc.mem_alloc())
print(gc.mem_free())
print(gc.mem_alloc()+gc.mem_free())

# for x in range(10):
while True:
    del lul
    lul = []
    print(x,gc.mem_alloc())
    # print(x,gc.mem_free())
    # print(x,gc.mem_alloc()+gc.mem_free())
