import sensor, image
import lcd
import pyb
import time
from image import SEARCH_EX, SEARCH_DS
from pyb import UART
from pyb import LED

#用于存储图片模型
#多模板识别
templates = ["2.pgm", "3.pgm"]
#任务计时器
task_pid = 0;
#红色巡线阈值
red_line_threshold = (13, 100, -128, 127, -128, 127)
#用于保存识别数字的结果的变量
flag_number = 0





def task():
    global task_pid
    task_pid = task_pid + 1

#摄像头初始化
def sensor_init():
    sensor.reset()
    sensor.set_pixformat(sensor.GRAYSCALE)
    sensor.set_framesize(sensor.QQVGA)
    sensor.skip_frames(10)
    # Set sensor settings
    sensor.set_contrast(1)
    sensor.set_gainceiling(16)

#串口初始化
def uart_init():
    uart = UART(3, 115200, timeout_char=1000)                         # i使用给定波特率初始化
    uart.init(115200, bits=8, parity=None, stop=1, timeout_char=1000) # 使用给定参数初始化

def main():

    #对调用的一些外部变量进行一个声明
    global task_pid, template

    #摄像头初始化
    sensor_init()

    #串口初始化
    uart3 = UART(3, 115200, timeout_char=100)

    #定时器初始化
    tim = pyb.Timer(4,freq=1000)
    #定时器中断回调函数，执行 LED（3）蓝灯状态反转
    tim.callback(lambda t:task())



    #模板识别部分


    while(True):
        img = sensor.snapshot()

        r_2 = img.find_template(template_3, 0.70, step=4, search=SEARCH_EX) #, roi=(10, 0, 60, 60))

        if r_2:
           img.draw_rectangle(r_2)
           flag_number = 3

        else:
            flag_number = 0

        print(flag_number)

        if(task_pid >= 100):
            task_pid = 0
            #在此处填写100ms任务周期中应该完成的任务
            img.binary([red_line_threshold])
            line_red = img.get_regression([(255,255)], robust = True)

            #现在的话求的就是线的误差是正确的
            error_line = abs(line_red.rho())-img.width()/2

            #计算出要传给32的一些数据
            error_middle = int(error_line)


            if(error_line < 0):
                error_high = abs(error_middle) // 10;
            else:
                error_high = abs(error_middle) // 10
            error_low = abs(error_middle) - error_high * 10

            #现在将数据通过串口进行传输
            #发送起始信号
            #第一个字节的数据
            uart3.write('a')


            #先去传输数据的正负符号

            #第二个字节的数据
            if(error_line < 0):
                uart3.write(str(0))

            else:
                uart3.write(str(1))

            #第三四个字节的数据
            #现在来传输误差的高位
            uart3.write(str(error_high))
            #传输误差低位
            uart3.write(str(error_low))

            #最后传输的就是数字识别的结果
            uart3.write(str(flag_number))









main()
