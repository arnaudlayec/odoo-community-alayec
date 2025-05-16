
This module helps managing multiple vendor acknowledgments for Purchase Order
(arrival dates and confirmation of product unit prices(1)).

Nativally, Odoo already supports arrival date per order lines but it is
not user-friendly to set them for many lines in a raw with different date per
lines. This module adds a helper wizard accessible from the Purchase Order
to register order acknowledgments attachment (if any), confirmed arrival dates
per order lines and whether the product price was confirmed by the vendor (1).

It also reminds the original requested arrival date of the Purchase Order,
and simplifies the reminder-mail feature. Natively, reminder-mail can be sent N
days before Purchase Order requested delivery date. This module hiding this
option in partner and Purchase Order form, and simply allow any user to send
reminder-mail from the Purchase Order.

(1) To help in keeping seller prices up-to-date, it is recommended to also use 1
    of this 2 modules: `purchase_order_supplierinfo_update`
    or `purchase_orderline_supplierinfo_update`
