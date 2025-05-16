
Scenario entry: a purchase order acknowledgments received from a seller
with an attachment (like a .pdf or email).

#. Browse to Purchase Orders (confirmed ones).
#. You may filter by *Not confirmed arrivals*.
#. Open the Purchase Order form and use [+New] button next to *Confirmed arrivals*
    field to open the helper wizard.
    Note: you may also use the menu *Purchase / Orders / Vendors acknowledgments*
#. Enter the confirmed arrival date as main field, add attachment, and an optional comment.
#. All non-confirmed lines are automatically proposed to be linked with this acknowledgment:
    select/remove lines not confirmed by the seller.
#. Lines are editable so that unit price or discount (if `purchase_discount` is installed) can
    be updated.
#. *Planned arrival* is also editable in PO lines. It follows by default the *Confirmed arrival*
    date of the wizard but can be changed manually per lines to manage exception cases.
#. Save the wizard.
#. The PO arrival confirmation state button updates itself.
#. If all the order line are confirmed, the *Send a reminder* button disapears (next to
    the above *Requested arrival* field).
#. In case of mistake, end-user may remove an acknowledged arrival date. PO lines will keep
    last saved arrival date but will be marked again as *Not confirmed*.
