# -*- coding: utf-8 -*-
import json
import io
import xlsxwriter
from odoo import models,fields
from odoo.http import request


class StudentWizard(models.TransientModel):
    _name = 'student.wizard'
    _description = 'Student wizard'

    room_id = fields.Many2one('room.management', string='Room')
    student_id = fields.Many2one('student.information', string='Student')

    def action_print_report(self):
        data = {
            'student_id': self.student_id.id,
            'room_id' : self.room_id.id
        }
        return self.env.ref('hostel_management.student_report_pdf').report_action(self, data=data)

    def action_print_xlsx(self):
        data = {
            'model_id': self.id,
            'student_id': self.student_id.id,
            'room_id': self.room_id.id,
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'student.wizard',
                'options': json.dumps(data),
                'output_format': 'xlsx',
                'report_name': 'Student Excel Report',
            },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        room_id = data.get('room_id')
        student_id = data.get('student_id')
        student = request.env['student.information'].browse(student_id) if student_id else None
        room = request.env['room.management'].browse(room_id) if room_id else student.room_id if student else None

        query = """
                SELECT 
                    si.id, 
                    si.name, 
                    rm.name AS room_name,
                    si.pending_amount,
                    si.invoice_status
                FROM student_information si
                LEFT JOIN room_management rm ON si.room_id = rm.id
                WHERE 1=1
            """
        params = []

        if room_id:
            query += " AND si.room_id = %s"
            params.append(room_id)

        if student_id:
            query += " AND si.id = %s"
            params.append(student_id)

        request.env.cr.execute(query, tuple(params))
        results = request.env.cr.dictfetchall()

        for result in results:
            result['invoice_status'] = dict(self.env['student.information']._fields['invoice_status'].selection).get(
                result['invoice_status'])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        head_format = workbook.add_format({'font_size': 22, 'align': 'center', 'bold': True, })
        cell_format = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True, 'bg_color':'#f2f2f2',
                                           'border':1})
        text_format = workbook.add_format({'font_size': 10, 'align':'center', 'border':1})

        sheet.merge_range('F2:J3', 'STUDENT REPORT', head_format)

        row = 5
        if room_id and not student_id:
            sheet.write(row, 4, 'Room ', cell_format)
            sheet.write(row, 5, room.name, text_format)
            row += 2
        elif student_id:
            sheet.write(row, 4, 'Student ', cell_format)
            sheet.write(row, 5, student.name, text_format)
            row += 1
            if room:
                sheet.write(row, 4, 'Room', cell_format)
                sheet.write(row, 5, room.name, text_format)
                row += 1
            row += 1

        columns = [('Sl.no', 10)]
        if not student_id:
            columns.append(('Student', 20))
        if not room_id and not student_id:
            columns.append(('Room', 20))
        columns += [('Pending Amount', 15), ('Invoice Status', 15)]

        for col, (header,width) in enumerate(columns):
            sheet.set_column(col + 4, col + 4, width)
            sheet.write(row, col + 4, header, cell_format)
        row += 1
        sl = 1

        for rec in results:
            col = 4
            sheet.write(row,col, sl, text_format)
            col += 1
            if not student_id:
                sheet.write(row, col, rec.get('name'), text_format)
                col += 1
            if not room_id and not student_id:
                sheet.write(row, col, rec.get('room_name'), text_format)
                col += 1
            sheet.write(row, col, rec.get('pending_amount'), text_format)
            col += 1
            sheet.write(row, col, rec.get('invoice_status'), text_format)
            row += 1
            sl += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
