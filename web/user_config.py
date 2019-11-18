import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('user_config', __name__, url_prefix='/config')

@bp.route('/camera')
def camera_config():
    return render_template('camera-config.html')
