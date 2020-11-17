# **pacmel** - a Maya package creation utility

You give it:
* a bunch of file paths
* a target .mel-path
* a code snippet

It gives you:
* a mel file that can be dropped onto Maya

When dropped:
* the original files are extracted to temp
* your code snippet is executed with the path and the list of files in variables
  * `_pacmel_dir`
  * `_pacmel_files`

Yet another tool for tools ... pacmel started off as a tiny part in another spare time project: [melDrop](https://github.com/ewerybody/melDrop) which is supposed to be a kind of package manager ui for the Maya 3D software.

In contrast to melDrop pacmel now has a nice and tiny functional scope. 



### how does this .mel file look like?
* **`$zipblob`** variable contains the zipped files in the package as one huge base64 string
* **`$codeblob`** contains the code that the packages install script also zipped and converted to base64 to work nicely with mel
* one single mel call to `python` with a script that
  * builds a path to a pacmel temp directory
  * decodes the base64 strings to in memory zip-file objects
  * unzipps the files to the pacmel temp
  * reads the codeblob zip
  * calls `exec` with the codeblob and `_pacmel_dir` and `_pacmel_files` in the globals so they are available to the install script

For example:
```mel
string $zipblob = "\
UEsDBBQAAAAIAOeRk0zvGL1jUgAAAFAAAAAbAAAAcGFjbWVsL3BhY21lbCBvbiBnaXRodWIuVVJM\
i/bMK0ktykstCc7ILypJLi2J5eUKDfKxzSgpKSi20tdPzyzJKE3SS87P1U8tTy2qTMpPqdQvSEzO\
Tc3h5fJ08cksLrHl5fLIL/FOrbQ14OUCAFBLAwQUAAAACABFbphMhkEeI7EGAADqEwAAEAAAAHBh\
...
Y21lbC50ZW1wbGF0ZVBLAQIUABQAAAAIAHlwmEzvdZ5MQAIAAMQEAAASAAAAAAAAAAAAAAC2gbsI\
AABwYWNtZWwvX19pbml0X18ucHlQSwECFAAUAAAACABigZNMptGMugkwAADtiwAADgAAAAAAAAAA\
AAAAtoErCwAAcGFjbWVsL0xJQ0VOU0VQSwUGAAAAAAUABQBHAQAAYDsAAAAA\
";
string $codeblob = "\
UEsDBBQAAAAIAENxmEwizkRr7gUAAIYUAAAIAAAAY29kZWJsb2KtWEtv3DYQvutXcA0EktCNDm2d\
g4FFEeQBBEWbIHF7cQyBK1FeNhKpkpSd/fedIfWgKO16gYaHtSUO5/XNi7q6uopaWjSsJlxoQ+ua\
ZvZVACPyk71wWUPSE452nwWiZal/dtxxp4ORJ4LoGz6V2fgbr7wuQhTlYPHnDqa/xpUG9DpkGLYB\
...
uNrJri7tjKs6cJWATNBEPonNV0HIByz96CmYLmFwK8lJT8WIIMyYJbAUHNodXIBlpwpmGzlgR1a+\
/OFXp6nwnPu+19/E6zNE0X9QSwECFAAUAAAACABDcZhMIs5Ea+4FAACGFAAACAAAAAAAAAAAAAAA\
gAEAAAAAY29kZWJsb2JQSwUGAAAAAAEAAQA2AAAAFAYAAAAA\
";
python("import os, base64, zipfile, StringIO\n\
_pacmel_dir = os.path.join(os.getenv('TEMP'), 'pacmel_dfcfe75d-d02e-41e2-b574-9341584d9628')\n\
_pacmel_files = []\n\
_fob, _cob = StringIO.StringIO(), StringIO.StringIO()\n\
_fob.write(base64.decodestring('" + $zipblob + "'))\n\
_cob.write(base64.decodestring('" + $codeblob + "'))\n\
with zipfile.ZipFile(_fob, 'r') as tmpzip:\n\
    for f in tmpzip.namelist():\n\
        _pacmel_files.append(tmpzip.extract(f, _pacmel_dir))\n\
with zipfile.ZipFile(_cob, 'r') as tmpzip:\n\
    _code_blob = tmpzip.read('codeblob')\n\
exec(_code_blob, {'_pacmel_dir': _pacmel_dir, '_pacmel_files': _pacmel_files})\n\
");
```
