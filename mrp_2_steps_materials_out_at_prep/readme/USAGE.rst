
From a MO in the state *draft*, *confirmed*, *in progress* or *to close*, you may
already with native feature:
1. add new components to the MO: Odoo will re-use any existing PREP-picking or create
   a new one to cascade the change. Then, the added component will be added to this draft
   PREP-picking.
2. Increase the *Demand* quantity of a componant already in the MO:
   Odoo will merge the demand with the already existing line in the MO.
   Then like point 1: the change cascades to the PREP pickings.
3. Decrease the *Demand* quantity:
   If the decreasing is in the limit of any *Demand* quantity in a draft PREP-picking:
   like point 2.
   Else, Odoo will create a new and separate PREP picking with flipped Source and Destination
   locations:
   - Source will be *Pre-production*
   - Destination will be *Stock*
4. To cancel a need of a component, add a new line with the same quantity than the
   existing line, but negative.

Additionaly, one should notice this module:
- prevent closing a MO if some PREP-pickings are still opened
- components's field "To Consume" is always readonly, no matter MO's Lock status,
  to force any modifications to go through above rules cascading to the preparation pickings
- set the Components lines with `manual_consumption=True` and neutralize 
  the automatic update of Components `quantity_done` which happened when
  modifying component' **To Consume** and MO's **Producing quantity**
- in case of MO backorders, filters which pickings is linked to which MO
