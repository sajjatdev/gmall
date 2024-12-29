from odoo import http
from odoo.http import request, Response
import json
import logging
from odoo import Command
from odoo import http, fields

_logger = logging.getLogger(__name__)


class Order(http.Controller):

    @http.route('/api/order', type='http', auth='user', methods=['POST'], csrf=False)
    def convert_cart_to_sales_order(self, **params):
        try:
            # Parse JSON data from the request
            params = json.loads(request.httprequest.data)

            user_id = request.env.user.id
            promotion_code = params.get('promotion_code')
            partner_id = params.get('partner_id')
            if not partner_id:
                # Retrieve the user's contacts and child contacts for address validation
                user_partner = request.env['res.partner'].sudo().search([('id', '=', partner_id)])

                child_contacts = request.env.user.partner_id
                child_contacts = request.env.user.partner_id.child_ids

                # # Ensure the user has at least one address
                if user_partner not in child_contacts:
                    return request.make_response(
                        json.dumps({'error': 'No address found for the user'}),
                        status=400,
                        headers={'Content-Type': 'application/json'}
                    )
            else:
                user_partner = request.env.user.partner_id

            # Retrieve the cart for the user
            cart = request.env['cart'].sudo().search([('user_id', '=', user_id)])
            if not cart:
                return request.make_response(
                    json.dumps({'error': 'No cart found'}),
                    status=404,
                    headers={'Content-Type': 'application/json'}
                )

            if not cart.product_id:
                return request.make_response(
                    json.dumps({'error': 'Cart is empty'}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )

            # Group cart lines by the creator of the product
            order_data = {}
            for line in cart:
                creator_id = line.product_id.create_uid.id
                if creator_id not in order_data:
                    order_data[creator_id] = {
                        'order_lines': [],
                        'user_id': user_id
                    }
                product = request.env['product.product'].sudo().search([('product_tmpl_id', '=', line.product_id.id)],
                                                                       limit=1)
                order_data[creator_id]['order_lines'].append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': line.quantity,
                    'price_unit': line.product_id.list_price,
                    'color_id': line.color_id.id if line.color_id else False,
                    'size_id': line.color_id.id if line.color_id else False,
                }))

            # Check for promotion and apply the corresponding pricelist
            pricelist = False
            if promotion_code:
                pricelist = request.env['product.pricelist'].sudo().search([('promotion_code', '=', promotion_code)],
                                                                           limit=1)

            # Prepare sales orders
            sale_orders = []
            for creator_id, data in order_data.items():
                # Default address is the user's address
                address_id = user_partner.id

                # Create sale orders
                sale_order = request.env['sale.order'].sudo().create({
                    'partner_id': address_id,
                    'order_line': data['order_lines'],
                })
                if pricelist:
                    sale_order.pricelist_id = pricelist.id

                sale_order.action_update_prices()
                sale_order.action_confirm()
                sale_orders.append(sale_order.id)

            if sale_orders:
                invoicing_wizard = request.env['sale.advance.payment.inv'].sudo().create({
                    'sale_order_ids': [Command.link(s) for s in sale_orders],
                    'advance_payment_method': 'delivered',
                })
                invoicing_wizard.create_invoices()
                sale = request.env['sale.order'].sudo().browse(sale_orders[0])
                invoice = sale.invoice_ids[0]
                invoice.action_post()
                invoice_data = {
                    'customer': {
                        'id': invoice.partner_id.id,
                        'name': invoice.partner_id.name,
                        'email': invoice.partner_id.email,
                        'phone': invoice.partner_id.phone,
                        'street': invoice.partner_id.street,
                        'street2': invoice.partner_id.street2,
                        'city': invoice.partner_id.city,
                        'zip': invoice.partner_id.zip,
                        'country_id': invoice.partner_id.country_id.id,
                        'country_name': invoice.partner_id.country_id.name,
                    },
                    'invoice_lines': [
                        {
                            'product': line.product_id.name,
                            'quantity': line.quantity,
                            'price_unit': line.price_unit,
                            'subtotal': line.price_subtotal,
                            'tax': sum(t.amount for t in line.tax_ids)
                        } for line in invoice.invoice_line_ids
                    ],
                    'total_untaxed': invoice.amount_untaxed,
                    'total_taxed': invoice.amount_total
                }

            # Optionally, delete the cart after converting it to sales orders
            cart.unlink()
            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'Sales orders created',
                    'invoice_ids': invoice.id,
                    'invoice_data': invoice_data
                }),
                status=200,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            _logger.error(f"Error converting cart to sales order for user {user_id}: {e}")
            return request.make_response(
                json.dumps({'error': f'An unexpected error occurred{e}'}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/api/payment', type='http', auth='user', methods=['POST'], csrf=False)
    def reconcile_payment(self, **params):
        try:
            # Parse JSON data from the request
            params = json.loads(request.httprequest.data)
            invoice_id = params.get('invoice_id')
            payment_amount = params.get('payment_amount')
            transaction_id = params.get('transaction_id')

            if not (invoice_id and payment_amount and transaction_id):
                return Response(
                    json.dumps(
                        {'error': 'Missing required parameters: invoice_id, payment_amount, transaction_id'}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )

            # Fetch the invoice
            invoice = request.env['account.move'].sudo().browse(invoice_id)
            if not invoice or invoice.state != 'posted':
                return Response(
                    json.dumps({'error': 'Invoice not found or not in posted state'}),
                    status=404,
                    headers={'Content-Type': 'application/json'}
                )
            if invoice.payment_state in ('paid', 'in_payment'):
                return Response(
                    json.dumps(
                        {'error': 'Invoice payment state is already paid'}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )
            payment_journal = request.env['account.journal'].sudo().search([('type', '=', 'bank')], limit=1)

            # Create a payment
            payment = request.env['account.payment'].sudo().create({
                'partner_id': invoice.partner_id.id,
                'amount': payment_amount,
                'date': fields.Date.today(),
                'journal_id': payment_journal.id,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'ref': transaction_id,
            })

            # Post the payment
            payment.action_post()
            # Reconcile the payment with the invoice
            (invoice + payment.move_id).line_ids \
                .filtered(lambda x: x.account_id.account_type == 'asset_receivable') \
                .reconcile()

            return Response(
                json.dumps({
                    'success': True,
                    'message': 'Payment created and reconciled successfully',
                    'payment_id': payment.id,
                }),
                status=200,
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            _logger.error(f"Error processing payment: {e}")
            return Response(
                json.dumps({'error': f'An unexpected error occurred: {e}'}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )
