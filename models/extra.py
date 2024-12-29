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


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    promotion_code = fields.Char(string="Promotion Code")
    _sql_constraints = [
        ('promotion_code_unique', 'unique(promotion_code)',
         "The promotion code must be unique. Please select a different one.")
    ]


class ProductSize(models.Model):
    _name = 'product.size'
    _description = "Product Size"

    name = fields.Char("Size")


class ProductColor(models.Model):
    _name = 'product.color'
    _description = "Product Color"

    name = fields.Char("Color")


class ProductFavorite(models.Model):
    _name = 'product.favorite'
    _description = "Product Favorite"

    user_id = fields.Many2one('res.users', string="User")
    product_id = fields.Many2one('product.template', string="Product")


class Cart(models.Model):
    _name = 'cart'
    _description = "Cart Model"

    user_id = fields.Many2one('res.users', string="User", required=True)
    product_id = fields.Many2one('product.template', string="Product", required=True)
    quantity = fields.Integer(string="Quantity", default=1, required=True)
    size_id = fields.Many2one('product.size', string="Size")
    color_id = fields.Many2one('product.color', string="Color")

    @api.model
    def add_to_cart(self, user_id, product_id, quantity=1, size_id=None, color_id=None):
        """Adds or updates a cart record for the user."""
        cart_line = self.search([
            ('user_id', '=', user_id),
            ('product_id', '=', product_id),
            ('size_id', '=', size_id),
            ('color_id', '=', color_id)
        ], limit=1)

        if cart_line:
            cart_line.quantity += quantity
        else:
            self.create({
                'user_id': user_id,
                'product_id': product_id,
                'quantity': quantity,
                'size_id': size_id,
                'color_id': color_id
            })

    @api.model
    def get_cart(self, user_id):
        """Retrieves the cart for a specific user."""
        cart_lines = self.sudo().search([('user_id', '=', user_id)])
        return [{
            'product_id': line.product_id.id,
            'product_name': line.product_id.name,
            'quantity': line.quantity,
            'size_id': [line.size_id.id, line.size_id.name] if line.size_id else [],
            'color_id': [line.color_id.id, line.size_id.name] if line.color_id else [],
        } for line in cart_lines]

    @api.model
    def delete_from_cart(self, user_id, product_id, size_id=None, color_id=None):
        """Removes a specific product from the cart."""
        cart_line = self.search([
            ('user_id', '=', user_id),
            ('product_id', '=', product_id),
            ('size_id', '=', size_id),
            ('color_id', '=', color_id)
        ], limit=1)
        if cart_line:
            cart_line.unlink()
