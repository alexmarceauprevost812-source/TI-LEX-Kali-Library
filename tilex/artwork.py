"""Original vector-style pictograms drawn locally, without image downloads."""
import tkinter as tk


def pictogram(parent, command, fallback='🐉', background='#182229'):
    canvas = tk.Canvas(parent, width=88, height=68, bg=background, highlightthickness=0)
    blue = '#61c5ff'
    if command == 'nmap':
        canvas.create_polygon(5, 34, 23, 14, 44, 8, 65, 14, 83, 34, 65, 53, 44, 60, 23, 53,
                             fill='', outline=blue, width=5, smooth=True)
        canvas.create_oval(25, 14, 63, 54, fill='#bedfff', outline=blue, width=3)
        canvas.create_oval(34, 23, 54, 47, fill='#193b55', outline='')
        canvas.create_oval(35, 24, 43, 32, fill='white', outline='')
    elif command == 'wireshark':
        canvas.create_polygon(9, 60, 23, 35, 45, 14, 72, 5, 56, 29, 54, 59,
                             fill='#0686e6', outline=blue, width=3, smooth=True)
    elif command in ('tcpdump', 'tshark'):
        canvas.create_line(6, 38, 20, 38, 26, 23, 35, 53, 44, 8, 51, 43, 59, 30, 67, 38, 83, 38,
                           fill='#d2e8f6', width=5, joinstyle='round')
    elif command == 'lynis':
        canvas.create_polygon(44, 6, 75, 18, 70, 42, 59, 55, 44, 64, 29, 55, 18, 42, 13, 18,
                             fill='', outline='#b7c4d0', width=5)
    elif command == 'git':
        canvas.create_polygon(44, 4, 78, 34, 44, 65, 10, 34, fill='#f05232', outline='')
        canvas.create_line(31, 19, 56, 42, fill=background, width=5)
        canvas.create_line(42, 29, 42, 53, fill=background, width=5)
        for x, y in ((31, 19), (56, 42), (42, 53)):
            canvas.create_oval(x-5, y-5, x+5, y+5, fill=background, outline='')
    elif command == 'python3':
        canvas.create_polygon(25, 6, 55, 6, 61, 14, 61, 34, 29, 34, 29, 44, 12, 44, 12, 22, 25, 22,
                             fill='#3686b9', smooth=True)
        canvas.create_polygon(63, 61, 33, 61, 27, 53, 27, 34, 59, 34, 59, 24, 76, 24, 76, 46, 63, 46,
                             fill='#ffd84d', smooth=True)
        canvas.create_oval(35, 12, 40, 17, fill='white', outline='')
        canvas.create_oval(49, 50, 54, 55, fill=background, outline='')
    else:
        canvas.create_text(44, 34, text=fallback, fill=blue, font=('DejaVu Sans', 30))
    return canvas
