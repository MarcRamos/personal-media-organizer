from datetime import datetime
from PIL import Image

def get_image_year_month(path):
    """
    Extract (year, month) from the best available EXIF datetime field.
    Returns (year, month) or raises Exception if no EXIF datetime is present.
    """

    tags = [
        (36867, 37521),  # DateTimeOriginal + SubSecTimeOriginal
        (36868, 37522),  # DateTimeDigitized + SubSecTimeDigitized
        (306,   37520),  # DateTime + SubSecTime
    ]

    img = Image.open(path)
    exif = img.getexif() or img._getexif()  # fallback for old Pillow

    if not exif:
        raise Exception(f"Image {path} does not have EXIF data.")

    std_fmt = '%Y:%m:%d %H:%M:%S.%f'

    for main_tag, subsec_tag in tags:
        dat = exif.get(main_tag)
        sub = exif.get(subsec_tag, 0)

        if isinstance(dat, tuple):
            dat = dat[0]
        if isinstance(sub, tuple):
            sub = sub[0]

        if dat:
            full = f"{dat}.{sub}"
            try:
                T = datetime.strptime(full, std_fmt)
                return T.year, T.month
            except Exception:
                # If weird format: ignore and continue
                pass

    raise Exception(f"No valid EXIF datetime found in image {path}.")
