def update_canvas(canvas, force_update=False):
    '''Update the scrollable area after its size changes.'''
    if force_update or canvas.bbox("all") != canvas.bbox("view"):
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))