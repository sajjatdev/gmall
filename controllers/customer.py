from odoo import http
from odoo.http import request
import json


class AddressController(http.Controller):

    @http.route('/api/CreateAndUpdateAddress', type='http', auth='user', methods=['POST'], csrf=False)
    def update_profile_or_address(self, **post):
        try:
            # Fetch the logged-in user's partner
            user_partner = request.env.user.partner_id
            post = json.loads(request.httprequest.data)
            # Determine operation type
            if post.get('update_profile', False):  # Update the profile (parent partner)
                user_partner.sudo().write({
                    'name': post.get('name', user_partner.name),
                    'street': post.get('street', user_partner.street),
                    'city': post.get('city', user_partner.city),
                    'zip': post.get('zip', user_partner.zip),
                    'country_id': post.get('country_id', user_partner.country_id.id),
                    'phone': post.get('phone', user_partner.phone),
                    'email': post.get('email', user_partner.email),
                })
                response_data = {
                    'message': 'Profile updated successfully.',
                    'profile_id': user_partner.id,
                    'code': 200
                }
            else:
                address_id = post.get('id')
                if address_id:
                    # Update an existing child address
                    address = request.env['res.partner'].sudo().browse(int(address_id))
                    if address and address.parent_id == user_partner:
                        address.write({
                            'street': post.get('street', address.street),
                            'city': post.get('city', address.city),
                            'zip': post.get('zip', address.zip),
                            'country_id': post.get('country_id', address.country_id.id),
                            'phone': post.get('phone', address.phone),
                            'email': post.get('email', address.email),
                        })
                        response_data = {
                            'message': 'Address updated successfully.',
                            'address_id': address.id,
                            'code': 200
                        }
                    else:
                        return request.make_response(
                            json.dumps({'error': 'Address not found or not associated with your account', 'code': 404}),
                            status=404,
                            headers={'Content-Type': 'application/json'}
                        )
                else:
                    # Create a new child address
                    new_address = request.env['res.partner'].sudo().create({
                        'name': post.get('name', 'Default Name'),
                        'street': post.get('street'),
                        'city': post.get('city'),
                        'zip': post.get('zip'),
                        'country_id': post.get('country_id'),
                        'phone': post.get('phone'),
                        'email': post.get('email'),
                        'parent_id': user_partner.id,  # Associate with the logged-in user
                        'type': 'delivery',
                    })
                    response_data = {
                        'message': 'Address created successfully.',
                        'address_id': new_address.id,
                        'code': 200
                    }

            # Successful response
            return request.make_response(
                json.dumps(response_data),
                status=200,
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            # Handle exceptions
            return request.make_response(
                json.dumps({'error': str(e), 'code': 500}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )
