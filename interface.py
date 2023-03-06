import os
import curses
import pyperclip

import tables
import inputfield
import visuals

class Editor:
    def __init__(self, key_hint: dict,
                 max_cell_len: int,
                 table: tables.Table,
                 absolute_path: str,
                 read_only: bool,
                 new_file: bool):
        self.key_hint = key_hint
        self.max_cell_length = max_cell_len
        self.table = table
        self.absolute_path = absolute_path
        self.read_only = read_only
        self.new_file = new_file

        self.info = visuals.Info(default_message = self.key_hint["edit"] + self.key_hint["quit"] + " ")
        if self.read_only:
            self.info = visuals.Info(default_message = self.key_hint["quit"] + " ")

        self.table_height = self.table.row_count + 1
        self.table_width = self.table.column_count * self.max_cell_length + self.table.column_count * 3

    def edit(self, scr):
        scr.keypad(True)
        scr.clear()
        curses.curs_set(False)
        curses.halfdelay(1)

        pointer = visuals.Pointer(1, 1)

        shown_collumns = []
        shown_rows = []
        x_shift = 0
        y_shift = 0

        changes = False
        if self.new_file:
            changes = True

        address = f"({pointer.column:>3}:{pointer.row:<3})"
        row_width = len(str(self.table.row_count))
        height, width = scr.getmaxyx()

        input_win = curses.newwin(1, width - 2, height - 1, 2)
        key_pad = curses.newpad(1, 1)

        def clean(string: str):
            string = string.strip()
            returnstring = ""
            for letter in string:
                if letter in ["\n", "\r", os.linesep]:
                    returnstring += " "
                else:
                    returnstring += letter
            return returnstring

        def update_table_size():
            nonlocal row_width

            self.table_height = self.table.row_count + 1
            self.table_width = self.table.column_count * self.max_cell_length + self.table.column_count * 3
            row_width = len(str(self.table.row_count))

        def save_as():
            self.info.set_alert('?', "Save as: " + self.key_hint["confirm"] + self.key_hint["cancel"])
            update_all()
            file_path = inputfield.get_input(input_win, self.absolute_path, CancelReturnsNone= True)
            if file_path:
                try:
                    tables.file_save(self.table, file_path)
                    self.info.reset_alert()
                    update_all()
                    return 1
                except PermissionError:
                    show_error("Error: Access denied")
                    return 2
            self.info.reset_alert()
            update_all()
            return 0

        def show_error(message: str):
            self.info.set_alert('!', message + self.key_hint["confirm"])
            update_all()
            inputfield.get_input(input_win)
            self.info.reset_alert()
            update_all()

        def show_prompt(message: str):
            self.info.set_alert('?', message + "[y/n]" + self.key_hint["cancel"])
            update_all()
            answer = inputfield.get_input(input_win)
            if str(answer).strip().lower() in ['yes', 'y']:
                answer = True
            elif str(answer).strip().lower() in ['no', 'n']:
                answer = False
            else:
                answer = None
            self.info.reset_alert()
            update_all()
            return answer


        def get_quoting_ind(quoting):
            try:
                return visuals.QUOTING_INDICATORS[quoting]
            except IndexError:
                return ' '

        def update_info(message: str = None, show_mode: bool = False):
            if message:
                self.info.message = message
                self.info.show_mode = show_mode

            message = self.info.message

            if self.info.show_mode:
                spacer_len = (width-2)-(len(self.info.message) + len(" Mode:") + row_width)
                if spacer_len > 0:
                    message = f"{message}{' ':^{spacer_len}} Mode:"

            if len(message) >= width - 1:
                message = ' '

            info_win = curses.newwin(1, width - row_width, height - 2, row_width)
            info_win.addstr(0, 0, f"{message:<{width - row_width - 1}}", curses.A_REVERSE)
            info_win.noutrefresh()

        def update_table():
            table_pad = curses.newpad(max(self.table_height, height), max(self.table_width, width))
            shown_collumns.clear()
            shown_rows.clear()
            for y in range(self.table.row_count - y_shift):
                x_display = 0
                y = y + y_shift
                for x in range(self.table.column_count - x_shift):
                    x = x + x_shift
                    cell_display = self.table.get_cell(x + 1, y + 1)
                    if cell_display is None or cell_display == '':
                        cell_display = "-"
                    cell_display = str(cell_display).strip()
                    if len(cell_display) > self.max_cell_length:
                        cell_display = cell_display[:self.max_cell_length - 3]
                        cell_display = cell_display + "..."
                    cell_display = f" {cell_display:^{min(self.table.max_len(x + 1), self.max_cell_length)}} "
                    if pointer.column_number == x + 1 and pointer.row == y + 1:
                        table_pad.addstr(y - y_shift, x_display, cell_display, curses.A_BLINK)
                    else:
                        table_pad.addstr(y - y_shift, x_display, cell_display)
                    x_display = x_display + min(self.table.max_len(x + 1), self.max_cell_length) + 2
                    table_pad.addstr(y - y_shift, x_display, '|')
                    x_display += 1
                    if x_display < width - 3 and tables.get_column(x + 1) not in shown_collumns:
                        shown_collumns.append(tables.get_column(x + 1))
                if y < height - 3 + y_shift:
                    shown_rows.append(y + 1)
            table_pad.noutrefresh(0, 0, 1, row_width, height - 3, width - 2)

        def update_indicator():
            indicator_win = curses.newwin(height - 2, 2, 1, width - 1)
            indicators = ''
            if self.info.alert:
                indicators += self.info.alert
            indicators += get_quoting_ind(self.table.dialect.quoting)
            indicators = f"{indicators:<{height - 3}}"
            for index, symbol in enumerate(indicators):
                indicator_win.addstr(index, 0, symbol, curses.A_REVERSE)
            if self.read_only:
                indicator_win.addstr(height - 3, 0, "R", curses.A_REVERSE + curses.A_UNDERLINE)
            else:
                indicator_win.addstr(height - 3, 0, self.info.mode, curses.A_REVERSE)
            indicator_win.noutrefresh()

        def update_columns():
            column_pad = curses.newpad(1, max(self.table_width + 2, width - 1))
            x_display = 0
            for x in range(self.table.column_count - x_shift):
                x = x + x_shift
                colum_len = min(self.table.max_len(x + 1), self.max_cell_length)
                column_name = f" {str(tables.get_column(x + 1)):^{colum_len}} |"
                column_pad.addstr(0, x_display, column_name, curses.A_REVERSE)
                x_display = x_display + colum_len + 3
            if x_display < width - 2:
                column_spacer = ' ' * ((width - 2) - x_display)
                column_pad.addstr(0, x_display, column_spacer, curses.A_REVERSE)
            column_pad.noutrefresh(0, 0, 0, row_width, 0, width - 2)

        def update_rows():
            row_pad = curses.newpad(max(self.table_height, height - 2), row_width)
            for y in range(self.table.row_count - y_shift):
                y = y + y_shift
                row_pad.addstr(y - y_shift, 0, f"{str(y + 1):^{row_width}}", curses.A_REVERSE)
            if y + 1 < height - 3:
                row_spacer  = ' '
                for i in range(y + 1, height - 3):
                    row_pad.addstr(i, 0, f"{row_spacer:^{row_width}}", curses.A_REVERSE)
            row_pad.noutrefresh(0, 0, 1, 0, height - 3, row_width)

        def update_x():
            x_win = curses.newwin(1, row_width, 0, 0)
            if x_shift > 0 and y_shift > 0:
                x_win.insstr(0, 0, f"{'X':^{row_width}}", curses.A_REVERSE)
            elif x_shift > 0:
                x_win.insstr(0, 0, f"{'<':^{row_width}}", curses.A_REVERSE)
            elif y_shift > 0:
                x_win.insstr(0, 0, f"{'^':^{row_width}}", curses.A_REVERSE)
            else:
                x_win.insstr(0, 0, f"{' ':^{row_width}}", curses.A_REVERSE)
            x_win.noutrefresh()

        def update_v():
            v_win = curses.newwin(1, row_width, height - 2, 0)
            if shown_rows[-1] != self.table.row_count:
                v_win.insstr(0, 0, f"{'V':^{row_width}}", curses.A_REVERSE)
            else:
                v_win.insstr(0, 0, f"{' ':^{row_width}}", curses.A_REVERSE)
            v_win.noutrefresh()

        def update_r():
            r_win = curses.newwin(1, 2, 0, width - 1)
            if shown_collumns[-1] != tables.get_column(self.table.column_count):
                r_win.insstr(0, 0, ">", curses.A_REVERSE)
            else:
                r_win.insstr(0, 0, " ", curses.A_REVERSE)
            r_win.noutrefresh()

        def update_input():
            nonlocal input_win

            input_length = width - 2 - len(address)
            cell_pad = curses.newpad(1, input_length + 1)
            input_win = curses.newwin(1, input_length, height - 1, 2)
            cell_pad.erase()
            value = str(self.table.get_cell(pointer.column, pointer.row))
            value = f"> {value}"
            if len(value) > input_length:
                value = value[:input_length - 3] + "..."
            cell_pad.addstr(0, 0, value)
            cell_pad.noutrefresh(0, 0, height - 1, 0, height - 1, input_length)

        def update_address():
            address = f"({pointer.column:>3}:{pointer.row:<3})"
            address_win = curses.newwin(1, len(address), height - 1, width - len(address))
            address_win.insstr(0, 0, address, curses.A_REVERSE)
            address_win.noutrefresh()

        def update_all():
            scr.clear()
            update_table()
            update_x()
            update_v()
            update_r()
            update_info()
            update_columns()
            update_rows()
            update_input()
            update_address()
            update_indicator()
            curses.flash()

        def move(direction: str = None, repeat: int = 1):
            nonlocal x_shift, y_shift

            match direction:
                case 'up' if pointer.row > 1:
                    for _ in range(repeat):
                        pointer.up()
                        if pointer.row not in shown_rows:
                            y_shift -= 1
                case 'down' if pointer.row < self.table.row_count:
                    for _ in range(repeat):
                        pointer.down()
                        if pointer.row not in shown_rows:
                            y_shift += 1
                case 'left' if pointer.column_number > 1:
                    for _ in range(repeat):
                        pointer.left()
                        if pointer.column not in shown_collumns:
                            x_shift -= 1
                case 'right' if pointer.column_number < self.table.column_count:
                    for _ in range(repeat):
                        pointer.right()
                        if pointer.column not in shown_collumns:
                            x_shift += 1
            update_table()
            update_r()
            update_v()
            update_x()
            update_columns()
            update_rows()
            update_input()
            update_address()

        update_all()
        curses.doupdate()

        key_pad.keypad(True)

        while True:
            user_input = key_pad.getch()
            height, width = scr.getmaxyx()
            match user_input:
                case visuals.KEY_F5.code:
                    update_all()
                case visuals.KEY_Q.code:
                    if changes:
                        answer = show_prompt("Do you want to save changes to the file?")
                        if answer is True:
                            result = 2
                            while result == 2:
                                result = save_as()
                            if result == 1:
                                break
                        if answer is False:
                            break
                    else:
                        break
                case visuals.KEY_S.code:
                    save_as()
                    changes = False
                case curses.KEY_RESIZE:
                    height, width = scr.getmaxyx()
                    update_all()
                case curses.KEY_UP:
                    move('up')
                case curses.KEY_DOWN:
                    move('down')
                case curses.KEY_LEFT:
                    move('left')
                case curses.KEY_RIGHT:
                    move('right')
                case curses.KEY_HOME | curses.KEY_SHOME:
                    move('left', pointer.column_number - 1)
                case curses.KEY_END | curses.KEY_SEND:
                    move('right', self.table.column_count - pointer.column_number)
                case visuals.KEY_PGUP.code:
                    move('up', pointer.row - 1)
                case visuals.KEY_PGDN.code:
                    move('down', self.table.row_count - pointer.row)
                case 27:
                    user_input2 = key_pad.getch()
                    match user_input2:
                        case visuals.KEY_C.code:
                            pyperclip.copy(self.table.get_cell(pointer.column, pointer.row))
                        case visuals.KEY_V.code if not self.read_only:
                            changes = True
                            self.table.set_cell(pointer.column,
                                                pointer.row,
                                                clean(pyperclip.paste()))
                            move()
                        case visuals.KEY_X.code if not self.read_only:
                            changes = True
                            pyperclip.copy(self.table.get_cell(pointer.column, pointer.row))
                            self.table.set_cell(pointer.column, pointer.row, None)
                            move()
            if not self.read_only:
                match user_input:
                    case curses.KEY_ENTER | 10 | 13 if self.info.mode == 'R':
                        self.info.mode = 'E'
                        self.info.set_message(self.key_hint["confirm"] + self.key_hint["cancel"],
                                              True)
                        update_info()
                        update_indicator()
                        update_input()
                        update_address()
                        value = self.table.get_cell(pointer.column, pointer.row)
                        value = inputfield.get_input(input_win, value)
                        self.table.set_cell(pointer.column, pointer.row, value)
                        changes = True
                        self.info.reset_messsage()
                        self.info.mode = 'R'
                        update_all()
                    case visuals.KEY_DELETE.code:
                        self.table.set_cell(pointer.column, pointer.row, None)
                        changes = True
                        move()
                    case visuals.KEY_C.code:
                        self.table.insert_column(pointer.column_number)
                        changes = True
                        update_table_size()
                        update_table()
                        move('right')
                    case visuals.KEY_V.code:
                        self.table.insert_row(pointer.row)
                        changes = True
                        update_table_size()
                        update_table()
                        move('down')
                    case visuals.KEY_SC.code:
                        self.table.insert_column(pointer.column_number - 1)
                        changes = True
                        update_table_size()
                        update_table()
                        move()
                    case visuals.KEY_SV.code:
                        self.table.insert_row(pointer.row - 1)
                        changes = True
                        update_table_size()
                        update_table()
                        move()
                    case visuals.KEY_X.code if self.table.column_is_empty(pointer.column) \
                        or show_prompt(f"Remove column {pointer.column}? "):
                        if self.table.column_count == 2:
                            self.table.insert_column(pointer.column_number + 1)
                        self.table.remove_column(pointer.column_number)
                        changes = True
                        update_table_size()
                        update_table()
                        move('left')
                    case visuals.KEY_Z.code if self.table.row_is_empty(pointer.row) \
                        or show_prompt(f"Remove row {pointer.row}? "):
                        if self.table.row_count == 1:
                            self.table.insert_row(pointer.row + 1)
                        self.table.remove_row(pointer.row)
                        changes = True
                        update_table_size()
                        update_table()
                        move('up')
                    case visuals.KEY_SX.code:
                        if self.table.column_count == 2:
                            self.table.insert_column(pointer.column_number + 1)
                        self.table.remove_column(pointer.column_number)
                        changes = True
                        update_table_size()
                        update_table()
                        move('left')
                    case visuals.KEY_SZ.code:
                        if self.table.row_count == 1:
                            self.table.insert_row(pointer.row + 1)
                        self.table.remove_row(pointer.row)
                        changes = True
                        update_table_size()
                        update_table()
                        move('up')
            curses.doupdate()

def start(**kwargs):
    """
    Starts the editor
    """

    file_name = kwargs.get("filename")
    temp_file = kwargs.get("temp_file")

    key_hint = {'edit':    f' {visuals.KEY_ENTER.text}:edit',
                'confirm': f' {visuals.KEY_ENTER.text}:confirm',
                'quit':    f' {visuals.KEY_Q.text}:quit',
                'cancel':  f' {visuals.KEY_ESC.text}:cancel',
                'update':  f' {visuals.KEY_F5.text}:update',
                }

    table = tables.file_open(file_name)

    editor = Editor(key_hint=key_hint,
                    max_cell_len=kwargs.get("cell_size"),
                    table=table,
                    absolute_path=kwargs.get("absolute_path"),
                    read_only=kwargs.get("read_only"),
                    new_file=kwargs.get("new_file"))

    try:
        curses.wrapper(editor.edit)
    except Exception as exception:
        tables.file_save(table, temp_file)
        raise exception
    if os.path.exists(temp_file):
        os.remove(temp_file)
