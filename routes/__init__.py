from flask import Blueprint

from .users import users_bp
from .llms import llm_bp
from .tables import tables_bp
from .history import history_bp

# This file can serve as a central import hub for Blueprints
blueprints = [users_bp, llm_bp, tables_bp, history_bp]
