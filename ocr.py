#!/usr/bin/python3
from PIL import Image
import pytesseract
import requests
import os
import json
from datetime import datetime
from pytz import timezone
from requests_html import HTMLSession
import argparse


class CaptchaOCR:
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


class ActivityHelper():
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.session = HTMLSession()

    def get_chptcha(self):
        # get captcha code
        ocr = CaptchaOCR(
            'https://mkp-tsbank.cdn.hinet.net/tscccms/CodeController/kaptcha')
        return ocr.parse(), ocr.get_image_response()

    def login(self):
        code, response = self.get_chptcha()
        self.cookie = response.cookies['SESSION']
        print('Cookie: %s' % self.cookie)

        data = {
            'verifyCode': code,
            'cust_id': self.id,
            'eventId': ''}
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://mkp-tsbank.cdn.hinet.net/tscccms/login',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'SESSION=%s' % self.cookie}

        r = self.session.post(
            'https://mkp-tsbank.cdn.hinet.net/tscccms/checkVerifyCode', data=data, headers=headers)

        result = r.html.html
        if result == 'notPassCode' or result == 'overLimit' or result == 'noPass' or result == 'errorFormat':
            print("Error: ", result)

    def find_all(self):
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://mkp-tsbank.cdn.hinet.net/tscccms/login',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'SESSION=%s' % self.cookie}
        r = self.session.get(
            'https://mkp-tsbank.cdn.hinet.net/tscccms/register/select', headers=headers)
        activities = r.html.find(
            '.form-item:not(.form-item-selected) input:checkbox[name="event-select"]')
        datas = []

        for item in activities:
            event_values = item.attrs['value'].split('_')
            datas.append({
                'eventId': event_values[0],
                'installmentEvent': event_values[1],
                'regEndDate': datetime.strptime(event_values[2], '%a %b %d %H:%M:%S %Z %Y').strftime('%Y-%m-%dT%H:%M:%S.000+08:00').__str__()
            })
            print('Selected: %s' % datas)
            break
        return datas

    def select_all(self):
        datas = self.find_all()
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://mkp-tsbank.cdn.hinet.net/tscccms/register/select',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': 'SESSION=%s' % self.cookie,
            'Accept': 'text/plain, */*; q=0.01'}

        r = self.session.post('https://mkp-tsbank.cdn.hinet.net/tscccms/register/save',
                              data=json.dumps(datas), headers=headers)

        print('Result: %s' % (int(r.text) == len(datas)))

    def execute(self):
        self.login()
        self.select_all()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers from image.')
    parser.add_argument('-u' ,'-', dest='url')

    helper = ActivityHelper('R123957365')
    helper.execute()
