from sc16is752 import RS485Port, SC16IS752
import time


# RP2350-PiZero -> Waveshare 2-CH RS485 HAT mapping from the reference repo:
# GP19 = MISO, GP20 = MOSI, GP21 = SCK, GP18 = CS, GP24 = IRQ
# GP27 = TXDEN1, GP22 = TXDEN2
bridge = SC16IS752(
    spi_id=0,
    sck_pin=21,
    mosi_pin=20,
    miso_pin=19,
    cs_pin=18,
    irq_pin=24,
    baudrate=1_000_000,
)

ch1 = RS485Port(bridge, SC16IS752.CHANNEL_A, txden_pin=27, baudrate=9600)
ch2 = RS485Port(bridge, SC16IS752.CHANNEL_B, txden_pin=22, baudrate=9600)


def loopback_test():
    while True:
        msg1 = b"Hello from CH1\r\n"
        ch1.write(msg1)
        rx2 = ch2.read_line(timeout_ms=1000)
        print("CH1 -> CH2:", rx2)

        msg2 = b"Hello from CH2\r\n"
        ch2.write(msg2)
        rx1 = ch1.read_line(timeout_ms=1000)
        print("CH2 -> CH1:", rx1)

        time.sleep(1)


loopback_test()
