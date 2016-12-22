#!/usr/bin/env python
import os

from django.core.management import settings, execute_from_command_line

import yaml
import click

@click.group()
@click.option('--config', default='settings.yaml', help='YAML Settings file for ODM2Admin')
@click.option('--debug', is_flag=True, help='A flag to run ODM2Admin in debug mode')
@click.option('--port', default=8000, help='The port to run ODM2Admin')
@click.pass_context
def cli(ctx, config, debug, port):
    """odm2djangoadmin command line to run server"""

    ctx.obj = dict()
    ctx.obj['CONFIG'] = config
    ctx.obj['DEBUG'] = debug
    ctx.obj['PORT'] = port

@cli.command()
@click.pass_context
def runserver(ctx):
    with open(ctx.obj['CONFIG'], 'r') as src:
        configs = yaml.load(src)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "templatesAndSettings.settings")

    settings.DEBUG = ctx.obj['DEBUG']

    settings.VERBOSE_NAME = configs['Name']
    settings.SITE_HEADER = configs['Site Header']
    settings.SITE_TITLE = configs['Site Title']

    settings.MAP_CONFIG = configs['Map Config']
    settings.DATA_DISCLAIMER = configs['Data Disclaimer']

    settings.SECRET_KEY = configs['Secret Key']
    settings.ROOT = configs['Root']

    settings.DATABASES['default']['NAME'] = configs['Database config']['name']
    settings.DATABASES['default']['USER'] = configs['Database config']['user']
    settings.DATABASES['default']['PASSWORD'] = configs['Database config']['password']
    settings.DATABASES['default']['HOST'] = configs['Database config']['host']
    settings.DATABASES['default']['PORT'] = configs['Database config']['port']

    settings.ADMINS = configs['Administrator']
    execute_from_command_line(['manage.py','runserver', str(ctx.obj['PORT'])])



