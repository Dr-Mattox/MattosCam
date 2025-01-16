# ssd1306.py - Driver basico para displays SSD1306 I2C 128x64 o 128x32
# Fuente: Adaptado de https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py

from micropython import const
import framebuf

# Control commands
SET_CONTRAST        = const(0x81)
SET_ENTIRE_ON       = const(0xa4)
SET_NORM_INV        = const(0xa6)
SET_DISP            = const(0xae)
SET_MEM_ADDR        = const(0x20)
SET_COL_ADDR        = const(0x21)
SET_PAGE_ADDR       = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP       = const(0xa0)
SET_MUX_RATIO       = const(0xa8)
SET_COM_OUT_DIR     = const(0xc0)
SET_DISP_OFFSET     = const(0xd3)
SET_COM_PIN_CFG     = const(0xda)
SET_DISP_CLK_DIV    = const(0xd5)
SET_PRECHARGE       = const(0xd9)
SET_VCOM_DESEL      = const(0xdb)
SET_CHARGE_PUMP     = const(0x8d)

class SSD1306:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.fb = fb
        self.fill = fb.fill
        selfpixel = fb.pixel
        self.hline = fb.hline
        self.vline = fb.vline
        self.line = fb.line
        self.rect = fb.rect
        self.fill_rect = fb.fill_rect
        self.text = fb.text
        self.scroll = fb.scroll
        self.blit = fb.blit
        self.init_display()

    def init_display(self):
        self.reset()
        self.write_cmd(SET_DISP | 0x00)  # off
        self.write_cmd(SET_MEM_ADDR)
        self.write_cmd(0x00)  # horizontal
        self.write_cmd(SET_SEG_REMAP | 0x01)
        self.write_cmd(SET_COM_OUT_DIR | 0x08)
        if self.height == 32:
            self.write_cmd(SET_MUX_RATIO)
            self.write_cmd(0x1F)
            self.write_cmd(SET_DISP_OFFSET)
            self.write_cmd(0x00)
            self.write_cmd(SET_DISP_START_LINE | 0x00)
        else:
            self.write_cmd(SET_MUX_RATIO)
            self.write_cmd(0x3F)
            self.write_cmd(SET_DISP_OFFSET)
            self.write_cmd(0x00)
            self.write_cmd(SET_DISP_START_LINE | 0x00)
        self.write_cmd(SET_DISP_CLK_DIV)
        self.write_cmd(0x80)
        self.write_cmd(SET_PRECHARGE)
        self.write_cmd(0xf1 if not self.external_vcc else 0x22)
        self.write_cmd(SET_COM_PIN_CFG)
        self.write_cmd(0x02 if self.height == 32 else 0x12)
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(0xff)
        self.write_cmd(SET_ENTIRE_ON)
        self.write_cmd(SET_NORM_INV)
        if not self.external_vcc:
            self.write_cmd(SET_CHARGE_PUMP)
            self.write_cmd(0x14)
        self.write_cmd(SET_DISP | 0x01)  # on
        self.fill(0)
        self.show()

    def write_cmd(self, cmd):
        raise NotImplementedError

    def reset(self):
        pass

    def show(self):
        raise NotImplementedError

class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co = 1, D/C# = 0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def show(self):
        for page in range(self.pages):
            self.write_cmd(SET_PAGE_ADDR)
            self.write_cmd(page)
            self.write_cmd(page)
            self.write_cmd(SET_COL_ADDR)
            self.write_cmd(0x00)
            self.write_cmd(self.width - 1)
            self.i2c.writeto(self.addr, bytearray([0x40]) + self.buffer[page*self.width:(page+1)*self.width])
