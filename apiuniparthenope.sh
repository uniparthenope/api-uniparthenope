#! /bin/bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_APP=apiuniparthenope.py
export FLASK_ENV=development

flask run -h 0.0.0.0 -p 5000