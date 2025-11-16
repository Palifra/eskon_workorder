# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ConstructionBookEntry(models.Model):
    _name = 'construction.book.entry'
    _description = 'Construction Book Entry (Страница од градежна книга)'
    _order = 'page_number desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Референца',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    book_id = fields.Many2one(
        'construction.book',
        string='Градежна книга',
        required=True,
        ondelete='cascade'
    )

    page_number = fields.Integer(
        string='Страна на книга',
        required=True,
        default=1,
        help='Реден број на страница во градежната книга'
    )

    # === Project Info (inherited from book but can be overridden) ===
    project_name = fields.Char(
        string='Проект',
        related='book_id.construction_name',
        store=True,
        readonly=True
    )

    # === Contractors ===
    main_contractor = fields.Char(
        string='Изведувач',
        help='Главен изведувач'
    )

    subcontractor = fields.Char(
        string='Подизведувач',
        help='Подизведувач (ако има)'
    )

    supervision = fields.Char(
        string='Надзор',
        help='Надзорен орган'
    )

    investor = fields.Char(
        string='Инвеститор',
        related='book_id.investor_name',
        store=True,
        readonly=True
    )

    # === Site Info ===
    site_address = fields.Char(
        string='Адреса на градилиште',
        help='Адреса и назив на градилиштето'
    )

    site_name = fields.Char(
        string='Назив на градилиште',
        help='Назив на градилиштето'
    )

    # === Period ===
    period_start = fields.Date(
        string='Почеток на период',
        required=True,
        default=fields.Date.context_today
    )

    period_end = fields.Date(
        string='Крај на период',
        required=True,
        default=fields.Date.context_today
    )

    period_display = fields.Char(
        string='Период',
        compute='_compute_period_display',
        store=True
    )

    # === Work Description ===
    work_description = fields.Text(
        string='Опис на работа',
        help='Опис од понуда / договор, број на договор'
    )

    contract_number = fields.Char(
        string='Број на договор',
        help='Број на договорот за работите'
    )

    # === Work Lines ===
    line_ids = fields.One2many(
        'construction.book.entry.line',
        'entry_id',
        string='Работни позиции',
        help='Детален список на извршени работи'
    )

    # === Totals ===
    total_quantity = fields.Float(
        string='Вкупно количина',
        compute='_compute_totals',
        store=True,
        help='Вкупна сума на количините'
    )

    line_count = fields.Integer(
        string='Број на ставки',
        compute='_compute_totals',
        store=True
    )

    # === Signatures ===
    contractor_signatory = fields.Char(
        string='Потпис изведувач',
        help='Име, презиме на лицето што потпишува за изведувачот'
    )

    contractor_signed_date = fields.Date(
        string='Датум потпис изведувач'
    )

    supervisor_signatory = fields.Char(
        string='Потпис надзор',
        help='Име, презиме на надзорниот инженер што потпишува'
    )

    supervisor_signed_date = fields.Date(
        string='Датум потпис надзор'
    )

    # === Status ===
    state = fields.Selection([
        ('draft', 'Нацрт'),
        ('confirmed', 'Потврдена'),
        ('signed', 'Потпишана'),
    ], string='Статус', default='draft', tracking=True)

    # === Notes ===
    notes = fields.Text(
        string='Забелешки',
        help='Дополнителни забелешки'
    )

    @api.depends('period_start', 'period_end')
    def _compute_period_display(self):
        for entry in self:
            if entry.period_start and entry.period_end:
                if entry.period_start == entry.period_end:
                    entry.period_display = entry.period_start.strftime('%d.%m.%Y')
                else:
                    entry.period_display = f"{entry.period_start.strftime('%d.%m.%Y')} - {entry.period_end.strftime('%d.%m.%Y')}"
            else:
                entry.period_display = ''

    @api.depends('line_ids', 'line_ids.quantity')
    def _compute_totals(self):
        for entry in self:
            entry.line_count = len(entry.line_ids)
            entry.total_quantity = sum(entry.line_ids.mapped('quantity'))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('construction.book.entry') or _('New')
        return super().create(vals)

    def action_confirm(self):
        """Confirm the entry"""
        self.ensure_one()
        self.write({'state': 'confirmed'})
        return True

    def action_sign(self):
        """Mark entry as signed"""
        self.ensure_one()
        if not self.contractor_signatory or not self.supervisor_signatory:
            raise ValidationError(_('Мора да се внесат потписите на изведувачот и надзорот!'))
        self.write({'state': 'signed'})
        return True

    def action_reset_draft(self):
        """Reset to draft"""
        self.ensure_one()
        self.write({'state': 'draft'})
        return True

    @api.constrains('period_start', 'period_end')
    def _check_period_dates(self):
        for entry in self:
            if entry.period_start and entry.period_end:
                if entry.period_end < entry.period_start:
                    raise ValidationError(_('Крајот на периодот не може да биде пред почетокот!'))

    @api.constrains('page_number')
    def _check_page_number(self):
        for entry in self:
            if entry.page_number <= 0:
                raise ValidationError(_('Бројот на страница мора да биде позитивен!'))


class ConstructionBookEntryLine(models.Model):
    _name = 'construction.book.entry.line'
    _description = 'Construction Book Entry Line (Работна позиција)'
    _order = 'sequence, id'

    entry_id = fields.Many2one(
        'construction.book.entry',
        string='Страница',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(
        string='№ п/п',
        default=10,
        help='Реден број на позицијата'
    )

    location = fields.Char(
        string='Локација',
        help='Location / место каде е извршена работата'
    )

    # === Work Description ===
    description = fields.Char(
        string='Изведена позиција',
        required=True,
        help='Опис на извршената работа'
    )

    details = fields.Text(
        string='Детали',
        help='Детали за позицијата'
    )

    # === Measurement ===
    uom = fields.Char(
        string='Единица мерка',
        default='ком',
        help='Единица мерка (м, м2, ком, кг, итн.)'
    )

    quantity = fields.Float(
        string='Количина',
        required=True,
        default=1.0,
        help='Количина на извршена работа'
    )

    # === Optional: Link to product for better tracking ===
    product_id = fields.Many2one(
        'product.product',
        string='Производ',
        help='Опционално поврзување со производ од магацин'
    )

    # === Calculated ===
    total = fields.Float(
        string='Вкупно',
        compute='_compute_total',
        store=True
    )

    notes = fields.Text(
        string='Забелешки'
    )

    @api.depends('quantity')
    def _compute_total(self):
        for line in self:
            # For now, total equals quantity (no unit price)
            # This can be extended to include unit price if needed
            line.total = line.quantity

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            if self.product_id.uom_id:
                self.uom = self.product_id.uom_id.name
