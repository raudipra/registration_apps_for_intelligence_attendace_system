import uuid

def upload_form(ektp: dict, img_face1, img_face2, img_face3, img_ektp) -> str:
    """Uploads the form data to an API

    In return, the API will return an ID (string),
    that can be used to attach images related to the form (i.e. faces and eKTP)
    """

    # TODO stub
    # for now just return a random id
    return str(uuid.uuid4()).strip('-')
