#!/usr/bin/env python

import sys
from struct import *
import psycopg2
import bcrypt
# For now only with postgresql
conn = psycopg2.connect("dbname=diaspora_development user=diaspora host=127.0.0.1 password=diaspora")
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
    # replace this with the value from config/initializers/devise.rb
    pepper = '065eb8798b181ff0ea2c5c16aee0ff8b70e04e2ee6bd6e08b49da46924223e39127d5335e466207d42bf2a045c12be5f90e92012a4f05f7fc6d9f3c875f4c95b'
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