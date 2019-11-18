import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('personnel', __name__, url_prefix='/personnel')

@bp.route('/register')
def register_initial_screen():
    return render_template('/welcome-register.html', default_capture_method=current_app.config['DEFAULT_TRIGGER_MODE'])

@bp.route('/register/face', methods=('GET',))
def capture_face():
    capture = request.args.get('capture', default=current_app.config['DEFAULT_TRIGGER_MODE'], type=str)
    if capture == 'trigger':
        return render_template('/face-capture/face-capture-trigger.html')
    elif capture == 'burst':
        return render_template('/face-capture/face-capture-burst.html')
    elif capture == 'timer':
        return render_template('/face-capture/face-capture-timer.html')
    else:
        return render_template('/face-capture/face-capture-trigger.html')
