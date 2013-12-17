# coding=utf-8

"""
Helper for running the behave BDD utility.

Add the following to your *requirements.txt* file:

* behave

"""
from herring.herring_app import task
from project_settings import Project, packages_required

required_packages = [
    'behave'
]

if packages_required(required_packages):
    from runner import script

    @task(help='You may append behave options when invoking the features task.')
    def features():
        """Run behave features"""
        script('behave {features} {args}'.format(features=Project.features_dir, args=' '.join(task.argv)))
