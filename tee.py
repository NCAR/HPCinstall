import sys

class tee_out :
    def __init__(self, logfile):
        self.stdout = sys.stdout
        self.log = logfile

    def __del__(self) :
        self.close()

    def close(self):
        self.log.close()
        sys.stdout = self.stdout

    def write(self, text) :
        self.stdout.write(text)
        self.log.write(text)

    def flush(self) :
        self.stdout.flush()
        self.log.flush()

_open_tees = []

def close_all_files():
    for t in _open_tees:
        t.close()

def overwrite_out_to(filename):
    sys.stdout = tee_out(open(filename, "w"))
    _open_tees.append(sys.stdout)

def overwrite_err_to(filename):
    saved = sys.stderr
    outputlog = open(filename, "w")
    sys.stderr = tee(saved, outputlog)
    _open_tees.append(sys.stderr)

