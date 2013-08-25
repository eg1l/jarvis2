#!/usr/bin/env python

import requests
from jobs import AbstractJob
from pyquery import PyQuery as pq


class Wattmeter(AbstractJob):

    def __init__(self, conf):
        self.interval = conf['interval']
        self.url = conf['url']
        self.name = conf['name']
        self.wh = self._get_power()

    def _get_power(self):
        r = requests.get(self.url)
        if r.status_code == 200 and len(r.content) > 0:
            return self._parse(r.content)
        return {}

    def _parse(self, html):
        d = pq(html)
        return d.text().split(' ')

    def get(self):
        wh = self._get_power()
        if len(wh) == 2:
            deltaTime = float(wh[0]) - float(self.wh[0])
            deltaW = float(wh[1]) - float(self.wh[1])
            self.wh = wh
            wh = float((deltaW / deltaTime) / 10) if deltaTime != 0 else 0
            return {'value': {self.name: wh}}
        return None
