#!/usr/bin/env python

import requests
from pyquery import PyQuery as pq
from jobs import AbstractJob


class Ambient(AbstractJob):

    def __init__(self, conf):
        self.sensors = conf['sensors']
        self.interval = conf['interval']

    def _get_sensor_value(self, url):
        r = requests.get(url)
        if r.status_code == 200 and len(r.content) > 0:
            return self._parse(r.content)
        return {}

    def _parse(self, html):
        d = pq(html)
        return d.text().split(' ')

    def get(self):
        data = {'sensors': {}}
        for location, url in self.sensors:
            sensorValue = self._get_sensor_value(url)
            if len(sensorValue) > 0:
                data['sensors'].update({
                    location: {
                        'temperature': sensorValue[0],
                        'humidity': sensorValue[1],
                    }
                })
        return data
