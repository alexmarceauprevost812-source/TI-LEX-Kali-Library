#!/usr/bin/env python3
"""Graphical launcher; the terminal launcher remains main.py."""
try:
    from tilex.gui import main
except ModuleNotFoundError as exc:
    if exc.name not in ('tkinter', '_tkinter'):
        raise
    print('Tkinter absent. Kali : sudo apt install python3-tk ; Termux : pkg install python-tkinter. Sous Windows, installer le composant Tcl/Tk de Python.')
    raise SystemExit(1)

if __name__ == '__main__':
    raise SystemExit(main())
