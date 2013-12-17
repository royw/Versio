# coding=utf-8
"""
Project documentation support.

Supports Sphinx (default) and EpyDoc.

Normal usage is to invoke the *doc* task.


Add the following to your *requirements.txt* file:

* Pygments
* Sphinx
* sphinx-bootstrap-theme
* sphinx-pyreverse
* sphinxcontrib-plantuml
* sphinxcontrib-blockdiag
* sphinxcontrib-actdiag
* sphinxcontrib-nwdiag
* sphinxcontrib-seqdiag

"""

__docformat__ = 'restructuredtext en'

import fnmatch
import os
import re
from herring.herring_app import task, run
from runner import system
from simple_logger import info, warning
from project_settings import Project, packages_required

required_packages = [
    'Pygments',
    'Sphinx',
    'sphinx-bootstrap-theme',
    'sphinx-pyreverse',
    'sphinxcontrib-plantuml',
    'sphinxcontrib-blockdiag',
    'sphinxcontrib-actdiag',
    'sphinxcontrib-nwdiag',
    'sphinxcontrib-seqdiag']

if packages_required(required_packages):
    from cd import cd
    from clean import clean
    from executables import executables_available
    from recursively_remove import recursively_remove
    from safe_edit import safe_edit

    @task(depends=['clean'])
    def doc_clean():
        """Remove documentation artifacts"""
        recursively_remove(os.path.join(Project.docs_dir, '_src'), '*')
        recursively_remove(os.path.join(Project.docs_dir, '_epy'), '*')
        recursively_remove(os.path.join(Project.docs_dir, '_build'), '*')

    def _name_dict(file_name):
        """extract the name dictionary from the automodule lines in the sphinx src file"""
        name_dict = {}
        with open(file_name, 'r') as in_file:
            for line in in_file.readlines():
                match = re.match(r'.. automodule:: (\S+)', line)
                if match:
                    value = match.group(1)
                    key = value.split('.')[-1]
                    if '__init__' not in value:
                        name_dict[key] = value
        return name_dict

    def _package_line(module_name):
        """create the package figure lines for the given module"""
        line = ''
        package_image = "uml/packages_{name}.svg".format(name=module_name.split('.')[-1])
        classes_image = "uml/classes_{name}.svg".format(name=module_name.split('.')[-1])
        image_path = os.path.join(Project.docs_dir, '_src', package_image)
        if os.path.exists(image_path):
            info("adding figure %s" % image_path)
            line += "\n.. figure:: {image}\n    :width: 1100 px\n\n    {name} Packages\n\n".format(
                image=package_image,
                name=module_name)
            line += "\n.. figure:: {image}\n\n    {name} Classes\n\n".format(
                image=classes_image,
                name=module_name)
        else:
            warning("%s does not exist!" % image_path)
        return line

    def _class_line(module_name, class_name):
        """create the class figure lines for the given module and class"""
        line = ''
        classes_image = "uml/classes_{module}.{name}.png".format(module=module_name, name=class_name)
        image_path = os.path.join(Project.docs_dir, '_src', classes_image)
        if os.path.exists(image_path):
            info("adding figure %s" % image_path)
            line += "\n.. figure:: {image}\n\n    {name} Class\n\n".format(
                image=classes_image,
                name=class_name)
        else:
            warning("%s does not exist!" % image_path)
        return line

    def hack_doc_src_file(file_name):
        """
        Hack the generated doc source file to add UML and inheritance diagram support.

        :param file_name: The source file generated by sphinx-apidoc
        :type file_name: str
        """
        # TODO: this is way too complex - Refactor!

        # autodoc generates:
        #
        # :mod:`ArgumentServiceTest` Module
        # ---------------------------------
        #
        # .. automodule:: util.unittests.ArgumentServiceTest
        #
        # need to add package path from automodule line to module name in mod line.

        if os.path.splitext(file_name)[1] != '.rst':
            return

        # build dict from automodule lines where key is base name, value is full name
        name_dict = _name_dict(file_name)

        module_name = os.path.splitext(os.path.basename(file_name))[0]

        # substitute full names into mod lines with base names.
        with safe_edit(file_name) as files:
            in_file = files['in']
            out_file = files['out']
            info("Editing %s" % file_name)

            line_length = 0
            package = False
            class_name = ''
            for line in in_file.readlines():
                match = re.match(r':mod:`(.+)`(.*)', line)
                if match:
                    key = match.group(1)
                    if key in name_dict:
                        value = name_dict[key]
                        line = ''.join(":mod:`%s`%s\n" % (value, match.group(2)))
                    line_length = len(line)
                    package = re.search(r':mod:.+Package', line)
                    class_name = key
                elif re.match(r'[=\-\.][=\-\.][=\-\.]+', line):
                    if line_length > 0:
                        line = "%s\n" % (line[0] * line_length)
                        if package:
                            line += _package_line(module_name)
                        else:
                            line += _class_line(module_name, class_name)
                out_file.write(line)

            out_file.write("\n\n")
            title = "%s Inheritance Diagrams" % module_name
            out_file.write("%s\n" % title)
            out_file.write('-' * len(title) + "\n\n")
            for value in sorted(name_dict.values()):
                out_file.write(".. inheritance-diagram:: %s\n" % value)
            out_file.write("\n\n")

    @task(depends=['doc_clean'])
    def api_doc():
        """Generate API sphinx source files from code"""
        with cd(Project.docs_dir):
            os.system("sphinx-apidoc -d 6 -o _src ../%s" % Project.package)

    def _customize_doc_src_files():
        """change the auto-api generated sphinx src files to be more what we want"""
        for root, dirs, files in os.walk(os.path.join(Project.docs_dir, '_src')):
            for file_name in files:
                if file_name != 'modules.rst':
                    hack_doc_src_file(os.path.join(root, file_name))

            # ignore dot sub-directories ('.*') (mainly for skipping .svn directories)
            for name in dirs:
                if name.startswith('.'):
                    dirs.remove(name)

    def clean_doc_log(file_name):
        """
        Removes sphinx/python 2.6 warning messages.

        Sphinx is very noisy with some warning messages.  This method removes these noisy warnings.

        Messages to remove:

        * WARNING: py:class reference target not found: object
        * WARNING: py:class reference target not found: exceptions.Exception
        * WARNING: py:class reference target not found: type
        * WARNING: py:class reference target not found: tuple

        :param file_name: log file name
         :type file_name: str
        """
        with safe_edit(file_name) as files:
            in_file = files['in']
            out_file = files['out']
            for line in in_file.readlines():
                match = re.search(r'WARNING: py:class reference target not found: (\S+)', line)
                if match:
                    if match.group(1) in ['object', 'exceptions.Exception', 'type', 'tuple']:
                        continue
                out_file.write(line)

    def _create_module_diagrams(path):
        """
        create module UML diagrams

        :param path: the module path
         :type path: str
        """
        if not executables_available(['pyreverse']):
            return
        for module_path in [root for root, dirs, files in os.walk(path)]:
            init_filename = os.path.join(module_path, '__init__.py')
            if os.path.exists(init_filename):
                name = os.path.basename(module_path).split(".")[0]
                cmd_line = 'PYTHONPATH="{path}" pyreverse -o svg -p {name} {module}'.format(path=Project.pythonPath,
                                                                                            name=name,
                                                                                            module=module_path)
                info(cmd_line)
                os.system(cmd_line)

    def _create_class_diagrams(path):
        """
        Create class UML diagram

        :param path: path to the module file.
        :type path: str
        """
        if not executables_available(['pynsource']):
            return
        files = [os.path.join(dir_path, f)
                 for dir_path, dir_names, files in os.walk(path)
                 for f in fnmatch.filter(files, '*.py')]
        for src_file in files:
            name = src_file.replace(Project.herringfile_dir + '/', '').replace('.py', '.png').replace('/', '.')
            output = "classes_{name}".format(name=name)
            cmd_line = "pynsource -y {output} {source}".format(output=output, source=src_file)
            info(cmd_line)
            os.system(cmd_line)

    @task(depends=['api_doc'])
    def doc_diagrams():
        """Create UML diagrams"""
        path = os.path.join(Project.herringfile_dir, Project.package)
        with cd(Project.uml_dir):
            _create_module_diagrams(path)
            _create_class_diagrams(path)

    @task(depends=['api_doc', 'doc_diagrams', 'update_readme'])
    def sphinx_docs():
        """Generate sphinx API documents"""
        _customize_doc_src_files()
        with cd(Project.docs_dir):
            os.system('PYTHONPATH=%s sphinx-build -b html -d _build/doctrees -w docs.log -a -E -n . _build/html' %
                      Project.pythonPath)
            clean_doc_log('docs.log')

    @task()
    def idoc():
        """Incremental build docs for testing purposes"""
        with cd(Project.docs_dir):
            os.system('PYTHONPATH=%s sphinx-build -b html -d _build/doctrees -w docs.log -n . _build/html' %
                      Project.pythonPath)
            clean_doc_log('docs.log')

    @task(depends=['api_doc'])
    def epy_docs():
        """Generate epy API documents"""
        with cd(Project.docs_dir):
            cmd_args = ['epydoc', '-v', '--output', '_epy', '--graph', 'all', 'bin', 'db', 'dst', 'dut', 'lab',
                        'otto', 'pc', 'tests', 'util']
            run(cmd_args)

    @task(depends=['sphinx_docs'])
    def doc():
        """Generate API documents"""
        pass

    @task(depends=['doc'])
    def doc_post_clean():
        """Generate docs then clean up afterwards"""
        clean()

    @task()
    def update_readme():
        """Update the README.txt from the application's --longhelp output"""
        text = system("%s --longhelp" % os.path.join(Project.herringfile_dir, Project.package, Project.main))
        with open("README.txt", 'w') as readme_file:
            readme_file.write(text)

    @task(depends=['doc_clean'])
    def rstlint():
        """Check the RST in the source files"""
        if not executables_available(['rstlint.py']):
            return
        rst_files = [os.path.join(dir_path, f)
                     for dir_path, dir_names, files in os.walk(Project.herringfile_dir)
                     for f in fnmatch.filter(files, '*.rst')]

        src_files = [os.path.join(dir_path, f)
                     for dir_path, dir_names, files in os.walk(Project.herringfile_dir)
                     for f in fnmatch.filter(files, '*.py')]

        for src_file in rst_files + src_files:
            cmd_line = 'rstlint.py {file}'.format(file=src_file)
            result = system(cmd_line, verbose=False)
            if not re.search(r'No problems found', result):
                info(cmd_line)
                info(result)
