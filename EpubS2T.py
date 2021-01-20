import os
import shutil
import zipfile
from opencc import OpenCC
cc = OpenCC('s2t')
epub_path = '/Users/chunyen/Downloads/投资最重要的事(全新升级版).epub'


def get_file_name(epub_path):
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


def CN_to_TW(path):
    print('Processing...')
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if name.endswith(".html"):
                with open(os.path.join(root, name), 'r+') as file:
                    text = file.read()
                text = cc.convert(text)
                with open(os.path.join(root, name), 'w') as file:
                    file.write(text)


def main():
    path = get_file_name(epub_path)  # grnerate temp file path
    unzip(path, epub_path)  # Unzip epub file
    os.chdir(path)  # Change path
    CN_to_TW(path)  # Translate zh_CN to zh_TW with OpenCC
    zip(path)  # Pack epub file
    shutil.rmtree(path)  # Delete temp files
    print('Sucessful')


if __name__ == '__main__':
    main()
