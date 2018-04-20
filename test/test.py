'''
Test for pacmel. Should be run with a Maya environment

@created 19.04.2018
@author: eric
'''
import os
import json
import uuid
import time
import unittest

from maya import mel

import pacmel
import hashlib


_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_TESTCODE = """
d = {'_pacmel_dir': _pacmel_dir,
     '_pacmel_files': _pacmel_files}
tmp_json = '%s'
import json
with open(tmp_json, 'w') as fob:
    json.dump(d, fob)
"""


class Test(unittest.TestCase):

    def test_single_file_code_snippet(self):
        rndstr, files, target_mel, tmp_json, temp_dir = make_simple_setup()

        code_to_exec = _TESTCODE % tmp_json

        pacmel.pac(files, target_mel, code_to_exec)
        self.assertTrue(os.path.isfile(target_mel))

        # now call maya to execute the mel file:
        mel.eval('source "%s";' % target_mel.replace('\\', '/'))

        self.assertTrue(os.path.isfile(tmp_json))

        with open(tmp_json) as fob:
            pacmel_vars = json.load(fob)

        self.assertTrue(os.path.isdir(pacmel_vars['_pacmel_dir']))
        self.assertEqual(len(pacmel_vars['_pacmel_files']), 1)
        self.assertTrue(os.path.isfile(pacmel_vars['_pacmel_files'][0]))

        with open(pacmel_vars['_pacmel_files'][0]) as fob:
            self.assertEqual(fob.read(), rndstr)

        cleanup([files[0], tmp_json, pacmel_vars['_pacmel_files'][0], target_mel],
                [temp_dir, pacmel_vars['_pacmel_dir']])

    def test_single_file_code_file(self):
        rndstr, files, target_mel, _, temp_dir = make_simple_setup()

        tmp_json = os.path.join(os.getenv('TEMP'),
                                '%s.json' % 'pacmel_test_c6af51ca-3b34-457a-9dba-626d0de3e98d')
        if os.path.isfile(tmp_json):
            self.skipTest('json testfile already exists: %s' % tmp_json)

        code_to_exec = os.path.join(_THIS_DIR, 'py_test_code')
        self.assertTrue(os.path.isfile(code_to_exec))

        pacmel.pac(files, target_mel, code_to_exec)
        self.assertTrue(os.path.isfile(target_mel))

        # now call maya to execute the mel file:
        mel.eval('source "%s";' % target_mel.replace('\\', '/'))

        self.assertTrue(os.path.isfile(tmp_json))

        with open(tmp_json) as fob:
            pacmel_vars = json.load(fob)

        self.assertTrue(os.path.isdir(pacmel_vars['_pacmel_dir']))
        self.assertEqual(len(pacmel_vars['_pacmel_files']), 1)
        self.assertTrue(os.path.isfile(pacmel_vars['_pacmel_files'][0]))

        with open(pacmel_vars['_pacmel_files'][0]) as fob:
            self.assertEqual(fob.read(), rndstr)

        cleanup([files[0], tmp_json, pacmel_vars['_pacmel_files'][0], target_mel],
                [temp_dir, pacmel_vars['_pacmel_dir']])

    def test_pac_dir(self):
        rndstr = 'pacmel_test_' + str(uuid.uuid4())
        tmp_json = os.path.join(os.getenv('TEMP'), '%s.json' % rndstr)
        code_to_exec = _TESTCODE % tmp_json
        target_mel = os.path.join(os.getenv('TEMP'), rndstr + '.mel')
        test_dir = os.path.dirname(pacmel.__file__)

        pacmel.pac_dir(test_dir, target_mel, code_to_exec)
        self.assertTrue(os.path.isfile(target_mel))
        # now call maya to execute the mel file:
        mel.eval('source "%s";' % target_mel.replace('\\', '/'))
        self.assertTrue(os.path.isfile(tmp_json))

        with open(tmp_json) as fob:
            pacmel_vars = json.load(fob)

        self.assertEqual(len(pacmel_vars['_pacmel_files']), len(os.listdir(test_dir)))
        root_dir = os.path.dirname(test_dir)
        for pacpath in pacmel_vars['_pacmel_files']:
            relpath = os.path.relpath(pacpath, pacmel_vars['_pacmel_dir'])
            this_test = os.path.join(root_dir, relpath)
            self.assertEqual(file_hash(pacpath), file_hash(this_test))

        cleanup_folders = [os.path.dirname(pacmel_vars['_pacmel_files'][0]),
                           pacmel_vars['_pacmel_dir']]
        cleanup([tmp_json, target_mel] + pacmel_vars['_pacmel_files'],
                cleanup_folders)


def make_simple_setup():
    rndstr = 'pacmel_test_' + str(uuid.uuid4())
    temp_dir = os.path.join(os.getenv('TEMP'), rndstr)
    assert(os.path.isdir(temp_dir) is False)
    os.makedirs(temp_dir)
    assert(os.path.isdir(temp_dir))

    tempfile = os.path.join(temp_dir, 'testfile.tmp')
    with open(tempfile, 'w') as fobj:
        fobj.write(rndstr)

    files = [tempfile]
    target_mel = os.path.join(os.getenv('TEMP'), rndstr + '.mel')
    assert(os.path.isfile(target_mel) is False)

    tmp_json = os.path.join(os.getenv('TEMP'), '%s.json' % rndstr)
    assert(os.path.isfile(tmp_json) is False)
    return rndstr, files, target_mel, tmp_json, temp_dir


def cleanup(files, dirs):
    for path in files:
        os.remove(path)
        assert(os.path.isfile(path) is False)
    for path in dirs:
        os.rmdir(path)
        assert(os.path.isdir(path) is False)


def file_hash(path):
    with open(path, 'rb') as fob:
        buff = fob.read(65536)
        hashob = hashlib.sha256()
        while len(buff):
            hashob.update(buff)
            buff = fob.read(65536)
        return hashob.digest()


if __name__ == '__main__' or __name__ == 'test.test':
    t0 = time.time()
    import maya.standalone
    maya.standalone.initialize(name='python')
    print('\nstandalone.init took: %.3fs' % (time.time() - t0))

if __name__ == '__main__':
    unittest.main(verbosity=2)
