from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help="Orientation of garden")
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string='State',
        selection=[('new', 'New'), ('offer received', 'Offer Received'), ('offer accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
        help="State of property",
        required=True,
        copy=False,
        default='new'
        )
    property_type_id = fields.Many2one("estate.property.type", string="Type")
    buyer = fields.Many2one('res.partner', string='Buyer', copy=False)
    salesperson = fields.Many2one('res.partner', string='Salesman', default=lambda self: self.env.user.partner_id)
    tag_ids = fields.Many2many('estate.property.tag')
    offer_ids = fields.One2many("estate.property.offer", "property_id")
    total_area = fields.Integer(compute="_compute_total")
    best_price = fields.Float(compute="_compute_best_price")

    _sql_constraints = [
        ('expected_price_positive','CHECK (expected_price > 0)','This expected price must be strictly positive'),
        ('selling_price_positive','CHECK (selling_price > 0)','This selling price must be positive'),
        ('name_unique', 'UNIQUE (name)', 'The name must be unique'),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    
    @api.depends("offer_ids")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = None
    
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None
    
    def action_cancel(self):
        for record in self:
            if not record.state == 'sold':
                record.state = 'canceled'
            else:
                raise UserError(_("Sold properties cannot be canceled"))
        return True
    
    def action_sold(self):
        for record in self:
            if not record.state == 'canceled':
                record.state = 'sold'
            else:
                raise UserError(_("Canceled properties cannot be sold"))
        return True
    
    def action_set_offer(self):
        offer_accepted = self.offer_ids.search([('status', '=', 'accepted')])
        if len(offer_accepted) > 1:
            raise UserError(_("There can only be one offer as accepted"))
        self.selling_price = offer_accepted.price
        self.buyer = offer_accepted.partner_id
        return True

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for record in self:
            if float_compare(record.expected_price * 0.9, record.selling_price, precision_digits=2) == 1:
                raise ValidationError(_("The selling price must be at least 90% of the expected price. You must reduce the expected price if you want to accept this offer"))
