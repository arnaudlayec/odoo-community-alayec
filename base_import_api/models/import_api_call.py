# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command, exceptions, _
from odoo.tools import format_datetime, html2plaintext
from markupsafe import Markup

import logging
_logger = logging.getLogger(__name__)

class ImportApiCall(models.Model):
    _name = 'import.api.call'
    _inherit = ['mail.thread']
    _description = 'API call logger'
    _rec_name = 'display_name'

    #===== Fields =====#
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        readonly=True,
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('success', "Success"),
            ('info', "Info"),
            ('warning', "Warning"),
            ('error', "Error"),
        ],
        default="success",
        compute='_compute_state',
        store=True,
    )
    state_text = fields.Char(
        string='State (description)',
        compute='_compute_state_text',
    )
    verified = fields.Boolean(
        string='Verified',
        compute='_compute_verified',
        store=True,
        readonly=False,
    )
    model = fields.Char(string='Model', readonly=True)
    config = fields.Json(
        string='Config payload',
        help='Received config in JSON payload',
    )
    data = fields.Json(
        string='Data payload',
        help='Received data in JSON payload',
    )
    report = fields.Text(
        string='Detailed report',
        help='Using Markdown syntax for formatting',
        compute='_compute_report',
        readonly=True,
    )
    line_ids = fields.One2many(
        comodel_name='import.api.line',
        inverse_name='logger_id',
        string='Log lines',
        readonly=True,
    )
    # for view
    archived_line_ids = fields.One2many(
        related='line_ids',
        string='Previous logs',
        context={"active_test": False},
        domain=[("active", "=", "False")],
    )

    #===== Compute =====#
    @api.depends("model", "create_date")
    def _compute_display_name(self):
        for logger in self:
            if not logger.model in self.env:
                logger.display_name = _("Unknown model")
            else:
                model = self.env[logger.model]._description
                date = format_datetime(self.env, logger.create_date)
                logger.display_name = f"[{model}] {date}"

    @api.depends('line_ids.record_id', 'line_ids.message')
    def _compute_state(self):
        """ Compute `state` as per line_ids.state
            *WIHTOUT* moving `state` at a lower level than already set
        """
        for logger in self:
            lines = logger.line_ids.filtered(lambda x: x.state != 'global')
            states = set(lines.mapped('state'))

            # all lines failed
            if states == {"error"}:
                logger.state = 'error'
            # some line failed
            elif logger.state != 'error' and bool("error" in states):
                logger.state = 'warning'
            # all lines imported, some with message
            elif logger.state not in ('error', 'warning') and bool("info" in states):
                logger.state = 'info'
            # defaut: all lines imported, no review needed
            elif logger.state not in ('error', 'warning', 'info'):
                logger.state = 'success'
    
    @api.depends('state')
    def _compute_state_text(self):
        states = {
            "success": _("All records imported successfully"),
            "info": _("Records imported, some needing user review"),
            "warning": _("Some import lines failed or user review is required"),
            "error": _("Blocking failure: no record imported"),
        }
        for logger in self:
            logger.state_text = states[logger.state]

    @api.depends('state')
    def _compute_verified(self):
        for logger in self:
            logger.verified = bool(logger.state == 'success')
    
    #===== Logics =====#
    @api.model
    def _init(self, model, payload):
        """ Create logger and add subscribers """
        logger = self.create({
            'company_id': self.env.company.id,
            'config': payload.get('config', {}),
            'data': payload.get('data', {}),
            'model': model,
        })
        # followers
        group = self.env.ref("base_import_api.group_import_api_user")
        logger.message_subscribe(group.users.partner_id.ids)
        return logger
    
    def _finish(self):
        """ Notify subscribers """
        self.message_post(
            body=Markup(self.report),
        )
    
    def _reset(self):
        self.line_ids.active = False
    
    #===== Lines =====#
    def _add_line(
        self, message, vals={}, field='', value=None,
        flush=None, record=None,
    ):
        vals = {
            "logger_id": self.id,
            "external_id": vals.get("external_id"),
            "record_id": record.id if record else False,
            'message': message,
            'field': field,
            'value': value or vals.get(field),
        }
        line = self.env['import.api.line'].create(vals)
        _logger.info(f"[API import] {line._display()}")
        
        if isinstance(flush, bool) and flush:
            self._flush_lines(vals)
        
        return line
    
    def _flush_lines(self, vals, record=None):
        """ Must be call at the end of record import work.
            It flushes `chatter_msg` in logs.line_ids,
            setting `record_id`
        """
        for message in vals.get("chatter_msg", []):
            self._add_line(html2plaintext(message), vals, record=record)
        vals["chatter_msg"] = []

    #===== Report =====#
    @api.depends('line_ids.record_id', 'line_ids.message')
    def _compute_report(self):
        for logger in self:
            logger.report = logger._generate_report()
    
    def _generate_report(self, format='markdown'):
        """ :option format: None or Markdown """
        if not self.line_ids:
            return _("No report available.")
        else:
            return self._get_report_headers(format) + self._get_report_lines(format)
    
    def _get_report_headers(self, format):
        res = self._get_external_id_by_state()
        report = _("""
            # Import of %(model_description)s (%(res_model)s)\n
            \n
            ## Summary\n
            Global state of import: %(state)s\n
            - Imported records (with no message): %(success)d\n
            - Imported records (with message): %(success_info)d\n
            - Failed records: %(failed)d\n
            \n
        """,
            model_description=self.env[self.model]._description if self.model in self.env else False,
            res_model=self.model,
            state=self.state_text,
            success=len(res['success']),
            success_info=len(res['info']),
            failed=len(res['error']),
        )
        if res['global']:
            lines = self.line_ids.filtered(lambda x: x.state == 'global')
            report += _(
                "## Global messages\n %s",
                "\n" . join(lines.mapped("message"))
            )
        return report
    
    def _get_report_lines(self, format):
        report = ''
        sections = dict(self._fields['state']._description_selection(self.env))
        for line_state, subtitle in sections.items():
            lines = self.line_ids.filtered(lambda x: x.external_id and x.state == line_state)
            report += _("""
                ## %(subtitle)s\n
                External IDs: %(external_ids)s\n
                \n
            """, 
                subtitle=subtitle,
                external_ids=' ' . join(lines.mapped("external_id")),
            )

            for line in lines.filtered('message'):
                report += " - " + line._display() + "\n"
        return report
    
    #===== API response =====#
    def _get_api_response(self) -> dict:
        """ Prepare data the returned by the API """
        res = self._get_external_id_by_state()
        response = {
            'logger_id': self.id, # technical ID of API call (storing log details in Odoo)
            'state': self.state, # values: 'success', 'info', 'warning', 'error'
            'state_text': self.state_text, # same as 'state' but in natural language
            'report': self.report,
            'mapped_ids': {
                external_id: record_id
                for x in res.values()
                for external_id, record_id in x.items()
            },
            'to_review': list(res['info'].keys()),
            'failed': list(res['error'].keys()),
        }
        _logger.debug(f"[API import] Response: {response}")
        return response
    
    def _get_external_id_by_state(self):
        res = {state[0]: {} for state in self.line_ids._fields['state'].selection}
        for line in self.line_ids.read(["state", "external_id", "record_id"]):
            res[line['state']][line['external_id']] = line['record_id']
        return res

    #===== Button =====#
    def action_toggle_verified(self):
        for logger in self:
            logger.verified = not logger.verified
    
    def action_replay(self):
        for logger in self:
            if not logger.model in self.env:
                raise exceptions.ValidationError(_("Unknown model"))
            logger._reset()
            Model = self.env[logger.model]
            Model.import_api({
                'config': logger.config,
                'data': logger.data,
            })
