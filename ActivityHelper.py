#!/usr/bin/python3
# -*- coding: utf-8 -*
from PIL import Image
import pytesseract, requests, os, json, argparse, logging
from datetime import datetime
from pytz import timezone
from requests_html import HTMLSession
from CaptchaOCR import OCR

class ActivityHelper():
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.session = HTMLSession()

    def get_chptcha(self):
        # get captcha code
        ocr = OCR(
            'https://mkp-tsbank.cdn.hinet.net/tscccms/CodeController/kaptcha')
        return ocr.parse(), ocr.get_image_response()

    def login(self):
        code, response = self.get_chptcha()
        self.cookie = response.cookies['SESSION']
        logging.info('Cookie: %s' % self.cookie)

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
        if result == 'notPassCode':
            print('驗證碼檢核錯誤')
        elif result == 'overLimit':
            print('系統忙線中，請稍後再試!')
        elif result == 'noPass':
            print('卡片申請人身分證字號查無資料')
        elif result == 'errorFormat':
            print('身分證字號或統一編號有誤')
        elif result == 'errorLength':
            print('身分證字號或統一編號輸入長度有誤')
            

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
            logging.debug('Selected: %s' % datas)
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
        logging.info('Result: %s' % (int(r.text) == len(datas)))

    def get_unselected_events(self):
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://mkp-tsbank.cdn.hinet.net/tscccms/login',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'SESSION=%s' % self.cookie}
        r = self.session.get(
            'https://mkp-tsbank.cdn.hinet.net/tscccms/register/select', headers=headers)
        activities = r.html.find(
            '.form-item:not(.form-item-selected) .form-item-title span:not(.sr-only)')
        activities_desc = r.html.find(
            '.form-item .form-item-more-description')
        
        results = []

        for i in range(len(activities)):
            results.append({
                'title': activities[i].text,
                'desc': activities_desc[i].text
            })

        return json.dumps(results)

    def register(self):
        self.login()
        self.select_all()

    def get_events(self):
        self.login()
        return self.get_unselected_events()

def init_logging():
    logging.basicConfig(filename='ActivityHelper.log', level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# main
if (__name__ == "__main__"):
    init_logging()
    try:
        parser = argparse.ArgumentParser(description='Register taishin activities.')
        parser.add_argument('action', default='register')
        parser.add_argument('-u' ,'--user', dest='user_id')

        if not parser.parse_args().user_id:
            raise Exception('Please assign user via -u')

        helper = ActivityHelper(parser.parse_args().user_id)
        if parser.parse_args().action == 'register':
            helper.register()
        elif parser.parse_args().action == 'get':
            print(helper.get_events())
    except Exception as e:
        print(e)
