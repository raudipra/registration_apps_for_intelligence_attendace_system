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

def is_multiple_faces_valid(imgs) -> int:
    """Checks if all images, each contains a face.

    Testing is done by uploading all images to an API at once

    API return codes:
    - 0: all images OK
    - 1: no face detected (at least on one image)
    - 2: multiple faces detected (at least on one image)
    """
    # TODO stub
    return 0