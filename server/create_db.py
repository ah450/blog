#!/usr/bin/env python
from app.models import *
from app.server import db

db.create_all()
