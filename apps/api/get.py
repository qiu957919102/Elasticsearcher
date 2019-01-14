# -*- coding: utf-8 -*-

from apps.api import api


@api.route('/get/test')
def test():
    return 'test'
