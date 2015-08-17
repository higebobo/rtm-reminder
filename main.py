#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
import hashlib
import json
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import optparse
import os
import urllib

from config import APP_NAME, DEFAULT_ENCODING, LOG_DIR, API_KEY, \
     SHARED_SECRET, TOKEN, API_URL, AUTH_URL, FORMAT, MAIL_HOST, MAIL_SENDER, \
     ADMINS, MAIL_USER, MAIL_PASSWORD, MAIL_MOBILE_RECIPIENTS, MAIL_RECIPIENTS
from mail import send_mail

class RTMError(Exception):
    '''RTM Error'''
    
    def __init__(self, value='RTM Error'):
        if value:
            self.value = value

    def __str__(self):
        return repr(self.value)

def _make_signature(**params):
    '''make api signature for rtm api'''
    
    # sort parameters by key and concat them with key and value
    sorted_params = [k + params[k] for k in sorted(params.keys())]
    
    # insert shared secret into joined parameters
    data = SHARED_SECRET + ''.join(sorted_params)
    
    # generate md5 hash
    signature = hashlib.md5(data).hexdigest()
    
    return signature

def _make_request_url(request_url, **params):
    '''make request url for rpm api'''
    
    return '%s?%s' % (request_url, urllib.urlencode(params))

def get_response(request_url=API_URL, **params):
    '''get response method'''
    
    # generate api signature
    api_sig = _make_signature(**params)

    # add api signature into parameters
    params['api_sig'] = api_sig

    # make request url for getting response
    _request_url = _make_request_url(request_url, **params)

    # get response
    response = urllib.urlopen(_request_url).read()

    return response

def get_task(task_filter=None):
    result = []
    
    # set parameters    
    params = {'api_key': API_KEY,
              'method': 'rtm.tasks.getList',
              'perms': 'read',
              'auth_token': TOKEN,
              'format': FORMAT}

    if task_filter:
        params['filter'] = task_filter

    # get response
    response = json.loads(get_response(**params))
    
    # parse json and return result
    if response['rsp']['stat'] == 'ok':
        tasks = response['rsp']['tasks']
        if not tasks.has_key('list'):
            return result
        tasks_list = tasks['list']
        if isinstance(tasks_list, dict):
            tasks_list = [tasks_list]
        for x in tasks_list:
            # skip no taskseries
            if not x.has_key('taskseries'):
                continue
            taskseries = x['taskseries']
            if isinstance(taskseries, dict):
                taskseries = [taskseries]
            for ts in taskseries:
                ts_id = ts['id']
                name = ts['name']
                tags = ts['tags']
                tag_list = []
                if tags:
                    tag_list = tags['tag']
                    if not isinstance(tag_list, list):
                        tag_list = [tag_list]
                ## for notes
                notes = ts['notes']
                if isinstance(notes, dict):
                    notes = [notes]
                note_list = []
                for n in notes:
                    for key, value in n.items():
                        if not isinstance(value, list):
                            value =  [value]
                        for v in value:
                            note_list.append(v['$t'])
                ## for task
                task = ts['task']
                if isinstance(task, list):
                    task = sorted(task, key=lambda x:x['added'],
                                  reverse=True)[0]
                completed = task['completed']
                due = task['due']
                priority = task['priority']
                task_id = task['id']
                result.append({'id': ts_id, 'name': name, 'due': due, 'priority': priority, 'notes': note_list, 'tags': tag_list})

        result = sorted(result, key=lambda x:x['due'])

    else:
        raise RTMError('Failed to get response')

    return result

def sample():
    task_filter = 'status:incomplete AND dueWithin:"1 month of today"'
    for task in get_task(task_filter):
        print '*', task['due'], task['name'].encode(DEFAULT_ENCODING)

def check_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser()
    parser.add_option(
        '-t', '--target',
        type='choice',
        choices=['tommorow', 'two_weeks', 'six_month'],
        default='tommorow',)
    parser.add_option(
        '-i', '--important',
        action='store_true',
        default=False,
        help='send mail to mobile phone')

    (options, args) = parser.parse_args()
    return (options, args)

def main():
    # check args
    options, args = check_args()
    
    ## logging
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    # define handler
    hdlr = RotatingFileHandler(os.path.join(LOG_DIR, ('info.log')))
    mail_hdlr = SMTPHandler(mailhost=MAIL_HOST, fromaddr=MAIL_SENDER,
                            toaddrs=ADMINS,
                            subject='%s App Error' % APP_NAME.capitalize(),
                            credentials=(MAIL_USER, MAIL_PASSWORD),
                            secure=())
    # set formatter
    hdlr.setFormatter(formatter)
    mail_hdlr.setFormatter(formatter)
    # set level
    hdlr.setLevel(logging.INFO)
    mail_hdlr.setLevel(logging.ERROR)
    # add handler
    logger.addHandler(hdlr)
    logger.addHandler(mail_hdlr)

    if options.target == 'tommorow':
        subject = u'明日の予定'
        task_filter = 'status:incomplete AND due:"tommorow"'
    elif options.target == 'two_weeks':
        subject = u'直近の予定'
        task_filter = 'status:incomplete AND dueWithin:"2 week of today"'
    elif options.target == 'six_month':
        subject = u'今後の予定'
        task_filter = 'status:incomplete AND NOT list:"出勤時刻" AND dueWithin:"6 months of today"'

    body = ''
    for task in get_task(task_filter):
        body += '* %s %s\n' %(task['due'], task['name'])
        
    if not body:
        return
    
    if options.important:
        to_addr = MAIL_MOBILE_RECIPIENTS + MAIL_RECIPIENTS
        subject += u'(重要)'
        task_filter += ' AND (priority:1 OR list:"出勤時刻")"'
    else:
        to_addr = MAIL_RECIPIENTS

    to_addr = MAIL_MOBILE_RECIPIENTS + MAIL_RECIPIENTS
    try:
        send_mail(subject=subject, body=body, to_addr=to_addr)
        logger.info('send %s task' % options.target)
    except Exception as e:
        logger.exception(str(e))
    
if __name__ == "__main__":
    main()
