# -*- coding: utf-8 -*-
"""
Created on Wed May 17 16:06:30 2017

@author: sapjz
"""
import subprocess
import os

print(os.getcwd())
#subprocess.call('pip install --upgrade --no-deps --force-reinstall kabuki',cwd='../kabuki')
#subprocess.call('pip install --upgrade --no-deps --force-reinstall hddm',cwd='../hddm')

subprocess.call('python setup.py install',cwd='../kabuki')
subprocess.call('python setup.py install',cwd='../hddm')
