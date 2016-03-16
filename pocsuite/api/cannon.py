#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014-2015 pocsuite developers (http://seebug.org)
See the file 'docs/COPYING' for copying permission
"""

import time
import requests
from pocsuite.lib.core.data import kb
from pocsuite.lib.core.data import conf
from pocsuite.lib.core.common import filepathParser
from pocsuite.lib.core.common import multipleReplace
from pocsuite.lib.core.common import StringImporter
from pocsuite.lib.core.common import delModule
from pocsuite.lib.core.settings import POC_IMPORTDICT
from pocsuite.lib.core.settings import HTTP_DEFAULT_HEADER
from pocsuite.api.utils import logger
from pocsuite.api.utils import CUSTOM_LOGGING


class Cannon():

    def __init__(self, target, info={}):
        self.target = target
        self.pocString = info["pocstring"]
        self.pocName = info["pocname"]
        self.mode = "verify"
        self.delmodule = False
        self.params = {}
        conf.isPycFile = False
        conf.httpHeaders = {}

        try:
            kb.registeredPocs
        except Exception:
            kb.registeredPocs = {}


    def registerPoc(self):
        pocString = multipleReplace(self.pocString, POC_IMPORTDICT)
        _, self.moduleName = filepathParser(self.pocName)
        try:
            importer = StringImporter(self.moduleName, pocString)
            importer.load_module(self.moduleName)
        except ImportError, ex:
            pass  # TODO

    def run(self):
        try:
            self.registerPoc()
            poc = kb.registeredPocs[self.moduleName]
            result = poc.execute(self.target, mode=self.mode)
            output = (self.target, self.pocName, result.vulID, result.appName, result.appVersion, "success" if result.is_success() else "failed", time.strftime("%Y-%m-%d %X", time.localtime()), result.result)
            if self.delmodule:
                delModule(self.moduleName)
            return output
        except Exception as errMsg:
            logger.log(CUSTOM_LOGGING.ERROR, errMsg)
