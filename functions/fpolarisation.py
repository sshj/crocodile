# Tim Cornwell <realtimcornwell@gmail.com>
#
# Definition of structures needed by the function interface. These are mostly
# subclasses of astropy classes.
#

from astropy.table import Table


class fmkernel(Table):
    """ Mueller kernel with NDData, antenna1, antenna2, time
    """

class fjones(Table):
    """ Jones kernel with NDData, antenna1, antenna2, time
    """

if __name__ == '__main__':
    import os
    print(os.getcwd())
