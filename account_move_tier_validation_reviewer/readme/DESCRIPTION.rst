
This module adds *Reviewers* field on Account Move and
pre-populate it from Purchase and Sale Orders seller or buyer.

This is convenient when only original buyer or seller must be validator of the invoice.
Note: since this module re-uses `invoice_user_id` field of `account.move`, it also
sets a default value to the current user as validator for any bills not created from
SO or PO. 
