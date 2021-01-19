import os
import shutil
import zipfile
import ebooklib
from ebooklib import epub
from opencc import OpenCC
cc = OpenCC('s2t')
epub_path = '/Users/chunyen/Downloads/投资最重要的事(全新升级版).epub'
path = '/Users/chunyen/Downloads/convert'


def mkdir(path):
    # 判斷目錄是否存在
    folder = os.path.exists(path)
    if not folder:
        # 如果不存在，則建立新目錄
        os.makedirs(path)
        print('-----建立成功-----')
    else:
        # 如果目錄已存在，則不建立，提示目錄已存在
        print(path+' 目錄已存在')


def zip(path):
    zf = zipfile.ZipFile('{}.epub'.format(path), 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for name in files:
            zf.write(os.path.join(root, name))


def unzip(path, epub_path):
    mkdir(path)
    os.chdir(path)
    zf = zipfile.ZipFile(epub_path, 'r')
    zf.extractall()


def CN_to_TW(path):
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if name.endswith(".html"):
                # create new html file
                file = open(os.path.join(root, name), 'r+')
                text = file.read()
                file.close()
                text = cc.convert(text)
                file = open(os.path.join(root, name), 'w')
                file.write(text)  # write in content
                file.close()


unzip(path, epub_path)
os.chdir(path)  # change address
CN_to_TW(path)
zip(path)
shutil.rmtree(path)
