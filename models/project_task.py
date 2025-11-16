# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # === Workorder Type ===
    is_workorder = fields.Boolean(
        string='Работен налог',
        default=False,
        help='Означи дали оваа задача е работен налог'
    )

    workorder_type = fields.Selection([
        ('installation', 'Инсталација'),
        ('maintenance', 'Одржување'),
        ('service', 'Сервис'),
        ('inspection', 'Инспекција'),
        ('project', 'Проект'),
    ], string='Тип на работа', default='installation')

    @api.onchange('is_workorder')
    def _onchange_is_workorder(self):
        """Set company_id when marking as workorder"""
        if self.is_workorder and not self.company_id:
            self.company_id = self.env.company

    # === Team Assignment ===
    worker_ids = fields.Many2many(
        'hr.employee',
        'project_task_worker_rel',
        'task_id',
        'employee_id',
        string='Инсталатери/Техничари',
        help='Работници доделени на овој налог'
    )

    team_leader_id = fields.Many2one(
        'hr.employee',
        string='Одговорен техничар',
        help='Главен одговорен за работниот налог'
    )

    total_workers = fields.Integer(
        string='Вкупно работници',
        compute='_compute_total_workers',
        store=True
    )

    # === Fleet Integration ===
    vehicle_ids = fields.Many2many(
        'fleet.vehicle',
        'project_task_vehicle_rel',
        'task_id',
        'vehicle_id',
        string='Возила',
        help='Возила доделени за овој налог'
    )

    primary_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Главно возило',
        help='Примарно возило за транспорт'
    )

    # === Equipment & Materials ===
    equipment_ids = fields.Many2many(
        'product.product',
        'project_task_equipment_rel',
        'task_id',
        'product_id',
        string='Опрема',
        domain=[('type', '=', 'consu')],
        help='Опрема и алати потребни за работата'
    )

    equipment_line_ids = fields.One2many(
        'workorder.equipment.line',
        'task_id',
        string='Задолжена опрема',
        help='Детална листа на опрема со количини и статус'
    )

    total_equipment_lines = fields.Integer(
        string='Број на ставки',
        compute='_compute_equipment_stats',
        store=True
    )

    equipment_all_returned = fields.Boolean(
        string='Сè вратено',
        compute='_compute_equipment_stats',
        store=True,
        help='Дали целата опрема е вратена'
    )

    material_notes = fields.Text(
        string='Забелешки за материјали',
        help='Дополнителни информации за материјали'
    )

    # === Construction Diary ===
    diary_ids = fields.One2many(
        'construction.diary',
        'task_id',
        string='Градежен дневник',
        help='Дневни записи за овој работен налог'
    )

    diary_count = fields.Integer(
        string='Број на записи',
        compute='_compute_diary_count',
        store=True
    )

    # === Workorder Status ===
    workorder_state = fields.Selection([
        ('draft', 'Нацрт'),
        ('planned', 'Планиран'),
        ('in_progress', 'Во тек'),
        ('on_hold', 'Паузиран'),
        ('completed', 'Завршен'),
        ('cancelled', 'Откажан'),
    ], string='Статус на налог', default='draft', tracking=True)

    # === Location ===
    work_location = fields.Char(
        string='Локација на работа',
        help='Адреса или опис на локацијата'
    )

    work_location_notes = fields.Text(
        string='Забелешки за локација',
        help='Дополнителни информации за пристап, паркинг, итн.'
    )

    # === Time Tracking ===
    planned_start = fields.Datetime(
        string='Планиран почеток',
        help='Планиран датум и време на почеток'
    )

    planned_end = fields.Datetime(
        string='Планиран крај',
        help='Планиран датум и време на завршување'
    )

    actual_start = fields.Datetime(
        string='Реален почеток',
        help='Реален датум и време на почеток'
    )

    actual_end = fields.Datetime(
        string='Реален крај',
        help='Реален датум и време на завршување'
    )

    estimated_hours = fields.Float(
        string='Проценети часови',
        help='Проценето време за завршување'
    )

    # === Customer Information ===
    customer_contact = fields.Char(
        string='Контакт лице',
        help='Име на контакт лицето кај клиентот'
    )

    customer_phone = fields.Char(
        string='Телефон на клиент',
        help='Телефонски број за контакт'
    )

    # === Work Description ===
    work_description = fields.Html(
        string='Опис на работа',
        help='Детален опис на работата што треба да се изврши'
    )

    completion_notes = fields.Html(
        string='Забелешки по завршување',
        help='Забелешки и коментари по завршување на работата'
    )

    # === Computed Fields ===
    @api.depends('worker_ids')
    def _compute_total_workers(self):
        for task in self:
            task.total_workers = len(task.worker_ids)

    @api.depends('equipment_line_ids', 'equipment_line_ids.state')
    def _compute_equipment_stats(self):
        for task in self:
            task.total_equipment_lines = len(task.equipment_line_ids)
            if task.equipment_line_ids:
                task.equipment_all_returned = all(
                    line.state in ['returned', 'consumed']
                    for line in task.equipment_line_ids
                )
            else:
                task.equipment_all_returned = True

    @api.depends('diary_ids')
    def _compute_diary_count(self):
        for task in self:
            task.diary_count = len(task.diary_ids)

    def action_view_diary(self):
        """Open construction diary entries for this workorder"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Градежен Дневник'),
            'res_model': 'construction.diary',
            'view_mode': 'list,form,calendar',
            'domain': [('task_id', '=', self.id)],
            'context': {
                'default_task_id': self.id,
                'default_worker_ids': [(6, 0, self.worker_ids.ids)],
            },
        }

    # === Actions ===
    def action_start_work(self):
        """Start the workorder"""
        self.ensure_one()
        self.write({
            'workorder_state': 'in_progress',
            'actual_start': fields.Datetime.now(),
        })
        return True

    def action_complete_work(self):
        """Complete the workorder"""
        self.ensure_one()
        self.write({
            'workorder_state': 'completed',
            'actual_end': fields.Datetime.now(),
        })
        return True

    def action_pause_work(self):
        """Pause the workorder"""
        self.ensure_one()
        self.write({
            'workorder_state': 'on_hold',
        })
        return True

    def action_resume_work(self):
        """Resume paused workorder"""
        self.ensure_one()
        self.write({
            'workorder_state': 'in_progress',
        })
        return True

    def action_cancel_work(self):
        """Cancel the workorder"""
        self.ensure_one()
        self.write({
            'workorder_state': 'cancelled',
        })
        return True

    def action_plan_work(self):
        """Set workorder to planned state"""
        self.ensure_one()
        if not self.planned_start or not self.planned_end:
            raise ValidationError(_('Мора да поставите планиран почеток и крај!'))
        self.write({
            'workorder_state': 'planned',
        })
        return True

    def action_reset_to_draft(self):
        """Reset workorder to draft"""
        self.ensure_one()
        self.write({
            'workorder_state': 'draft',
            'actual_start': False,
            'actual_end': False,
        })
        return True

    def action_create_stock_request(self):
        """Create stock picking request for equipment/materials"""
        self.ensure_one()
        if not self.equipment_line_ids:
            raise ValidationError(_('Нема опрема/материјали за барање!'))

        # Find or create picking type for workorder requests
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id.company_id', '=', self.company_id.id),
        ], limit=1)

        if not picking_type:
            raise ValidationError(_('Не е пронајден тип на испорака. Конфигурирајте го магацинот!'))

        # Get locations
        location_src = picking_type.default_location_src_id
        location_dest = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
        if not location_dest:
            location_dest = picking_type.default_location_dest_id

        # Create picking
        picking_vals = {
            'picking_type_id': picking_type.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'origin': self.name,
            'location_id': location_src.id,
            'location_dest_id': location_dest.id,
            'scheduled_date': self.planned_start or fields.Datetime.now(),
            'note': f'Работен налог: {self.name}\nЛокација: {self.work_location or ""}',
        }

        picking = self.env['stock.picking'].create(picking_vals)

        # Create stock moves for each equipment line
        for line in self.equipment_line_ids.filtered(lambda l: l.state == 'draft'):
            move_vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.qty_issued,
                'product_uom': line.product_uom_id.id,
                'picking_id': picking.id,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
            }
            self.env['stock.move'].create(move_vals)

            # Update equipment line with picking reference
            line.write({
                'picking_id': picking.id,
                'state': 'issued',
                'issue_date': fields.Datetime.now(),
            })

        # Link picking to workorder (store in notes or create field)
        self.message_post(
            body=_('Креиран магацински документ: <a href="/web#id=%s&model=stock.picking">%s</a>') % (picking.id, picking.name)
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Магацински документ'),
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_return_equipment(self):
        """Create return stock picking for equipment from field to warehouse"""
        self.ensure_one()

        # Filter lines that have remaining quantity to return
        lines_to_return = self.equipment_line_ids.filtered(
            lambda l: l.state in ['issued', 'partial_return'] and l.qty_remaining > 0
        )

        if not lines_to_return:
            raise ValidationError(_('Нема опрема за враќање! Сите ставки се веќе вратени или потрошени.'))

        # Find incoming picking type (returns)
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', self.company_id.id),
        ], limit=1)

        if not picking_type:
            raise ValidationError(_('Не е пронајден тип на прием. Конфигурирајте го магацинот!'))

        # Get locations - reverse of issue (customer -> stock)
        location_src = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
        if not location_src:
            location_src = picking_type.default_location_src_id
        location_dest = picking_type.default_location_dest_id

        # Create return picking
        picking_vals = {
            'picking_type_id': picking_type.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'origin': f'Враќање: {self.name}',
            'location_id': location_src.id,
            'location_dest_id': location_dest.id,
            'scheduled_date': fields.Datetime.now(),
            'note': f'Враќање од работен налог: {self.name}\nЛокација: {self.work_location or ""}',
        }

        picking = self.env['stock.picking'].create(picking_vals)

        # Create stock moves for each equipment line with remaining quantity
        for line in lines_to_return:
            move_vals = {
                'name': f'Враќање: {line.product_id.name}',
                'product_id': line.product_id.id,
                'product_uom_qty': line.qty_remaining,
                'product_uom': line.product_uom_id.id,
                'picking_id': picking.id,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
            }
            self.env['stock.move'].create(move_vals)

            # Update equipment line - mark as returned
            new_qty_returned = line.qty_returned + line.qty_remaining
            line.write({
                'qty_returned': new_qty_returned,
                'return_date': fields.Datetime.now(),
            })
            # State will be updated by _compute_qty_remaining and action_return

        # Update equipment line states
        for line in lines_to_return:
            line.action_return()

        # Post message with link
        self.message_post(
            body=_('Креиран документ за враќање: <a href="/web#id=%s&model=stock.picking">%s</a>') % (picking.id, picking.name)
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Документ за враќање'),
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # === Constraints ===
    @api.constrains('planned_start', 'planned_end')
    def _check_planned_dates(self):
        for task in self:
            if task.planned_start and task.planned_end:
                if task.planned_end < task.planned_start:
                    raise ValidationError(_('Планираниот крај не може да биде пред планираниот почеток!'))

    @api.constrains('team_leader_id', 'worker_ids')
    def _check_team_leader(self):
        for task in self:
            if task.team_leader_id and task.worker_ids:
                if task.team_leader_id not in task.worker_ids:
                    raise ValidationError(_('Одговорниот техничар мора да биде дел од тимот!'))
