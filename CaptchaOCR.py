#!/usr/bin/python3
from PIL import Image
import pytesseract
import requests
import os
import json
from datetime import datetime
from pytz import timezone
from requests_html import HTMLSession

class OCR:
    def __init__(self, target):
        self.target = target
        self.tmp_path = 'tmp'

    def create_tmp_dir(self):
        try:
            if not os.path.exists('tmp'):
                os.mkdir(self.tmp_path)
        except OSError:
            print("Creation of the directory %s failed" % self.tmp_path)
        else:
            print("Successfully created the directory %s " % self.tmp_path)

    def parse(self):
        img_path = self.target

        if self.target.startswith('http'):
            img_path = self.download_image(self.target)

        img = Image.open(img_path)
        text = pytesseract.image_to_string(img, lang='eng')
        print('Captcha: %s' % text)
        return text

    def download_image(self, url):
        dest = 'tmp/captcha.jpg'
        self.response = requests.get(
            url, headers={'User-Agent': 'Mozilla/5.0'})
        img_data = self.response.content

        self.create_tmp_dir()
        with open(dest, 'wb') as handler:
            handler.write(img_data)

        return dest

    def get_image_response(self):
        return self.response