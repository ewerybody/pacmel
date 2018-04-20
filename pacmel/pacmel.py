"""
melDrop.pacmel
Super simple Maya deployment utility.

You give it a bunch of files,
a snippet of code to execute and
a target mel file name.

It zips the given files, base64 encodes them along with the code snippet
and creates a Maya droppable mel file.

When dropped onto maya the mel code hands the base64 to python
which decodes, extracts to temp and calls the snippet with a list of the files given.

@created: 14.04.2016
@author: eric
"""
import os
import uuid
import base64
import zipfile
from StringIO import StringIO


_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_PATH = os.path.join(_THIS_DIR, 'pacmel.template')


def pac(files, mel, code_to_exec):
    """
    Assembles the given files into a zip, translates to base64, puts this into
    a mel string and amends a code snipped to be executed after the final extraction.

    In this code snipped there will be 2 variables available:
        _pacmel_dir - A string path to the extracted folder.
        _pacmel_files - The list of files in the folder.

    :param list files: list of files to bundle. Alternatively you can put tuples
        into the list which are like (source_path, path_in_zip). these ignore the
        "pack_flat" setting.
    :param str mel: target mel file path
    :param str code_to_exec: String snippet to execute after the extraction, or
        string path to a .py-file which would be read instead.
    """
    if not isinstance(files, list):
        raise TypeError('Please provide files as a list of paths'
                        'or list of tuples (path, archive_path)!')

    # prepare the file list
    file_tuples = []
    for item in files:
        if isinstance(item, tuple):
            filepath, arcname = item
        else:
            filepath = item
            arcname = os.path.basename(item)
        if not os.path.isfile(filepath):
            raise RuntimeError('File not existent: "%s"' % filepath)
        else:
            file_tuples.append((filepath, arcname))

    # zip the given files to memory
    zip_file_obj = StringIO()
    with zipfile.ZipFile(zip_file_obj, 'w', zipfile.ZIP_DEFLATED) as zipzob:
        for filepath, arcname in file_tuples:
            zipzob.write(filepath, arcname)

    # encode into mel
    zipblob = base64.encodestring(zip_file_obj.getvalue()).replace('\n', '\\\n')
    mel_code = 'string $zipblob = "\\\n' + zipblob + '";\n'

    # append python code
    with open(_TEMPLATE_PATH, 'r') as fobj:
        py_code = fobj.read()

    if os.path.isfile(code_to_exec):
        with open(code_to_exec, 'r') as fobj:
            code_to_exec = fobj.read()

    # create code blob, put it to mel code as well
    zip_code_obj = StringIO()
    with zipfile.ZipFile(zip_code_obj, 'w', zipfile.ZIP_DEFLATED) as zipzob:
        zipzob.writestr('codeblob', code_to_exec)
    codeblob = base64.encodestring(zip_code_obj.getvalue()).replace('\n', '\\\n')
    mel_code += 'string $codeblob = "\\\n' + codeblob + '";\n'

    py_code = py_code.format(zipname='pacmel_%s' % str(uuid.uuid4()))
    py_code = py_code.replace('\r\n', '\\n\\\n')

    c = """python("%s");""" % py_code
    mel_code += c + '\n'

    # write the mel file
    with open(mel, 'w') as fobj:
        fobj.write(mel_code)


def pac_dir(path, mel, code_to_exec):
    """
    Given a path to a directory it will assemble all the file/folder
    structure as list of tuples like::

        [(fullpath/dirname/filename1, dirname/filename1),
         (fullpath/dirname/filename2, dirname/filename2),
         ...]

    and hand it to pacmel.

    :param str path: String path to existing.
    :param str mel: target mel file path
    :param str code_to_exec: String snippet to execute after the extraction, or
        string path to a .py-file which would be read instead.
    """
    if not os.path.isdir(path):
        raise RuntimeError('Given path is not an existing directory! (%s)' % path)

    parent_dir = os.path.dirname(path)
    file_tuples = []
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            arcpath = os.path.relpath(filepath, parent_dir)
            file_tuples.append((filepath, arcpath))
    if not file_tuples:
        raise RuntimeError('There were no files to collect at given path! (%s)' % path)

    pac(file_tuples, mel, code_to_exec)
