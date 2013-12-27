# coding=utf-8
"""
Set of Herring tasks for packaging a project.

In early development, the install/uninstall tasks are useful.
Less so after you start deploying to a local pypi server.

"""
__docformat__ = 'restructuredtext en'

import os
from getpass import getpass

from herring.herring_app import task
from version import bump, get_project_version
from project_settings import Project
from local_shell import LocalShell
from remote_shell import RemoteShell
from simple_logger import error, info
from query import query_yes_no
from cd import cd


# cleaning is necessary to remove stale .pyc files, particularly after
# refactoring.
@task(depends=['doc_post_clean'])
def build():
    """ build the project as a source distribution """
    if Project.version == '0.0.0':
        bump()
    with LocalShell() as local:
        local.system("python setup.py sdist")
        # run("python setup.py bdist")


@task(depends=['build'])
def install():
    """ install the project """
    with LocalShell() as local:
        local.system("python setup.py install --record install.record")


@task()
def uninstall():
    """ uninstall the project"""
    with LocalShell() as local:
        if os.path.exists('install.record'):
            local.system("cat install.record | xargs rm -rf")
            os.remove('install.record')
        else:
            # try uninstalling with pip
            local.run(['pip', 'uninstall', Project.herringfile_dir.split(os.path.sep)[-1]])


@task()
def deploy():
    """ copy latest sdist tar ball to server """
    version = Project.version
    project_version_name = "{name}-{version}.tar.gz".format(name=Project.name, version=version)
    project_latest_name = "{name}-latest.tar.gz".format(name=Project.name)

    pypi_dir = Project.pypi_path
    dist_host = Project.dist_host
    dist_dir = '{dir}/{name}'.format(dir=pypi_dir, name=Project.name)
    # dist_url = '{host}:{path}/'.format(host=dist_host, path=dist_dir)
    dist_version = '{dir}/{file}'.format(dir=dist_dir, file=project_version_name)
    dist_latest = '{dir}/{file}'.format(dir=dist_dir, file=project_latest_name)
    dist_file = os.path.join(Project.herringfile_dir, 'dist', project_version_name)

    password = Project.password or getpass("password for {user}@{host}: ".format(user=Project.user,
                                                                                 host=Project.dist_host))
    Project.password = password

    with RemoteShell(user=Project.user, password=password, host=dist_host, verbose=True) as remote:
        remote.run('mkdir -p {dir}'.format(dir=dist_dir))
        remote.run('rm {path}'.format(path=dist_latest))
        remote.put(dist_file, dist_dir)
        remote.run('ln -s {src} {dest}'.format(src=dist_version, dest=dist_latest))


@task()
def release_github():
    """tag it with the current version"""
    with LocalShell() as local:
        local.run('git tag {name}-{ver} -m "Adds a tag so we can put this on PyPI"'.format(
            name=Project.package,
            ver=get_project_version(Project.package)))
        local.run('git push --tags origin master')


@task()
def release_pypi_test():
    """register and upload package to pypi-test"""
    with LocalShell() as local:
        local.run('python setup.py register -r test')
        local.run('python setup.py sdist upload -r test')


@task()
def release_pypi_live():
    """register and upload package to pypi"""
    with LocalShell() as local:
        local.run('python setup.py register -r pypi')
        local.run('python setup.py sdist upload -r pypi')


@task()
def upload_docs():
    """upload docs to http://pythonhosted.org"""
    # TODO this should work but doesn't:
    # with LocalShell() as local:
    #     local.run('python setup.py upload_docs --upload-dir={dir}'.format(dir=Project.docs_html_dir))
    # so instead we zip the docs then the user must manually upload
    zip_name = '../{name}-docs-{ver}.zip'.format(
        name=Project.package,
        ver=get_project_version(Project.package))
    with cd(Project.docs_html_dir):
        with LocalShell() as local:
            local.run('zip -r {zip}'.format(zip=zip_name))
    info("""\
    Please log on to https://pypi.python.org/pypi
    Then select "{name}" under "Your packages".
    Next use the "Browse" button to select "{zip}" and press "Upload Documentation".
    """.format(name=Project.name))


@task()
def release():
    """Releases the project to github and pypi"""
    if not os.path.exists(os.path.expanduser('~/.pypirc')):
        error('You must have a configured ~/.pypirc file.  '
              'See http://peterdowns.com/posts/first-time-with-pypi.html'
              'Hint, do not use comments in your .pypirc')
        return

    release_github()
    release_pypi_test()
    if query_yes_no('Is the new package on pypi-test (http://testpypi.python.org/pypi)?'):
        release_pypi_live()
        upload_docs()
