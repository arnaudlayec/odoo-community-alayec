
This module adds *Reviewers* field on Account Move and
pre-populate it from the Purchase buyer or Sale Orders seller.

This is convenient when the original buyer or seller must be validator of the invoice.

*Note 1*: because this module uses `account_move.invoice_user_id` to store the validator user,
this field must always be set else the module `account_move_tier_validation` throw an error.
Therefore, it is set by default to the current context user for account move created on
the fly.

*Note 2*: this module post a message in the Chatter (of `comment` type, thus throwing
notification to users) when the account move is validated. To prevent sending notification
to the customer or provider, this module cancel adding them by default to account move's
followers.
