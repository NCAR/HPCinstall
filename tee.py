import sys

OUT=0
ERR=1

class _tee:
    def __init__(self, logfile, type):
        if type == OUT:
            self.stdout = sys.stdout
            self.stderr = None
        elif type == ERR:
            self.stdout = None
            self.stderr = sys.stderr
        self.log = logfile
        self.type = type

    def __del__(self) :
        self.close()

    def close(self):
        self.log.close()
        if self.type == OUT:
            sys.stdout = self.stdout
        elif type == ERR:
            sys.stderr = self.stderr

    def write(self, text):
        if self.type == OUT:
            self.stdout.write(text)
        elif type == ERR:
            self.stderr.write(text)
        self.log.write(text)

    def flush(self):
        if self.type == OUT:
            self.stdout.flush()
        elif type == ERR:
            self.stderr.flush()
        self.log.flush()

_open_tees = []

def close_all_files():
    for t in _open_tees:
        t.close()
        _open_tees.remove(t)

def overwrite_out_to(filename):
    _write_out_to(filename, "w")

def append_out_to(filename):
    _write_out_to(filename, "a")

def _write_out_to(filename, mode):
    sys.stdout = _tee(open(filename, mode), OUT)
    _open_tees.append(sys.stdout)

def overwrite_err_to(filename):
    _write_err_to(filename, "w")

def append_err_to(filename):
    _write_err_to(filename, "a")

def _write_err_to(filename, mode):
    sys.stderr = _tee(open(filename, mode), ERR)
    _open_tees.append(sys.stderr)
