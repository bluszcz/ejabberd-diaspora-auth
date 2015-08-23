***********************
ejabberd diaspora* auth
***********************

requirements
------------

* diaspora* postgres database
* ejabberd server
* python3 

installation
------------

    pip install 

ejabberd configuration
----------------------

    auth_method: external
    
    extauth_program: "/home/bluszcz/dev/repo/diaspora-ejabberd/diaspora_auth.py"

