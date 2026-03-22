import os
def get_procject_root()->str:
    '''
    获取工程所在的根目录
    :return: 字符串根目录
    '''
    #获取当前文件的绝对路径
    path = os.path.abspath(__file__)
    #获取文件所在的文件夹绝对路径
    path = os.path.dirname(path)
    #获取工程根目录
    path = os.path.dirname(path)
    return path

def get_abs_path(path:str)->str:
    '''
    获取绝对路径
    :param path: 相对路径
    :return: 绝对路径
    '''
    return os.path.join(get_procject_root(),path)

if __name__ == '__main__':
    print(get_abs_path("config/config.ini"))