# -*- coding: utf-8 -*-
import json
import math
import logging
from odoo import http, _, exceptions
from odoo.http import request
from .serializers import Serializer
from .exceptions import QueryFormatError
import requests

_logger = logging.getLogger(__name__)
import json


def error_response(error, msg):
    return {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": 200,
            "message": msg,
            "data": {
                "name": str(error),
                "debug": "",
                "message": msg,
                "arguments": list(error.args),
                "exception_type": type(error).__name__
            }
        }
    }


_logger = logging.getLogger(__name__)


class APIController(http.Controller):

    @http.route(
        '/api/getCategories',
        type='http', auth="public", methods=['POST'], website=False, csrf=False)
    def post_model_data_product_category(self, **params):

        records = request.env['product.category'].sudo().search([])

        allowed_fields = {"name", "name_ar", "id", "create_uid", "image_1920"}

        if "query" in params:
            raw_query = params["query"]
            query_fields = set(raw_query.split(","))
            sanitized_query_fields = query_fields.intersection(allowed_fields)
            if sanitized_query_fields:
                query = "{" + ",".join(sanitized_query_fields) + "}"
            else:
                query = "{" + ",".join(allowed_fields) + "}"
        else:
            query = "{" + ",".join(allowed_fields) + "}"

        if "order" in params:
            orders = json.loads(params["order"])
        else:
            orders = ""

        if "filter" in params:
            filters = json.loads(params["filter"])
            records = request.env['product.category'].sudo().search(filters, order=orders)

        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "page_size" in params:
            page_size = int(params["page_size"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)

            if "page" in params:
                current_page = int(params["page"])
            else:
                current_page = 1  # Default page Number
            start = page_size * (current_page - 1)
            stop = current_page * page_size
            records = records[start:stop]
            next_page = current_page + 1 \
                if 0 < current_page + 1 <= total_page_number \
                else None
            prev_page = current_page - 1 \
                if 0 < current_page - 1 <= total_page_number \
                else None

        if "limit" in params:
            limit = int(params["limit"])
            records = records[0:limit]

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "result": data
        }
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )

    @http.route(
        '/api/getProducts',
        type='http', auth="public", methods=['POST'], website=False, csrf=False)
    def post_model_data_product_product(self, **params):
        records = request.env['product.template'].sudo().search([])
        query = "{ id,name, name_ar,  list_price,description_sale,description_sale_ar, qty_available ,taxes_id { name , amount } ,categ_id { id ,name ,name_ar ,image_1920  },create_uid  ,size_ids {id ,name } ,color_ids {id ,name },image_1920,product_template_image_ids { id ,name, image_1920} }"
        if "order" in params:
            orders = json.loads(params["order"])
        else:
            orders = ""
        if "filter" in params:
            filters = json.loads(params["filter"])
            records = request.env['product.template'].sudo().search(filters, order=orders)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "page_size" in params:
            page_size = int(params["page_size"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)

            if "page" in params:
                current_page = int(params["page"])
            else:
                current_page = 1  # Default page Number
            start = page_size * (current_page - 1)
            stop = current_page * page_size
            records = records[start:stop]
            next_page = current_page + 1 \
                if 0 < current_page + 1 <= total_page_number \
                else None
            prev_page = current_page - 1 \
                if 0 < current_page - 1 <= total_page_number \
                else None

        if "limit" in params:
            limit = int(params["limit"])
            records = records[0:limit]

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "result": data
        }
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )

    @http.route(
        '/api/getCustomer',
        type='http', auth='user', methods=['GET'], csrf=False)
    def post_model_data_customer(self, **params):
        records = request.env.user.partner_id
        query = "{id,name,vat,email,phone,mobile ,title { id , name }, street, street2, city, state_id { id,name,code } ,zip , country_id {id,name,code } , child_ids {id,  name,type,vat,email,phone,mobile ,title { id , name }, street, street2, city, state_id { id,name,code } ,zip , country_id {id,name,code } }}  "

        if "order" in params:
            orders = json.loads(params["order"])
        else:
            orders = ""

        if "filter" in params:
            filters = json.loads(params["filter"])
            records = request.env['res.partner'].search(filters, order=orders)

        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "page_size" in params:
            page_size = int(params["page_size"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)

            if "page" in params:
                current_page = int(params["page"])
            else:
                current_page = 1  # Default page Number
            start = page_size * (current_page - 1)
            stop = current_page * page_size
            records = records[start:stop]
            next_page = current_page + 1 \
                if 0 < current_page + 1 <= total_page_number \
                else None
            prev_page = current_page - 1 \
                if 0 < current_page - 1 <= total_page_number \
                else None

        if "limit" in params:
            limit = int(params["limit"])
            records = records[0:limit]

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            res = error_response(e, e.msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "result": data
        }
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )
