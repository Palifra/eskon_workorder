# -*- coding: utf-8 -*-
{
    'name': 'ESKON Workorder Management',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Работни налози за електрични инсталации',
    'description': """
ESKON Workorder Management
==========================

Модул за управување со работни налози за електрични инсталации,
монтажа на системи за заштита, видео надзор и автоматика.

Функционалности:
- Проширени работни налози (project.task)
- Доделување на работници (HR интеграција)
- Доделување на возила (Fleet интеграција)
- Опрема и материјали
- Статуси на работни налози
- Градежен дневник
- Извештаи и следење

Автор: ЕСКОН-ИНЖЕНЕРИНГ ДООЕЛ Струмица
    """,
    'author': 'ЕСКОН-ИНЖЕНЕРИНГ ДООЕЛ Струмица',
    'website': 'https://www.eskon.com.mk',
    'license': 'LGPL-3',
    'depends': [
        'project',
        'hr',
        'fleet',
        'stock',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/paper_format.xml',
        'report/construction_book_report.xml',
        'report/construction_book_entry_report.xml',
        'report/construction_diary_report.xml',
        'views/construction_diary_views.xml',
        'views/construction_book_views.xml',
        'views/construction_book_entry_views.xml',
        'views/project_task_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
