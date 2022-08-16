import ast
import os
import re
import sys
from os.path import exists

CAMEL_CASE_template = re.compile(r"([A-Z]\w+)+")

# the first element reffers to "S001", the second to "S002" and so on.
errors = (('S001', 'Too long. Please make sure that each line is no longer than 49 characters'),
          ('S002', 'Indentation is not a multiple of four'),
          ('S003', 'Unnecessary semicolon after a statement (note that semicolons are acceptable in comments)'),
          ('S004', 'Less than two spaces before inline comments'),
          ('S005', 'TODO found (in comments only and case-insensitive)'),
          ('S006', 'More than two blank lines preceding a code line (applies to the first non-empty line).'),
          ('S007', 'Too many spaces after construction_name (def or class)'),
          )


# ERRORS = []

def output_the_error(_path, _line, error_code):
    print(f"{_path}: Line {_line + 1}: {errors[error_code][0]}", errors[error_code][1])


def is_snake_case(var):
    template = re.compile(r"\A_*[a-z0-9]+(_?[a-z0-9]+)*_*")
    return template.match(var)  # is equivalent to re.match(template, var)


class AstAnalyzer(ast.NodeVisitor):
    def __init__(self, pth):
        self.pth = pth
        super().__init__()

    # S008
    def visit_ClassDef(self, node: ast.ClassDef):
        if not CAMEL_CASE_template.match(node.name):
            print(f"{self.pth}: Line {node.lineno}: S008 Class name class_name should be written in CamelCase.")
        self.generic_visit(node)

    # S009, S010, S012
    def visit_FunctionDef(self, node: ast.FunctionDef):
        # getting fun names
        if not is_snake_case(node.name):
            print(f"{self.pth}: Line {node.lineno}: S009 Function name <{node.name}> should be written in snake_case.")

        # getting arg names
        for x in node.args.args:
            if not is_snake_case(x.arg):
                print(f"{self.pth}: Line {node.lineno}: S010 Argument name <{x.arg}> should be written in snake_case.")

        # getting list of mutable default args just one error is enough
        mutable_default_args = [type(x) for x in node.args.defaults if isinstance(x, (ast.List, ast.Dict, ast.Set))]
        if mutable_default_args:
            print(f"{self.pth}: Line {node.lineno}: S012 The default argument value is mutable.")
        self.generic_visit(node)

    # S011
    def visit_Name(self, node: ast.Assign):
        if isinstance(node.ctx, ast.Store):
            if not is_snake_case(node.id):  # node.id == variable_name
                print(f"{self.pth}: Line {node.lineno}: S011 Variable <{node.id}> should be written in snake_case")


def scan_code(code, _path):
    for line in range(len(code)):
        comment_start_index = code[line].find("#")

        # S001 check
        if len(code[line]) > 49:
            output_the_error(_path, line, 0)

        # S002 check
        if len(code[line]) >= 5:
            identation = len(code[line]) - len(code[line].lstrip(" "))
            if identation % 4 != 0:
                output_the_error(_path, line, 1)

        # S003 check
        if ";" in code[line]:
            if any([comment_start_index == -1 and code[line][-1] == ";",
                    # semicolon as a last symbol in the string (to avoid fake warning)
                    comment_start_index > code[line].find(";")]):
                output_the_error(_path, line, 2)

        # S004 check
        if len(code[line]) >= 3 and "#" in code[line]:
            if comment_start_index > 0:  # in-line comment
                if not re.search(r"\s{2}#", code[line]):
                    output_the_error(_path, line, 3)

        # S005 check
        if "todo" in code[line].lower():
            if comment_start_index != -1 and comment_start_index < code[line].lower().find("todo"):
                output_the_error(_path, line, 4)

        # S006 check
        if line >= 2 and code[line]:
            if code[line - 1] == code[line - 2] == code[line - 3]:
                output_the_error(_path, line, 5)

        # S007 check
        if re.search(r"[class|def]\s{2,}", code[line]):
            output_the_error(_path, line, 6)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit(print("error. 2 positional arguments expected."))

    path = sys.argv[1].lower()
    if not exists(path):
        exit(print('path does not exist'))

    if path.endswith(".py"):
        with open(path, "r") as file:
            code_as_list: list = [x.strip("\n") for x in file.readlines()]
            scan_code(code_as_list, path)

        with open(path, "r") as file:
            tree = ast.parse(file.read(), type_comments=True)
            analyzer = AstAnalyzer(path)
            analyzer.visit(tree)

    else:
        python_scripts: list = []
        for dirpath, dirnames, files in os.walk(path):
            for file_name in files:
                if file_name.endswith('.py'):
                    python_scripts.append(os.path.join(dirpath, file_name))

        python_scripts: tuple = tuple(sorted(python_scripts))  # saving some memory
        for python_script in python_scripts:
            with open(python_script, "r") as file:
                code_as_list: list = [x.strip("\n") for x in file.readlines()]
                scan_code(code_as_list, python_script)

            with open(python_script, "r") as file:
                tree = ast.parse(file.read(), type_comments=True)
                analyzer = AstAnalyzer(python_script)
                analyzer.visit(tree)
