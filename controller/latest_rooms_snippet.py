from odoo import http
from odoo.http import request

class WebsiteRooms(http.Controller):
    @http.route('/get_latest_rooms', auth="public", type='json', website=True)
    def get_latest_hostel_rooms(self):
        """Get the latest 4 rooms for the snippet."""
        latest_rooms = request.env['room.management'].sudo().search_read([('state', 'in', ['empty', 'partial'])],
                                  fields=['name', 'room_type', 'beds', 'rent', 'total_rent','id'],
                                  order='create_date desc', limit=4)
        values = {
            'latest_rooms': latest_rooms,
        }
        return values
