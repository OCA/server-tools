# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 XCG Consulting
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import os.path
import sys


def main():
    if len(sys.argv) != 4:
        print("usage: autotodo.py <folder> <exts> <tags>")
        sys.exit(1)

    folder = sys.argv[1]
    exts = sys.argv[2].split(',')
    tags = sys.argv[3].split(',')
    todolist = {tag: [] for tag in tags}

    os.path.walk(folder, scan_folder, (exts, tags, todolist))
    create_autotodo(folder, todolist)


def write_info(f, infos, folder):
    # Check sphinx version for lineno-start support

    import sphinx

    if sphinx.version_info < (1, 3):
        lineno_start = False
    else:
        lineno_start = True

    for i in infos:
        path = i[0]
        line = i[1]
        lines = (line - 3, line + 4)
        class_name = (
            ":class:`%s`" %
            os.path.basename(os.path.splitext(path)[0])
        )
        f.write(
            "%s\n"
            "%s\n\n"
            "Line %s\n"
            "\t.. literalinclude:: %s\n"
            "\t\t:language: python\n"
            "\t\t:lines: %s-%s\n"
            "\t\t:emphasize-lines: %s\n"
            %
            (
                class_name,
                "-" * len(class_name),
                line,
                path,
                lines[0], lines[1],
                line,
            )
        )
        if lineno_start:
            f.write("\t\t:lineno-start: %s\n" % lines[0])
        f.write("\n")


def create_autotodo(folder, todolist):
    with open('autotodo', 'w+') as f:
        for tag, info in todolist.iteritems():
            f.write("%s\n%s\n\n" % (tag, '=' * len(tag)))
            write_info(f, info, folder)


def scan_folder((exts, tags, res), dirname, names):
    file_info = {}
    for name in names:
        (root, ext) = os.path.splitext(name)
        if ext in exts:
            file_info = scan_file(os.path.join(dirname, name), tags)
            for tag, info in file_info.iteritems():
                if info:
                    res[tag].extend(info)


def scan_file(filename, tags):
    res = {tag: [] for tag in tags}
    with open(filename, 'r') as f:
        for line_num, line in enumerate(f):
            for tag in tags:
                if tag in line:
                    res[tag].append((filename, line_num, line[:-1].strip()))
    return res


if __name__ == "__main__":
    main()
