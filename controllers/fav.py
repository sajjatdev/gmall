from odoo import http
from odoo.http import request
import json


class FavoriteAPI(http.Controller):
    @http.route('/api/favorites', type='http', auth='user', methods=['GET'], csrf=False)
    def get_favorites(self, **params):
        """
        Fetch all favorites for the logged-in user.
        """
        try:
            user_id = request.env.user.id
            favorites = request.env['product.favorite'].sudo().search([('user_id', '=', user_id)])

            # Prepare the response data
            data = [{
                'id': fav.id,
                'product_id': fav.product_id.id,
                'name': fav.product_id.name,
                'name_ar': fav.product_id.name_ar,
                'user_id': fav.user_id.id
            } for fav in favorites]

            return request.make_response(
                json.dumps({'data': data, 'code': 200}),
                status=200,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e), 'code': 500}),
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/api/favorites', type='http', auth='user', methods=['POST'], csrf=False)
    def create_favorite(self, **params):
        """
        Add a product to the user's favorites.
        """
        try:
            # Parse the incoming JSON request body
            params = json.loads(request.httprequest.data)
            product_id = params.get('product_id')
            user_id = request.env.user.id

            favorites = request.env['product.favorite'].sudo().search(
                [('user_id', '=', user_id), ('product_id', '=', product_id)])
            if favorites:
                return request.make_response(
                    json.dumps({'success': False, 'message': 'Product is already added to favorites', 'code': 200,
                                "id": favorites.id}), status=200,

                    headers={'Content-Type': 'application/json'}
                )

            if not product_id:
                return request.make_response(
                    json.dumps({'error': 'Product ID is required', 'code': 400}),
                    headers={'Content-Type': 'application/json'}
                )

            # Create a new favorite record
            request.env['product.favorite'].create({
                'product_id': product_id,
                'user_id': user_id
            })

            return request.make_response(
                json.dumps({'success': True, 'message': 'Product added to favorites', 'code': 200}),
                status=200,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e), 'code': 500}),
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/api/favorites/<int:favorite_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_favorite(self, favorite_id, **params):
        """
        Remove a product from the user's favorites.
        """
        try:
            # Fetch the favorite record by ID
            favorite = request.env['product.favorite'].browse(favorite_id)

            if not favorite or favorite.user_id.id != request.env.user.id:
                return request.make_response(
                    json.dumps({'error': 'Favorite not found or access denied', 'code': 404}),
                    headers={'Content-Type': 'application/json'}
                )

            # Delete the record
            favorite.unlink()

            return request.make_response(
                json.dumps({'success': True, 'message': 'Favorite deleted successfully', 'code': 200}),
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e), 'code': 500}),
                headers={'Content-Type': 'application/json'}
            )
