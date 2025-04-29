/** @odoo-module */
import { renderToElement } from "@web/core/utils/render";
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

function chunkArray(array, size) {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
        chunks.push(array.slice(i, i + size));
    }
    return chunks;
}

publicWidget.registry.get_product_tab = publicWidget.Widget.extend({
    selector : '.categories_section',
    async willStart() {
        const result = await rpc('/get_latest_rooms', {});
        if(result && result.latest_rooms.length>0){
            const chunks = chunkArray(result.latest_rooms,4)
            if(chunks.length>0){
                chunks[0].is_active = true
            }
            const uniqueId = Date.now();
            this.$target.empty().html(renderToElement('hostel_management.category_data', {
                room_chunks:chunks,
                uniqueId:uniqueId
            }))
        }
    },
});
