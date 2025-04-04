# -*- coding: utf-8 -*-
from odoo import models, fields

class CleaningService(models.Model):
    _name = 'cleaning.service'
    _description = 'Cleaning Service'
    _rec_name = 'cleaning_staff'

    room_id = fields.Many2one('room.management', string="Room", tracking=True)
    start_time = fields.Datetime(string="Start Time", default=fields.datetime.now())
    cleaning_staff = fields.Many2one('res.users', string="Staff", required=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', copy=False, string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    state = fields.Selection(selection=[('new', 'New'), ('assigned', 'Assigned'), ('done', 'Done')], required=True,
                             tracking=True, default='new', readonly=True, store=True)


    def action_assign(self):
        """Assigns the cleaning request to the current user and sets the state to 'assigned' """
        self.ensure_one()

        self.write({
            'state': 'assigned',
            'cleaning_staff': self.env.user.id,
        })

    def action_complete(self):
        """Marks the cleaning request as 'done' and sets the room state to 'empty' if applicable """
        self.ensure_one()

        self.write({'state': "done"})
        if self.room_id:
            self.room_id.write({'state': 'empty'})
