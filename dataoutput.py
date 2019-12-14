#!python


class DataOutput:
    """Handles output to either file or console"""

    def __init__(self, datafile=None):
        self.datafile = datafile

    def write(self, data):
        if self.datafile is not None and self.datafile != "stdout":
            try:
                with open(self.datafile, 'w') as f:
                    for line in data:
                        f.write(line)
            except:
                print("Error opening file {}".format(self.datafile))
                exit(1)
        else:
            for line in data:
                print(line)
