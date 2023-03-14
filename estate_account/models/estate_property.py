from odoo import fields, models, Command


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        res = super().action_sold()
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        self.env["account.move"].create(
            {
                "partner_id" : self.buyer_id.id,
                "move_type" : "out_invoice",
                "journal_id" : journal.id,
                "invoice_line_ids": [
                    Command.create({
                        "name": self.name,
                        "quantity": 1.0,
                        "price_unit": self.selling_price * 6.0 / 100.0,
                    }),
                    Command.create({
                        "name": "Administrative fees",
                        "quantity": 1.0,
                        "price_unit": 100.0,
                    }),
                ],
            }
        )

        return res