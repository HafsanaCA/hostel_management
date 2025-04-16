from odoo import models, api


class StudentLeaveReportPdf(models.AbstractModel):
    _name = 'report.hostel_management.student_leave_report_template'
    _description = 'Student Leave Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        query = """
            SELECT row_number() OVER() AS sl_no,
            s.name AS student_name, r.name AS room_name, l.leave_date, l.arrival_date, 
            (l.leave_date - l.arrival_date) AS duration
            FROM leave_request l
            JOIN student_information s ON s.id = l.student_id
            JOIN room_management r ON r.id = s.room_id
            WHERE (%(student_id)s IS NULL OR s.id = %(student_id)s)
            AND (%(room_id)s IS NULL OR r.id = %(room_id)s)
            AND (%(arrival_date)s IS NULL OR l.arrival_date >= %(arrival_date)s)
            AND (%(leave_date)s IS NULL OR l.leave_date >= %(leave_date)s)  
        """

        if data is None:
            data = {}

        self.env.cr.execute(query, data)
        results = self.env.cr.dictfetchall()

        return {
            'doc_ids': docids,
            'doc_model': 'leave.request.report',
            'docs': results,
            'data': data,
            'report_title': "Students Leave Request Report"
        }
