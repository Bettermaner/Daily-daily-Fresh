from django.core.files.storage import FileSystemStorage
from fdfs_client.client import *


class FdfsStorage(FileSystemStorage):

    def _save(self, name, content):
        client = Fdfs_client('/etc/fdfs/client.conf')
        try:
            data = content.read()
            ret = client.upload_by_buffer(data)
            print(ret)
        except Exception as e:
            print(e)
        if ret.get('Status') != 'Upload successed.':
            raise Exception('FastDFS上传文件失败, Status不正确.')
        path = ret.get('Remote file_id')
        print(path)
        return path

    def url(self, name):
        return 'http://127.0.0.1:8888/'+super().url(name)

