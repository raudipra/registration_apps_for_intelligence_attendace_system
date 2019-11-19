import sys
import cv2
import numpy as np
import pytesseract
from fuzzywuzzy import fuzz

img = cv2.imread('specimens/ektp-4.jpg', cv2.IMREAD_GRAYSCALE)
ret, th = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)

ocr_result = pytesseract.image_to_string(th, lang='ind')

result = {
    'provinsi': '',
    'kabupaten_kota': '',
    'nik': '',
    'nama': '',
    'tempat_lahir': '',
    'tanggal_lahir': '',
    'jenis_kelamin': '',
    'gol_darah': '',
    'alamat': '',
    'rtrw': '',
    'kel_desa': '',
    'kecamatan': '',
    'agama': '',
    'status_perkawinan': '',
    'pekerjaan': ''
}

# filter spaces/blanks
lines = list(filter(lambda s: not (s.isspace() or s == ''), ocr_result.splitlines()))

i = 0
length = len(lines)

# parse province
result['provinsi'] = lines[i][8:].strip()

# parse kota/kabupaten
i += 1
kota_ratio = fuzz.partial_ratio('kota', lines[i].lower())
kabupaten_ratio = fuzz.partial_ratio('kabupaten', lines[i].lower())
if kota_ratio > kabupaten_ratio:
    result['kabupaten_kota'] = lines[i][4:].strip()
else:
    result['kabupaten_kota'] = lines[i][9:].strip()

# parse NIK
# note: from now on, ':' may be treated as '1'
i += 1
result['nik'] = lines[i][6:].strip()

# parse name
i += 1
result['nama'] = lines[i][6:].strip()

# parse birth place and date
i += 1
birth_place_date = lines[i][18:].strip()
result['tempat_lahir'] = birth_place_date[:birth_place_date.find(',')].strip()
result['tanggal_lahir'] = birth_place_date[birth_place_date.find(',')+1:].strip()

# parse gender and blood type
i += 1
result['jenis_kelamin'] = lines[i][15:lines[i].lower().find('go')].strip()
result['gol_darah'] = lines[i][lines[i].lower().find('darah')+7:].strip()

# parse address
i += 1
result['alamat'] = lines[i][8:].strip()

# parse rt/rw
i += 1
result['rtrw'] = lines[i][6:].strip()

# parse kel/desa
i += 1
result['rtrw'] = lines[i][10:].strip()

# parse kecamatan
i += 1
result['kecamatan'] = lines[i][11:].strip()

# parse agama
i += 1
result['agama'] = lines[i][7:].strip()

# parse marital status
i += 1
result['status_perkawinan'] = lines[i][18:].strip()

i += 1
result['pekerjaan'] = lines[i][11:].strip()
