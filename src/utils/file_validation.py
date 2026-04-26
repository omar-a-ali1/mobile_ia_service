ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}


def validate_image_file(file):
    # 1. Check extension
    filename = file.filename.lower()
    if "." not in filename:
        return False, "File has no extension"

    ext = filename.split(".")[-1]
    if ext not in ALLOWED_EXTENSIONS:
        return False, "Invalid file extension"

    # 2. Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, "Invalid MIME type"

    return True, None