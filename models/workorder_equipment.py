# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WorkorderEquipmentLine(models.Model):
    _name = 'workorder.equipment.line'
    _description = 'Workorder Equipment Line'
    _order = 'task_id, sequence, id'

    sequence = fields.Integer(string='Редослед', default=10)
    task_id = fields.Many2one(
        'project.task',
        string='Работен налог',
        required=True,
        ondelete='cascade'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Опрема/Материјал',
        required=True,
        domain=[('type', 'in', ['consu', 'product'])]
    )

    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Единица мерка',
        related='product_id.uom_id',
        readonly=True
    )

    # Quantities
    qty_issued = fields.Float(
        string='Издадено',
        digits='Product Unit of Measure',
        default=1.0,
        help='Количина издадена за работниот налог'
    )

    qty_used = fields.Float(
        string='Употребено',
        digits='Product Unit of Measure',
        default=0.0,
        help='Количина реално употребена'
    )

    qty_returned = fields.Float(
        string='Вратено',
        digits='Product Unit of Measure',
        default=0.0,
        help='Количина вратена во магацин'
    )

    qty_remaining = fields.Float(
        string='Останато',
        compute='_compute_qty_remaining',
        store=True,
        help='Количина која треба да се врати'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Нацрт'),
        ('issued', 'Издадено'),
        ('partial_return', 'Делумно вратено'),
        ('returned', 'Целосно вратено'),
        ('consumed', 'Потрошено'),
    ], string='Статус', default='draft')

    # Additional info
    serial_number = fields.Char(
        string='Сериски број',
        help='Сериски број на опремата (за следење)'
    )

    notes = fields.Text(
        string='Забелешки',
        help='Дополнителни информации за опремата'
    )

    issue_date = fields.Datetime(
        string='Датум на издавање',
        help='Кога е издадена опремата'
    )

    return_date = fields.Datetime(
        string='Датум на враќање',
        help='Кога е вратена опремата'
    )

    issued_by_id = fields.Many2one(
        'hr.employee',
        string='Издал',
        help='Вработен кој ја издал опремата'
    )

    received_by_id = fields.Many2one(
        'hr.employee',
        string='Примил',
        help='Вработен кој ја примил опремата'
    )

    # Stock integration (optional)
    picking_id = fields.Many2one(
        'stock.picking',
        string='Реверс документ',
        help='Поврзан stock picking (реверс)'
    )

    @api.depends('qty_issued', 'qty_returned', 'qty_used')
    def _compute_qty_remaining(self):
        for line in self:
            line.qty_remaining = line.qty_issued - line.qty_returned - line.qty_used

    def action_issue(self):
        """Mark equipment as issued"""
        for line in self:
            line.write({
                'state': 'issued',
                'issue_date': fields.Datetime.now(),
            })
        return True

    def action_return(self):
        """Mark equipment as returned"""
        for line in self:
            if line.qty_remaining <= 0:
                line.state = 'returned'
            else:
                line.state = 'partial_return'
            line.return_date = fields.Datetime.now()
        return True

    def action_mark_consumed(self):
        """Mark as consumed (for materials)"""
        for line in self:
            line.write({
                'state': 'consumed',
                'qty_used': line.qty_issued,
                'qty_remaining': 0,
            })
        return True

    @api.constrains('qty_returned', 'qty_issued')
    def _check_qty_returned(self):
        for line in self:
            if line.qty_returned > line.qty_issued:
                raise ValidationError(_('Вратената количина не може да биде поголема од издадената!'))

    @api.constrains('qty_used', 'qty_issued')
    def _check_qty_used(self):
        for line in self:
            if line.qty_used > line.qty_issued:
                raise ValidationError(_('Употребената количина не може да биде поголема од издадената!'))
