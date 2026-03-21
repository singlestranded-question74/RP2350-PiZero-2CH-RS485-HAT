from machine import Pin, SPI, SoftSPI
import time


class SC16IS752:
    XTAL_HZ = 14_745_600

    CHANNEL_A = 0x00
    CHANNEL_B = 0x02

    CMD_READ = 0x80
    CMD_WRITE = 0x00

    REG_RHR = 0x00
    REG_THR = 0x00
    REG_IER = 0x01
    REG_FCR = 0x02
    REG_IIR = 0x02
    REG_LCR = 0x03
    REG_MCR = 0x04
    REG_LSR = 0x05
    REG_MSR = 0x06
    REG_SPR = 0x07
    REG_TXLVL = 0x08
    REG_RXLVL = 0x09
    REG_IODIR = 0x0A
    REG_IOSTATE = 0x0B
    REG_IOCONTROL = 0x0E
    REG_EFCR = 0x0F

    REG_DLL = 0x00
    REG_DLH = 0x01
    REG_EFR = 0x02

    LSR_DATA_READY = 0x01
    LSR_THR_EMPTY = 0x20
    LSR_TX_EMPTY = 0x40

    def __init__(
        self,
        spi_id=0,
        sck_pin=21,
        mosi_pin=20,
        miso_pin=19,
        cs_pin=18,
        irq_pin=24,
        baudrate=1_000_000,
        use_soft_spi=True,
    ):
        if use_soft_spi:
            self.spi = SoftSPI(
                baudrate=baudrate,
                polarity=0,
                phase=0,
                bits=8,
                firstbit=SPI.MSB,
                sck=Pin(sck_pin),
                mosi=Pin(mosi_pin),
                miso=Pin(miso_pin),
            )
        else:
            self.spi = SPI(
                spi_id,
                baudrate=baudrate,
                polarity=0,
                phase=0,
                bits=8,
                firstbit=SPI.MSB,
                sck=Pin(sck_pin),
                mosi=Pin(mosi_pin),
                miso=Pin(miso_pin),
            )
        self.cs = Pin(cs_pin, Pin.OUT, value=1)
        self.irq = Pin(irq_pin, Pin.IN, Pin.PULL_UP)
        self._tx = bytearray(2)
        self._rx = bytearray(2)

    def _addr(self, reg, channel, read=False):
        return ((reg & 0x0F) << 3) | (channel & 0x02) | (self.CMD_READ if read else 0)

    def _write_reg(self, reg, channel, value):
        self._tx[0] = self._addr(reg, channel, read=False)
        self._tx[1] = value & 0xFF
        self.cs(0)
        self.spi.write(self._tx)
        self.cs(1)

    def _read_reg(self, reg, channel):
        self._tx[0] = self._addr(reg, channel, read=True)
        self._tx[1] = 0xFF
        self.cs(0)
        self.spi.write_readinto(self._tx, self._rx)
        self.cs(1)
        return self._rx[1]

    def _set_divisor(self, channel, divisor):
        ier = self._read_reg(self.REG_IER, channel)
        lcr = self._read_reg(self.REG_LCR, channel)

        self._write_reg(self.REG_IER, channel, ier | 0x10)
        self._write_reg(self.REG_LCR, channel, 0x80)
        self._write_reg(self.REG_DLH, channel, (divisor >> 8) & 0xFF)
        self._write_reg(self.REG_DLL, channel, divisor & 0xFF)
        self._write_reg(self.REG_LCR, channel, lcr)
        self._write_reg(self.REG_IER, channel, ier)

    def begin(self, channel, baudrate=9600):
        self._write_reg(self.REG_LCR, channel, 0xBF)
        self._write_reg(self.REG_EFR, channel, 0x10)
        self._write_reg(self.REG_LCR, channel, 0x03)
        self._write_reg(self.REG_FCR, channel, 0x06)
        self._write_reg(self.REG_FCR, channel, 0xF1)
        self._write_reg(self.REG_SPR, channel, 0x41)
        self._write_reg(self.REG_IODIR, channel, 0xFF)
        self._write_reg(self.REG_IOSTATE, channel, 0x00)
        self._write_reg(self.REG_IER, channel, 0x01)
        self.set_baudrate(channel, baudrate)

    def set_baudrate(self, channel, baudrate):
        divisor = int(self.XTAL_HZ / 16 / baudrate)
        if divisor <= 0:
            raise ValueError("invalid baudrate")
        self._set_divisor(channel, divisor)

    def bytes_available(self, channel):
        return self._read_reg(self.REG_RXLVL, channel)

    def tx_space(self, channel):
        return self._read_reg(self.REG_TXLVL, channel)

    def line_status(self, channel):
        return self._read_reg(self.REG_LSR, channel)

    def write(self, channel, data):
        if isinstance(data, str):
            data = data.encode()
        if not data:
            return 0

        total = 0
        mv = memoryview(data)
        while total < len(mv):
            room = self.tx_space(channel)
            if room == 0:
                time.sleep_ms(1)
                continue

            chunk = mv[total : total + room]
            buf = bytearray(len(chunk) + 1)
            buf[0] = self._addr(self.REG_THR, channel, read=False)
            buf[1:] = chunk
            self.cs(0)
            self.spi.write(buf)
            self.cs(1)
            total += len(chunk)
        return total

    def read(self, channel, nbytes=1, timeout_ms=1000):
        if nbytes <= 0:
            return b""

        out = bytearray()
        deadline = time.ticks_add(time.ticks_ms(), timeout_ms)
        while len(out) < nbytes:
            available = self.bytes_available(channel)
            if available:
                count = min(available, nbytes - len(out))
                for _ in range(count):
                    out.append(self._read_reg(self.REG_RHR, channel))
                continue
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                break
            time.sleep_ms(1)
        return bytes(out)

    def read_line(self, channel, timeout_ms=1000):
        out = bytearray()
        deadline = time.ticks_add(time.ticks_ms(), timeout_ms)
        while True:
            data = self.read(channel, 1, timeout_ms=10)
            if data:
                out.extend(data)
                if data == b"\n":
                    return bytes(out)
                deadline = time.ticks_add(time.ticks_ms(), timeout_ms)
                continue
            if out and time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                return bytes(out)
            if not out and time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                return b""

    def flush(self, channel, timeout_ms=1000):
        deadline = time.ticks_add(time.ticks_ms(), timeout_ms)
        while True:
            lsr = self.line_status(channel)
            if (lsr & self.LSR_THR_EMPTY) and (lsr & self.LSR_TX_EMPTY):
                return True
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                return False
            time.sleep_ms(1)


class RS485Port:
    def __init__(self, bridge, channel, txden_pin, baudrate=9600):
        self.bridge = bridge
        self.channel = channel
        self.txden = Pin(txden_pin, Pin.OUT, value=0)
        self.bridge.begin(channel, baudrate)

    def write(self, data):
        self.txden(1)
        time.sleep_us(100)
        count = self.bridge.write(self.channel, data)
        self.bridge.flush(self.channel)
        time.sleep_us(100)
        self.txden(0)
        return count

    def read(self, nbytes=1, timeout_ms=1000):
        return self.bridge.read(self.channel, nbytes, timeout_ms)

    def read_line(self, timeout_ms=1000):
        return self.bridge.read_line(self.channel, timeout_ms)

    def any(self):
        return self.bridge.bytes_available(self.channel)
