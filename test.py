'''
Test for pacmel. Should be run with a Maya environment

@created 19.04.2018
@author: eric
'''
import os
import uuid
import unittest
from maya import mel

import pacmel
import time


TESTCODE = """
d = {'_pacmel_dir': _pacmel_dir,
     '_pacmel_files': _pacmel_files}
tmp_json = '%s'
import json
with open(tmp_json, 'w') as fob:
    json.dump(d, fob)
"""


class Test(unittest.TestCase):
    def test_single_file(self):
        rndstr = 'pacmel_test_' + str(uuid.uuid4())
        temp_dir = os.path.join(os.getenv('TEMP'), rndstr)
        self.assertFalse(os.path.isdir(temp_dir))
        os.makedirs(temp_dir)
        self.assertTrue(os.path.isdir(temp_dir))

        tempfile = os.path.join(temp_dir, 'testfile.tmp')
        with open(tempfile, 'w') as fobj:
            fobj.write(rndstr)

        files = [tempfile]
        target_mel = os.path.join(os.getenv('TEMP'), rndstr + '.mel')
        self.assertFalse(os.path.isfile(target_mel))

        tmp_json = os.path.join(os.getenv('TEMP'), '%s.json' % rndstr)
        self.assertFalse(os.path.isfile(tmp_json))

        code_to_exec = TESTCODE % tmp_json

        pacmel.pac(files, target_mel, code_to_exec)
        self.assertTrue(os.path.isfile(target_mel))

        # now call maya to execute the mel file:
        mel.eval('source "%s";' % target_mel.replace('\\', '/'))

        self.assertTrue(os.path.isfile(tmp_json))

        import json
        with open(tmp_json) as fob:
            tmpdata = json.load(fob)

        self.assertTrue(os.path.isdir(tmpdata['_pacmel_dir']))
        self.assertEqual(len(tmpdata['_pacmel_files']), 1)
        self.assertTrue(os.path.isfile(tmpdata['_pacmel_files'][0]))

        with open(tmpdata['_pacmel_files'][0]) as fob:
            self.assertEqual(fob.read(), rndstr)

        # cleanup files
        for path in [tempfile, tmp_json, tmpdata['_pacmel_files'][0]]:
            os.remove(path)
            self.assertFalse(os.path.isfile(path))
        for path in [temp_dir, tmpdata['_pacmel_dir']]:
            os.rmdir(path)
            self.assertFalse(os.path.isdir(path))


if __name__ == '__main__' or __name__ == 'test':
    t0 = time.time()
    import maya.standalone
    maya.standalone.initialize(name='python')
    print('\nstandalone.init took: %.1fsec' % (time.time() - t0))

if __name__ == '__main__':
    unittest.main(verbosity=2)
