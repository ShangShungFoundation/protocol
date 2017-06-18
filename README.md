Protocol
========

Correspondence Protocol System

Inspired by the workshop in Merigar 2017. with Bruno and Peter 

Tested with Django1.9 and Python3.5

Features:
---------

* Supports digital (emails) and physical correspondence
* Supports incomig and outgoing correspondance
* Allows single correspondance and threads (curespondance interchange)
* User friendly integration with gmail (or any other email provider)
* Stores all attached email documents
* Automatically asigned unique Protocol reference
* Protocol establish storage directory corresponding to category hierarchy
* Supports multiple physical storage locations for distributed institutions
* Browsing and searching content
* Restricted access to correspondance and stored documents

Installing
----------
Assuming that you got virtualenv (python virtual envirement) created and activated.

Install via pip:

    pip install -e git+https://k1000@gitlab.com/k1000/cps.git#egg=protocol
    
Add to INSTALLED_APPS in settings.py file

Configuration
-------------
Optionally in settings.py set:


Usage
-----


TODO:
-----
* Setting checksum to proove document
* 