# -*- coding: utf-8 -*-
from odoo import models, api


class StudentReportPdf(models.AbstractModel):
    _name = 'report.hostel_management.student_report_template'
    _description = 'Student Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        student_id = data.get('student_id')
        room_id = data.get('room_id')

        query = """
            SELECT si.id, si.name, si.pending_amount, rm.name AS room_name, si.invoice_status
            FROM student_information si
            LEFT JOIN room_management rm ON si.room_id = rm.id  
            WHERE 1=1         
        """

        params = []

        if room_id:
            query += " AND si.room_id = %s"
            params.append(room_id)

        if student_id:
            query += "AND si.id = %s"
            params.append(student_id)

        self.env.cr.execute(query, tuple(params))
        results = self.env.cr.dictfetchall()

        for result in results:
            result['invoice_status'] = dict(self.env['student.information']._fields['invoice_status'].selection).get(
                result['invoice_status'])

        return {
            'doc_ids': docids,
            'doc_model': 'student.wizard',
            'docs': results,
            'data': data
        }
