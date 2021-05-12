from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk,Image
from zwset import *
from pathlib import Path,PurePath
from os.path import dirname, isdir, exists
from os import chdir, mkdir
from shutil import copy
root = Tk()
root.title('zwdoc')
#variables
new_file_count=0
documents=[]#where all the pages go, i.e. all data pretaining to documents
pictures=[]
class page:
    def __init__(self,title):
        self.show_img = image_default_open
        self.name=title
        self.frame= Frame(notebook)
        self.frame.pack()
        notebook.add(self.frame, text = title)
        self.text= Text(self.frame,wrap='word',width=text_x, height=text_y,undo=True,bg=bg_color,fg=fg_color,exportselection=True,spacing1=space_1,spacing2=space_2,spacing3=space_3)
        self.text.grid(column=0,row=0,sticky=(N,S,E,W))
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.scrollx = ttk.Scrollbar(self.frame,orient=HORIZONTAL,command=self.text.xview)
        self.scrolly = ttk.Scrollbar(self.frame, orient=VERTICAL,command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrolly.set)
        self.text.configure(xscrollcommand=self.scrollx.set)
        self.scrolly.grid(column=1,row=0,sticky=(N,S))
        self.scrollx.grid(column=0,row=1,sticky=(W,E))
        self.text.edit_modified(0)
        global startup
        if startup:
            start_frame.destroy()
            startup=False
    def insert(self,data):
        self.text.insert('1.0',data)
        self.text.edit_modified(0)
    def export(self,target):
        self.unload_imgs()
        pre=self.text.get('1.0','end')
        b=PurePath(dirname(self.name)).joinpath('zwdocimg')
        if Path(b).exists():
            chdir(b)
        items = set()
        search='1.0'
        while True:
            pos=self.text.search('/zwdoc.img:*',search,regexp=True,stopindex='end')#this regex needs to be changed
            search=pos+' + 13 chars'
            if pos == '':
                break
            y=0
            while pos[y] != '.':
                y=y+1
            dat=self.text.get(pos+'+12 chars',pos[:y]+'.end')
            dat = Path(dat).resolve()
            items.add(dat)
            #change path
            self.text.delete(pos,pos[:y]+'.end')
            self.text.insert(pos,'/zwdoc.img:*'+PurePath(dat).name)
        place=PurePath(target).joinpath('zwdocimg')
        if not isdir(place):
            mkdir(place)
        for x in items:
            copy(x,place.joinpath(x.name))#err here, same file
            d=open(PurePath(target).joinpath(PurePath(self.name).name),'w')
            d.write(self.text.get('1.0','end'))
            d.close()
        if not PurePath(dirname(self.name))== PurePath(target):
            self.text.delete('1.0','end')
            self.insert(pre)
        if image_default_open:
            self.load_imgs()
    def load_imgs(self):#add handleing for paths with space after them
        b=PurePath(dirname(self.name)).joinpath('zwdocimg')
        if Path(b).exists():
            chdir(b)
        while True:
            drawn=False
            pos=self.text.search('/zwdoc.img:*','1.0',regexp=True)#this regex needs to be changed
            if pos == '':
                return()
            y=0
            while pos[y] != '.':
                y=y+1
            dat=self.text.get(pos+'+12 chars',pos[:y]+'.end')
            dat = str(Path(dat))
            for x in pictures:
                if x.title == dat:
                    self.text.delete(pos,pos[:y]+'.end')
                    x.draw(self,pos)
                    drawn=True
            if drawn==False:
                z=picture(dat)
                pictures.append(z)
                self.text.delete(pos,pos[:y]+'.end')
                z.draw(self,pos)
    def unload_imgs(self):
        for x in self.text.image_names():
            target=self.text.index(x)
            cut=x.find('\n')
            self.text.delete(target)
            self.text.insert(target,'/zwdoc.img:*'+x[:cut])
class picture:
    def __init__(self,title):
        temp=Image.open(title)
        w,h=temp.size
        whr=w/h
        new_h=h
        new_w=w
        if not max_height == 0 and not max_width==0:
            if h > max_height and w > max_width:
                if h - max_height > w - max_width:
                    new_h = max_height
                    new_w = new_h * whr
                else:
                    new_w = max_width
                    new_h = new_w / whr
            elif h>max_height:
                new_h = max_height
                new_w = new_h * whr
            elif w>max_width:
                new_w = max_width
                new_h = new_w / whr
            temp=temp.resize((int(new_w),int(new_h)))
        self.data=ImageTk.PhotoImage(temp)
        self.title=title
    def dump(self):
        self.data=0
    def draw(self,page,location):
        page.text.image_create(location,image=self.data,name=str(self.title+'\n'))
class locations:
    def __init__(self):
        self.position='0.0'
        self.previous=StringVar('')
class find:
    def __init__(self,page):
        self.dict= {}
        self.prev_doc = 0
        self.entry_find = StringVar()
        self.entry_replase = StringVar()
        self.regex=IntVar(0)
        self.f=Toplevel(root)
        self.notebook = ttk.Notebook(self.f)
        self.notebook.grid(column=0,row=0,sticky=(N,S,E,W))
        self.frame1=Frame(self.notebook)
        self.frame2=Frame(self.notebook)
        self.notebook.add(self.frame1,text='Find')
        self.notebook.add(self.frame2,text='Find & Replace')
        self.notebook.enable_traversal()
        self.entry_box_1=Entry(self.frame1,textvariable=self.entry_find)
        self.entry_box_2=Entry(self.frame2,textvariable=self.entry_find)
        self.entry_box_3=Entry(self.frame2,textvariable=self.entry_replase)
        self.button_find_f1=Button(self.frame1,text='Find',command=self.search_f)
        self.button_find_r1=Button(self.frame1,text='Find previous',command=self.search_r)
        self.button_find_f2=Button(self.frame2,text='Find',command=self.search_f)
        self.button_find_r2=Button(self.frame2,text='Find previous',command=self.search_r)
        self.button_replace=Button(self.frame2,text='Replace',command=self.replace)
        self.button_replace_all=Button(self.frame2,text='Replace all',command=self.replace_all)
        self.replace_label=Label(self.frame2,text='Replace with:')
        self.check1= Checkbutton(self.frame1,text='Use regex',variable=self.regex)
        self.check2= Checkbutton(self.frame2,text='Use regex',variable=self.regex)
        self.entry_box_1.grid(column=0,row=0,padx=2,pady=2)
        self.button_find_f1.grid(column=0,row=1,sticky=(W,E),padx=2,pady=2)
        self.button_find_r1.grid(column=1,row=1,sticky=(W,E),padx=2,pady=2)
        self.entry_box_2.grid(column=0,row=0,padx=2,pady=2)
        self.replace_label.grid(column=1,row=0,padx=2,pady=2)
        self.entry_box_3.grid(column=2,row=0,padx=2,pady=2)
        self.check1.grid(column=0,row=2)
        self.button_find_f2.grid(column=0,row=1,sticky=(W,E),padx=2,pady=2)
        self.button_find_r2.grid(column=1,row=1,sticky=(W,E),padx=2,pady=2)
        self.button_replace.grid(column=2,row=1,sticky=(W,E),padx=2,pady=2)
        self.button_replace_all.grid(column=3,row=1,sticky=(W,E),padx=2,pady=2)
        self.f.resizable(False,False)
        self.check2.grid(column=0,row=2)
        if page:
            self.notebook.select(1)
    def search_f(self):
        length=StringVar(0)
        data=self.entry_find
        x=id_frame()
        if x not in self.dict:
            self.dict[x]=locations()
        pos=self.dict[x].position
        pre=self.dict[x].previous
        target=documents[x].text.search(data.get(),pos,regexp=self.regex,stopindex='end',count=length)
        if target==pos and pre.get()==data.get():
            target=documents[x].text.search(data.get(),pos+'+ 1 chars',regexp=self.regex,stopindex='end',count=length)
        if target=='':
            if pos=='0.0':
                messagebox.showinfo(message='not found')
            else:
                self.dict[x].position='0.0'
                self.search_f()#err here
        else:
            documents[x].text.focus()
            documents[x].text.tag_remove('sel','1.0','end')
            documents[x].text.tag_add('sel',target,target + ' + '+str(length.get())+' chars')
            documents[x].text.mark_set(INSERT,target)
            documents[x].text.see(target)
            self.dict[x].position=target
            self.dict[x].previous=data
    def search_r(self):
        length=StringVar(0)
        data=self.entry_find
        x=id_frame()
        if x not in self.dict:
            self.dict[x]=locations()
        pos=self.dict[x].position
        pre=self.dict[x].previous
        if pos=='0.0':
            pos='end'
        target=documents[x].text.search(data.get(),pos,regexp=self.regex,stopindex='1.0',count=length,backwards=True)
        if target=='':
            if pos=='end':
                messagebox.showinfo(message='not found') 
            else:
                self.dict[x].position='end'
                self.search_r()
        else:
            documents[x].text.focus()
            documents[x].text.tag_remove('sel','1.0','end')
            documents[x].text.tag_add('sel',target,target + ' + '+str(length.get())+' chars')
            documents[x].text.mark_set(INSERT,target)
            documents[x].text.see(target)
            self.dict[x].position=target
            self.dict[x].previous=data
    def replace(self):
        length=StringVar(0)
        data=self.entry_find
        rep=self.entry_replase
        x=id_frame()
        if x not in self.dict:
            self.dict[x]=locations()
        pos=self.dict[x].position
        pre=self.dict[x].previous
        target=documents[x].text.search(data.get(),pos,regexp=self.regex,stopindex='end',count=length)
        if target=='':
            if pos == '0.0':
                return 1
            else:
                self.dict[x].position='0.0'
                self.replace()
        else:
            documents[x].text.focus()
            documents[x].text.delete(target,target + ' + ' + str(length.get())+' chars')
            documents[x].text.insert(target,self.entry_replase.get())
            documents[x].text.tag_remove('sel','1.0','end')
            documents[x].text.tag_add('sel',target,target + ' + '+str(len(self.entry_replase.get()))+' chars')
            documents[x].text.mark_set(INSERT,target)
            documents[x].text.see(target)
            self.dict[x].position=target
            self.dict[x].previous=data
            return 0
    def replace_all(self):
        x=0
        while x==0:
            x=self.replace()
#functions###########################################################################################
def new_file(foo=0):
    global new_file_count
    if new_file_count==0:
        name='New file'
    else:
        name='New file '+str(new_file_count)
    new_file_count=new_file_count+1
    new=page(name)
    documents.append(new)
    notebook.select(notebook.index(new.frame))
def open_file(foo=0):
    filename = filedialog.askopenfilename(filetypes=file_formats)
    if not exists(filename):
        #messagebox.showerror(message='file does not exist')
        return()
    f= open(filename,'r')
    w=f.read()
    f.close()
    new = page(filename)
    new.insert(w)
    documents.append(new)
    notebook.select(notebook.index(new.frame))
    x=id_frame()
    if image_default_open:
        documents[x].load_imgs()
def id_frame():
    x=notebook.select()
    if len(x)==0:
        x='.!notebook.!frame-1'
    x=x[17:]
    if x=='':
        x='1'
    x=int(x)
    x=x-1
    return(x)

def save_file(foo=0):
    x=id_frame()
    if x < 0:
        messagebox.showerror(message='bad page')
        return()
    save(x)

def save (x):
    if documents[x].name[:8]=='New file':
        save_as_file(page=x)
        return()
    documents[x].unload_imgs()
    f=open(documents[x].name,'w')
    if f == '':
        return()
    d=documents[x].text.get('1.0','end')
    f.write(d)
    f.close()
    if documents[x].show_img:
        documents[x].load_imgs()
    documents[x].text.edit_modified(0)
def save_as_file(useless='',page=-100):
    if page==-100:
        x=id_frame()
    else:
        x=page
    if x < 0:
        messagebox.showerror(message='bad page')
        return()
    documents[x].unload_imgs()
    d=documents[x].text.get('1.0','end')
    filename = filedialog.asksaveasfilename(filetypes=file_formats)
    if filename == '':
        #this means pannel was closed
        return()
    f=open(filename,'w')
    f.write(d)
    f.close
    if documents[x].show_img:
        documents[x].load_imgs()
    documents[x].text.edit_modified(0)
    documents[x].name = filename
    notebook.tab(x,text=filename)
def export_file(foo=0):
    p=id_frame()
    #verify every img, copy to selected directory, copy the file also, replace pathes with relitive ones
    if documents[p].name[:8]=='New file':
        save_as_file(page=p)
    target=filedialog.askdirectory(title='select folder to export into')
    documents[p].export(target)
def close_file(foo=0):#forget()tab, but first check if changed somehow
    p=id_frame()
    if p<0:
        messagebox.showerror(message='bad page')
        return()
    if modified(p):
        saveyn(p)
    notebook.forget(documents[p].frame)
    documents[p]=False
def exit_file(foo=0):#close program, do same check as before
    a=0
    for x in documents:
        if not x:
            continue
        if x.text.edit_modified():
            saveyn(a)
        a=a+1
    end()
def undo_edit(foo=0):#there is also nothing to undo/redo errors
    p=id_frame()
    documents[p].text.edit_undo()
def redo_edit(foo=0):
    p=id_frame()
    documents[p].text.edit_redo()
def cut_edit(foo=0):
    p=id_frame()
    documents[p].text.event_generate("<<Cut>>")
def copy_edit(foo=0):
    p=id_frame()
    documents[p].text.event_generate("<<Copy>>")
def paste_edit(foo=0):
    p=id_frame()
    documents[p].text.event_generate("<<Paste>>")
def select_all_edit(foo=0):
    p=id_frame()
    documents[p].text.tag_add('sel','1.0','end')
def find_edit(foo=0):
    x=find(False)
def replace_edit(foo=0):
    x=find(True)
def show_img_view(foo=0):
    p=id_frame()
    documents[p].load_imgs()
    documents[p].show_img=True
def hide_img_view(foo=0):
    p=id_frame()
    documents[p].unload_imgs()
    documents[p].show_img=False
def img_insert(foo=0):#open dialogue, insert \n#!path\n or something of that sort
    filename = filedialog.askopenfilename()
    p=id_frame()
    x = picture(filename)
    pictures.append(x)
    x.draw(documents[p],'insert')#draw in 1 in position 2
    documents[p].text.edit_modified(1)
def end():
    root.destroy()
def modified (p):
    a=documents[p].text.edit_modified()
    return a
def saveyn (t):
    m=documents[t].name+' has unsaved progress, do you want to save'
    if messagebox.askyesno(message=m):
        save(t)
#functions for key binds#######################################################
def bind(x):
    a,b=x
    root.bind_all(a,b)

keybinds=(('<Control-n>', new_file),('<Control-N>', new_file),('<Control-o>',open_file),('<Control-O>',open_file),('<Control-s>', save_file),\
          ('<Control-S>', save_file),('<Control-Shift-s>',save_as_file),('<Control-Shift-s>',save_as_file),('<Control-e>',export_file),\
          ('<Control-E>',export_file),('<Control-f>',find_edit),('<Control-F>',find_edit),('<Control-Shift-f>',replace_edit),\
          ('<Control-Shift-F>',replace_edit),('<F1>',show_img_view),('<F2>',hide_img_view),('<Control-i>',img_insert),('<Control-I>',img_insert),\
          ('WM_DELETE_WINDOW',exit_file))

for x in keybinds:
    bind(x)
#menu config#####################################################################################
root.option_add('*tearOff', FALSE)
menubar = Menu(root)
root['menu'] = menubar
mefile=Menu(menubar)
meedit = Menu(menubar)
meview = Menu(menubar)
meinsert = Menu(menubar)
menubar.add_cascade(menu=mefile, label='File')
menubar.add_cascade(menu=meedit, label='Edit')
menubar.add_cascade(menu=meview, label='View')
menubar.add_cascade(menu=meinsert, label='Insert')
mefile.add_command(label='New', command=new_file)
mefile.add_command(label='Open', command=open_file)
mefile.add_command(label='Save', command=save_file)
mefile.add_command(label='Save As', command=save_as_file)
mefile.add_command(label='Export', command=export_file)
mefile.add_command(label='Close', command=close_file)
mefile.add_command(label='Exit', command=exit_file)
meedit.add_command(label='Undo', command=undo_edit)
meedit.add_command(label='Redo', command=redo_edit)
meedit.add_command(label='Cut', command=cut_edit)
meedit.add_command(label='Copy', command=copy_edit)
meedit.add_command(label='Paste', command=paste_edit)
meedit.add_command(label='Find', command=find_edit)
meedit.add_command(label='Find & Replace', command=replace_edit)
meedit.add_command(label='Select All', command=select_all_edit)
meview.add_command(label='Show Images', command=show_img_view)
meview.add_command(label='Hide Images', command=hide_img_view)
meinsert.add_command(label='Image',command=img_insert)
#Pages config#####################################################################################
notebook = ttk.Notebook()
notebook.grid(column=0,row=0,sticky=(N,S,E,W))
notebook.enable_traversal()
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
#startup pane
if startup_pane:
    start_frame= Frame(root,height=start_h,width=start_w,bg=bg_color)
    start_frame.grid(column=0,row=0)
    startup=True
root.mainloop()
