"""
http://gabrielelanaro.github.io/blog/2014/12/12/extract-docstrings.html

python mydocstringtest/__main__.py --module "mydocstringtest" --exclude "mydocstringtest\nested" "any\other\exclusion" > readme.md
"""
import argparse
import ast
import textwrap
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Convert script to markdown.')
    parser.add_argument('--module', type=str, help='path to module .. all nested *.py files are taken into account')
    parser.add_argument('--target', type=str, help='list of excluded files resp. folders')
    parser.add_argument('--exclude', nargs='*', help='list of excluded files resp. folders', default=[])
    args = parser.parse_args()

    files = [f for f in Path(args.module).rglob('*.py')
             if not f.name.startswith('__init__')]

    for e in args.exclude:
        files = [f for f in files
                 if not str(f).startswith(e)]

    def write(file, text):
        file.write(text + "\n")

    for file in files:
        relpath = os.path.relpath(str(file), args.module)  # cut the path to module
        target_path = os.path.join(args.target, relpath)  # join the relative path with the target folder
        path = os.path.splitext(target_path)[0] + ".md"  # change file extension '.py' to '.md'

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))  # create directories if not existing

        with open(path, "x") as output:
            with open(str(file)) as fd:
                file_contents = fd.read()
            module = ast.parse(file_contents)

            write(output, "# {}".format(os.path.basename(str(file))))
            write(output, "*{}*".format(relpath.replace("\\", "/")))

            def extract(nodes, level):
                for node in nodes:
                    if level == 2 and isinstance(node, ast.Expr):
                        docstring = None
                        try:
                            docstring = node.value.s
                        except AttributeError:
                            pass
                        if docstring is not None:
                            write(output, "```")
                            write(output, node.value.s[1:-1])
                            write(output, "```")

                    if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                        headline = "{} {}".format("#"*level, node.name)
                        if isinstance(node, ast.FunctionDef):
                            if len(node.args.args) > 0:
                                headline = headline + "("

                            for i, par in enumerate(node.args.args):
                                if i != 0:
                                    headline = headline + ", "
                                # headline = headline + par.arg + ": " + type(par.arg).__name__
                                headline = headline + par.arg

                            if len(node.args.args) > 0:
                                headline = headline + ")"
                        write(output, headline)

                        if ast.get_docstring(node) is not None:
                            write(output, "```")
                            write(output, textwrap.dedent(ast.get_docstring(node)))
                            write(output, "```")
                        else:
                            write(output, "Description missing.")

                        if len(node.body) > 0:
                            extract(node.body, level+1)

            extract(module.body, 2)


if __name__ == "__main__":
    main()
