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

{
    'name': '',
    'version': '1.0',
    'category': '',
    'sequence': 6,
    'summary': '',
    "author": "Odoie",
    'company': 'Odoie',
    'maintainer': 'Odoie',
    'website': "https://www.Odoie.com",
    "description": """ """,
    'depends': ['sale_management', 'account', 'stock','product'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/product_category.xml',
        'views/product_template.xml',
        'views/sale_order.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
}
