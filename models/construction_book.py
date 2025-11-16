# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ConstructionBook(models.Model):
    _name = 'construction.book'
    _description = 'Construction Book (Градежна Книга)'
    _order = 'name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Книга бр.',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    # === Основни информации за градба ===
    construction_name = fields.Char(
        string='Назив на градба',
        required=True,
        help='Назив на градбата'
    )

    construction_address = fields.Text(
        string='Адреса на градба',
        required=True,
        help='Адреса на градбата'
    )

    building_permit_number = fields.Char(
        string='Одобрение за градење бр.',
        help='Број на одобрение за градење'
    )

    building_permit_date = fields.Date(
        string='Датум на одобрение',
        help='Датум на издавање на одобрението'
    )

    issued_by = fields.Char(
        string='Издадено од',
        help='Орган кој го издал одобрението'
    )

    # === Инвеститор ===
    investor_id = fields.Many2one(
        'res.partner',
        string='Инвеститор',
        help='Инвеститор (име и презиме односно назив и седиште)'
    )

    investor_name = fields.Char(
        string='Име на инвеститор',
        help='Име и презиме / назив на инвеститор'
    )

    investor_address = fields.Text(
        string='Седиште на инвеститор',
        help='Адреса/седиште на инвеститорот'
    )

    # === Проектант ===
    designer_company = fields.Char(
        string='Проектант',
        help='Назив на правно лице - проектант'
    )

    designer_license = fields.Char(
        string='Лиценца бр. (проектант)',
        help='Број на лиценца на проектантот'
    )

    chief_designer_name = fields.Char(
        string='Главен проектант',
        help='Име и презиме на главен проектант'
    )

    chief_designer_authorization = fields.Char(
        string='Овластување бр. (главен проектант)',
        help='Број на овластување на главен проектант'
    )

    # === Изведувач ===
    contractor_company = fields.Char(
        string='Изведувач',
        help='Назив на правното лице - изведувач'
    )

    contractor_license = fields.Char(
        string='Лиценца бр. (изведувач)',
        help='Број на лиценца на изведувачот'
    )

    construction_engineer_name = fields.Char(
        string='Инженер за изведба',
        help='Име и презиме на инженер за изведба кој раководи со изградбата'
    )

    construction_engineer_authorization = fields.Char(
        string='Овластување бр. (инженер за изведба)',
        help='Број на овластување на инженер за изведба'
    )

    # === Надзор ===
    supervision_company = fields.Char(
        string='Надзор',
        help='Назив на правно лице - надзор'
    )

    supervision_license = fields.Char(
        string='Лиценца бр. (надзор)',
        help='Број на лиценца на надзорот'
    )

    supervision_engineer_name = fields.Char(
        string='Надзорен инженер',
        help='Име и презиме на надзорен инженер'
    )

    supervision_engineer_authorization = fields.Char(
        string='Овластување бр. (надзорен инженер)',
        help='Број на овластување на надзорен инженер'
    )

    # === Датуми ===
    construction_start_date = fields.Date(
        string='Датум на почеток на изградбата',
        help='Датум кога започнала изградбата'
    )

    construction_end_date = fields.Date(
        string='Датум на завршеток',
        help='Датум на завршеток на изградбата'
    )

    construction_period = fields.Char(
        string='Период на изградба',
        help='Период/времетраење на изградбата'
    )

    # === Поврзување со работни налози ===
    task_ids = fields.Many2many(
        'project.task',
        'construction_book_task_rel',
        'book_id',
        'task_id',
        string='Работни налози',
        domain=[('is_workorder', '=', True)],
        help='Поврзани работни налози'
    )

    diary_ids = fields.One2many(
        'construction.diary',
        'book_id',
        string='Дневнички записи',
        help='Сите дневнички записи поврзани со оваа градежна книга'
    )

    diary_count = fields.Integer(
        string='Број на записи',
        compute='_compute_diary_count',
        store=True
    )

    entry_ids = fields.One2many(
        'construction.book.entry',
        'book_id',
        string='Страници',
        help='Страници со записи на извршени работи'
    )

    entry_count = fields.Integer(
        string='Број на страници',
        compute='_compute_entry_count',
        store=True
    )

    # === Статус ===
    state = fields.Selection([
        ('draft', 'Нацрт'),
        ('active', 'Активна'),
        ('completed', 'Завршена'),
        ('archived', 'Архивирана'),
    ], string='Статус', default='draft', tracking=True)

    # === Компанија ===
    company_id = fields.Many2one(
        'res.company',
        string='Компанија',
        default=lambda self: self.env.company
    )

    # === Забелешки ===
    notes = fields.Text(
        string='Забелешки',
        help='Дополнителни забелешки'
    )

    @api.depends('diary_ids')
    def _compute_diary_count(self):
        for book in self:
            book.diary_count = len(book.diary_ids)

    @api.depends('entry_ids')
    def _compute_entry_count(self):
        for book in self:
            book.entry_count = len(book.entry_ids)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('construction.book') or _('New')
        return super().create(vals)

    def action_activate(self):
        """Activate the construction book"""
        self.ensure_one()
        self.write({'state': 'active'})
        return True

    def action_complete(self):
        """Mark construction as completed"""
        self.ensure_one()
        if not self.construction_end_date:
            self.write({'construction_end_date': fields.Date.today()})
        self.write({'state': 'completed'})
        return True

    def action_archive(self):
        """Archive the construction book"""
        self.ensure_one()
        self.write({'state': 'archived'})
        return True

    def action_view_diaries(self):
        """View all diary entries"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Дневнички записи'),
            'res_model': 'construction.diary',
            'view_mode': 'list,form,calendar',
            'domain': [('book_id', '=', self.id)],
            'context': {'default_book_id': self.id},
        }

    def action_view_entries(self):
        """View all book entries/pages"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Страници'),
            'res_model': 'construction.book.entry',
            'view_mode': 'list,form',
            'domain': [('book_id', '=', self.id)],
            'context': {
                'default_book_id': self.id,
                'default_main_contractor': self.contractor_company,
                'default_supervision': self.supervision_company,
                'default_site_name': self.construction_name,
                'default_site_address': self.construction_address,
            },
        }

    @api.constrains('construction_start_date', 'construction_end_date')
    def _check_dates(self):
        for book in self:
            if book.construction_start_date and book.construction_end_date:
                if book.construction_end_date < book.construction_start_date:
                    raise ValidationError(_('Датумот на завршеток не може да биде пред датумот на почеток!'))
