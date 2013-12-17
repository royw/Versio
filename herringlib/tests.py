# coding=utf-8
"""
Add the following to your *requirements.txt* file:

* coverage
* nose

"""

__docformat__ = 'restructuredtext en'

from herring.herring_app import task, run
from project_settings import Project, packages_required

required_packages = [
    'coverage',
    'nose'
]

if packages_required(required_packages):
    @task()
    def test():
        """ Run the unit tests """
        run(("nosetests -vv --where=%s" % Project.tests_dir).split(' '))
