#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
import ConfigParser
import os

ABS_PATH = os.path.dirname(__file__)
SITE_CONFIG_FILE = 'site.cfg'
DEFAULT_CONFIG_FILE = 'default.cfg'

config = ConfigParser.ConfigParser()
config.read(os.path.join(ABS_PATH, SITE_CONFIG_FILE))
config.read(os.path.join(ABS_PATH, DEFAULT_CONFIG_FILE))

##
## DEFAULT
##
APP_NAME = config.get('DEFAULT', 'app_name')
DEFAULT_ENCODING = config.get('DEFAULT', 'encoding')
ADMINS = config.get('DEFAULT', 'admins').split(',')

##
## directory
##
LOG_DIR = os.path.join(ABS_PATH, config.get('directory', 'log'))

##
## mail
##
MAIL_HOST = config.get('mail', 'host')
MAIL_PORT = config.getint('mail', 'port')
MAIL_USER = config.get('mail', 'user')
MAIL_PASSWORD = config.get('mail', 'password')
MAIL_SENDER = config.get('mail', 'sender')
MAIL_RECIPIENTS = config.get('mail', 'recipients').split(',')
MAIL_MOBILE_RECIPIENTS = config.get('mail', 'mobile_recipients').split(',')
EMAIL_CHARSET = config.get('mail', 'charset')

##
## rtm
##
API_URL = config.get('rtm', 'api_url')
AUTH_URL = config.get('rtm', 'auth_url')
FORMAT = config.get('rtm', 'format')

##
## auth
##
API_KEY = config.get('auth', 'api_key')
SHARED_SECRET = config.get('auth', 'shared_secret')
TOKEN = config.get('auth', 'token')
