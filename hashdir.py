import hashlib, os

def hash(directory, verbose=False):
    SHAhash = hashlib.md5()
    for root, dirs, files in os.walk(directory):
        for names in files:
            filepath = os.path.abspath(os.path.expanduser(os.path.join(root, names)))
            if verbose:
                print 'Hashing', filepath
            try:
                f1 = open(filepath, 'rb')
                while 1:
                # Read file in as little chunks
                    buf = f1.read(4096)
                    if not buf : break
                    SHAhash.update(hashlib.md5(buf).hexdigest())

            finally:
              f1.close()
              SHAhash.update(hashlib.md5(filepath).hexdigest())

    return SHAhash.hexdigest()
