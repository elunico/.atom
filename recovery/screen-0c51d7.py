from typing import Tuple, Dict, Any, List, Union
import curses
import json
import os
import math

CursesWindow = Any


class FontEffect:
    def __init__(self, attribute: int) -> None:
        self.attribute = attribute


FontEffect.BOLD = FontEffect(curses.A_BOLD)
FontEffect.UNDERLINE = FontEffect(curses.A_UNDERLINE)
FontEffect.INVERT = FontEffect(curses.A_STANDOUT)
FontEffect.PLAIN = FontEffect(0)


def color_constant_for_name(name):
    prop = "COLOR_{}".format(name.upper())
    try:
        return getattr(curses, prop)
    except AttributeError:
        curses.endwin()
        raise ValueError("colors.json color '{}' is not a valid curses color".format(name))


class Color(FontEffect):
    _colors: Dict[str, int] = {}

    @staticmethod
    def named(name) -> 'Color':
        return Color(curses.color_pair(Color._colors[name]))

    @staticmethod
    def init_color_pairs():
        curses.start_color()
        thisDir = os.path.split(__file__)[:-1]
        with open(os.path.join(*tuple(thisDir), 'colors.json')) as f:
            clrs = json.load(f)['pairs']
            num = 1
            for (k, d) in clrs.items():
                curses.init_pair(num, color_constant_for_name(
                    d['foreground']), color_constant_for_name(d['background']))
                Color._colors[k] = num
                num += 1

    def __init__(self, attribute) -> None:
        super().__init__(attribute)


class TextStyle:
    def __init__(self, length: int, attrs: Tuple[FontEffect, ...]) -> None:
        self.length = length
        self.attributes = attrs

    def attr(self) -> int:
        attr = 0
        for s in self.attributes:
            attr |= s.attribute
        return attr


class NoStyle(TextStyle):
    def __init__(self):
        super().__init__(0, (0,))

    def attr(self) -> int:
        return 0


# Line = List[str]
# TextCoordinate = Tuple[int, int]
# LineCache = List[Line]
# StyleCache = Dict[TextCoordinate, TextStyle]


class Screen:
    def __init__(self, win: CursesWindow, lines: int, cols: int) -> None:
        self.win = win
        self.lines = lines
        self.cols = cols
        self.buffer: List[Union[str, TextStyle]] = []

        self.dirty = False
        self.line_cache: List[List[str]] = [[]]
        self.style_cache: Dict[Tuple[int, int], TextStyle] = {}
        self.start_line = 0

        self.win.border

    def nl(self, count=1):
        self.add_str('\n' * count)

    def set_style(self, *styles: FontEffect):
        self.dirty = True
        self.buffer.append(TextStyle(0, styles))

    def _add_to_buffer(self, string: str):
        self.buffer.extend([i for i in string])

    def _update_cache(self):
        self.line_cache, self.style_cache = self._transform_buffer(self.buffer)

    def add_str(self, string: str):
        self.dirty = True
        self._add_to_buffer(string)
        return math.ceil(len(string) / self.cols)

    def add_str_wrapped(self, string: str):
        self.dirty = True
        words = string.split(' ')
        chars = 0
        lines = 1
        # this is to fix issue #2 on github
        # normally hitting self.cols requires moving to the next line
        # but if there is no more words it actually is still only 1 line
        more_words = True
        for word in words:
            if len(word) + chars == self.cols:
                self._add_to_buffer(word)
                chars = 0
                lines += 1
                more_words = False
            elif len(word) + chars > self.cols:
                self._add_to_buffer('\n')
                self._add_to_buffer(word + ' ')
                chars = len(word) + 1
                lines += 1
                more_words = True
            else:
                self._add_to_buffer(word + ' ')
                chars += len(word) + 1
                more_words = True
        return lines if more_words else lines - 1

    def _transform_buffer(
        self,
        buffer: List[Union[str, TextStyle]]
    ) -> Tuple[List[List[str]], Dict[Tuple[int, int], TextStyle]]:

        lines: List[List[str]] = [[]]
        styles: Dict[Tuple[int, int], TextStyle] = {}
        count = 0
        line = 0
        for elt in buffer:
            if isinstance(elt, TextStyle):
                if count == self.cols:
                    styles[(line + 1, 0)] = elt
                else:
                    styles[(line, count)] = elt
                continue
            if count == self.cols:
                line += 1
                count = 0
                lines.append([])
                if elt != '\n':
                    lines[line].append(elt)
                    count += 1
            else:
                lines[line].append(elt)
                count += 1
                if elt == '\n':
                    line += 1
                    count = 0
                    lines.append([])
        return lines, styles

    def _text_in_view(self) -> \
            Tuple[List[List[str]], Dict[Tuple[int, int], TextStyle]]:
        if self.dirty:
            self._update_cache()
            self.dirty = False
        return (self.line_cache[self.start_line:self.lines + self.start_line],
                self.style_cache)

    def render(self) -> None:
        self.win.clear()
        lines, styles = self._text_in_view()

        # if the screen is completely full
        # i.e. the lines go to the end and chars
        # in the last line go to the end
        # we must elide the last character
        if len(lines) == self.lines:
            if len(lines[-1]) == self.cols:
                lines[-1] = lines[-1][:-1]

        # if there is a new line anywhere else
        # in the last line, it must wait until the next
        # screen.
        try:
            i = lines[-1].index('\n')
            lines[-1] = lines[-1][:i]
        except ValueError:
            pass

        # index for finding attributes must start
        # at the line the display begins at
        lineno = self.start_line
        c = 0
        currentAttr = self.style_for_line(self.start_line, styles).attr()
        for line in lines:
            for char in line:
                if (lineno, c) in styles:
                    currentAttr = styles[(lineno, c)].attr()
                self.win.addstr(char, currentAttr)
                c += 1
            c = 0
            lineno += 1
        self.win.refresh()

    def style_for_line(
        self,
        line: int,
        styles: Dict[Tuple[int, int], TextStyle]
    ) -> TextStyle:
        keys = list(sorted((i for i in styles.keys() if (i[0] - line) < 0),
                           key=lambda pair: (abs(pair[0] - line), pair[1])))
        return NoStyle() if len(keys) == 0 else styles[keys[0]]

    def to_top(self):
        self.start_line = 0

    def to_bottom(self):
        self.start_line = (len(self.line_cache) - self.lines) + 1

    def shift_up(self, amount=1):
        self.start_line = max(0, self.start_line - amount)

    def shift_down(self, amount=1):
        linecnt = len(self.line_cache)
        if linecnt < self.lines - 1:
            return
        if self.start_line + amount >= ((linecnt - self.lines) + 1):
            self.start_line = (linecnt - self.lines) + 1
        else:
            self.start_line = self.start_line + amount

    def subwin(self, *args, **kwargs):
        return self.win.subwin(*args, **kwargs)

    def getch(self, *args, **kwargs):
        return self.win.getch(*args, **kwargs)
