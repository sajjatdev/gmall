from odoo import http
from odoo.http import request
import json
import base64


class InvoiceController(http.Controller):

    @http.route('/api/getInvoices', type='http', auth='user', methods=['GET'],
                csrf=False)
    def get_user_invoices(self):
        try:
            # Fetch the current user's partner and child partners
            user_partner = request.env.user.partner_id
            partner_ids = [user_partner.id] + user_partner.child_ids.ids

            # Fetch invoices
            invoices = request.env['account.move'].sudo().search([
                ('partner_id', 'in', partner_ids),
                ('move_type', '=', 'out_invoice')  # Customer invoices
            ])

            # Prepare response data
            data = [{
                'id': invoice.id,
                'name': invoice.name,
                'date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else None,
                'amount_total': invoice.amount_total,
                'partner_id': invoice.partner_id.id,
                'partner_name': invoice.partner_id.name,
                'payment_status': invoice.payment_status,
            } for invoice in invoices]

            # Return successful response
            return request.make_response(
                json.dumps({'data': data, 'code': 200}),
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

    @http.route('/api/getInvoicePDF', type='http', auth='user', methods=['GET'])
    def get_invoice_pdf(self, invoice_id):
        try:
            # Validate and fetch the invoice
            invoice = request.env['account.move'].sudo().browse(int(invoice_id))
            if not invoice or invoice.move_type != 'out_invoice':
                return request.make_response(
                    json.dumps({'error': 'Invoice not found or invalid ID', 'code': 404}),
                    status=404,
                    headers={'Content-Type': 'application/json'}
                )

            # Render the PDF
            # pdf_content, _ = request.env.ref('account.account_invoices').sudo()._render_qweb_pdf([invoice.id])
            pdf_content, _ = request.env["ir.actions.report"].sudo()._render_qweb_pdf(
                "account.account_invoices", [invoice.id]
            )

            # Encode the PDF in Base64
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

            # Return the response
            return request.make_response(
                json.dumps({'pdf_base64': pdf_base64, 'code': 200}),
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
