# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ConstructionDiaryWorkerLine(models.Model):
    _name = 'construction.diary.worker.line'
    _description = 'Construction Diary Worker Line'
    _order = 'sequence, id'

    diary_id = fields.Many2one(
        'construction.diary',
        string='Дневник',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(default=10)

    qualification = fields.Char(
        string='Квалификација',
        required=True,
        help='Тип на работник (монтер, инженер, итн.)'
    )

    count = fields.Integer(
        string='Број',
        required=True,
        default=1
    )


class ConstructionDiaryVehicleLine(models.Model):
    _name = 'construction.diary.vehicle.line'
    _description = 'Construction Diary Vehicle Line'
    _order = 'sequence, id'

    diary_id = fields.Many2one(
        'construction.diary',
        string='Дневник',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(default=10)

    vehicle_type = fields.Char(
        string='Вид',
        required=True,
        help='Тип на возило'
    )

    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Возило',
        help='Поврзување со fleet возило (опционално)'
    )

    count = fields.Integer(
        string='Број',
        required=True,
        default=1
    )


class ConstructionDiaryMachineLine(models.Model):
    _name = 'construction.diary.machine.line'
    _description = 'Construction Diary Machine Line'
    _order = 'sequence, id'

    diary_id = fields.Many2one(
        'construction.diary',
        string='Дневник',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(default=10)

    machine_type = fields.Char(
        string='Вид',
        required=True,
        help='Тип на градежна машина'
    )

    count = fields.Integer(
        string='Број',
        required=True,
        default=1
    )
