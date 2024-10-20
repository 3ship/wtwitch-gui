import assets
import refresh
from tkinter import messagebox

def error_message(e):
    messagebox.showerror(title='Error',
                        message=f'{e}\n\n Check your internet connection!',
                        )

def askyesno(frame, canvas, prompt, row):
    global current_yesno_frame
    if current_yesno_frame is not None:
        current_yesno_frame.destroy()
        current_yesno_frame = None

    def on_yes(event=None):
        nonlocal response
        response = True
        askyesno_frame.destroy()

    def on_no():
        nonlocal response
        response = False
        askyesno_frame.destroy()

    askyesno_frame = assets.default_frame(frame)
    askyesno_frame.grid(row=row, column=0, columnspan=5)
    current_yesno_frame = askyesno_frame

    label = assets.default_label(askyesno_frame, text=prompt)
    label.grid(row=0, column=0, padx=6, sticky='ew', columnspan=2)

    yes_button = assets.default_button(askyesno_frame, text="Yes", command=on_yes)
    yes_button.grid(row=2, column=0, sticky='ew', pady=6)

    no_button = assets.default_button(askyesno_frame, text="No", command=on_no)
    no_button.grid(row=2, column=1, sticky='ew')
    refresh.update_canvas(canvas)
    response = None
    askyesno_frame.wait_window()
    refresh.update_canvas(canvas)
    return response


def askstring(frame, canvas, prompt, initial_value=""):
    global current_query_frame
    if current_query_frame is not None and current_query_frame.master == frame:
        current_query_frame.destroy()
        current_query_frame = None

    def on_submit(event=None):
        nonlocal response
        response = entry.get()
        askstring_frame.destroy()

    def on_cancel():
        nonlocal response
        response = None
        askstring_frame.destroy()

    askstring_frame = assets.default_frame(frame)
    askstring_frame.grid(row=1, column=0, columnspan=5)
    current_query_frame = askstring_frame
    label = assets.default_label(askstring_frame, text=prompt)
    label.grid(row=0, column=0, padx=6, sticky='ew', columnspan=2)
    entry = assets.default_entry(askstring_frame)
    entry.grid(row=1, column=0, padx=6, pady=4, columnspan=2)
    entry.bind("<Return>", on_submit)
    entry.insert(0, initial_value)
    entry.focus_set()
    cancel_button = assets.default_button(askstring_frame,
                                    text="Cancel",
                                    command=on_cancel
                                    )
    cancel_button.grid(row=2, column=0, sticky='ew', pady=6)
    submit_button = assets.default_button(askstring_frame,
                                    text="Enter",
                                    command=on_submit
                                    )
    submit_button.grid(row=2, column=1, sticky='ew')
    refresh.update_canvas(canvas)
    response = None
    askstring_frame.wait_window()
    return response

current_yesno_frame = None
current_query_frame = None