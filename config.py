# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import subprocess

from libqtile.config import Key, Screen, Group, Drag, Click, Match
from libqtile.lazy import lazy
from libqtile import layout, bar, widget, hook
from libqtile.widget.backlight import ChangeDirection
from libqtile.log_utils import logger

from typing import List  # noqa: F401

from mods import lighten, darken, palette, Volume, log_error, execute, ModKeyboardLayout


mod = "mod4"
alt = 'mod1'
ctrl = 'control'


'''
Command groups:

 - Layout switching:
    - next layout: mod+tab
    - specific layout: mod + <letter>
        - monad tall: mod + t
        - max: mod + m
        - tile (expose all): mod + e
  - mod + alt - layout related window operations
  - mod + <number> - goto groups
  - mod + shift - send window to group
  - mod + alt + left/right - move between groups


'''


keys = [
    # Switch between windows in current stack pane
    Key([alt], "Up", lazy.layout.up()),
    Key([alt], "Down", lazy.layout.down()),
    Key([alt], "Left", lazy.layout.left()),
    Key([alt], "Right", lazy.layout.right()),
    #Key(['shift'], 'Tab', lazy.layout.next()),
    #Key([alt, 'shift'], 'Tab', lazy.layout.previous()),

    # Move windows up or down in current stack
    Key([mod, alt], "Up", lazy.layout.shuffle_up()),
    Key([mod, alt], "Down", lazy.layout.shuffle_down()),
    Key([mod, alt], "m", lazy.layout.swap_main()),
    Key([mod, alt], "o", lazy.layout.maximize()),
    Key([mod, alt], "g", lazy.layout.grow()),
    Key([mod, alt], "s", lazy.layout.shrink()),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout()),
    Key([mod, 'shift'], "Tab", lazy.prev_layout()),

    # Groups
    Key([ctrl, alt], 'Right', lazy.screen.next_group()),
    Key([ctrl, alt], 'Left', lazy.screen.prev_group()),

    # Qtile commands
    Key([mod, ctrl], "r", lazy.restart()),
    Key([mod, ctrl], "q", lazy.shutdown()),
    Key([mod], "w", lazy.window.kill()),
    # Key([ctrl, alt], "l", lazy.spawn("i3lock --color 000000")),
    Key([ctrl, alt], "l", lazy.spawn("xscreensaver-command -lock")),
    Key([mod, ctrl], "s", lazy.spawn("mons -s")),
    Key([mod, ctrl], "p", lazy.spawn("mons -o")),


    # Custom commands/apps
    Key([mod], "space", lazy.spawn("rofi -show run")),
    Key([alt], "grave", lazy.spawn("rofi -show window")),
    Key([mod], "Return", lazy.spawn("terminator")),

    # Show help
    Key([mod], "h", lazy.spawn("rofi -show 'Key Bindings' -modes \"Key Bindings:/home/pavle/.config/qtile/keybindings.sh\"")),

    Key([], 'XF86AudioRaiseVolume', lazy.widget['mod_volume'].volume_up()),
    Key([], 'XF86AudioLowerVolume', lazy.widget['mod_volume'].volume_down()),
    Key([], 'XF86AudioMute', lazy.widget['mod_volume'].toggle_muted()),
    Key([], 'XF86AudioMicMute', lazy.widget['mod_volume'].toggle_mic_muted()),
    Key([], 'XF86MonBrightnessDown', lazy.widget['backlight'].change_backlight(ChangeDirection.DOWN)),
    Key([], 'XF86MonBrightnessUp', lazy.widget['backlight'].change_backlight(ChangeDirection.UP)),

    # Keyboar Layout
    Key([alt], 'Shift_L', lazy.widget['modkeyboardlayout'].next_keyboard()),
    Key([alt], 'Shift_R', lazy.widget['modkeyboardlayout'].next_keyboard()),
]

groups = [Group(i) for i in "12345678"]
for i in groups:
    keys.extend([
        # mod1 + letter of group = switch to group
        Key([mod], i.name, lazy.group[i.name].toscreen()),

        # mod1 + shift + letter of group = switch to & move focused window to group
        Key([mod, "shift"], i.name, lazy.window.togroup(i.name)),
    ])

layouts = [
    layout.Max(),
    layout.MonadTall(
        border_focus = palette.primary,
        border_normal = palette.background,
        border_width = 1,
    ),
    layout.MonadWide(
        border_focus = palette.primary,
        border_normal = palette.background,
        border_width = 1,
    ),
]

widget_defaults = dict(
    font='sans',
    fontsize=10,
    padding=3,
    foreground=palette.foreground,
    background=palette.background,
)
extension_defaults = widget_defaults.copy()

keyboardLayoutWidget = ModKeyboardLayout(
    configured_keyboards = ['us', 'mk'],
    fmt='[⌨  {}]',
    background=darken(palette.background, 0.5),
    font='monospace bold',
)

def parse_text(sep, sel, max_width):

    def _parse_text(text):
        windows = text.split(sep)
        result = []
        for win in windows:
            if len(win) > max_width:
                if win.startswith(sel[0]):
                    win = win.removeprefix(sel[0]).removesuffix(sel[1])
                    if len(win) > max_width:
                        win = win[0:max_width-3] + '...'
                    win = win.join(sel)
                else:
                    win = win[0:max_width-3] + '...'
            result.append(win)
        return sep.join(result)
    
    return _parse_text

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.GroupBox(
                    borderwidth=0,
                    font='monospace',
                    highlight_method='block',
                    rounded=False,
                    active=lighten(palette.foreground, 1),
                    foreground=palette.foreground,
                    inactive=palette.foreground,
                    this_current_screen_border=palette.primary,
                    margin_y=2,
                ),
                # widget.TaskList(
                #     background=palette.background,
                #     highlight_method='block',
                #     border=darken(palette.primary, 0.4),
                #     foreground=lighten(palette.foreground, 0.5),
                #     borderwidth=0,
                #     max_title_width=200,
                #     rounded=False,
                #     urgent_alert_method='block',
                #     urgent_border=palette.danger,
                #     #padding_y=0,
                #     margin_y=0,
                #     icon_size=14,
                #     font='monospace',
                # ),
                widget.WindowTabs(
                    background=palette.background,
                    foreground=lighten(palette.foreground, 0.5),
                    font='monospace',
                    separator=' || ',
                    selected=('<span color="black" bgcolor="#feecee">', '</span>'),
                    parse_text=parse_text(' || ', ('<span color="black" bgcolor="#feecee">', '</span>'), 35),
                ),
                widget.Systray(),
                widget.Sep(
                    size_percent=100,
                    padding=5,
                    linewidth=0,
                    background=palette.background,
                    foreground=darken(palette.background, 0.5),
                ),
                widget.CurrentLayoutIcon(
                    background=darken(palette.background, 0.5),
                    scale=0.6,
                    font='monospace',
                ),
                widget.CurrentLayout(
                    background=darken(palette.background, 0.5),
                    font='monospace',
                ),
                widget.Battery(
                    fmt='[{}]',
                    format='⚡ {percent:2.0%} {char}',
                    charge_char='⇧',
                    discharge_char='⇩',
                    empty_char='☠',
                    background=darken(palette.background, 0.5),
                ),
                widget.Backlight(
                    backlight_name='intel_backlight',
                    change_command='brightnessctl s {0}%',
                    step=5,
                    format='[💡 {percent:2.0%}]',
                    background=darken(palette.background, 0.5),
                    font='monospace bold',
                ),
                Volume(
                    background=darken(palette.background, 0.5),
                    font='monospace bold',
                ),
                #widget.KeyboardLayout(
                keyboardLayoutWidget,
                widget.Clock(
                    format='[ %Y-%m-%d %a %I:%M:%S %p ]',
                    foreground=palette.background,
                    background=palette.foreground,#darken(palette.background, 0.5),
                    font='monospace bold',
                ),
            ],
            20,
            **{
                'background': palette.background,
                'fontsize': 20,
                'font':'monospace',
            },
        ),
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]

# Hooks
@hook.subscribe.startup_complete
@log_error
def autostart():
    home = os.path.expanduser('~/.config/qtile/scripts/autostart.sh')
    subprocess.call(['bash',  home])

#@hook.subscribe.startup
#def startup():
#    execute("xrandr", "--output", "DP-1", "--primary")
#    execute("xrandr", "--output", "eDP-1", "--off")

@hook.subscribe.client_focus
@log_error
def on_window_focus(client):
    keyboardLayoutWidget.cmd_window_focus(client)


dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(wm_class='pavucontrol'),
])
auto_fullscreen = True
focus_on_window_activation = "smart"

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
