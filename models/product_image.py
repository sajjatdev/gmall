# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from odoo import api, fields, models, tools, _

class ProductImage(models.Model):
    _name = 'product.image'
    _description = "Product Image"
    _inherit = ['image.mixin']

    image_1920 = fields.Image()
    name = fields.Char(string='Name')
    product_tmpl_id = fields.Many2one('product.template', "Product Template", index=True, ondelete='cascade')
