import sys
import cv2
import numpy as np
import pytesseract
import os
import traceback
from datetime import datetime
import warnings
from fuzzywuzzy import fuzz
import imutils

def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(encoded_data.decode('base64'), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    return img

def parse_ektp(img) -> dict:
    result = {
        'nik': '',
        'nama': '',
        'tempat_lahir': '',
        'tanggal_lahir': '',
        'jenis_kelamin': ''
    }

    result['nik'] = extract_nik(img)
    return {**result, **extract_personal_details(img)}


def resize(img, targetWidth = 600):
    """
    Resizes an image, based on a targetWidth
    """
    height, width, depth = img.shape
    scale = targetWidth/width
    newX, newY = width * scale, height * scale
    resized = cv2.resize(img, (int(newX), int(newY)))
    return resized

def normalize_image(img):
    """
    'Normalizes' the image: crop the image based on the location of ID card alone.

    Further enhancement may include orientation correction.
    """
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 4, 11)

    # dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    eroded = cv2.dilate(denoised, kernel, iterations=1)

    # do thresholding
    grey = cv2.cvtColor(eroded, cv2.COLOR_BGR2GRAY)
    th2 = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

    # close the edges
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
    edged = cv2.morphologyEx(th2, cv2.MORPH_OPEN, kernel)

    # Finding contours
    contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    # find the largest contour
    ROI = None
    if len(contours) != 0:
        # find the biggest area
        contours = sorted(contours, key = cv2.contourArea, reverse = True)
        # Find bounding box and extract ROI
        x,y,w,h = cv2.boundingRect(contours[0])
        ROI = img[y:y+h, x:x+w]

    # resize
    resized = None
    if ROI is not None:
        resized = resize(ROI)
    else:
        resized = resize(img)

    return resized

def extract_nik(img) -> str:
    """
    Extracts the ID (NIK) of e-KTP from the cropped/normalized image instance.

    Make sure you have installed the `ocr.traineddata` from `web/ocr/train` and the Indonesian language data (`ind`)
    to the Tesseract folder.
    """

    # coordinates are fixed.
    x1_nik, y1_nik, x2_nik, y2_nik = 145, 55, 410, 90
    x = x1_nik
    w = x2_nik-x1_nik
    y = y1_nik
    h = y2_nik-y1_nik
    img_nik = img[y:y+h, x:x+w]

    # some specimens of eKTP (e.g. `ektp-4.jpg`) are not using standard OCR-A font.
    # therefore, `ind` is used as a fallback
    return pytesseract.image_to_string(img_nik, lang='ocr+ind')

def denoise_grayscale(img):
    """
    Apply fast denoising and converts an image to grayscale.
    """
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.fastNlMeansDenoising(img, None, 10, 4, 11)

def extract_personal_details(img) -> dict:
    """
    Extracts the personal details (name, birth place/date, gender) of e-KTP from the cropped/normalized image instance.
    Make sure you have installed the Indonesian language (ind) data to the Tesseract folder.
    """
    x1_base, y1_base, x2_base, y2_base = 155, 90, 360, 130

    # try the OCR using multiple processing.
    # strategies:
    # - 1: no processing
    # - 2: grayscale + denoising
    # - 3: grayscale + denoising + binary threshold + close morph
    # - 4: grayscale + denoising + adaptive mean thresholding + close morph
    # this function will try each processing one by one uses 'best-first' strategy, based on the parsed date.
    result = {
        'nama': '',
        'tempat_lahir': '',
        'tanggal_lahir': '',
        'jenis_kelamin': ''
    }
    end = False
    strategy = 1
    name_lines = 1
    try:
        # step 1: parse the name and birth_date
        while not end:
            x = x1_base
            w = x2_base-x1_base
            y = y1_base
            h = int((y2_base-y1_base) * ((2 + name_lines - 1)/2))

            img_name_birth = img[y:y+h, x:x+w]
            parse = ''
            # preprocesing
            if strategy == 1: # no processing
                pass
            elif strategy == 2: # grayscale + denoising
                img_name_birth = denoise_grayscale(img_name_birth)
            elif strategy == 3: # 2 + binary threshold + close morph
                denoised = denoise_grayscale(img_name_birth)

                # threshold
                ret, img_name_birth = cv2.threshold(denoised, 100, 255, cv2.THRESH_BINARY)

                # morph
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                img_name_birth = cv2.morphologyEx(img_name_birth, cv2.MORPH_CLOSE, kernel)
            elif strategy == 4: # 2 + adaptive mean threshold + close morph
                denoised = denoise_grayscale(img_name_birth)

                # threshold
                img_name_birth = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 4)

                # morph
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                img_name_birth = cv2.morphologyEx(img_name_birth, cv2.MORPH_CLOSE, kernel)

            # parse
            parse = pytesseract.image_to_string(img_name_birth, lang='ind').split('\n')
            parse = list(filter(None, parse))
            # try to recognize date
            name_str = ''
            date_str = ''
            birthplace_str = ''
            len_line = len(parse)
            for line_idx, line in enumerate(parse):
                words = list(filter(None, line.split(' ')))
                for idx, word in enumerate(words):
                    # check the first character
                    if not word[0].isdigit():
                        if line_idx < len_line - 1:
                            if name_str == '':
                                name_str += word
                            else:
                                name_str += str(' ' + word)
                        else:
                            birthplace_str += ''.join(e for e in word if e.isalnum())
                    else: # start parsing for date
                        for charpos, ch in enumerate(word):
                            if ch.isdigit():
                                date_str += ch
            # handle case: long name, max 2 lines.
            if date_str == '':
                if name_lines < 2 and len_line > 1:
                    warnings.warn('Possibility of expanded name. Expanding lines...')
                    name_lines += 1
                    continue
                else: # treat as the date parsing failed. just return the name.
                    warnings.warn("failed to detect any digit with strategy %d" % strategy)
                    if strategy < 5:
                        strategy += 1
                        continue
                    else:
                        result['nama'] = ''.join(e for e in name_str if e.isalnum() or e == '\'' or e == ' ')
                        result['tempat_lahir'] = birthplace_str
                        end = True
            else:
                try:
                    date = datetime.strptime(date_str, "%d%m%Y")
                    if date.year < 1910: # sanity check: date should not be older than 1910
                        raise ValueError('Parsed year is ' + date.year)
                    result['nama'] = ''.join(e for e in name_str if e.isalnum() or e == '\'' or e == ' ')
                    result['tempat_lahir'] = birthplace_str
                    result['tanggal_lahir'] = date.strftime("%Y-%m-%d")
                    end = True
                except ValueError as error:
                    # no valid date. change strategy
                    warnings.warn("failed to parse date '" + date_str + '\'')
                    if strategy < 5:
                        strategy += 1
                    else:
                        result['nama'] = ''.join(e for e in name_str if e.isalnum() or e == '\'' or e == ' ')
                        result['tempat_lahir'] = birthplace_str
                        end = True
    except ValueError as error:
        warnings.warn(error, stacklevel=2)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        print(traceback.format_exc())

    prev_h = h
    # continue parsing the gender
    y1_base, x2_base, y2_base = y1_base + prev_h, 260, y2_base + prev_h - 20

    end = False
    strategy = 1
    try:
        # step 1: parse the name and birth_date
        while not end:
            x = x1_base
            w = x2_base-x1_base
            y = y1_base
            h = y2_base-y1_base

            img_gender = img[y:y+h, x:x+w]
            parse = ''
            # preprocesing
            if strategy == 1: # no processing
                pass
            elif strategy == 2: # grayscale + denoising
                img_gender = denoise_grayscale(img_gender)
            elif strategy == 3: # 2 + binary threshold + close morph
                denoised = denoise_grayscale(img_gender)

                # threshold
                ret, img_gender = cv2.threshold(denoised, 100, 255, cv2.THRESH_BINARY)

                # morph
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                img_gender = cv2.morphologyEx(img_gender, cv2.MORPH_CLOSE, kernel)
            elif strategy == 4: # 2 + adaptive mean threshold + close morph
                denoised = denoise_grayscale(img_gender)

                # threshold
                img_gender = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 4)

                # morph
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                img_gender = cv2.morphologyEx(img_gender, cv2.MORPH_CLOSE, kernel)

            # parse
            parse = pytesseract.image_to_string(img_gender, lang='ind')
            parse = parse.upper()

            # if parse is blank, try other methods
            if parse == '':
                warnings.warn('Failed to parse gender with strategy %d.' % strategy)
                if strategy < 5:
                    strategy += 1
                    warnings.warn('Trying other method...')
                    continue
                else:
                    warnings.warn('Giving up')
                    break

            # try to recognize gender from parse
            if parse[0] == 'L':
                result['jenis_kelamin'] = 'LAKI-LAKI'
            elif parse[0] == 'P':
                result['jenis_kelamin'] = 'PEREMPUAN'
            else:
                # try fuzzy string match
                if fuzz.partial_ratio('LAKI-LAKI', parse) > fuzz.partial_ratio('PEREMPUAN', parse):
                    result['jenis_kelamin'] = 'LAKI-LAKI'
                else:
                    result['jenis_kelamin'] = 'PEREMPUAN'

            end = True
    except ValueError as error:
        warnings.warn(error, stacklevel=2)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        print(traceback.format_exc())

    return result

def extract_info_from_ektp(img: str) -> dict:
    """
    Parses an eKTP image from a given path or a data-uri using OCR, to extract containing data.
    """
    if os.path.isfile(img):
        process = cv2.imread(img)
    else:
        # treat as data uri
        process = data_uri_to_cv2_img(img)

    return extract_info_from_ektp_cv2(process)

def extract_info_from_ektp_cv2(img) -> dict:
    """
    Parses an eKTP image from a cv2 instance.
    """
    img = normalize_image(img)
    return parse_ektp(img)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: ' + sys.argv[0] + ' <image path>')
        sys.exit(0)

    print(extract_info_from_ektp(sys.argv[1]))
