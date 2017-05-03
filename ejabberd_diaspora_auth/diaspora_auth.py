#!/usr/bin/python3

import sys
import os
import re
import logging
from struct import *

import psycopg2
import bcrypt
import yaml

re_pepper = re.compile(r'.*config.pepper = "([a-z0-9]*)')

# Setup the logging
PID = os.getpid()
logger = logging.getLogger('diaspora_auth')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(filename='/tmp/diaspora_auth.log')
formatter = logging.Formatter('%(asctime)s - %(name)s '+str(PID)+'- %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

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
db_config = parse_yaml_file(filename)['production']
filename = os.path.join(DIASPORA_DIR, "config/initializers/devise.rb")
pepper = get_pepper(filename)

try:
    db_password = db_config['password']
except:
    db_password = db_config['postgresql']['password']
try:
    db_host = db_config['host']
except:
    db_host = db_config['postgresql']['host']

try:    
    db_user = db_config['username']
except:
    db_user = db_config['postgresql']['username']

try:    
    db_port = db_config['port']
except:
    db_port = db_config['postgresql']['port']    
    
db_dbname = 'diaspora_production'
connection_string = "dbname=%s user=%s host=%s password=%s port=%s" % (db_dbname, db_user, db_host, db_password, db_port)

conn = psycopg2.connect(connection_string)
cur = conn.cursor()

def get_user(cur, username):
    cur.execute("SELECT username, encrypted_password FROM users WHERE username =%s;", (username,))
    user = cur.fetchone()    
    return user

def valid_user(cur, username):
    cur.execute("SELECT count(username) FROM users WHERE username =%s;", (username,))
    result = cur.fetchone()
    if result[0]==1:
        return True
    else:
        return False
    
def auth_user(cur, username, password):
    logger.debug('auth_user')
    user = get_user(cur, username)
    encrypted_password = user[1]
    password_txt = '%s%s' % (password, pepper)
    if bcrypt.hashpw(password_txt.encode('utf-8'), encrypted_password.encode('utf-8')) == encrypted_password.encode('utf-8'):
        logger.debug("TRUE")
        return True
    else:
        logger.debug("FALSE")
        return False

def from_ejabberd():
    logger.debug('before_input')
    input_length = sys.stdin.read(2)
    (size,) = unpack(bytes('>h', 'UTF-8'), bytes(input_length, 'UTF-8'))
    logger.debug(input_length)
    return sys.stdin.read(size).split(':')

def to_ejabberd(bool):
    logger.debug("to_ejabebrd %s beg" % bool)
    answer = 0
    if bool:
        answer = 1
    token = pack('>hh', 2, answer)
    sys.stdout.buffer.write(token)
    sys.stdout.buffer.flush()
    sys.stdout.flush()
    logger.debug("to_ejabebrd %s end" % bool)

def auth(username, server, password):
    return auth_user(cur, username, password)

def isuser(username, server):
    return valid_user(cur, username)

def setpass(username, server, password):    
    return False

try:
    while True:
        data = from_ejabberd()
        success = False
        logger.debug(str(data))
        if data[0] == "auth":
            logger.debug("start auth")
            success = auth(data[1], data[2], data[3])
            logger.debug("end auth")
        elif data[0] == "isuser":
            success = isuser(data[1], data[2])
        elif data[0] == "setpass":
            success = setpass(data[1], data[2], data[3])
        logger.debug("send to ejabberd %s" % success)
        to_ejabberd(success)
        logger.debug("sent to ejabberd %s" % success)
except Exception:
    logger.error('problem happened', exc_info=True)
