"""
http://gabrielelanaro.github.io/blog/2014/12/12/extract-docstrings.html

python mydocstringtest/__main__.py --module "mydocstringtest" --exclude "mydocstringtest\nested" "any\other\exclusion" > readme.md
"""
import argparse
import ast
import textwrap
import os
from enum import Enum
from pathlib import Path

INDENT = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'


class Required(Enum):
    NO = "No"
    YES = "Yes"


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

            def extract(nodes, level, is_enum=False):
                for nx, node in enumerate(nodes):
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

                    if is_enum and isinstance(node, ast.Assign):
                        write(output, '| {} | {} |'.format(node.targets[0].id, node.value.s))
                        if nx == len(nodes)-1:
                            write(output, '')  # Additional linebreak after enumeration table

                    if isinstance(node, ast.AnnAssign):
                        write(output, '**{}**\n'.format(node.target.id))
                        default_value = None
                        required = Required.YES
                        if isinstance(node.value, ast.NameConstant):
                            default_value = node.value.value
                            required = Required.NO
                        write(output, INDENT + 'Required: {}\n'.format(required.value))
                        if required is Required.NO:
                            write(output, INDENT + 'Default: {}\n'.format(default_value))
                        if hasattr(node.annotation, 'id'):
                            type_value = node.annotation.id
                        else:
                            type_value = '{}[{}]'.format(node.annotation.value.id, node.annotation.slice.value.id)
                        write(output, INDENT + 'Type: {}\n'.format(type_value))

                    if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                        is_enum = False
                        if hasattr(node, 'bases') is True and any(hasattr(b, 'id') and b.id == 'Enum' for b in node.bases):
                            is_enum = True

                        headline = "{} {}".format("#"*level, node.name)
                        headline = headline + "("
                        if isinstance(node, ast.ClassDef) and hasattr(node, 'bases') is True:
                            for i, par in enumerate(node.bases):
                                if i != 0:
                                    headline = headline + ", "
                                if hasattr(par, 'id'):
                                    headline = headline + par.id
                                elif hasattr(par, 'attr'):
                                    headline = headline + par.attr

                        if isinstance(node, ast.FunctionDef):
                            for i, par in enumerate(node.args.args):
                                if i != 0:
                                    headline = headline + ", "
                                headline = headline + par.arg
                                if hasattr(par, 'annotation') and hasattr(par.annotation, 'id'):
                                    headline = headline + ': ' + par.annotation.id

                        headline = headline + ")"
                        write(output, headline)

                        if ast.get_docstring(node) is not None:
                            write(output, "```")
                            write(output, textwrap.dedent(ast.get_docstring(node)))
                            write(output, "```")
                        else:
                            write(output, "Description missing.\n")

                        if is_enum:
                            write(output, '| Name | Value |')
                            write(output, '| --- | --- |')

                        if len(node.body) > 0:
                            extract(nodes=node.body, level=level+1, is_enum=is_enum)

            extract(module.body, 2)


if __name__ == "__main__":
    main()
