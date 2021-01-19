import ebooklib
import os
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


def html(path, name, text):
    os.chdir(path)  # change address
    file = open(name, 'w')  # create new html file
    file.write(text)  # write in content
    file.close()


def epubTohtml(epub_path, path):
    mkdir(path)
    book = epub.read_epub(epub_path)
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        converted = cc.convert(item.get_content())
        html(path+'/OEBPS', item.get_name(), converted)


epubTohtml(epub_path, path)
