# -*- coding: utf-8 -*-
#############################################################################
#    odoie
#    Copyright (C) 2022-TODAY odoie.com
#    Author: odoie (<https://www.odoie.com>)
#    License: GNU LGPL v3
#############################################################################
import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    _inherit = 'product.category'

    name_ar = fields.Char("Arabic Name")
    image_1920 = fields.Binary(string="Image")
