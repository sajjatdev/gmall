# -*- coding: utf-8 -*-
#############################################################################
#
#    odoie
#
#    Copyright (C) 2022-TODAY odoie.com
#    Author: odoie (<https://www.odoie.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import logging
from odoo import _, api, fields, models, Command
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    color_id = fields.Many2one('product.color', string='Color')
    size_id = fields.Many2one('product.size', string='Size')
