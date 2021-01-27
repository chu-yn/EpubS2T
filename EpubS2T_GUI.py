import os
import sys
import time
import getopt
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
    print('File address: ' + os.path.abspath(epub_path))
    filename = cc.convert(filename)
    path = os.path.abspath(os.path.join(address, filename + '_converted'))
    print('Temp file: ' + path)
    return path


def mkdir(path):
    # 判斷目錄是否存在
    folder = os.path.exists(path)
    if not folder:
        # 如果不存在，則建立新目錄
        os.makedirs(path)
        print('Temp File Create Successful')
    else:
        # 如果目錄已存在，則不建立，提示目錄已存在
        print(path+' Temp File Existed')


def zip(path):
    print('Packing Epub File')
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
    print('Processing...')
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
        messagebox.showinfo(title='Warnig', message='Language not choosed')
    else:
        cc = OpenCC(lang)
        path = get_file_name(epub_path, cc)  # grnerate temp file path
        unzip(path, epub_path)  # Unzip epub file
        os.chdir(path)  # Change path
        lang_trans(path, cc)  # Translate zh_CN to zh_TW with OpenCC
        zip(path)  # Pack epub file
        shutil.rmtree(path)  # Delete temp files
        messagebox.showinfo(message='Sucessful')


def main():
    window = tk.Tk()
    window.title('EpubS2T')
    window.geometry('400x300')
    epub_path = tk.StringVar()
    lang = tk.StringVar()
    header_label = tk.Label(window, text='簡繁轉換', font=('Arial', 24))
    header_label.grid(row=0, column=0)
    tk.Label(window, text='File', font=('Arial', 14)).grid(row=1, column=0)
    entry_path = tk.Entry(window, textvariable=epub_path)
    entry_path.grid(row=1, column=1)

    def browsefunc():
        filename = filedialog.askopenfilename(initialdir='~/',
                                              title='Select file',
                                              filetypes=[("epub files", "*.epub")])
        epub_path.set(filename)

    tk.Button(window, text="Browse", command=browsefunc).grid(row=1, column=2)

    tk.Label(window, text='Mode', font=('Arial', 14)).grid(row=2, column=0)
    lang_entry = ttk.Combobox(window, textvariable=lang)
    lang_entry.grid(row=2, column=1)
    lang_entry['values'] = ['s2t', 's2tw', 't2s', 't2tw']

    tk.Button(window, text="Convert", command=lambda: converter(
        epub_path.get(), lang.get())).grid(row=3, column=1)

    window.mainloop()


if __name__ == '__main__':
    main()
