from django.core.files.storage import Storage


# class MyStorage(Storage):
#     def _open(self, name, mode='rb'):
#         pass
#
#     def _save(self, name, content):
#         pass
#
#     def url(self, name):
#         return "http://192.168.48.133:8888/" + name
class MyStorage(Storage):
    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        pass

    def url(self, name):
        # 默认url是返回name
        # 当前的name 就是 file_id
        # group1/M00/00/01/CtM3BVrLmiKANEeLAAFfMRWFbY86177278

        return "http://192.168.48.133:8888/" + name
