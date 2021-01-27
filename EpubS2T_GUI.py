import os
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
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
                with open(os.path.join(root, name), 'r+') as file:
                    text = file.read()
                text = cc.convert(text)
                with open(os.path.join(root, name), 'w') as file:
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
        header_label = tk.Label(self.window, text='語言轉換', font=('Arial', 24))
        header_label.grid(row=0, column=0)

        # path choosed UI
        tk.Label(self.window, text='File').grid(row=1, column=0)
        entry_path = tk.Entry(self.window, textvariable=self.epub_path)
        entry_path.grid(row=1, column=1)
        tk.Button(self.window, text="Browse",
                  command=self.browsefunc).grid(row=1, column=2)

        # mode chose UI
        tk.Label(self.window, text='Mode').grid(row=2, column=0)
        lang_entry = ttk.Combobox(self.window, textvariable=self.lang)
        lang_entry.grid(row=2, column=1)
        lang_entry['values'] = ['s2t', 's2tw', 't2s', 't2tw']

        # progressbar
        prog = ttk.Progressbar(self.window, length=200, mode="determinate",
                               orient=tk.HORIZONTAL)
        prog.grid(row=3, column=1)

        # convert UI
        tk.Button(self.window, text="Convert", command=lambda: self.process(
            self.epub_path.get(), self.lang.get(), prog)).grid(row=4, column=1)

        # quit UI
        tk.Button(self.window, text='Quit',
                  command=self.quitfunc).grid(row=5, column=1)

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
        shutil.rmtree(path)  # Delete temp files
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

    # quit function
    def quitfunc(self):
        self.window.destroy()


def main():
    app = UI()
    app.window.mainloop()


if __name__ == '__main__':
    main()
