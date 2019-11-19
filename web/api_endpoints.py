import functools

import cv2
import numpy as np
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash
from .api import face_check

bp = Blueprint('api_endpoints', __name__, url_prefix='/api')

@bp.route('/check_face', methods=('POST',))
def check_face():
    myrequest = request
    if 'img' not in request.files:
        response = make_response({
            'message': 'No valid image detected.'
        }, 400)
        response.mimetype = 'application/json'
        return response

    # handle image
    imgfile = request.files['img']
    if imgfile.filename == '':
        response = make_response({
            'message': 'No valid image detected.'
        }, 400)
        response.mimetype = 'application/json'
        return response

    # convert image to cv2 instance (TODO: check for non-file)
    img = cv2.imdecode(np.fromstring(imgfile.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    result = face_check.is_single_face_valid(img)
    response_body = {
        'result': result
    }
    response = make_response(response_body)
    response.mimetype = 'application/json'
    if result != 0:
        response.status = 422

    return response

