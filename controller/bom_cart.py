from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale


class CustomWebsiteSale(WebsiteSale):

    @route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, access_token=None, revive='', **post):
        response = super().cart(access_token=access_token, revive='', **post)

        order = request.website.sale_get_order()
        website = request.env['res.config.settings'].search([],order='create_date desc', limit=1)
        product_ids = website.bom_product_ids.ids

        bom_components = {}
        cart_items = []
        for line in order.order_line:
            product = line.product_id
            if product.id in product_ids:
                bom = request.env['mrp.bom'].search([('product_tmpl_id', '=', product.product_tmpl_id.id)], limit=1)
                if bom:
                    bom_components[product.id] = bom.bom_line_ids
                cart_items.append(product)

        response.qcontext.update({
            'cart_bom_components': bom_components,
            'cart_items': cart_items,
            'product_ids': product_ids
        })

        return response