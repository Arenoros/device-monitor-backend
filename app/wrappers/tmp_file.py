import os
import tempfile

class TempFile:
    # 
    def __init__(self):
        #fd = os.open(path, flags, mode) 
        self._hndl, self.path = tempfile.mkstemp(suffix='.ptmp')
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.remove()
        pass
    
    def remove(self):
        os.close(self._hndl)
        os.unlink(self.path)

    def write(self, data):
        if type(data) is bytes:
            os.write(self._hndl, data)
        else:
            os.write(self._hndl, data.encode())

    @property
    def fd(self):
        return self._handl

    def read(self):
        os.lseek(fd, 0, 0) 
        data = os.read(self._hndl, os.path.getsize(fd))
        return data.decode()
