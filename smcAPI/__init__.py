"""Sancta Maria College API.

This module contains a python API for Sancta Maria College.
As of this version this module has support for the following services:
	-Main Webpage (http://www.sanctamaria.school.nz)
	-Sancta Maria Portal (https://portal.sanctamaria.school.nz/student/index.php)
	-Sancta Maria Schoology (http://schoology.sanctamaria.school.nz)

Todo:
	* Remove function writeTo
	* Convert text dates into datetime dates

Author: Jackson Chadfield
Email : ibjacksonc@hotmail.com
"""

__title__ = 'smcAPI'
__author__ = 'Jackson Chadfield'
__version__ = '1.0.0b'

from .main import SanctaMaria
from .portal import Portal
