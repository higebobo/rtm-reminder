#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate, parseaddr, formataddr
import smtplib

from config import MAIL_HOST, MAIL_PORT, MAIL_USER, MAIL_PASSWORD, \
     MAIL_SENDER, MAIL_RECIPIENTS, MAIL_MOBILE_RECIPIENTS, EMAIL_CHARSET

def create_message(subject, body, from_addr, to_addr, bccs, encoding):
    msg = MIMEText(body, 'plain', encoding)
    msg['Subject'] = Header(subject, encoding)
    msg['Date'] = formatdate()
    msg['From'] = from_addr
    if isinstance(to_addr, tuple):
        to_addr = list(to_addr)
    if isinstance(to_addr, list):
        msg['To'] = ', '.join(to_addr)
    else:
        msg['To'] = to_addr
    if bccs:
        if isinstance(bccs, list):
            msg['BCC'] = ', '.join(bccs)
        else:
            msg['BCC'] = bccs
    return msg

def send(subject, msg, to_addr, from_addr, bccs, host, port, username,
         password):
    s = smtplib.SMTP(host, port)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(username, password)
    if isinstance(to_addr, str):
        to_addr = [to_addr]
    elif isinstance(to_addr, tuple):
        to_addr = list(to_addr)
    if isinstance(bccs, str):
        bccs = [bccs]
    elif isinstance(bccs, tuple):
        bccs = list(bccs)
    s.sendmail(from_addr, to_addr+bccs, msg.as_string())
    s.close()

def send_mail(subject, body, from_addr=MAIL_SENDER, to_addr=MAIL_RECIPIENTS,
              bccs=[], host=MAIL_HOST, port=MAIL_PORT, username=MAIL_USER,
              password=MAIL_PASSWORD, encoding=EMAIL_CHARSET):
    msg = create_message(subject, body, from_addr, to_addr, bccs, encoding)
    send(subject, msg, to_addr, from_addr, bccs, host, port, username,
         password)

def test_send():
    send_mail(subject=u'テスト', body=u'こんにちは')
