"""
pacmel - Maya deployment utility.
https://github.com/ewerybody/pacmel
"""
from pacmel import pac, pac_dir, get_dir_file_tuple


def uninstall():
    """
    Since there is no pip in Maya. We need to help ourselves this way
    """
    from maya import cmds
    if not cmds.about(batch=True):
        result = cmds.confirmDialog(
            title='Uninstall pacmel',
            message='Are you sure to delete any pacmel files?',
            button=['Yes', 'Cancel'],
            icon='critical')
        if result != 'Yes':
            return
    _uninstall()


def _uninstall():
    # remove the files
    import os
    import shutil
    import uuid
    pacmel_dir = os.path.dirname(os.path.abspath(__file__))
    tmp_dir = os.path.join(os.getenv('TEMP'), str(uuid.uuid4()))
    os.rename(pacmel_dir, tmp_dir)
    shutil.rmtree(tmp_dir)
    if not os.path.isdir(pacmel_dir):
        print('pacmel successfully removed! (%s)' % pacmel_dir)

    # remove the module from python
    import sys
    for m in [m for m in sys.modules if m.startswith('pacmel')]:
        del sys.modules[m]
    try:
        del sys.modules['__main__'].pacmel
    except Exception:
        pass
