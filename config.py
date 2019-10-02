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

from libqtile.config import Key, Screen, Group, Drag, Click
from libqtile.command import lazy
from libqtile import layout, bar, widget

from typing import List  # noqa: F401

from mods import lighten, darken, palette

mod = "mod4"
alt = 'mod1'
ctrl = 'control'

keys = [
    # Switch between windows in current stack pane
    Key([alt], "Up", lazy.layout.up()),
    Key([alt], "Down", lazy.layout.down()),
    Key([alt], "Left", lazy.layout.left()),
    Key([alt], "Right", lazy.layout.right()),
    Key([alt], 'Tab', lazy.layout.next()),
    
    # Move windows up or down in current stack
    Key([mod, alt], "Up", lazy.layout.shuffle_down()),
    Key([mod, alt], "Down", lazy.layout.shuffle_up()),
    Key([mod, alt], "m", lazy.layout.swap_main()),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout()),

    # Groups
    Key([ctrl, alt], 'Right', lazy.screen.next_group()),
    Key([ctrl, alt], 'Left', lazy.screen.prev_group()),

    
    # Qtile commands
    Key([mod, ctrl], "r", lazy.restart()),
    Key([mod, ctrl], "q", lazy.shutdown()),
    Key([mod], "w", lazy.window.kill()),

    # Custom commands/apps
    Key([mod], "space", lazy.spawn("rofi -show run")),
    Key([mod], "Return", lazy.spawn("terminator")),
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
    )
]

widget_defaults = dict(
    font='sans',
    fontsize=10,
    padding=3,
    foreground=palette.foreground,
    background=palette.background,
)
extension_defaults = widget_defaults.copy()

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
                    margin_y=0,
                ),
                widget.Prompt(),
                widget.WindowName(),
                widget.Systray(),
                widget.Battery(
                    format='⚡ {percent:2.0%}{char}',
                    background=lighten(palette.warning, 0.15),
                    foreground=darken(palette.foreground, 0.5),
                    charge_char='↑',
                    discharge_char='↓',
                    empty_char='☠'
                ),
                widget.Clock(format='%Y-%m-%d %a %I:%M %p'),
            ],
            18,
            **{
                'background': palette.background,
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

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    {'wmclass': 'confirm'},
    {'wmclass': 'dialog'},
    {'wmclass': 'download'},
    {'wmclass': 'error'},
    {'wmclass': 'file_progress'},
    {'wmclass': 'notification'},
    {'wmclass': 'splash'},
    {'wmclass': 'toolbar'},
    {'wmclass': 'confirmreset'},  # gitk
    {'wmclass': 'makebranch'},  # gitk
    {'wmclass': 'maketag'},  # gitk
    {'wname': 'branchdialog'},  # gitk
    {'wname': 'pinentry'},  # GPG key password entry
    {'wmclass': 'ssh-askpass'},  # ssh-askpass
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
