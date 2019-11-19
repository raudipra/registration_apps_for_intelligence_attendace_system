def is_single_face_valid(img) -> int:
    """Checks if the selected image contains a face.

    Testing is done by uploading the image to an API

    API return codes:
    - 0: OK
    - 1: no face detected
    - 2: multiple faces detected.
    """
    # TODO stub
    return 0

def is_three_faces_valid(img_face1, img_face2, img_face3) -> dict:
    """Checks if all images, each contains a face.

    Testing is done by uploading all images to an API at once

    API return code (per image):
    - 0: all images OK
    - 1: no face detected (at least on one image)
    - 2: multiple faces detected (at least on one image)
    """
    # TODO stub
    return {
        'face1_detection_result': 0,
        'face2_detection_result': 0,
        'face3_detection_result': 0
    }
