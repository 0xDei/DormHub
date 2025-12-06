import flet as ft
from datetime import datetime

from pages.sections.section import Section
from utils.element_factory import create_info_card

class Residents(Section):
    def __init__(self, admin_page):
        super().__init__()