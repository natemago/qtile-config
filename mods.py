from colorsys import rgb_to_hls, hls_to_rgb
from types import SimpleNamespace
from libqtile.widget import base
from libqtile import bar
from subprocess import Popen, PIPE
from threading import Timer


# Color helpers
def hex_to_rgb(hex):
    if not hex:
        return (0,0,0)
    if hex[0] == '#':
        hex = hex[1:]
    if len(hex) not in [3,6]:
        raise Exception('Invalid color: ' + hex)
    if len(hex) == 3:
        hex = [c + '0' for c in hex]
    return tuple([int(hex[n:n+2], 16) for n in [0,2,4]])


def rgb_to_hex(r,g,b):
    return '#' + ''.join(['%02x'%c for c in [r,g,b]])


def adjust_color_lightness(color, p):
    r, g, b = hex_to_rgb(color)
    h, l, s = rgb_to_hls(r/255, g/255, b/255)
    l = max(min(l*p, 1.0), 0.0)
    color = rgb_to_hex(*tuple([int(c * 255) for c in hls_to_rgb(h, l, s)]))
    return color


def lighten(color, factor=0.1):
    return adjust_color_lightness(color, 1 + factor)

def darken(color, factor=0.1):
    return adjust_color_lightness(color, 1 - factor)

palette = SimpleNamespace(
    primary='#2c5182',
    secondary='#3a2d68',
    danger='#963239',
    warning='#9d9340',
    success='#277a2b',
    info='#3a2d68',
    background='#303030',
    foreground='#909090',
)


def execute(*args):
    with Popen(args, stdout=PIPE) as process:
        return process.stdout.read().decode('utf-8')
    

def delay(fn, secs):
    Timer(secs, fn).start()


class Volume(base._TextBox):
    
    def __init__(self, **config):
        config['name'] = 'mod_volume'
        super(Volume, self).__init__('#V#', bar.CALCULATED, **config)
        self._show_volume()
    
    def _show_volume(self):
        vol = int(execute('pamixer', '--get-volume'))
        self.text =  str(vol) + ' ' + '▮'*(vol//20) + '▯'*(5 - vol//20)
        self.draw()

    def cmd_volume_up(self):
        execute('pamixer', '-i', '5')
        self._show_volume()
    
    def cmd_volume_down(self):
        execute('pamixer', '-d', '5')
        self._show_volume()
    

    
