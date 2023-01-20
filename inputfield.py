import curses

class input_field:
    def __init__(self, window, contents: str = None) -> None:
        self.contents_backup = contents 
        if contents:
            self.contents = list(str(contents))
        else:
            self.contents = [' ']
        self.window = window
        self.len = window.getmaxyx()[1]
        self.shift = 0
        self.max_shown = self.len - 2
        self.cursor_pos = min(self.max_shown - 1, len(self.contents))

    def cursor_left(self):
        if self.cursor_pos > 0:
            self.cursor_pos -= 1
            if self.cursor_pos < self.shift:
                self.shift -= 1


    def cursor_right(self):
        if self.cursor_pos < len(self.contents):
            self.cursor_pos += 1
            if self.cursor_pos > self.max_shown + self.shift:
                self.shift += 1

    def cursor_home(self):
        while self.cursor_pos > 0:
            self.cursor_left()

    def cursor_end(self):
        while self.cursor_pos < len(self.contents):
            self.cursor_right()

    def set_character(self, character):
        try:
            self.contents[self.cursor_pos] = character
            self.cursor_right()
        except IndexError as IE:
            if self.cursor_pos == len(self.contents):
                self.contents += character
                self.cursor_right()
            else:
                raise IndexError from IE

    def backspace(self):
        if self.contents:
            self.contents.pop(self.cursor_pos - 1)
            self.cursor_left()

    def gather(self):
        if self.contents == ' ':
            return None
        return ''.join(self.contents).strip()

    def show(self):
        self.window.clear()
        screen_pos = 0
        for i in range(0 + self.shift, min(self.max_shown + self.shift, len(self.contents))):
            if self.cursor_pos == i:
                self.window.addch(0, screen_pos, self.contents[i], curses.A_REVERSE)
            else:
                self.window.addch(0, screen_pos, self.contents[i])
            screen_pos += 1
        if (self.cursor_pos == len(self.contents) and
            self.cursor_pos < self.max_shown + self.shift + 1):
            self.window.addch(0, screen_pos, ' ', curses.A_REVERSE)
        self.window.refresh()

def get_input(window, contents: str = None, CancelReturnsNone: bool = False):
    special_keys = [ 10, 13, -1, 27,
                    curses.KEY_ENTER,
                    curses.KEY_BACKSPACE,
                    curses.KEY_DC,
                    curses.KEY_SDC,
                    curses.KEY_IC,
                    curses.KEY_HOME,
                    curses.KEY_SHOME,
                    curses.KEY_END,
                    curses.KEY_SEND,
                    curses.KEY_RIGHT,
                    curses.KEY_LEFT,
                    curses.KEY_DOWN,
                    curses.KEY_UP,
                    curses.KEY_NPAGE,
                    curses.KEY_PPAGE,
                    curses.KEY_F0,
                    curses.KEY_RESIZE
                   ]

    input_window = input_field(window, contents)
    window.keypad(1)

    while True:
        input_window.show()
        key = window.getch()
        if key not in special_keys:
            input_window.set_character(chr(key))
        if key == curses.KEY_RIGHT:
            input_window.cursor_right()
        if key == curses.KEY_LEFT:
            input_window.cursor_left()
        if key == curses.KEY_HOME or key == curses.KEY_SHOME:
            input_window.cursor_home()
        if key == curses.KEY_END or key == curses.KEY_SEND:
            input_window.cursor_end()
        if key == curses.KEY_BACKSPACE:
            input_window.backspace()
        if key == 27:
            if CancelReturnsNone:
                return None
            return input_window.contents_backup
        if key in [curses.KEY_ENTER, 10, 13]:
            return input_window.gather()
