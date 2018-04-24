"""
pacmel package creation script

@author: eric
"""
import os
import pacmel
from pprint import pprint

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PACMEL_DIR = os.path.join(_THIS_DIR, 'pacmel')


def pac_yourself():
    """
    packs the necessary files of itself into a pacmel.mel
    """
    _PACMEL_DIR

    # provide a code snippet to execute
    install_code = os.path.join(_THIS_DIR, 'pacmel.install.snippet')

    # create a path to target mel file
    mel = os.path.join(_THIS_DIR, 'pacmel.mel')
    # and fire it of:
    file_tuple = pacmel.get_dir_file_tuple(_PACMEL_DIR)
    file_tuple.append((os.path.join(_THIS_DIR, 'LICENSE'), os.path.join('pacmel', 'LICENSE')))
    pprint(file_tuple)
    pacmel.pac(file_tuple, mel, install_code)
    print('mel: %s' % mel)


if __name__ == '__main__':
    pac_yourself()
