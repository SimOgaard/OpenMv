from fpioa_manager import fm
from machine import UART
from board import board_info
import time

fm.register(board_info.PIN15, fm.fpioa.UART1_TX, force=True)

uart_A = UART(UART.UART1, 9800,8,0,0, timeout=1000, read_buf_len=4096)

write_str = 'I think so'

while True:
    uart_A.write(write_str)
    time.sleep(1)
