#!/bin/python3
# -*- utf-8 -*-


class DataOutput:
    """Handles output to either file or console"""

    def __init__(self, target=None):
        self.target = target

    def write(self, data):
        """
        Write data to self.target.
        @param data: str: The data to write.
        @return: None.
        """
        if self.target is not None and self.target != "stdout":
            try:
                with open(self.target, 'w') as f:
                    for line in data:
                        f.write(line)
            except:
                print("Error opening file {}".format(self.target))
                exit(1)
        else:
            for line in data:
                print(line)
