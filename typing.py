import os
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
from collections import Counter
import time

PROGRAM_NAME = "Jdawg's Typing mastery MF"
file_name = None

root = Tk()
# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

w = 500
h = 350

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# root.geometry('350x350+50+50')
# set the dimensions of the screen
# and where it is place -->
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
root.title(PROGRAM_NAME)

# fingers
L1 = ["1", "q", "a", "z", '`', '~', "!"] # left pinky
L2 = ["2", "w", "s", "x", "@"] # left ring
L3 = ["3", "de", "d", "c", "#"] # left middle
L4 = ["4", "5", "r", "f", "v", "t", "g", "b", "$", "%"] # left index
R2 = ["6", "7", "y", "h", "n", "u", "j", "m", "^", "&"] # right index
R3 = ["8", "i", "k", ",", "*"] # right middle
R4 = ["9", "o", "l", ".", "("] # right ring
# R5 = ["0", "p", ";", "/". "?", ")", "-", "_", "+", "=", "{", "[", "}", "]", "|", "\\" ] # right pinky

# timer (seconds)
start_timer = time.time()

# number of character typed
chars = 0

# characters per second
# cpm cps x s/m
# wpm - 5 chars = 1 word

cursor_color = "#%02x%02x%02x" % (226, 57, 199)
foreground_color = "#%02x%02x%02x" % (171, 178, 191)
background_color = "#%02x%02x%02x" % (0, 2, 42)


def update_line_numbers(event=None):
    line_numbers = get_line_numbers()
    line_number_bar.config(state='normal')
    line_number_bar.delete('1.0', 'end')
    line_number_bar.insert('1.0', line_numbers)
    line_number_bar.config(state='disabled')


def highlight_line(interval=100):
    content_text.tag_remove("active_line", 1.0, "end")
    content_text.tag_add(
        "active_line", "insert linestart", "insert lineend+1c")
    content_text.after(interval, toggle_highlight)


def undo_highlight():
    content_text.tag_remove("active_line", 1.0, "end")


def toggle_highlight(event=None):
    if to_highlight_line.get():
        highlight_line()
    else:
        undo_highlight()


def on_content_changed(event=None):
    update_line_numbers()


def get_line_numbers():
    output = ''
    if show_line_number.get():
        row, col = content_text.index("end").split('.')
        for i in range(1, int(row)):
            output += str(i) + '\n'
    return output


def display_about_messagebox(event=None):
    tkinter.messagebox.showinfo(
        "About", PROGRAM_NAME + "\nTkinter GUI Application\n Development Blueprints")


def display_help_messagebox(event=None):
    tkinter.messagebox.showinfo(
        "Help", "Help Book: \nTkinter GUI Application\n Development Blueprints",
        icon='question')


def exit_editor(event=None):
    if tkinter.messagebox.askokcancel("Quit?", "Really quit?"):
        root.destroy()


def new_file(event=None):
    root.title("Untitled")
    global file_name
    file_name = None
    content_text.delete(1.0, END)
    on_content_changed()


def open_file(event=None):
    input_file_name = tkinter.filedialog.askopenfilename(defaultextension=".txt",
                                                         filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")])
    if input_file_name:
        global file_name
        file_name = input_file_name
        root.title('{} - {}'.format(os.path.basename(file_name), PROGRAM_NAME))
        content_text.delete(1.0, END)
        with open(file_name) as _file:
            content_text.insert(1.0, _file.read())
    on_content_changed()


def write_to_file(file_name):
    try:
        content = content_text.get(1.0, 'end')
        with open(file_name, 'w') as the_file:
            the_file.write(content)
    except IOError:
        tkinter.messagebox.showwarning("Save", "Could not save the file.")


def save_as(event=None):
    input_file_name = tkinter.filedialog.asksaveasfilename(defaultextension=".txt",
                                                           filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")])
    if input_file_name:
        global file_name
        file_name = input_file_name
        write_to_file(file_name)
        root.title('{} - {}'.format(os.path.basename(file_name), PROGRAM_NAME))
    return "break"

def save(event=None):
    global file_name
    if not file_name:
        save_as()
    else:
        write_to_file(file_name)
    return "break"


def select_all(event=None):
    content_text.tag_add('sel', '1.0', 'end')
    return "break"


def find_text(event=None):
    search_toplevel = Toplevel(root)
    search_toplevel.title('Find Text')
    search_toplevel.transient(root)
    search_toplevel.resizable(False, False)
    Label(search_toplevel, text="Find All:").grid(row=0, column=0, sticky='e')
    search_entry_widget = Entry(
        search_toplevel, width=25)
    search_entry_widget.grid(row=0, column=1, padx=2, pady=2, sticky='we')
    search_entry_widget.focus_set()
    ignore_case_value = IntVar()
    Checkbutton(search_toplevel, text='Ignore Case', variable=ignore_case_value).grid(
        row=1, column=1, sticky='e', padx=2, pady=2)
    Button(search_toplevel, text="Find All", underline=0,
           command=lambda: search_output(
               search_entry_widget.get(), ignore_case_value.get(),
               content_text, search_toplevel, search_entry_widget)
           ).grid(row=0, column=2, sticky='e' + 'w', padx=2, pady=2)

    def close_search_window():
        content_text.tag_remove('match', '1.0', END)
        search_toplevel.destroy()
    search_toplevel.protocol('WM_DELETE_WINDOW', close_search_window)
    return "break"


def search_output(needle, if_ignore_case, content_text,
                  search_toplevel, search_box):
    content_text.tag_remove('match', '1.0', END)
    matches_found = 0
    if needle:
        start_pos = '1.0'
        while True:
            start_pos = content_text.search(needle, start_pos,
                                                   nocase=if_ignore_case, stopindex=END)
            if not start_pos:
                break
            end_pos = '{}+{}c'.format(start_pos, len(needle))
            content_text.tag_add('match', start_pos, end_pos)
            matches_found += 1
            start_pos = end_pos
        content_text.tag_config(
            'match', foreground='red', background='yellow')
    search_box.focus_set()
    search_toplevel.title('{} matches found'.format(matches_found))


def cut():
    content_text.event_generate("<<Cut>>")
    on_content_changed()
    return "break"


def copy():
    content_text.event_generate("<<Copy>>")
    return "break"


def paste():
    content_text.event_generate("<<Paste>>")
    on_content_changed()
    return "break"


def undo():
    content_text.event_generate("<<Undo>>")
    on_content_changed()
    return "break"


def redo(event=None):
    content_text.event_generate("<<Redo>>")
    on_content_changed()
    return 'break'

new_file_icon = PhotoImage(file='icons/new_file.gif')
open_file_icon = PhotoImage(file='icons/open_file.gif')
save_file_icon = PhotoImage(file='icons/save.gif')
cut_icon = PhotoImage(file='icons/cut.gif')
copy_icon = PhotoImage(file='icons/copy.gif')
paste_icon = PhotoImage(file='icons/paste.gif')
undo_icon = PhotoImage(file='icons/undo.gif')
redo_icon = PhotoImage(file='icons/redo.gif')

menu_bar = Menu(root)
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label='New', accelerator='Ctrl+N', compound='left',
                      image=new_file_icon, underline=0, command=new_file)
file_menu.add_command(label='Open', accelerator='Ctrl+O', compound='left',
                      image=open_file_icon, underline=0, command=open_file)
file_menu.add_command(label='Save', accelerator='Ctrl+S',
                      compound='left', image=save_file_icon, underline=0, command=save)
file_menu.add_command(
    label='Save as', accelerator='Shift+Ctrl+S', command=save_as)
file_menu.add_separator()
file_menu.add_command(label='Exit', accelerator='Alt+F4', command=exit_editor)
menu_bar.add_cascade(label='File', menu=file_menu)

edit_menu = Menu(menu_bar, tearoff=0)
edit_menu.add_command(label='Undo', accelerator='Ctrl+Z',
                      compound='left', image=undo_icon, command=undo)
edit_menu.add_command(label='Redo', accelerator='Ctrl+Y',
                      compound='left', image=redo_icon, command=redo)
edit_menu.add_separator()
edit_menu.add_command(label='Cut', accelerator='Ctrl+X',
                      compound='left', image=cut_icon, command=cut)
edit_menu.add_command(label='Copy', accelerator='Ctrl+C',
                      compound='left', image=copy_icon, command=copy)
edit_menu.add_command(label='Paste', accelerator='Ctrl+V',
                      compound='left', image=paste_icon, command=paste)
edit_menu.add_separator()
edit_menu.add_command(label='Find', underline=0,
                      accelerator='Ctrl+F', command=find_text)
edit_menu.add_separator()
edit_menu.add_command(label='Select All', underline=7,
                      accelerator='Ctrl+A', command=select_all)
menu_bar.add_cascade(label='Edit', menu=edit_menu)


view_menu = Menu(menu_bar, tearoff=0)
show_line_number = IntVar()
show_line_number.set(1)
view_menu.add_checkbutton(label='Show Line Number', variable=show_line_number,
                          command=update_line_numbers)
show_cursor_info = IntVar()
show_cursor_info.set(1)
view_menu.add_checkbutton(
    label='Show Cursor Location at Bottom', variable=show_cursor_info)
to_highlight_line = BooleanVar()
view_menu.add_checkbutton(label='Highlight Current Line', onvalue=1,
                          offvalue=0, variable=to_highlight_line, command=toggle_highlight)
themes_menu = Menu(menu_bar, tearoff=0)
view_menu.add_cascade(label='Themes', menu=themes_menu)

color_schemes = {
    'Default': '#000000.#FFFFFF',
    'Greygarious': '#83406A.#D1D4D1',
    'Aquamarine': '#5B8340.#D1E7E0',
    'Bold Beige': '#4B4620.#FFF0E1',
    'Cobalt Blue': '#ffffBB.#3333aa',
    'Olive Green': '#D1E7E0.#5B8340',
    'Night Mode': '#FFFFFF.#000000',
}

theme_choice = StringVar()
theme_choice.set('Default')
for k in sorted(color_schemes):
    themes_menu.add_radiobutton(label=k, variable=theme_choice)
menu_bar.add_cascade(label='View', menu=view_menu)

about_menu = Menu(menu_bar, tearoff=0)
about_menu.add_command(label='About', command=display_about_messagebox)
about_menu.add_command(label='Help', command=display_help_messagebox)
menu_bar.add_cascade(label='About',  menu=about_menu)
root.config(menu=menu_bar)

shortcut_bar = Frame(root,  height=25)
shortcut_bar.pack(expand='no', fill='x')

# adding shortcut icons
icons = ('new_file', 'open_file', 'save', 'cut', 'copy', 'paste',
         'undo', 'redo', 'find_text')
for i, icon in enumerate(icons):
    tool_bar_icon = PhotoImage(file='icons/{}.gif'.format(icon))
    cmd = eval(icon)
    tool_bar = Button(shortcut_bar, image=tool_bar_icon, command=cmd)
    tool_bar.image = tool_bar_icon
    tool_bar.pack(side='left')

# to diplay text
T = Text(root, wrap='word', height=4, width=100, background=background_color, foreground=foreground_color)
T.pack() #.place(x=2,y=2)

# example = "And why do I bother with such an effort? Because I believe resilience is one of the most"
example = "And why do I bother with such an effort? I believe resilience is"
example1 = "important skills one can develop, mainly for two reasons."
# example2 = "The first reason is that it makes life just so much simple and enjoyable. Its great to know that there are only few catastrophes that could really affect your overall happiness. When happiness trully comes from within, most things that happen to you, no matter how bad, can’t really affect it. This gives you an enormous confidence, and lets you experiment with all sort of beneficial new ideas, which in turn result in more happiness and confidence."
# example2 = "The first reason is that it makes life just so much simple and enjoyable."
example2 = 'When the word "bodega" began to trend all over Twitter this week, I wondered whether something bad had happened in one those beloved, big-city neighbo'
T.config(font=("Courier", 18))

global correct
global incorrect
correct = 0
incorrect = 0
global c_correct
global c_incorrect
global error_pairs
c_correct = Counter()
c_incorrect = Counter()
c_error_pairs = Counter()
# maybe tuples (incorrect, meant) and count on that for confusion matrix

# get the word in which error was made
def get_word(sentence, c_num):
    after = [i for i, ltr in enumerate(sentence[c_num:]) if ltr == " "][0]
    before = [i for i, ltr in enumerate(sentence[:c_num]) if ltr == " "][-1]

    return sentence[before+1:after+c_num]

def split_article(article, num_chars):
    secciones = []
    prev = 0

    article_range = range(num_chars, len(article), num_chars)

    for r in article_range:
        secciones.append(article[prev:r])
        prev = r
        if r == article_range[-1]:
            secciones.append(article[prev:len(article)])
    return secciones


def load_new_chunk():
    global c_correct
    global c_incorrect
    global i
    if i < test_length:
        a.delete(0, 'end')
        T.config(state=NORMAL)
        T.delete(1.0, 'end')
        # print(i)
        # print(test[i])
        T.insert(1.0, test[i]) #, background='yellow')
        global example_length
        example_length = len(test[i])
        i += 1
        T.config(state=DISABLED) # so it cant be edited
        global start
        start = 0
        global pos
        pos = T.index(1.0)
        T.tag_add("cursor", pos)
        # T.tag_configure("cursor", foreground="red", underline=True)
        T.tag_configure("cursor", background=cursor_color, underline=True)
    else:
        print("You won!!")
        print("Correct Counter ",  c_correct)
        print("Incorrect Counter ",  c_incorrect)
        print("Error pairs: ", c_error_pairs)
        content_text.insert(1.0, c_error_pairs)
        content_text.insert(END, "\nAccuracy: {}".format(correct/(correct + incorrect)))
        # it would be cool if I could count the words as well
        #       given chracter location look for spaces before and after
        # done = True

# for text in test:
#     T.insert(END, example1) #, background='yellow')
#     T.config(state=DISABLED) # so it cant be edited
#     example_length = len(text)
#     start = 0
#     # cur = T.index("sel.first")
#     # print(cur)
#     pos = T.index(1.0)
# # T.tag_add("cursor", float(start + 1))
#     T.tag_add("cursor", pos)
#     # T.tag_configure("cursor", foreground="red", underline=True)
#     T.tag_configure("cursor", background="yellow", underline=True)



def callback(a, b, c):
    # callback expects 3 variables
    # not really needed as everything I need is defined locally
    # https://stackoverflow.com/questions/3876229/how-to-run-a-code-whenever-a-tkinter-widget-value-changes
    global correct
    global incorrect
    global c_correct
    global c_incorrect
    global start
    global pos
    current = a_var.get()
    length_current = len(current)
    global chars
    global example_length
    print(test[i-1][start])
    print(current[length_current-1])

    # to calculate timer in seconds
    global start_timer
    now = time.time()
    timer_seconds = now - start_timer
    chars += 1


    if test[i-1][start] == current[length_current-1]:
        c_correct.update(test[i-1][start])
        correct += 1
        start += 1
        print("Correct")
        # T.tag_remove("cursor", float(start - 1))
        T.tag_remove("cursor", pos)
        pos = pos + '+1c'
        T.tag_add("cursor", pos)
        T.tag_configure("cursor", background=cursor_color, underline=True)
        T.tag_configure("cursor", foreground="black", underline=True)

        # print("Timer: {}".format(timer_seconds))
        # print("Characters: {}".format(chars))

        print("correct: {}\nincorrect: {}\nAccuracy: {}".format(correct, incorrect, correct/(correct + incorrect)))
        cpm = chars/timer_seconds*60
        wpm = cpm/5
        print("cpm: ", cpm)
        print("wpm: ", wpm)

        if start >= example_length:
            print("start ", start)
            print("example length ", example_length)
            load_new_chunk()

    else:
        incorrect += 1
        c_incorrect.update(test[i-1][start])
        print(test[i-1])
        print(test[i-1][start])
        mistaken_word = get_word(test[i-1], start)
        print(mistaken_word)
        c_error_pairs.update([(mistaken_word, test[i-1][start], current[length_current-1])])

        print("NOT GOOD")
        T.tag_configure("cursor", foreground="red", underline=True)

a = Entry(root, width = 100)
a_var = StringVar()
a["textvariable"] = a_var
a.pack()
a_var.trace_variable("w", callback)

test = [example, example1, example2] # to be replaced with split_article()

global test_length
test_length = len(test)
# global i
i = 0
# start = 0
load_new_chunk()




line_number_bar = Text(root, width=4, padx=3, takefocus=0,  border=0,
                       background='khaki', state='disabled',  wrap='none')
line_number_bar.pack(side='left',  fill='y')

content_text = Text(root, wrap='word', undo=1)
content_text.pack(expand='yes', fill='both')
scroll_bar = Scrollbar(content_text)
content_text.configure(yscrollcommand=scroll_bar.set)
scroll_bar.config(command=content_text.yview)
scroll_bar.pack(side='right', fill='y')

content_text.bind('<KeyPress-F1>', display_help_messagebox)
content_text.bind('<Control-N>', new_file)
content_text.bind('<Control-n>', new_file)
content_text.bind('<Control-O>', open_file)
content_text.bind('<Control-o>', open_file)
content_text.bind('<Control-S>', save)
content_text.bind('<Control-s>', save)
content_text.bind('<Control-f>', find_text)
content_text.bind('<Control-F>', find_text)
content_text.bind('<Control-A>', select_all)
content_text.bind('<Control-a>', select_all)
content_text.bind('<Control-y>', redo)
content_text.bind('<Control-Y>', redo)

# added in this iteration
content_text.bind('<Any-KeyPress>', on_content_changed)
content_text.tag_configure('active_line', background='ivory2')
###



root.protocol('WM_DELETE_WINDOW', exit_editor)
root.mainloop()
