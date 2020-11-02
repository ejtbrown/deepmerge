# deepmerge
### Overview
File structure deep merge

Intended to merge multiple, similar copies of directory structures. It produces
an output directory that contains all of the paths and files of all of the
sources provided.

In the event of conflict (i.e. two source with the same path / filename):
- If the a file with that contents exists already in the output directory, it
  simply skips the conflict
- If the file is newer than what is presently in the output directory, it saves
  off a copy of the file presently in the output by appending the modified time
  to the filename, then copies the newer file in its place
- If the file is older than what is presently in the output directory, but has
  different contents, it copies the file into the output directory but with the
  modified time appended to the name
  
In this way, no data is lost from the source directories, but at the same time
there isn't needless duplication.

### Usage
The script takes three or more arguments:
1) The name of the destination directory (it will be created if it does not
   already exist)
2) The name of the first source directory
3) The name of the second source directory
_n_) The names of any additional source directories (separated by spaces)
