# coding=utf-8
"""
Set of Herring tasks for packaging a project.

In early development, the install/uninstall tasks are useful.
Less so after you start deploying to a local pypi server.

"""

__docformat__ = 'restructuredtext en'

import os


from herring.herring_app import task
from version import bump
from project_settings import Project, packages_required
from local_shell import LocalShell
from remote_shell import RemoteShell

required_packages = [
    'pexpect',
]


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


if packages_required(required_packages):
    # from pxssh import pxssh

    @task()
    def deploy():
        """ copy latest sdist tar ball to server """
        version = Project.version
        project_version_name = "{name}-{version}.tar.gz".format(name=Project.name, version=version)
        project_latest_name = "{name}-latest.tar.gz".format(name=Project.name)

        pypi_dir = Project.pypiDir
        dist_host = Project.distHost
        dist_dir = '{dir}/{name}'.format(dir=pypi_dir, name=Project.name)
        dist_url = '{host}:/{path}'.format(host=dist_host, path=dist_dir)
        dist_version = '{dir}/{file}'.format(dir=dist_dir, file=project_version_name)
        dist_latest = '{dir}/{file}'.format(dir=dist_dir, file=project_latest_name)
        dist_file = os.path.join(Project.herringfile_dir, 'dist', project_version_name)

        with RemoteShell(user=Project.user, password=Project.password, host=dist_host, verbose=True) as remote:
            remote.run('mkdir -p {dir}'.format(dir=dist_dir))
            remote.run('rm {path}'.format(path=dist_latest))
            remote.put(dist_file, dist_url)
            remote.run('ln -s {src} {dest}'.format(src=dist_version, dest=dist_latest))

        # ssh = pxssh()
        # ssh.login(dist_host, Project.user)
        # ssh.sendline('mkdir -p {dir}'.format(dir=dist_dir))
        # ssh.prompt()
        # info(ssh.before)
        # ssh.sendline('rm {path}'.format(path=dist_latest))
        # ssh.prompt()
        # info(ssh.before)
        # ssh.logout()
        #
        # run(['scp', dist_file, dist_url])
        #
        # ssh = pxssh()
        # ssh.login(dist_host, Project.user)
        # ssh.sendline('ln -s {src} {dest}'.format(src=dist_version, dest=dist_latest))
        # ssh.prompt()
        # ssh.logout()
