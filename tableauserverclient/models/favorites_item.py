import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger('tableau.models.favorites_item')

class Favorite:
    Workbook = 'workbook'
    Datasource = 'datasource'
    View = 'view'
    Project = 'project'