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

@bp.route('/check_face_three', methods=('POST',))
def check_face_three():
    # check validity of images
    err = {}
    keys = ['face1', 'face2', 'face3']
    for key in keys:
        if key not in request.files:
            err[key] = 'No valid image detected'
            continue
        if request.files[key].filename == '':
            err[key] = 'No valid image detected'

    if bool(err): # there is an error
        response = make_response(err, 400)
        response.mimetype = 'application/json'
        return response

    # convert images to cv2 instance (TODO: check for non-file)
    face1, face2, face3 = map(
        lambda key: cv2.imdecode(np.fromstring(request.files[key].read(), np.uint8), cv2.IMREAD_UNCHANGED),
        keys
    )
    result = face_check.is_three_faces_valid(face1, face2, face3)
    response = make_response(result)
    response.mimetype = 'application/json'
    if not all(v == 0 for v in list(result.values())):
        response.status = 422

    return response
