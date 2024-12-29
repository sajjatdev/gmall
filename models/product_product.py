# -*- coding: utf-8 -*-
#############################################################################
#    odoie
#    Copyright (C) 2022-TODAY odoie.com
#    Author: odoie (<https://www.odoie.com>)
#    License: GNU LGPL v3
#############################################################################

import base64
import logging
import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = 'product.template'

    name = fields.Char("Name ", translate=False, )
    name_ar = fields.Char("Arabic Name", translate=False, )

    size_ids = fields.Many2many(
        'product.size',
        string='Sizes',
    )

    color_ids = fields.Many2many(
        'product.color',
        string='Colors', )

    description_sale = fields.Text(translate=False, )

    description_sale_ar = fields.Text(
        'Sales Description AR', translate=False,
        help="A description of the Product that you want to communicate to your customers. "
             "This description will be copied to every Sales Order, Delivery Order and Customer Invoice/Credit Note")
    product_template_image_ids = fields.One2many(
        string="Extra Product Media",
        comodel_name='product.image',
        inverse_name='product_tmpl_id',
        copy=True,
    )
