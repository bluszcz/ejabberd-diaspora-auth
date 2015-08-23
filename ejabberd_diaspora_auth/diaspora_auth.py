#!/usr/bin/env python3

import sys
import os
import re
from struct import *
import psycopg2
import bcrypt
import yaml

re_pepper = re.compile(r'.*config.pepper = "([a-z0-9]*)')

def parse_yaml_file(filename):
    result = yaml.load(open(filename))
    return result

def get_pepper(filename):
    for line in open(filename).readlines():
        if line.find('config.pepper')>-1:
            if re_pepper.match(line):
                pepper = (re_pepper.findall(line))[0]
                return pepper
            return line

if os.environ.get('DIASPORA_DIR'):
    DIASPORA_DIR = os.environ.get('DIASPORA_DIR')
else:
    DIASPORA_DIR = "/home/diaspora/diaspora"
filename = os.path.join(DIASPORA_DIR, "config/database.yml")
db_config = parse_yaml_file(filename)
filename = os.path.join(DIASPORA_DIR, "config/initializers/devise.rb")
pepper = get_pepper(filename)
db_password = db_config['postgresql']['password']
db_host = db_config['postgresql']['host']
db_user = db_config['postgresql']['username']
db_dbname = 'diaspora_development'
connection_string = "dbname=%s user=%s host=%s password=%s" % (db_dbname, db_user, db_host, db_password)

conn = psycopg2.connect(connection_string)
cur = conn.cursor()

def get_user(cur, username):
    cur.execute("SELECT username, encrypted_password FROM users WHERE username = '%s';" %(username))
    user = cur.fetchone()    
    return user

def valid_user(cur, username):
    cur.execute("SELECT count(username) FROM users WHERE username = '%s';" %(username));
    result = cur.fetchone()
    if result[0]==1:
        return True
    else:
        return False
    
def auth_user(cur, useuth_rname, password):
    user = get_user(cur, "test")
    encrypted_password = user[1]
    password_txt = '%s%s' % (password, pepper)
    if bcrypt.hashpw(password_txt.encode('utf-8'), encrypted_password.encode('utf-8')) == encrypted_password.encode('utf-8'):
        return True
    else:
        return False

def from_ejabberd():
    input_length = sys.stdin.read(2)
    (size,) = unpack(bytes('>h', 'UTF-8'), bytes(input_length, 'UTF-8'))
    return sys.stdin.read(size).split(':')

def to_ejabberd(bool):
    answer = 0
    if bool:
        answer = 1
    token = pack('>hh', 2, answer)
    sys.stdout.buffer.write(token)
    sys.stdout.buffer.flush()
    sys.stdout.flush()

def auth(username, server, password):
    return auth_user(cur, username, password)
    

def isuser(username, server):
    return valid_user(cur, username)

def setpass(username, server, password):    
    return False

while True:
    data = from_ejabberd()
    success = False
    if data[0] == "auth":
        success = auth(data[1], data[2], data[3])
    elif data[0] == "isuser":
        success = isuser(data[1], data[2])
    elif data[0] == "setpass":
        success = setpass(data[1], data[2], data[3])
    to_ejabberd(success)