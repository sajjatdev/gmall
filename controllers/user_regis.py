from odoo import http, Command
from odoo.http import request, route
import json
import requests
import logging

_logger = logging.getLogger(__name__)


class UserRegistrationController(http.Controller):

    @http.route('/api/register', type='http', auth='none', methods=['POST'], csrf=False)
    def user_register(self, **kwargs):
        try:
            params = json.loads(request.httprequest.data)
            # Extract parameters
            full_name = params.get('full_name')
            email = params.get('email')
            password = params.get('password')
            confirm_password = params.get('confirm_password')
            mobile_number = params.get('mobile_number')
            # db = params.get('db')
            # Validation
            if not all([full_name, email, password, confirm_password, mobile_number]):
                return request.make_response(
                    json.dumps({
                                   'error': 'All fields are required: full_name, email, password, confirm_password , mobile_number'}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )

            if password != confirm_password:
                return request.make_response(
                    json.dumps({'error': 'Password and confirm password do not match'}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )

            # Check if the email is already registered
            existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if existing_user:
                return request.make_response(
                    json.dumps({'error': 'Email is already registered'}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )
            # Create the new user
            new_user = request.env['res.users'].sudo().create({
                'name': full_name,
                'login': email,
                'company_ids': [Command.link(request.env.ref('base.main_company').id)],
                'company_id': request.env.ref('base.main_company').id,
                'groups_id': [Command.link(request.env.ref('base.group_public').id)],
                'password': password,
            })
            new_user.partner_id.mobile = mobile_number
            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'User registered and authenticated successfully',
                    'user_id': new_user.id,
                    'partner_id': new_user.partner_id.id,
                }),
                status=201,
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            _logger.error(f"Error during user registration: {str(e)}")
            return request.make_response(
                json.dumps({'error': 'An unexpected error occurred', 'details': str(e)}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )
