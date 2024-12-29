from odoo import http
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)


class CartController(http.Controller):
    @http.route('/api/cart', type='http', auth='user', methods=['GET'], csrf=False)
    def get_cart(self, **params):
        try:
            user_id = request.env.user.id

            # Retrieve cart data
            cart_data = request.env['cart'].get_cart(user_id)

            return request.make_response(
                json.dumps({'cart': cart_data}),
                status=200,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            _logger.error(f"Error retrieving cart for user {user_id}: {e}")
            return request.make_response(
                json.dumps({'error': f'An unexpected error occurred {e}'}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/api/cart', type='http', auth='user', methods=['POST'], csrf=False)
    def add_to_cart(self, **params):
        try:
            user_id = request.env.user.id
            params = json.loads(request.httprequest.data)
            # Validate required parameters
            product_id = params.get('product_id')
            if not product_id:
                return request.make_response(
                    json.dumps({'error': 'Product ID is required'}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )

            try:
                product_id = int(product_id)
                quantity = int(params.get('quantity', 1))
                size_id = int(params.get('size_id', '0')) or None
                color_id = int(params.get('color_id', '0')) or None
            except ValueError:
                return request.make_response(
                    json.dumps({'error': 'Invalid input types'}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )

            # Add product to cart
            request.env['cart'].add_to_cart(user_id, product_id, quantity, size_id, color_id)

            return request.make_response(
                json.dumps({'success': True, 'message': 'Product added to cart'}),
                status=200,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            _logger.error(f"Error adding to cart for user {user_id}: {e}")
            return request.make_response(
                json.dumps({'error': f'An unexpected error occurred {e}'}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/api/cart', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_from_cart(self, **params):
        try:
            user_id = request.env.user.id
            params = json.loads(request.httprequest.data)
            # Validate required parameters
            product_id = params.get('product_id')
            if not product_id:
                return request.make_response(
                    json.dumps({'error': 'Product ID is required'}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )

            try:
                product_id = int(product_id)
                size_id = int(params.get('size_id', '0')) or None
                color_id = int(params.get('color_id', '0')) or None
            except ValueError:
                return request.make_response(
                    json.dumps({'error': 'Invalid input types'}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )

            # Delete product from cart
            request.env['cart'].delete_from_cart(user_id, product_id, size_id, color_id)

            return request.make_response(
                json.dumps({'success': True, 'message': 'Product removed from cart'}),
                status=200,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            _logger.error(f"Error deleting from cart for user {user_id}: {e}")
            return request.make_response(
                json.dumps({'error': 'An unexpected error occurred'}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )
