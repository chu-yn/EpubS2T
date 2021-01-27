import os
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from opencc.opencc import OpenCC


def get_file_name(epub_path, cc):
    (address, file) = os.path.split(epub_path)
    (filename, ext) = os.path.splitext(file)
    filename = cc.convert(filename)
    path = os.path.abspath(os.path.join(address, filename + '_converted'))
    return path


def mkdir(path):
    # 判斷目錄是否存在
    folder = os.path.exists(path)
    if not folder:
        # 如果不存在，則建立新目錄
        os.makedirs(path)


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


def unzip(path, epub_path):
    mkdir(path)
    os.chdir(path)
    with zipfile.ZipFile(epub_path, 'r') as zf:
        zf.extractall()


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


def converter(epub_path, lang):
    if epub_path == '':
        messagebox.showinfo(title='Warning', message='File not exist')
    elif lang == '':
        messagebox.showinfo(title='Warning', message='Language not choosed')
    else:
        cc = OpenCC(lang)
        path = get_file_name(epub_path, cc)  # grnerate temp file path
        unzip(path, epub_path)  # Unzip epub file
        os.chdir(path)  # Change path
        lang_trans(path, cc)  # Translate zh_CN to zh_TW with OpenCC
        zip(path)  # Pack epub file
        shutil.rmtree(path)  # Delete temp files
        messagebox.showinfo(message='Sucessful')


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

        # convert UI
        tk.Button(self.window, text="Convert", command=lambda: converter(
            self.epub_path.get(), self.lang.get())).grid(row=3, column=1)

        # quit UI
        tk.Button(self.window, text='Quit',
                  command=self.quitfunc).grid(row=4, column=1)

        self.window.mainloop()

    # browse function
    def browsefunc(self):
        filename = filedialog.askopenfilename(initialdir='~/',
                                              title='Select file',
                                              filetypes=[("epub files", "*.epub")])
        self.epub_path.set(filename)

    # quit function
    def quitfunc(self):
        self.window.destroy()


def main():
    app = UI()


if __name__ == '__main__':
    main()
