import os
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from tkinter.constants import LEFT
from opencc.opencc import OpenCC


# return file translated name + address
def get_file_name(epub_path, cc):
    (address, file) = os.path.split(epub_path)
    (filename, ext) = os.path.splitext(file)
    filename = cc.convert(filename)
    path = os.path.abspath(os.path.join(address, filename + '_converted'))
    return path


# make dir
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        # if not exist, create new dir
        os.makedirs(path)


# zip file in epub
def zip(path):
    filelist = []
    isdir = True
    if os.path.isfile(path):
        filelist.append(path)
        isdir = False
    else:
        for root, dirs, files in os.walk(path):
            for name in files:
                filelist.append(os.path.join(root, name))
    with zipfile.ZipFile('{}.epub'.format(path), "w", zipfile.zlib.DEFLATED) as zf:
        for tar in filelist:
            arcname = tar[len(path):] if isdir else os.path.basename(path)
            zf.write(tar, arcname)


# unzip zipfile
def unzip(path, epub_path):
    mkdir(path)
    os.chdir(path)
    with zipfile.ZipFile(epub_path, 'r') as zf:
        zf.extractall()


# read file and translate
def lang_trans(path, cc):
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if name.endswith(".html") or name.endswith(".xhtml") \
                    or name.endswith(".opf") or name.endswith(".ncx"):
                with open(os.path.join(root, name), 'r+', encoding='utf-8') as file:
                    text = file.read()
                text = cc.convert(text)
                with open(os.path.join(root, name), 'w', encoding='utf-8') as file:
                    file.write(text)


class UI:
    def __init__(self):
        # main UI
        self.window = tk.Tk()
        self.window.title('EpubS2T')
        self.window.geometry('400x300')
        self.epub_path = tk.StringVar()
        self.lang = tk.StringVar()

        # menubar UI
        menubar = tk.Menu(self.window)
        filemenu = tk.Menu(menubar)
        filemenu.add_command(label='Open', command=self.browsefunc)
        filemenu.add_command(label='Quit', command=self.quitfunc)
        menubar.add_cascade(label='Menu', menu=filemenu)
        self.window.config(menu=menubar)

        # title UI
        title = tk.Frame(self.window)
        tk.Label(title, text='語言轉換', font=('Arial', 24)).pack(ipady=5)
        title.pack()

        # path choosed UI
        file_choose = tk.Frame(self.window)
        tk.Label(file_choose, text='File').pack(side=LEFT)
        entry_path = tk.Entry(file_choose, textvariable=self.epub_path)
        entry_path.pack(side=LEFT, ipadx=5)
        tk.Button(file_choose, text="Browse",
                  command=self.browsefunc).pack(side=LEFT)
        file_choose.pack(ipady=5)

        # mode chose UI
        mode_choose = tk.Frame(self.window)
        tk.Label(mode_choose, text='Mode').pack(side=LEFT)
        lang_entry = ttk.Combobox(mode_choose, textvariable=self.lang)
        lang_entry.pack(side=LEFT)
        lang_entry['values'] = ['s2t', 's2tw', 't2s', 't2tw']
        mode_choose.pack(ipady=5)

        # progressbar
        progressbar = tk.Frame(self.window)
        prog = ttk.Progressbar(progressbar, length=250,
                               mode="determinate", orient=tk.HORIZONTAL)
        prog.pack()
        progressbar.pack(ipady=5)

        # convert UI
        convert = tk.Frame(self.window)
        tk.Button(convert, text="Convert", command=lambda: self.process(
            self.epub_path.get(), self.lang.get(), prog)).pack()
        convert.pack(ipady=5)

        # quit UI
        quit = tk.Frame(self.window)
        tk.Button(quit, text='Quit',
                  command=self.quitfunc).pack()
        quit.pack(ipady=5)

    # browse function
    def browsefunc(self):
        filename = filedialog.askopenfilename(initialdir='~/',
                                              title='Select file',
                                              filetypes=[("epub files", "*.epub")])
        self.epub_path.set(filename)

    # progressbar increse function
    def increment(self, prog, per):
        prog["value"] += per
        self.window.update()

    # converter function
    def converter(self, epub_path, lang, prog):
        cc = OpenCC(lang)
        self.increment(prog, 5)
        path = get_file_name(epub_path, cc)  # grnerate temp file path
        self.increment(prog, 5)
        unzip(path, epub_path)  # Unzip epub file
        self.increment(prog, 15)
        os.chdir(path)  # Change path
        self.increment(prog, 5)
        lang_trans(path, cc)  # Translate zh_CN to zh_TW with OpenCC
        self.increment(prog, 30)
        zip(path)  # Pack epub file
        self.increment(prog, 30)
        shutil.rmtree(path, ignore_errors=True)  # Delete temp files
        self.increment(prog, 10)

    # progress function
    def process(self, epub_path, lang, prog):
        if epub_path == '':
            messagebox.showinfo(title='Warning', message='File not exist')
        elif lang == '':
            messagebox.showinfo(
                title='Warning', message='Language not choosed')
        else:
            self.converter(epub_path, lang, prog)
            messagebox.showinfo(message='Sucessful')
            prog["value"] = 0
            self.window.update()

    # quit function
    def quitfunc(self):
        self.window.destroy()


def main():
    app = UI()
    app.window.mainloop()


if __name__ == '__main__':
    main()
