/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        console.log("Validating Order...");

        const order = this.currentOrder;
        const discountProductId = this.pos.config.discount_product_id?.id;

        const rawMax = this.pos.config.max_discount_amount;
        const maxDiscount = parseFloat(rawMax) || 50.0;
        console.log("Max Discount Amount (Configured or Default):", maxDiscount);

        let currentOrderDiscount = 0;
        order.get_orderlines().forEach((line) => {
            const product = line.get_product();
            const isDiscount = product?.id === discountProductId && line.get_unit_price() < 0;
            if (isDiscount) {
                currentOrderDiscount += Math.abs(line.get_unit_price() * line.get_quantity());
            }
        });

        console.log("Current Order Discount:", currentOrderDiscount);

        if (typeof this.pos.sessionDiscountTotal !== "number") {
            this.pos.sessionDiscountTotal = 0;
        }

        const totalDiscountWithThis = this.pos.sessionDiscountTotal + currentOrderDiscount;
        console.log("Cumulative Discount (This + Previous):", totalDiscountWithThis, "Limit:", maxDiscount);

        if (totalDiscountWithThis > maxDiscount) {
            await this.env.services.dialog.add(AlertDialog, {
                title: _t("Discount Limit Exceeded"),
                body: _t(
                    `The total discount in this session (${totalDiscountWithThis.toFixed(2)}) exceeds the maximum allowed (${maxDiscount.toFixed(2)}). You cannot give more discounts.`
                ),
            });
            return false;
        }

        this.pos.sessionDiscountTotal += currentOrderDiscount;

        return super.validateOrder(...arguments);
    }
});
