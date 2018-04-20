# pacmel
Maya package creation utility

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

Yet another tool for tools ... pacmel started off as a tiny part in another spare time project: melDrop which is supposed to be a kind of package manager ui for the Maya 3D software.

In contrast to melDrop pacmel now has a nice and tiny functional scope. 
