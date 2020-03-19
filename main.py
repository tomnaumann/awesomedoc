"""
http://gabrielelanaro.github.io/blog/2014/12/12/extract-docstrings.html

python mydocstringtest/main.py --module "mydocstringtest" --exclude "mydocstringtest\nested" "any\other\exclusion" > readme.md
"""
import argparse
import ast
import textwrap
import os
from pathlib import Path

parser = argparse.ArgumentParser(description='Convert script to markdown.')
parser.add_argument('--module', type=str, help='path to module .. all nested *.py files are taken into account')
parser.add_argument('--target', type=str, help='list of excluded files resp. folders')
parser.add_argument('--exclude', nargs='*', help='list of excluded files resp. folders', default=[])

args = parser.parse_args()
# args.module = "src/mydocstringtest/"

files = [f for f in Path(args.module).rglob('*.py')
         if not f.name.startswith('__init__')]

for e in args.exclude:
    files = [f for f in files
             if not str(f).startswith(e)]

for file in files:
    path = os.path.splitext(str(file))[0] + ".md"  # change file extension from '.py' to '.md'
    path = os.path.relpath(path, args.module)  # cut the path to module
    path = os.path.join(args.target, path)  # join the relative path with the target folder
    os.makedirs(os.path.dirname(path))  # create directories if not existing
    f = open(path, "x")
    f.write("Now the file has more content!")
    f.close()


    # with open(str(file)) as fd:
    #     file_contents = fd.read()
    #
    # module = ast.parse(file_contents)
    #
    #
    # def extract(nodes, level):
    #     for node in nodes:
    #         if level == 2 and isinstance(node, ast.Expr):
    #             docstring = None
    #             try:
    #                 docstring = node.value.s
    #             except AttributeError:
    #                 pass
    #             if docstring is not None:
    #                 print("```")
    #                 print(node.value.s[1:-1])
    #                 print("```")
    #
    #         if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
    #             headline = "{} {}".format("#"*level, node.name)
    #             if isinstance(node, ast.FunctionDef):
    #                 if len(node.args.args) > 0:
    #                     headline = headline + "("
    #
    #                 for i, par in enumerate(node.args.args):
    #                     if i != 0:
    #                         headline = headline + ", "
    #                     # headline = headline + par.arg + ": " + type(par.arg).__name__
    #                     headline = headline + par.arg
    #
    #                 if len(node.args.args) > 0:
    #                     headline = headline + ")"
    #             print(headline)
    #
    #             if ast.get_docstring(node) is not None:
    #                 print("```")
    #                 print(textwrap.dedent(ast.get_docstring(node)))
    #                 print("```")
    #             else:
    #                 print("Description missing.")
    #
    #             if len(node.body) > 0:
    #                 extract(node.body, level+1)
    #
    #
    # extract(module.body, 2)
