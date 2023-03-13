from odoo import api, fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        string='Status',
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        copy=False
        )
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    _sql_constraints = [
        ('price_positive','CHECK (price > 0)','This offer price must be strictly positive')
    ]

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = fields.Date.add(record.create_date, days=record.validity)
            else:
                record.date_deadline = fields.Date.add(fields.Date.today(), days=record.validity)
    
    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date:
                record.validity = (record.date_deadline - record.create_date.date()).days
            else:
                record.validity = (record.date_deadline - fields.Date.today()).days

    def action_confirm(self):
        for record in self:
            record.status = 'accepted'
        self.env['estate.property'].search([('id', '=', self.property_id.id)]).action_set_offer()

    def action_cancel(self):
        for record in self:
            record.status = 'refused'
    
    @api.model
    def create(self, vals):
        self.env['estate.property'].browse(vals['property_id']).check_offer(vals['price'])
        return super(EstatePropertyOffer, self).create(vals)