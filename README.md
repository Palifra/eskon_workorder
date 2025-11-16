# ESKON Workorder Management System

Odoo 18 module for managing work orders, construction diaries, and construction books for electrical installations and security systems companies.

## Features

### Work Order Management
- Extended project tasks with workorder-specific fields
- Team assignment (workers, team leader)
- Vehicle and equipment tracking
- Material management with stock integration
- Workflow states: Draft → Planned → In Progress → Completed
- Customer contact information
- Time tracking (planned vs actual)

### Construction Diary (Градежен дневник)
- Daily construction diary entries (legal requirement in Macedonia)
- Multi-shift work hour tracking
- Weather and temperature recording
- Worker tracking by qualification
- Equipment and material logging
- Safety and incident recording
- Photo attachments
- Multi-level approval workflow
- QWeb PDF reports

### Construction Book (Градежна книга)
- Official construction documentation
- Project details (investor, designer, contractor, supervision)
- Building permit information
- Page-based entry system with work items
- Signature tracking
- PDF reports with multi-page support

### Stock Integration
- Equipment issue from warehouse
- Equipment return tracking
- Serial number tracking
- Automatic stock picking creation

## Installation

1. Place the module in your Odoo addons directory
2. Update the apps list
3. Install the module

```bash
# Via shell
docker exec -i odoo_server odoo shell -d your_database --no-http << 'EOF'
env['ir.module.module'].update_list()
env.cr.commit()
module = env['ir.module.module'].search([('name', '=', 'eskon_workorder')])
module.button_immediate_install()
env.cr.commit()
EOF
```

## Dependencies

- `project` - Core project management
- `hr` - Human resources (employees)
- `fleet` - Vehicle fleet management
- `stock` - Inventory/stock management
- `mail` - Messaging and chatter

## Configuration

No special configuration required. The module integrates with existing Odoo modules.

## Usage

### Creating a Work Order
1. Go to Work Orders → All Orders
2. Click Create
3. Fill in the workorder details
4. Assign team (workers, vehicles)
5. Add equipment lines
6. Plan and execute the work

### Construction Diary
1. Go to Construction Diary → All Records
2. Create daily entries for each worksite
3. Record workers, materials, weather conditions
4. Confirm and approve entries
5. Print PDF reports

### Construction Book
1. Go to Construction Books → All Books
2. Create a book for the project
3. Add entries/pages with work items
4. Track signatures and approvals
5. Generate official PDF documentation

## Reports

- Construction Diary PDF (daily record)
- Construction Book PDF (project documentation)
- Construction Book Entry PDF (work items with multi-page support)

## Security

- Project Users: Read/Write/Create (no delete)
- Project Managers: Full CRUD permissions

## Technical Details

- **Version:** 18.0.1.0.0
- **Category:** Project
- **License:** LGPL-3
- **Author:** ЕСКОН-ИНЖЕНЕРИНГ ДООЕЛ Струмица
- **Website:** https://www.eskon.com.mk

## File Structure

```
eskon_workorder/
├── models/
│   ├── project_task.py              # Work order extension
│   ├── workorder_equipment.py       # Equipment tracking
│   ├── construction_diary.py        # Daily diary entries
│   ├── construction_diary_line.py   # Worker/vehicle/machine lines
│   ├── construction_book.py         # Main construction book
│   └── construction_book_entry.py   # Book pages/entries
├── views/
│   ├── project_task_views.xml       # Work order UI
│   ├── construction_diary_views.xml # Diary UI
│   ├── construction_book_views.xml  # Book UI
│   └── menu_views.xml               # Menu structure
├── report/
│   ├── construction_diary_report.xml
│   ├── construction_book_report.xml
│   └── construction_book_entry_report.xml
├── security/
│   └── ir.model.access.csv
└── data/
    └── paper_format.xml
```

## Related Modules

- [l10n_mk](https://github.com/Palifra/l10n_mk) - Macedonian Chart of Accounts
- [l10n_mk_project](https://github.com/Palifra/l10n_mk_project) - Project localization
- [l10n_mk_fleet](https://github.com/Palifra/l10n_mk_fleet) - Fleet localization
- [l10n_mk_inventory](https://github.com/Palifra/l10n_mk_inventory) - Inventory localization
- [l10n_mk_invoicing](https://github.com/Palifra/l10n_mk_invoicing) - Invoicing localization

## Support

- **Email:** info@eskon.com.mk
- **Website:** https://www.eskon.com.mk
- **GitHub:** https://github.com/Palifra

## License

This module is licensed under LGPL-3.

## Changelog

### 18.0.1.0.0 (2024-11-16)
- Initial release
- Work order management
- Construction diary with 3-shift support
- Construction book documentation
- PDF reports
- Stock integration for equipment
