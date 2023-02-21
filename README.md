# CSVEdit

CSVEdit is a terminal spreadsheet-like CSV file editor.

Written in python using curses library.

## Platform requirements

- Linux or Windows with WSL
- Python 3.7+
- pyperclip

## Installation

Since the project is not currently finished, there is no way to properly install it yet.
To try it out, you can download the project's files from GitHub and use it straight from the folder.

You might also need to allow the scripts to execute before using them:

Editor:

```bash
chmod +x interface.py
```

CSV file generator:

```bash
chmod +x csvgen.py
```

## Usage

You can open a csv file in the editor using interface.py from the command line:

```bash
./interface.py example_file.csv
```

The optional arguments are:

- `-h --help` - shows the usage
- `-n --new` - creates a new file instead of exiting with an error when trying to open a file that does not exist

## Editor keybinds

| Key        | Action                                  |
| ---------- | --------------------------------------- |
| q          | Exit the editor                         |
| s          | Save the current file as                |
| arrow keys | Navigate the table                      |
| home       | Jump to the first cell in the row       |
| end        | Jump to the last cell in the row        |
| PgUp       | Jump to the top of the column           |
| PgDn       | Jump to the bottom of the column        |
| enter      | Edit the current cell / Confirm changes |
| esc        | Cancel action / Discard changes         |
| delete     | Delete contents of the current cell     |
| c          | Add an empty column to the right        |
| C          | Add an empty column to the left         |
| v          | Add an empty row to the bottom          |
| V          | Add an empty row to the top             |
| Alt + c    | Copy cell contents to clipboard         |
| Alt + v    | Paste clipboard contents to the cell    |
| Alt + x    | Cut cell contents                       |
