# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import content_disposition
from odoo.tools import html_escape
from odoo.http import request, Controller, route
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class XLSXReportController(http.Controller):
    @http.route('/xlsx_reports', type='http', auth='user',
                csrf=False)
    def get_report_xlsx(self, model, options, output_format, report_name,
                        token='ads'):
        """ Return data to python file passed from the javascript"""
        session_unique_id = request.session.uid
        report_object = request.env[model].with_user(session_unique_id)
        options = json.loads(options)
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[('Content-Type', 'application/vnd.ms-excel'), (
                        'Content-Disposition',
                        content_disposition(f"{report_name}.xlsx"))
                             ]
                )
                report_object.get_xlsx_report(options, response)
                response.set_cookie('fileToken', token)
                return response
        except Exception:
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
            }
            return request.make_response(html_escape(json.dumps(error)))

class StudentRegistration(http.Controller):
    @http.route(['/register'], type='http', auth='public', website=True)
    def student_register_form(self, **kwargs):
        available_rooms = request.env['room.management'].search([('state', 'in', ['empty', 'partial'])])
        return request.render('hostel_management.student_registration_form', {
            'rooms': available_rooms,
        })

    @http.route(['/register/submit'], type='http', auth='public', website=True, csrf=True)
    def student_register_submit(self, **post):
        room_id = post.get('room_id')
        room = request.env['room.management'].sudo().browse(int(room_id)) if room_id else False
        student_vals = {
            'name': post.get('name'),
            'email': post.get('email'),
            'dob': post.get('dob'),
            'receive_mail': True if post.get('receive_mail') == 'on' else False,
            'room_id': post.get('room_id'),
        }
        student = request.env['student.information'].sudo().create(student_vals)
        print("The student details are.......", student.read())
        if room.state != 'full':
            room.write({
                'occupied_beds': room.occupied_beds + 1
            })
        return request.render('hostel_management.student_register_success')
