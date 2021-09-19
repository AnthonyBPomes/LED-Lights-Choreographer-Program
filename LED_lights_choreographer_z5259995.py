from tkinter import *
from numpy.lib.npyio import save
from pygame import mixer
import time
import tkinter.filedialog
import tkinter.messagebox
from PIL import ImageColor
from colorsys import rgb_to_hsv, hsv_to_rgb
import operator
import json

import serial

import numpy
from math import floor
from pydub import AudioSegment
from numpy import frombuffer, fromstring

mixer.init()

def timeline_slide(val):
    if isImporting:
        scroll_button_press([val,False])
    else:
        scroll_button_press([val,True])

def volume_control(val):
    mixer.music.set_volume(float(val)/100)

def save_to_json():
    if hasImported:
        file = tkinter.filedialog.asksaveasfile(filetypes=[('JSON', '*.json')],defaultextension = [('JSON', '*.json')]).name
        with open(file, 'w') as outfile:
            json.dump(light_sequence_list_for_output,outfile)
    else:
        tkinter.messagebox.showerror('ERROR','You must import an MP3 first')

def load_json():
    global sequence_speed, brightness_value
    if hasImported:
        file = tkinter.filedialog.askopenfilename()
        with open(file, 'r') as myfile:
            data=myfile.read()
        imported_list = json.loads(data)

        delete_all_markers.invoke()
        
        for marker in imported_list:
            button_press(marker['marker_colour'])
            slider.set(marker['frame'])
            root.update()
            timeline_slide(slider.get())
            sequence_speed = marker['speed']
            brightness_value = marker['brightness']
            mark_frame_button.invoke()
    else:
        tkinter.messagebox.showerror('ERROR','You must import an MP3 first')


isImporting = False
hasImported = False
def import_mp3():
    global hasImported, isImporting
    if hasImported:
        pause_sequence.invoke()
    name = tkinter.filedialog.askopenfilename()
    if not name:
        return None
    hasImported = True
    sound = AudioSegment.from_mp3(name)
    raw_data = sound.raw_data
    new_data = fromstring(raw_data, dtype=numpy.int16)
    mixer.music.load(name)
    test_music = mixer.Sound(name)
    song_length = round(test_music.get_length() * 5)
    slider.configure(to=song_length)
    isImporting = True
    waveform_gen(song_length,new_data)
    isImporting = False

# Test the send_to_arduino function by commenting out arduino variables

def send_to_arduino():
    if hasImported:
        try:
            #True
            arduino = serial.Serial(port='COM5', baudrate=9600, timeout=.1)
        except:
            tkinter.messagebox.showerror("ERROR", "Arduino port not found.")
            return None
        slider.set(0)
        play_sequence.invoke()
        for index, marker in enumerate(light_sequence_list_for_output):
            if index == 0:
                time_diff = (marker['frame'] / 5)
            else:
                time_diff = (marker['frame'] - light_sequence_list_for_output[index-1]['frame']) / 5
            time.sleep(time_diff)
            arduino.write(bytes(marker['marker_colour'], 'utf-8'))
            print(marker['marker_colour'])
    else:
        tkinter.messagebox.showerror('ERROR','You must import an MP3 first')

LED_remote_button_layout = [
    {'BRIGHT UP/\nSPEED UP': 'white','BRIGHT DOWN/\nSPEED DOWN': 'white', 'OFF/BLACK': 'black', 'ON/\nPREVIOUS COLOUR': 'mistyrose'},
    {'RED': '#FF0000', 'GREEN': '#008000', 'BLUE': '#0000FF', 'WHITE': '#FFFFFF'},
    {'DARK ORANGE': '#FF4500','LIME': '#32CD32','LIGHT BLUE': '#1E90FF','FLASH': "gray"},
    {'ORANGE': "#FF8C00", 'AQUA': '#20B2AA', 'INDIGO': '#4B0082', 'STROBE': 'gray'},
    {'LIGHT ORANGE': '#FFA500', 'DARK AQUA': '#008B8B', 'PURPLE': '#800080', 'FADE': 'gray'},
    {'YELLOW': '#FFFF00', 'TEAL': '#008080', 'VIOLET': '#9400D3', 'SMOOTH': 'gray'}
]

root = Tk()
root.geometry('800x820')
root.resizable(False, False)
root.title("LED Lights Choreographer")

menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=load_json)
filemenu.add_command(label="Save", command=save_to_json)
filemenu.add_command(label="Output to Arduino", command=send_to_arduino)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

root.config(menu=menubar)

i = 0
j = 0
k = 0

header = Frame(master=root,width=600,height=300)
header.pack()

colour_display_frame = Frame(master=header,width=200,height=200,bg="black")
colour_display_frame.pack(side=LEFT)

info_frame = Canvas(master=header,width=200,height=200,bg="white")
info_frame_col_id = info_frame.create_text(100,60,text="Colour: OFF/BLACK")
info_frame_nom_id = info_frame.create_text(100,90,text="Frame: 0")
info_frame_strobe_id = info_frame.create_text(100,120,text="Strobe Speed: 0.5 Seconds")
info_frame_bright_id = info_frame.create_text(100,150,text="Brightness Value: Level 7")
info_frame.pack(side=RIGHT)

slider = Scale(master=root,from_=0,to=0,orient=HORIZONTAL,length=500,width=150, command=timeline_slide, sliderlength=20)

slider.pack()

marker_frame = Frame(master=root,width=300,height=300)
marker_frame.pack()

scroll_button_frame = Frame(master=root,width=300,height=300)
scroll_button_frame.pack()

g = Frame(master=root,width=500,height=100,bg='brown')
g.pack()
g.place(x=150,y=223)

h = Frame(master=root,width=1,height=100,bg='black')
h.pack()
h.place(x=160,y=223)
root.update()

data_sample_counter = 0

go_next_marker_button = Button(master=marker_frame,text='NEXT\nMARKER',width=7,height=2,command=lambda m=['NEXT',True] : scroll_button_press(m))
go_next_marker_button.pack(side=RIGHT)

go_frame_forward_button = Button(master=marker_frame,text='->',width=5,height=2,command=lambda m=['->',True] : scroll_button_press(m))
go_frame_forward_button.pack(side=RIGHT)

mark_frame_button = Button(master=marker_frame,text='MARK\nFRAME',width=5,height=2,command=lambda m=['M',True] : scroll_button_press(m))
mark_frame_button.pack(side=RIGHT)

go_frame_backward_button = Button(master=marker_frame,text='<-',width=5,height=2,command=lambda m=['<-',True] : scroll_button_press(m))
go_frame_backward_button.pack(side=RIGHT)

go_prev_marker_button = Button(master=marker_frame,text='PREV\nMARKER',width=7,height=2,command=lambda m=['PREV',True] : scroll_button_press(m))
go_prev_marker_button.pack(side=RIGHT)

delete_all_markers = Button(master=scroll_button_frame,text='DELETE ALL MARKERS',command=lambda m=['DELALL',True] : scroll_button_press(m))
delete_all_markers.pack(side=RIGHT)

delete_marker = Button(master=scroll_button_frame,text='DELETE MARKER',command=lambda m=['DEL',True] : scroll_button_press(m))
delete_marker.pack(side=RIGHT)

play_sequence = Button(master=scroll_button_frame,text='PLAY SEQUENCE',command=lambda m=['PLAY',True] : scroll_button_press(m))
play_sequence.pack(side=RIGHT)

pause_sequence = Button(master=scroll_button_frame,text='PAUSE',command=lambda m=['PAUSE',True] : scroll_button_press(m))
pause_sequence.pack()

volume_label = Label(text='\nVolume')
volume_label.pack()

volume_slider = Scale(master=root,from_=0,to=100,orient=HORIZONTAL,length=150,width=10, command=volume_control)
volume_slider.set(50)
volume_slider.pack()

open_file = Button(master=root,text='Import .MP3',command=import_mp3)
open_file.pack()

button_frame = Frame(master=root)

prev_pressed_button = ()
curr_pressed_button = ()
prev_scroll_pos = slider.coords(value=None)[0]

light_sequence_list = []
light_sequence_list_for_output = []

is_playing = False

marker_jump = 0

flash_seq_colours = ('red','green','blue', 'yellow', 'purple', 'cyan', 'white')
flash_seq_running = False
fade_seq_colours = ('red','green','blue')
fade_seq_running = False
strobe_seq_colours = ('white', 'black')
strobe_seq_running = False
#smooth_seq_colours = {'#ff0000': [255,0,0], '#ffff00': [255,255,0], '#00ff00': [0,255,0], '#00ffff': [0,255,255], '#0000ff': [0,0,255], '#ff00ff': [255,0,255]}
smooth_seq_running = False
    
def scroll_button_press(scroll_button_info):
    global prev_scroll_pos, marker_jump, music_pos, sequence_speed, brightness_value
    if isImporting and scroll_button_info[1]:
        tkinter.messagebox.showerror('ERROR','MP3 is importing, wait until finished')
        return None

    if hasImported:
        if scroll_button_info[0] == '->':
            if slider.get() != slider.cget('to'):
                slider.set(slider.get()+1)
                
                if slider.get() == slider.cget('to'):
                    if isImporting:
                        return None
                    pause_sequence.invoke()

            for marker in light_sequence_list:
                if slider.get() == marker['frame']:
                    sequence_speed = marker['speed']
                    brightness_value = marker['brightness']
                    button_press(marker['marker_colour'])
                    update_status()

        elif scroll_button_info[0] == "<-":
            if slider.get():
                slider.set(slider.get()-1)

            for marker in light_sequence_list:
                if slider.get() == marker['frame']:
                    sequence_speed = marker['speed']
                    brightness_value = marker['brightness']
                    button_press(marker['marker_colour'])
                    update_status()

        elif scroll_button_info[0] == "NEXT":
            for marker in light_sequence_list:
                if slider.get() < marker['frame']:
                    slider.set(marker['frame'])
                    sequence_speed = marker['speed']
                    brightness_value = marker['brightness']
                    button_press(marker['marker_colour'])
                    update_status()
                    break

        elif scroll_button_info[0] == "PREV":
            for marker in reversed(light_sequence_list):
                if slider.get() > marker['frame']:
                    slider.set(marker['frame'])
                    sequence_speed = marker['speed']
                    brightness_value = marker['brightness']
                    button_press(marker['marker_colour'])
                    update_status()
                    break
                        
        elif scroll_button_info[0] == "M":
            if curr_pressed_button[0] != 'BRIGHT UP/\nSPEED UP' and curr_pressed_button[0] != 'BRIGHT DOWN/\nSPEED DOWN':
                marker_color = Frame(master=root,width=1,height=100,bg=curr_pressed_button[1])
            else:    
                marker_color = Frame(master=root,width=1,height=100,bg=prev_pressed_button[1])
            marker_color.place(x=h.winfo_x(),y=223)
            sequence_speed_marker = sequence_speed
            brightness_value_marker = brightness_value
            light_sequence_list.append(
                {'marker_ref': marker_color,
                'marker_colour': prev_pressed_button if curr_pressed_button[1] != 'black' else curr_pressed_button,
                'frame': slider.get(),
                'speed': sequence_speed_marker,
                'brightness': brightness_value_marker
                }
            )
            light_sequence_list_for_output.append(
                {
                'marker_colour': prev_pressed_button if curr_pressed_button[1] != 'black' else curr_pressed_button,
                'frame': slider.get(),
                'speed': sequence_speed_marker,
                'brightness': brightness_value_marker
                }
            )
            light_sequence_list.sort(key=operator.itemgetter('frame'))
            light_sequence_list_for_output.sort(key=operator.itemgetter('frame'))

        elif scroll_button_info[0] == "DEL":
            for marker in light_sequence_list:
                if slider.get() == marker['frame']:
                    marker['marker_ref'].destroy()
                    light_sequence_list.remove(marker)

        elif scroll_button_info[0] == "DELALL":
            if len(light_sequence_list) and tkinter.messagebox.askyesno('Delete All Markers', "Are you sure you want to delete all markers? This cannot be undone"):
                for marker in light_sequence_list:
                    marker['marker_ref'].destroy()
                light_sequence_list.clear()

        elif scroll_button_info[0] == "PLAY" and not is_playing:
            playback_sequence_play()
            mixer.music.play(0,start=slider.get() / 5)

        elif scroll_button_info[0] == "PAUSE" and is_playing:
            playback_sequence_pause()
            mixer.music.stop()

        else:
           marker_jump = slider.coords(value=scroll_button_info[0])[0] - prev_scroll_pos
           h.place(x=h.winfo_x()+marker_jump)
           prev_scroll_pos = slider.coords(value=scroll_button_info[0])[0]
           update_status()
    else:
        tkinter.messagebox.showerror('ERROR','You must import an MP3 first')

def playback_sequence_play():
    global player_sequence_job, is_playing
    if not is_playing:
        is_playing = True
    go_frame_forward_button.invoke()
    if slider.get() != slider.cget('to'):
        player_sequence_job = root.after(200,playback_sequence_play)

def playback_sequence_pause():
    global player_sequence_job, is_playing
    root.after_cancel(player_sequence_job)
    is_playing = False

def button_press(button_info):
    global prev_pressed_button, curr_pressed_button, fade_seq_running, strobe_seq_running, flash_seq_running, smooth_seq_running
    curr_pressed_button = button_info
    if '#' in curr_pressed_button[1]:
        temp_button = f'{button_info[1]}'
        temp_button_new = brightness_func(temp_button)
    if curr_pressed_button[0] == 'OFF/BLACK':
        colour_display_frame.configure(background=curr_pressed_button[1])
        try:
            colour_display_frame.after_cancel(colour_display_frame.after_id)
        except:
            pass

    if curr_pressed_button[0] != 'BRIGHT DOWN/\nSPEED DOWN' and curr_pressed_button[0] != "BRIGHT UP/\nSPEED UP" and curr_pressed_button[0] != 'ON/\nPREVIOUS COLOUR' and curr_pressed_button[0] != 'OFF/BLACK':
        prev_pressed_button = curr_pressed_button

    if button_info[0] == "FADE":
        fade_seq_running = True
        fade_seq()
    elif button_info[0] == "SMOOTH":
        smooth_seq_running = True
        smooth_seq()
    elif button_info[0] == "STROBE":
        strobe_seq_running = True
        strobe_seq()
    elif button_info[0] == "FLASH":
        flash_seq_running = True
        flash_seq()
    elif button_info[0] == "BRIGHT DOWN/\nSPEED DOWN":
        if prev_pressed_button[1] == 'gray':
            seq_speed_change('slow')
        else:
            brightness_change('down')
            button_press(prev_pressed_button)
    elif button_info[0] == "BRIGHT UP/\nSPEED UP":
        if prev_pressed_button[1] == 'gray':
            seq_speed_change('fast')
        else:
            brightness_change('up')
            button_press(prev_pressed_button)
    elif button_info[0] == 'ON/\nPREVIOUS COLOUR':
            button_press(prev_pressed_button)
    elif button_info[0] != 'OFF/BLACK':
        colour_display_frame.configure(background=temp_button_new)
    update_status()

sequence_speed = 500
brightness_value = 1

def seq_speed_change(speed):
    global sequence_speed
    if speed == 'slow' and sequence_speed < 1000:
        sequence_speed = sequence_speed + 100
    elif speed == 'fast' and sequence_speed > 100:
        sequence_speed = sequence_speed - 100
    update_status()

def brightness_change(brightness):
    global brightness_value
    if brightness == 'down' and brightness_value < 7:
        brightness_value = brightness_value + 1
    elif brightness == 'up' and brightness_value > 1:
        brightness_value = brightness_value - 1
    update_status()

def brightness_func(in_col):
    col = ImageColor.getcolor(in_col, "RGB")
    col_hsv = list(rgb_to_hsv(col[0],col[1],col[2]))
    col_hsv[2] = col_hsv[2] / brightness_value
    col_out = hsv_to_rgb(col_hsv[0],col_hsv[1],col_hsv[2])
    hex_col = '#%02x%02x%02x' % (int(col_out[0]), int(col_out[1]), int(col_out[2]))

    return hex_col

def flash_seq(a=0): 
    global flash_seq_running
    if prev_pressed_button[0] == "FLASH" and curr_pressed_button[0] == "FLASH" and flash_seq_running:
        flash_seq_running = False
        try:
            colour_display_frame.after_cancel(colour_display_frame.after_id)
        except:
            pass
    
    if a < len(flash_seq_colours) and prev_pressed_button[0] == "FLASH":
        colour_display_frame.configure(background=flash_seq_colours[a])
        colour_display_frame.after_id = colour_display_frame.after(sequence_speed, flash_seq, a+1)
    elif prev_pressed_button[0] == "FLASH":
        colour_display_frame.after_cancel(colour_display_frame.after_id)
        a = 0
        colour_display_frame.configure(background=flash_seq_colours[a])
        colour_display_frame.after_id = colour_display_frame.after(sequence_speed, flash_seq, a+1)

def fade_seq(a=0):
    global fade_seq_running
    if prev_pressed_button[0] == "FADE" and curr_pressed_button[0] == "FADE" and fade_seq_running:
        fade_seq_running = False
        try:
            colour_display_frame.after_cancel(colour_display_frame.after_id)
        except:
            pass

    if a < len(fade_seq_colours) and prev_pressed_button[0] == "FADE":
        colour_display_frame.configure(background=fade_seq_colours[a])
        colour_display_frame.after_id = colour_display_frame.after(sequence_speed, fade_seq, a+1)
    elif prev_pressed_button[0] == "FADE":
        colour_display_frame.after_cancel(colour_display_frame.after_id)
        a = 0
        colour_display_frame.configure(background=fade_seq_colours[a])
        colour_display_frame.after_id = colour_display_frame.after(sequence_speed, fade_seq, a+1)

red_dec = False
green_dec = False
blue_dec = False

def smooth_seq(r=255,g=0,b=0):
    global smooth_seq_running, red_dec, green_dec, blue_dec
    if prev_pressed_button[0] == "SMOOTH" and curr_pressed_button[0] == "SMOOTH" and smooth_seq_running:
        smooth_seq_running = False
        red_dec = False
        green_dec = False
        blue_dec = False
        try:
            colour_display_frame.after_cancel(colour_display_frame.after_id)
        except:
            pass
    smooth_speed = int(sequence_speed / 100)
    if r == 255 and g <= 255 and b == 0 and prev_pressed_button[0] == "SMOOTH" and red_dec == False and green_dec == False and blue_dec == False:
        colour_display_frame.configure(background='#%02x%02x%02x' % (r, g, b))
        if g == 255:
            red_dec = True
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r, g, b)
        else:
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r, g+1, b)
    elif r >= 0 and g == 255 and b == 0 and prev_pressed_button[0] == "SMOOTH" and red_dec == True and green_dec == False and blue_dec == False:
        colour_display_frame.configure(background='#%02x%02x%02x' % (r, g, b))
        if r == 0:
            red_dec = False
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r, g, b)
        else:
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r-1, g, b)
    elif r == 0 and g == 255 and b <= 255 and prev_pressed_button[0] == "SMOOTH" and red_dec == False and green_dec == False and blue_dec == False:
        colour_display_frame.configure(background='#%02x%02x%02x' % (r, g, b))
        if b == 255:
            green_dec = True
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r, g, b)
        else:
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r, g, b+1)
    elif r == 0 and g >= 0 and b == 255 and prev_pressed_button[0] == "SMOOTH" and red_dec == False and green_dec == True and blue_dec == False:
        colour_display_frame.configure(background='#%02x%02x%02x' % (r, g, b))
        if g == 0:
            green_dec = False
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r, g, b)
        else:
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r, g-1, b)
    elif r <= 255 and g == 0 and b == 255 and prev_pressed_button[0] == "SMOOTH" and red_dec == False and green_dec == False and blue_dec == False:
        colour_display_frame.configure(background='#%02x%02x%02x' % (r, g, b))
        if r == 255:
            blue_dec = True
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r, g, b)
        else:
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r+1, g, b)
    elif r == 255 and g == 0 and b >= 0 and prev_pressed_button[0] == "SMOOTH" and red_dec == False and green_dec == False and blue_dec == True:
        colour_display_frame.configure(background='#%02x%02x%02x' % (r, g, b))
        if b == 0:
            blue_dec = False
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r, g, b)
        else:
            colour_display_frame.after_id = colour_display_frame.after(smooth_speed, smooth_seq, r, g, b-1)

def strobe_seq(a=0):
    global strobe_seq_running
    if prev_pressed_button[0] == "STROBE" and curr_pressed_button[0] == "STROBE" and strobe_seq_running:
        strobe_seq_running = False
        try:
            colour_display_frame.after_cancel(colour_display_frame.after_id)
        except:
            pass
    
    if a < len(strobe_seq_colours) and prev_pressed_button[0] == "STROBE":
        colour_display_frame.configure(background=strobe_seq_colours[a])
        colour_display_frame.after_id = colour_display_frame.after(sequence_speed, strobe_seq, a+1)
    elif prev_pressed_button[0] == "STROBE":
        colour_display_frame.after_cancel(colour_display_frame.after_id)
        a = 0
        colour_display_frame.configure(background=strobe_seq_colours[a])
        colour_display_frame.after_id = colour_display_frame.after(sequence_speed, strobe_seq, a+1)

for button_row in LED_remote_button_layout:
    for button in button_row:
        frame = Frame(
            master=button_frame,
            relief=RAISED,
            borderwidth=1
        )
        frame.grid(row=i, column=j)
        gui_button = Button(
            master=frame,
            font=("Arial", 9),
            width=17,
            height=2,
            text=button,
            bg=button_row[button],
            fg="black" if button_row[button] != "black" else "white",
            command=lambda m=[button, button_row[button]] : button_press(m)
        )
        gui_button.pack()
        j += 1
        k += 1
    i += 1
    j = 0

def update_status():
    info_frame.itemconfig(info_frame_strobe_id,text="Strobe Speed: " + str(sequence_speed/1000) + " Seconds")
    info_frame.itemconfig(info_frame_bright_id,text="Brightness Value: Level " + str(abs(brightness_value-8)))
    info_frame.itemconfig(info_frame_nom_id,text="Frame: " + str(slider.get()))
    info_frame.itemconfig(info_frame_col_id,text="Colour: " + str(curr_pressed_button[0]))

waveform_bars_memory = []

def waveform_gen(song_length,new_data):

    # CLEAR BARS
    for bar in waveform_bars_memory:
        bar.destroy()
    waveform_bars_memory.clear()

    # GENERATE NEW AMP BARS
    data_sample_counter = 0
    slider.set(0)
    while data_sample_counter < song_length:
        amp_point = abs(new_data[int(slider.get() * ((44100 * 2) / 5))])
        amp_vis_bar = Frame(master=root,width=1,height=((100-(100*amp_point)/20000)),bg='white')
        waveform_bars_memory.append(amp_vis_bar)
        amp_vis_bar.pack()
        amp_vis_bar.place(x=h.winfo_x(),y=223)
        root.update()
        scroll_button_press(['->',False])
        data_sample_counter += 1


    slider.set(0)

button_frame.pack()

button_press(('OFF/BLACK','black'))
root.mainloop()