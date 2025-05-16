
Validating incoming picking with corrects product unit prices on original
Purchase Orders is a key stake to ensure a correct stock valuation, especially
for AVCO-valuated products.

This module improves *purchase_multiple_arrival_date* to helps accountants with:
* following their control of products' unit prices in Purchase Order, simply
  by checking what POs supplier acknowledgment were verified or not (and thus
  related POs lines)
* suggesting to update product's supplier info like price and discount(*), for futher
  purchase orders.

(*) discount is supported if `purchase_discount` is installed, but without hard dependency.