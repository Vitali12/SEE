
import tkinter as tk
from tkinter import ttk

def create_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.withdraw()  # Скрываем окно подсказки
    tooltip.overrideredirect(True)  # Убираем оконные элементы управления
    tooltip_label = ttk.Label(tooltip, text=text, relief='solid', background='lightyellow')
    tooltip_label.pack()

    def show_tooltip(event):
        tooltip.geometry(f"+{event.x_root + 20}+{event.y_root + 10}")
        tooltip.deiconify()

    def hide_tooltip(event):
        tooltip.withdraw()

    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)

root = tk.Tk()
button = ttk.Button(root, text="Наведи на меня")
button.pack(pady=20)

create_tooltip(button, "Это всплывающая подсказка")

root.mainloop()