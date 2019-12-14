#!python


class DataOutput:
    """Handles output to either file or console"""

    def __init__(self, datafile=None):
        self.datafile = datafile

    def write(self, data):
        for line in data:
            if self.datafile is not None and self.datafile != "stdout":
                try:
                    with open(self.datafile, 'a') as f:
                        f.write(line)
                except:
                    print("Error opening file {}".format(self.datafile))
                    exit(1)
            else:
                print(line)
