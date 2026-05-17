
This module helps decreasing the stock level of the components of Manufacturing Orders (MOs)
at the validation of the PREP-pickings of the MOs, instead of at the validation of the MOs
themselves, for all Warehouses configured with *2-steps* mode Manufacture.

It is useful for companies needing/having both:
- the 2-steps MO preparation mode to manage Back Orders for PREP pickings
  (not possible in 1-step PREP)
- MOs with *workcenters* lasting long, with parallel MOs with same components.
  They require their stock levels to be immediatly decreased on PREP pickings validations
  instead at the the whole Manufacturing Order (MO) validation.

How it works:
- It transforms the *Production* location into an **external** location, thus ignoring any
  product quantity in this location for stock level computation.
- The *Consumed* fields in MO's components become readonly. It is the sum of *Done* quantities
  from the done PREP pickings.
