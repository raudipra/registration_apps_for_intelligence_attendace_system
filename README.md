#\[Cognixy\] IAS - Registration Module

## How to Run (development)

1. Install required python dependencies using `pip install -e .`
2. Make sure `tesseract` is available in your system's PATH, with Indonesian `ind` language installed.
3. Copy the `ocr.traineddata` file from `web/ocr/train` to the location of your tesseract
4. Set environment variables `FLASK_APP=web` and `FLASK_ENV=development`
5. Run the development web server `flask run`

