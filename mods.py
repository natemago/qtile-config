from colorsys import rgb_to_hls, hls_to_rgb
from types import SimpleNamespace
from libqtile.widget import base, KeyboardLayout
from libqtile.command import lazy
from libqtile import bar
from libqtile.log_utils import logger
from subprocess import Popen, PIPE
from threading import Timer
from functools import wraps

SPEAKER_LEVELS = '🔈🔉🔊'
SPEAKER_MUTED = '🔇'
MIC_MUTED = '🎙'

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

# palette = SimpleNamespace(
#     primary='#2c5182',
#     secondary='#3a2d68',
#     danger='#963239',
#     warning='#9d9340',
#     success='#277a2b',
#     info='#3a2d68',
#     background='#303030',
#     foreground='#a0a0a0',
# )

palette = SimpleNamespace(
    primary='#e936ff',
    secondary='#5bbab4',
    danger='#bd0300',
    warning='#ff5200',
    success='#00deff',
    info='#0088ff',
    background='#4f4350',
    foreground='#b5a7b6',
)


def log_error(fn):

    @wraps(fn)
    def _wrap_logged(*args, **kwargs):
        try:
            return fn(*args, *kwargs)
        except Exception as e:
            logger.exception(e)
            raise e
    
    return _wrap_logged


@log_error
def execute(*args):
    with Popen(args, stdout=PIPE) as process:
        return process.stdout.read().decode('utf-8')
    

def delay(fn, secs):
    Timer(secs, fn).start()


class Volume(base._TextBox):
    
    def __init__(self, **config):
        config['name'] = 'mod_volume'
        config['font'] = 'Monospace'
        config['markup'] = True
        config['mouse_callbacks'] = {
            'Button1': self.show_audio_mixer
        }
        super(Volume, self).__init__('#V#', bar.CALCULATED, **config)
        
        self.speaker_leves = config.get('speaker_level_symbols', SPEAKER_LEVELS)
        self.speaker_muted = config.get('speaker_muted_symbol', SPEAKER_MUTED)
        self.frames = config.get('frame_symbols', '[]')
        self.frame_color = config.get('frame_color', palette.foreground)
        self.frame_background_color = config.get('frame_background_color', palette.background)
        self.show_frame = config.get('show_frame', True)
        self.audio_mixer_command = config.get('audio_mixer_command', 'pavucontrol')
        self.mic_muted = config.get('mic_muted', MIC_MUTED)

        self._show_volume()
    
    def _show_volume(self):
        vol = int(execute('pamixer', '--get-volume'))

        speaker_level = vol//(100//len(self.speaker_leves))
        if speaker_level == len(self.speaker_leves):
            speaker_level = len(self.speaker_leves) - 1
        
        if not vol or self._is_muted():
            speaker_level = '<span color="{}">{}</span>'.format(palette.danger, self.speaker_muted)
        else:
            speaker_level = self.speaker_leves[speaker_level]

        mic_muted = self._is_mic_muted()

        txt_format = '{} {:>3}'.format(speaker_level, vol)

        if mic_muted:
            txt_format = '{} {}'.format(
                '<span color="{}">{}</span>'.format(palette.danger, self.mic_muted),
                txt_format,
            )

        if self.show_frame:
            txt_format = '{}{}{}'.format(self.frames[0], txt_format, self.frames[1])

        self.text = txt_format

        self.draw()

    @log_error
    def show_audio_mixer(self, *args, **kwargs):
        print('::::show_audio_mixer: ', self.audio_mixer_command)
        from threading import Thread
        from subprocess import run

        thr = Thread(target=lambda: run(self.audio_mixer_command, shell=True))
        thr.start()

    @log_error
    def cmd_volume_up(self):
        execute('pamixer', '-i', '5')
        self._show_volume()
    
    @log_error
    def cmd_volume_down(self):
        execute('pamixer', '-d', '5')
        self._show_volume()
    

    def _is_muted(self):
        return execute('pamixer', '--get-mute').strip().lower() == 'true'
    
    def _is_mic_muted(self):
        return execute('pamixer', '--default-source', '--get-mute').strip().lower() == 'true'

    @log_error
    def cmd_mute(self):
        if self._is_muted():
            pass
        execute('pamixer', '--mute')
        self._show_volume()

    @log_error
    def cmd_unmute(self):
        if not self._is_muted():
            pass
        execute('pamixer', '--unmute')
        self._show_volume()
    
    @log_error
    def cmd_mic_mute(self):
        if self._is_mic_muted():
            pass
        execute('pamixer', '--default-source', '--mute')
        self._show_volume()

    @log_error
    def cmd_mic_unmute(self):
        if not self._is_mic_muted():
            pass
        execute('pamixer', '--default-source', '--unmute')
        self._show_volume()

    @log_error
    def cmd_toggle_muted(self):
        if self._is_muted():
            self.cmd_unmute()
        else:
            self.cmd_mute()
    
    @log_error
    def cmd_toggle_mic_muted(self):
        if self._is_mic_muted():
            self.cmd_mic_unmute()
        else:
            self.cmd_mic_mute()
    

class ModKeyboardLayout(KeyboardLayout):

    def __init__(self, **config):
        super().__init__(**config)
        self.focused_window = None
    
    def cmd_window_focus(self, window):
        logger.error("************************")
        self.focused_window = window

        logger.error('Window: {}'.format(window))
        if hasattr(window, 'keyboard') and window.keyboard:
            if window.keyboard == self.backend.get_keyboard():
                return
            logger.error('Has keyboard -> {}'.format(window.keyboard))
            self.backend.set_keyboard(window.keyboard, self.option)
            self.tick()
        elif self.configured_keyboards:
            if self.configured_keyboards[0] == self.backend.get_keyboard():
                return
            logger.error('Has default keyboard -> {}'.format(self.configured_keyboards[0]))
            self.backend.set_keyboard(self.configured_keyboards[0], self.option)
            self.tick()

    
    def next_keyboard(self):
        super().next_keyboard()
        if self.focused_window:
            self.focused_window.keyboard = self.backend.get_keyboard()

