## Static Python code analyser

Find style errors in your Python code file 

This analyser uses Abstract Syntax Tree and can deal with style errors like:

*`ast` features* 

- Class name not in `CamelCase`
- Function or function_argument name not in `snake_case`
- Variables in code not in `snake_case`
- Function default argument is mutable

And obvious:

- Too long lines in code
- Wrong `space` count in indentations 
- Semicolons in code only (not comments)
- Wrong comment from code offset
- Wrong empty line count before/after `def` or `class`

### Usage
```
$ python code_analyzer.py [path_to_file | path_to_dir] 
```
If directory path passed, program will go and recursively find all `.py` files
in directory

*Used things: regular expressions (`re`), file navigation (`os` and `sys`),
abstract syntax tree & OOP (`ast`)*
