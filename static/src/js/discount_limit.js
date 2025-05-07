/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        console.log("runninggggg......");

        const order = this.currentOrder;
        console.log("Current Order:", order);

        const maxDiscount = this.pos.pos_session ? this.pos.pos_session.max_discount_amount || 0 : 0;
        console.log("Max Discount Amount:", maxDiscount);

        const orderTotal = order.get_total_with_tax();

        const globalDiscountPercentage = order.discount || 0;
        const globalDiscountAmount = (orderTotal * (globalDiscountPercentage / 100)) || 0;

        console.log("Global Discount Calculation:");
        console.log("Order Total:", orderTotal);
        console.log("Global Discount Percentage:", globalDiscountPercentage);
        console.log("Global Discount Amount:", globalDiscountAmount, "Max Allowed:", maxDiscount);

        if (globalDiscountAmount > maxDiscount) {
            console.log("Discount limit exceeded! Showing the popup...");
            this.env.services.dialog.add(AlertDialog, {
                title: _t("Discount Limit Exceeded"),
                body: _t(
                    `Total discount of ${globalDiscountAmount.toFixed(2)} exceeds the allowed maximum of ${maxDiscount.toFixed(2)}.`
                ),
            });
            return false;
        }

        if (super.validateOrder) {
            console.log("Calling super.validateOrder...");
            return await super.validateOrder(...arguments);
        } else {
            console.error("super.validateOrder is not defined");
        }
    }
});
