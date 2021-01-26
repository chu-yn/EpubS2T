import os
import sys
import time
import getopt
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, messagebox
from opencc.opencc import OpenCC


def get_file_name(epub_path, cc):
    if epub_path == '':
        print('File not found')
        sys.exit()

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


def converter(epub_path, cc):
    path = get_file_name(epub_path, cc)  # grnerate temp file path
    unzip(path, epub_path)  # Unzip epub file
    os.chdir(path)  # Change path
    lang_trans(path, cc)  # Translate zh_CN to zh_TW with OpenCC
    zip(path)  # Pack epub file
    shutil.rmtree(path)  # Delete temp files
    print('Sucessful')


def main():
    window = tk.Tk()
    window.title('EpubS2T')
    window.geometry('800x600')
    epub_path = tk.StringVar()
    lang = tk.StringVar()
    header_label = tk.Label(window, text='簡繁轉換', font=('Arial', 24))
    header_label.grid(row=0, column=0)
    tk.Label(window, text='File', font=('Arial', 16)).grid(row=1, column=0)
    entry = tk.Entry(window, textvariable=epub_path)
    entry.grid(row=1, column=1)

    def browsefunc():
        filename = filedialog.askopenfilename(initialdir='~/',
                                              title='Select file',
                                              filetypes=[("epub files", "*.epub")])
        epub_path.set(filename)

    tk.Button(window, text="Browse", command=browsefunc).grid(row=1, column=2)

    tk.Label(window, text='Mode:', font=('Arial', 16)).grid(row=2, column=0)
    cb = ttk.Combobox(window, textvariable=lang)
    cb.grid(row=2, column=1)
    cb['values'] = ['s2t', 's2tw', 't2s']

    tk.Button(window, text="Convert", command=converter).grid(row=3, column=1)

    if not epub_path:
        print('file path is empty')
        sys.exit()
    '''
    cc = OpenCC(lang)
    print('Mode: ' + lang)
    start = time.perf_counter()
    converter(epub_path, cc)
    end = time.perf_counter()
    print(f'Time: {end - start}s')
    sys.exit()
    '''
    window.mainloop()


if __name__ == '__main__':
    main()
