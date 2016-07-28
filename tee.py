import sys

class tee :
    def __init__(self, _fd1, _fd2) :
        self.fd1 = _fd1
        self.fd2 = _fd2

    def __del__(self) :
        self.close()

    def close(self):
        if self.fd1 != sys.stdout and self.fd1 != sys.stderr :
            self.fd1.close()
        if self.fd2 != sys.stdout and self.fd2 != sys.stderr :
            self.fd2.close()

    def write(self, text) :
        self.fd1.write(text)
        self.fd2.write(text)

    def flush(self) :
        self.fd1.flush()
        self.fd2.flush()

_open_tees = []

def close_all_files():
    for t in _open_tees:
        t.close()

def overwrite_out_to(filename):
    saved = sys.stdout
    outputlog = open(filename, "w")
    sys.stdout = tee(saved, outputlog)
    _open_tees.append(sys.stdout)

def overwrite_err_to(filename):
    saved = sys.stderr
    outputlog = open(filename, "w")
    sys.stderr = tee(saved, outputlog)
    _open_tees.append(sys.stderr)

