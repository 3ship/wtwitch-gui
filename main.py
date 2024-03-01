import subprocess
import re
import tkinter as tk

def call_wtwitch():
    wtwitch_c = subprocess.run(['wtwitch', 'c'],
                               capture_output=True, text=True)
    #print(repr(wtwitch_c.stdout))
    off_streamers1 = re.findall('\[90m(\S*)\x1b', wtwitch_c.stdout)
    off_streamers2 = re.findall('\[90m(\S*),', wtwitch_c.stdout)
    offline_streamers = off_streamers1 + off_streamers2
    offline_streamers.sort()
    online_streamers = re.findall('\[92m(\S*)\x1b', wtwitch_c.stdout)
    return online_streamers, offline_streamers

def check_status():
    global status
    status = call_wtwitch()

def fetch_vods(streamer):
    wtwitch_v = subprocess.run(['wtwitch', 'v', streamer],
                               capture_output=True, text=True
                               )
    timestamps = re.findall('\[96m\[(\S* \S*)\]', wtwitch_v.stdout)
    titles = re.findall('\]\x1b\[0m\s*(\S.*)\s\x1b\[93m', wtwitch_v.stdout)
    for i in range(len(titles)):
        if len(titles[i]) > 70:
            titles[i] = titles[i][:70] + "..."
    return timestamps, titles

def button_clicked():
    showinfo(
        title="Info",
        message="Opening player"
        )

def vod_window(streamer):
    vods = fetch_vods(streamer)
    window = tk.Toplevel()
    window.title(f"{streamer}'s VODs")
    vframe = tk.Frame(window, padx=15, pady=15)
    vframe.grid()
    if len(vods[0]) == 0:
        warning_l = tk.Label(vframe, text=f"{streamer} has no VODs")
        warning_l.grid(column=0, row=0, ipadx=10, ipady=10)
    vodno = 1
    for timestamp in vods[0]:
        time_l = tk.Label(vframe, text=timestamp)
        time_l.grid(column=0, row=vodno, sticky='w', ipadx=8, ipady=5)
        vodno += 1
    vodno = 1
    for title in vods[1]:
        watch_b = tk.Button(vframe,
                      text="Watch",
                      command=lambda s=streamer, vodno=vodno:
                      [subprocess.run(['wtwitch', 'v', s, str(vodno)]),
                      button_clicked()]
                    )
        watch_b.grid(column=1, row=vodno, ipadx=12)
        vodno += 1
    vodno = 1
    for title in vods[1]:
        title_l = tk.Label(vframe, text=title)
        title_l.grid(column=2, row=vodno, sticky='w', ipadx=8)
        vodno += 1

def main_window(root):
    mainframe = tk.Frame(root)
    mainframe.pack(ipady=10, ipadx=10)
    # Create a refresh button:
    refresh = tk.Button(mainframe,
                        text="Refresh",
                        command=lambda root=root:
                                    [check_status(),
                                    main_window(root),
                                    mainframe.pack_forget(),
                                    mainframe.destroy()]
                        )
    refresh.pack(fill='x', side='top')
    #
    # Create section of online streamers with 'watch' and VOD buttons:
    #
    topframe = tk.Frame(mainframe)
    topframe.pack(side='top', fill='x')
    # Label:
    on_l = tk.Label(topframe, text="Online: ")
    on_l.pack(ipady=5)
    # Online streamer buttons:
    online_streamers = tk.Frame(topframe, padx=10, pady=10)
    online_streamers.pack(side='left')
    for streamer in status[0]:
        watch_b = tk.Button(online_streamers,
                      text=streamer,
                      command=lambda s=streamer:
                      [subprocess.run(['wtwitch', 'w', s]),
                      button_clicked()]
                      )
        watch_b.pack(fill='x', side='top')
    # VOD Buttons for online streamers:
    online_vods = tk.Frame(topframe, padx=10, pady=10)
    online_vods.pack(side='right')
    for streamer in status[0]:
        vods = tk.Button(online_vods,
                        text="Vods",
                        command=lambda s=streamer: vod_window(s)
                        )
        vods.pack(side='top')
    #
    # Create offline streamer section with VOD buttons:
    #
    bottomframe = tk.Frame(mainframe)
    bottomframe.pack(side='bottom', fill='x')
    # Label:
    off_l = tk.Label(bottomframe, text="Offline: ")
    off_l.pack()
    # Offline streamer buttons (deactivated):
    offline_streamers = tk.Frame(bottomframe, padx=10, pady=10)
    offline_streamers.pack(side='left')
    for streamer in status[1]:
        streamer_l = tk.Button(offline_streamers,
                                text=streamer,
                                state='disabled'
                                )
        streamer_l.pack(fill='x', side='top')
    # VOD Buttons for offline streamers:
    offlineframe2 = tk.Frame(bottomframe, padx=10, pady=10)
    offlineframe2.pack(side='right')
    for streamer in status[1]:
        ovods = tk.Button(offlineframe2,
                        text="Vods",
                        command=lambda s=streamer: vod_window(s)
                        )
        ovods.pack(side='top')


# Check the online/offline status once before window initialization:
status = call_wtwitch()
# Create the main window
root = tk.Tk()
root.title("wtwitch-gui")
main_window(root)
root.mainloop()
