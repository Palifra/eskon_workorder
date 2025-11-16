# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ConstructionDiary(models.Model):
    _name = 'construction.diary'
    _description = 'Construction Diary Entry'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Број на запис',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    task_id = fields.Many2one(
        'project.task',
        string='Работен налог',
        required=True,
        ondelete='cascade',
        domain=[('is_workorder', '=', True)]
    )

    project_id = fields.Many2one(
        'project.project',
        string='Проект',
        related='task_id.project_id',
        store=True
    )

    book_id = fields.Many2one(
        'construction.book',
        string='Градежна книга',
        help='Градежна книга на која припаѓа овој запис'
    )

    # === Header Info ===
    book_number = fields.Char(
        string='Книга бр.',
        help='Број на градежната книга'
    )

    construction_name = fields.Char(
        string='Градба',
        help='Назив на градбата'
    )

    main_contractor = fields.Char(
        string='Изведувач',
        help='Главен изведувач'
    )

    subcontractor = fields.Char(
        string='Подизведувач',
        help='Подизведувач (ако има)'
    )

    investor_name = fields.Char(
        string='Инвеститор',
        help='Назив на инвеститор'
    )

    site_address = fields.Char(
        string='Адреса на градилиште',
        help='Адреса и назив на градилиштето'
    )

    date = fields.Date(
        string='Ден/Датум',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )

    # === Weather Conditions ===
    weather = fields.Selection([
        ('sunny', 'Сончево'),
        ('cloudy', 'Облачно'),
        ('partly_cloudy', 'Делумно облачно'),
        ('rainy', 'Дождливо'),
        ('snowy', 'Снежно'),
        ('windy', 'Ветровито'),
        ('storm', 'Невреме'),
        ('foggy', 'Магливо'),
    ], string='Временски услови', required=True, default='sunny')

    temperature_min = fields.Float(string='Мин. температура (°C)')
    temperature_max = fields.Float(string='Макс. температура (°C)')

    # === Work Shifts (3 possible shifts) ===
    shift1_start = fields.Float(string='1. Смена од', default=8.0)
    shift1_end = fields.Float(string='1. Смена до', default=16.0)
    shift1_hours = fields.Float(
        string='1. Смена вк. часови',
        compute='_compute_shift_hours',
        store=True
    )

    shift2_start = fields.Float(string='2. Смена од', default=0.0)
    shift2_end = fields.Float(string='2. Смена до', default=0.0)
    shift2_hours = fields.Float(
        string='2. Смена вк. часови',
        compute='_compute_shift_hours',
        store=True
    )

    shift3_start = fields.Float(string='3. Смена од', default=0.0)
    shift3_end = fields.Float(string='3. Смена до', default=0.0)
    shift3_hours = fields.Float(
        string='3. Смена вк. часови',
        compute='_compute_shift_hours',
        store=True
    )

    total_work_hours = fields.Float(
        string='Вкупно работни часови',
        compute='_compute_shift_hours',
        store=True
    )

    # Backward compatibility
    shift_start = fields.Float(string='Почеток на смена', default=8.0)
    shift_end = fields.Float(string='Крај на смена', default=16.0)
    work_hours = fields.Float(
        string='Работни часови',
        compute='_compute_work_hours',
        store=True
    )

    # === Meter Readings ===
    electricity_meter = fields.Char(
        string='Состојба на струјомер',
        help='Состојба на мерач на електрична енергија'
    )

    water_meter = fields.Char(
        string='Состојба на водомер',
        help='Состојба на мерач на вода'
    )

    # === Technical Resources ===
    # Workers by qualification
    worker_line_ids = fields.One2many(
        'construction.diary.worker.line',
        'diary_id',
        string='Работни лица',
        help='Работници по квалификации'
    )

    total_workers_from_lines = fields.Integer(
        string='Вкупно работници',
        compute='_compute_total_workers',
        store=True
    )

    # Vehicles
    vehicle_line_ids = fields.One2many(
        'construction.diary.vehicle.line',
        'diary_id',
        string='Транспортни средства',
        help='Возила користени на градилиштето'
    )

    # Construction machines
    machine_line_ids = fields.One2many(
        'construction.diary.machine.line',
        'diary_id',
        string='Градежни машини',
        help='Машини користени на градилиштето'
    )

    # Legacy worker tracking
    worker_ids = fields.Many2many(
        'hr.employee',
        'construction_diary_worker_rel',
        'diary_id',
        'employee_id',
        string='Присутни работници (HR)'
    )

    workers_count = fields.Integer(
        string='Број на работници',
        compute='_compute_workers_count',
        store=True
    )

    # === Contractor's Record ===
    contractor_notes = fields.Html(
        string='Запис на изведувачот',
        required=True,
        help='Детален опис на извршените работи'
    )

    work_description = fields.Html(
        string='Опис на извршена работа',
        help='Детален опис на работите извршени денес (legacy)'
    )

    # === Materials and Equipment ===
    materials_used = fields.Text(
        string='Употребени материјали',
        help='Листа на материјали употребени денес'
    )

    equipment_used = fields.Text(
        string='Употребена опрема',
        help='Опрема и алати користени денес'
    )

    # === Safety and Incidents ===
    safety_notes = fields.Text(
        string='Безбедносни забелешки',
        help='Мерки за безбедност, инциденти, итн.'
    )

    incidents = fields.Boolean(
        string='Инциденти',
        default=False,
        help='Дали има забележани инциденти'
    )

    incident_description = fields.Text(
        string='Опис на инцидент',
        help='Детали за инцидентот доколку има'
    )

    # === Signatures - Contractor Side ===
    recorded_by_name = fields.Char(
        string='Пополнил (име и презиме)',
        help='Лице кое го пополнило дневникот'
    )

    recorded_by_id = fields.Many2one(
        'hr.employee',
        string='Пополнил',
        help='Лице кое го пополнило дневникот'
    )

    construction_manager_name = fields.Char(
        string='Раководен инженер за изведба',
        help='Име, презиме и потпис'
    )

    construction_manager_id = fields.Many2one(
        'hr.employee',
        string='Раководен инженер (HR)',
        help='Раководен инженер за изведба'
    )

    investor_representative = fields.Char(
        string='За инвеститор',
        help='Име, презиме и потпис'
    )

    # === Supervision Notes ===
    supervision_notes = fields.Text(
        string='Запис на надзорен инженер',
        help='Забелешки од надзорниот инженер, проектантски надзор и надлежен инспектор'
    )

    # === Signatures - Supervision Side ===
    supervision_engineer_name = fields.Char(
        string='Надзорен инженер',
        help='Име, презиме и потпис'
    )

    supervision_engineer_id = fields.Many2one(
        'hr.employee',
        string='Надзорен инженер (HR)',
        help='Надзорен инженер'
    )

    designer_supervisor_name = fields.Char(
        string='Проектантски надзор',
        help='Име, презиме и потпис'
    )

    inspector_name = fields.Char(
        string='Надлежен инспектор',
        help='Име, презиме и потпис'
    )

    inspection_performed = fields.Boolean(
        string='Извршена инспекција',
        default=False
    )

    inspection_notes = fields.Text(
        string='Забелешки од инспекција'
    )

    # === Photos/Attachments ===
    photo_ids = fields.Many2many(
        'ir.attachment',
        'construction_diary_photo_rel',
        'diary_id',
        'attachment_id',
        string='Фотографии',
        help='Фотографии од работата'
    )

    # === Status ===
    state = fields.Selection([
        ('draft', 'Нацрт'),
        ('confirmed', 'Потврден'),
        ('approved', 'Одобрен'),
    ], string='Статус', default='draft', tracking=True)

    approved_by_id = fields.Many2one(
        'hr.employee',
        string='Одобрил',
        help='Лице кое го одобрило записот'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Компанија',
        related='task_id.company_id',
        store=True
    )

    notes = fields.Text(
        string='Дополнителни забелешки'
    )

    # === Computed Methods ===
    @api.depends('shift1_start', 'shift1_end', 'shift2_start', 'shift2_end', 'shift3_start', 'shift3_end')
    def _compute_shift_hours(self):
        for record in self:
            # Calculate hours for each shift
            if record.shift1_end > record.shift1_start:
                record.shift1_hours = record.shift1_end - record.shift1_start
            else:
                record.shift1_hours = 0.0

            if record.shift2_end > record.shift2_start:
                record.shift2_hours = record.shift2_end - record.shift2_start
            else:
                record.shift2_hours = 0.0

            if record.shift3_end > record.shift3_start:
                record.shift3_hours = record.shift3_end - record.shift3_start
            else:
                record.shift3_hours = 0.0

            record.total_work_hours = record.shift1_hours + record.shift2_hours + record.shift3_hours

    @api.depends('shift_start', 'shift_end')
    def _compute_work_hours(self):
        for record in self:
            if record.shift_end > record.shift_start:
                record.work_hours = record.shift_end - record.shift_start
            else:
                record.work_hours = 0.0

    @api.depends('worker_ids')
    def _compute_workers_count(self):
        for record in self:
            record.workers_count = len(record.worker_ids)

    @api.depends('worker_line_ids', 'worker_line_ids.count')
    def _compute_total_workers(self):
        for record in self:
            record.total_workers_from_lines = sum(record.worker_line_ids.mapped('count'))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('construction.diary') or _('New')
        return super().create(vals)

    def action_confirm(self):
        """Confirm the diary entry"""
        self.ensure_one()
        if not self.contractor_notes and not self.work_description:
            raise ValidationError(_('Мора да внесете запис на изведувачот!'))
        self.write({'state': 'confirmed'})
        return True

    def action_approve(self):
        """Approve the diary entry"""
        self.ensure_one()
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.employee_id.id if self.env.user.employee_id else False,
        })
        return True

    def action_reset_to_draft(self):
        """Reset to draft"""
        self.ensure_one()
        self.write({'state': 'draft'})
        return True

    @api.constrains('date')
    def _check_date(self):
        for record in self:
            if record.date > fields.Date.today():
                raise ValidationError(_('Не може да се внесува дневник за иден датум!'))

    @api.constrains('temperature_min', 'temperature_max')
    def _check_temperature(self):
        for record in self:
            if record.temperature_min and record.temperature_max:
                if record.temperature_min > record.temperature_max:
                    raise ValidationError(_('Минималната температура не може да биде поголема од максималната!'))

    @api.onchange('book_id')
    def _onchange_book_id(self):
        """Auto-fill fields from construction book"""
        if self.book_id:
            self.book_number = self.book_id.name
            self.construction_name = self.book_id.construction_name
            self.main_contractor = self.book_id.contractor_company
            self.investor_name = self.book_id.investor_name
            self.site_address = self.book_id.construction_address
