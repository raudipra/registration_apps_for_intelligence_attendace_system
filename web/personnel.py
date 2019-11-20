import functools
import numpy as np
import cv2
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash
from .ocr.ektp import extract_info_from_ektp_cv2
from .api.form_upload import upload_form

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
    else: # unidentified: revert back to trigger.
        return render_template('/face-capture/face-capture-trigger.html')

@bp.route('/register/ektp', methods=('GET', 'POST'))
def capture_ektp():
    if request.method == 'POST':
        if 'img' not in request.files:
            response = make_response({
                'message': 'No valid image detected.'
            }, 400)
            response.mimetype = 'application/json'
            return response

        imgfile = request.files['img']
        if imgfile.filename == '':
            response = make_response({
                'message': 'No valid image detected.'
            }, 400)
            response.mimetype = 'application/json'
            return response

        # convert image to cv2 instance (TODO: check for non-file)
        img = cv2.imdecode(np.fromstring(imgfile.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        result = extract_info_from_ektp_cv2(img)
        return result

    return render_template('/ektp-form.html')

@bp.route('/register/preview')
def preview():
    return render_template('/preview-register.html')

@bp.route('/register', methods=('POST',))
def register_personnel():
    # check validity of images
    err = {}
    img_keys = ['img_face1', 'img_face2', 'img_face3', 'img_ektp']
    for key in img_keys:
        if key not in request.files:
            err[key] = 'No valid image detected'
            continue
        if request.files[key].filename == '':
            err[key] = 'No valid image detected'

    # check if the ektp form exists
    if 'ektp' not in request.form:
        err['ektp'] = 'missing data!'

    if bool(err): # there is an error
        response = make_response(err, 400)
        response.mimetype = 'application/json'
        return response

    ektp = json.loads(request.form['ektp'])
    img_face1, img_face2, img_face3, img_ektp = map(
        lambda key: cv2.imdecode(np.fromstring(request.files[key].read(), np.uint8), cv2.IMREAD_UNCHANGED),
        img_keys
    )

    form_id = upload_form(ektp, img_face1, img_face2, img_face3, img_ektp)

    response = make_response({ 'id': form_id })
    response.mimetype = 'application/json'
    return response
