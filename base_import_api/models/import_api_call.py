# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command, exceptions, _
from odoo.tools import format_datetime, html2plaintext
from markupsafe import Markup
from collections import defaultdict

import json
import logging
_logger = logging.getLogger(__name__)

class ImportApiCall(models.Model):
    _name = 'import.api.call'
    _inherit = ['mail.thread']
    _description = 'API call logger'
    _rec_name = 'display_name'
    _order = "date_last_call DESC"

    #===== Fields =====#
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        readonly=True,
        default=lambda self: self.env.company.id,
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('success', "Success"),
            ('info', "Info"),
            ('warning', "Warning"),
            ('error', "Error"),
            ('verified', "Verified"),
        ],
        compute='_compute_state',
        default="error",
        store=True,
        tracking=True,
    )
    state_text = fields.Char(
        string='State (description)',
        compute='_compute_state_text',
    )
    model = fields.Char(string='Model')
    model_description = fields.Char(
        compute="_compute_model_description",
    )
    config = fields.Json(
        string='Config payload',
        help='Received config in JSON payload',
        default='{}',
    )
    data = fields.Json(
        string='Data payload',
        help='Received data in JSON payload',
        default='{}',
    )
    report = fields.Html(
        string='Detailed report',
        help='Using Markdown syntax for formatting',
        compute='_compute_report',
        readonly=True,
    )
    date_last_call = fields.Datetime(
        string="Last import date",
        default=lambda self: self.env.cr.now(), # like create_date
    )
    line_ids = fields.One2many(
        comodel_name='import.api.line',
        inverse_name='logger_id',
        string='Log lines details',
        readonly=True,
    )
    # for view
    line_count = fields.Integer(
        string="Log lines",
        compute='_compute_counts',
    )
    previous_line_count = fields.Integer(
        string="Previous import log lines",
        compute='_compute_counts',
    )
    record_count = fields.Integer(
        string="Imported records",
        compute="_compute_counts",
    )

    #===== Compute =====#
    @api.depends("model", "create_date")
    def _compute_display_name(self):
        for logger in self:
            date = format_datetime(self.env, logger.create_date)
            logger.display_name = "[%s] %s" % (logger.model_description, date)

    @api.depends("model")
    def _compute_model_description(self):
        for logger in self:
            if not logger.model in self.env:
                logger.model_description = _("Unknown model")
            else:
                logger.model_description = _(logger.env[logger.model]._description)

    @api.depends('line_ids.record_id', 'line_ids.message', 'line_ids.verified')
    def _compute_state(self):
        """ Compute `state` as per line_ids.state & verified """
        for logger in self:
            lines = logger.line_ids.filtered(lambda x: x.state != 'global')
            states = set(lines.mapped('state'))

            # all lines failed
            if not bool(lines) or states == {"error"}:
                state = 'error'
            # some line failed
            elif bool("error" in states):
                state = 'warning'
            # all lines imported, some with message
            elif bool("info" in states):
                state = 'info'
            # defaut: all lines imported, no review needed
            else:
                state = 'success'
            
            # 'verified': overrides the previous one
            if lines and state in ("error", "warning", "info") and self._get_is_verified():
                state = 'verified'
            
            logger.state = state
    
    @api.depends('state')
    def _compute_state_text(self):
        states = {
            "success": _("All records imported successfully"),
            "info": _("Records imported, some needing user review"),
            "warning": _("Some import lines failed or user review is required"),
            "error": _("Blocking failure: no record imported"),
            "verified": _("Some issues, but all verified by a user"),
        }
        for logger in self:
            logger.state_text = states[logger.state]

    @api.depends("line_ids", "line_ids.active", "line_ids.record_id",)
    def _compute_counts(self):
        for logger in self:
            logger.line_count = len(logger.line_ids)

            all_lines = logger.with_context(active_test=False).line_ids
            logger.previous_line_count = len(all_lines.filtered(lambda x: not x.active))
            logger.record_count = len(set(all_lines.filtered("record_ref").mapped("record_id")))
    
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
        """ Update lines without `record_id` & notify followers """
        lines = self.line_ids.filtered(lambda x: not x.record_id and x.external_ref)
        external_refs = lines.mapped("external_ref")
        domain = [
            ("external_ref", "in", external_refs),
            ("create_date", ">=", self.date_last_call), # to ignore already existing records 
        ]
        records = self.env[self.model].search(domain)
        mapped_refs = {
            x["external_ref"]: x["id"]
            for x in records.read(["external_ref"])
        }
        for line in lines:
            line.record_id = mapped_refs.get(line.external_ref)
        # Chatter msg to followers
        report = Markup(self._get_report_headers("html"))
        self.message_post(body=report)

    
    #===== Lines =====#
    def _add_line(
        self, message='', parsed_data={}, field='', value=None, flush=False, line_vals={}
    ):
        """ :arg `flush`: should be used only if record is not created """
        vals = {
            "logger_id": self.id,
            "external_ref": parsed_data.get("external_ref"),
            'message': message,
            'field': field,
            'value': value or parsed_data.get(field),
            'model': self.model,
        } | line_vals

        line = self.env['import.api.line'].create(vals)
        _logger.info(f"[API import] {line._display()}")
        
        if flush:
            self._flush_lines(parsed_data)
        
        return line
    
    def _add_line_success(self, parsed_data, record=None, chatter_msg=[]):
        line_vals = {
            "message": (
                _("%s created", record._description if record else _("Record"))
                + (_(", ID %d", record.id) if record else "")
            ),
            "model": record._name if record else self.model,
            "record_id": record and record.id,
            "state": "success",
            "verified": True,
        }
        if chatter_msg:
            line_vals["message"] += "\n" + chatter_msg.pop()
        self._add_line(parsed_data=parsed_data, line_vals=line_vals)
    
    def _flush_lines(self, parsed_data):
        """ Must be call at the end of record import work.
            It flushes `chatter_msg` in logs.line_ids.
            If no warning, it logs 1 empty line (='success')
             to save `record_id`
        """
        chatter_msg = parsed_data.get("chatter_msg", [])
        if chatter_msg:
            for message in chatter_msg:
                message = message.strip()
                if message:
                    self._add_line(html2plaintext(message), parsed_data)
            parsed_data["chatter_msg"] = []
        else:
            # 'success' records: create an empty log line to keep it trace
            external_ref = parsed_data.get("external_ref")
            if external_ref:
                lines = self.line_ids.filtered(
                    lambda x: x.external_ref == external_ref
                )
                if not lines:
                    self._add_line_success(parsed_data)

    #===== Report =====#
    @api.depends('line_ids.record_id', 'line_ids.message')
    def _compute_report(self):
        for logger in self:
            logger.report = Markup(logger._generate_report('html'))
    
    def _generate_report(self, format='html'):
        """ :option format: 'html' or 'markdown' (default) """
        if not self.line_ids:
            return _("No report available.")
        else:
            return self._get_report_headers(format) + self._get_report_lines(format)
    
    def _get_report_headers(self, format='markdown'):
        report_data = self._get_report_data()
        report = ""
        for model, mapped_lines in report_data.items():
            report += _(
                "# Import of %(model_description)s (%(res_model)s)\n"
                "## Summary\n\n"
                "* %(success)d successful record(s), imported with no message\n"
                "* %(info)d imported record(s), with needed review\n"
                "* %(failed)d import(s) failed\n",
                model_description=(
                    self.env[model]._description
                    if model in self.env else _("Unknown model")
                ),
                res_model=model,
                success=len(set(mapped_lines['success'].mapped("external_ref"))),
                info=len(set(mapped_lines['info'].mapped("external_ref"))),
                failed=len(set(mapped_lines['error'].mapped("external_ref"))),
            )

            if mapped_lines['global']:
                report += _(
                    "## Global messages\n%s",
                    "\n" . join(mapped_lines["global"].mapped("message"))
                )
            
        return _convert_markdown(report, format)
    
    def _get_report_lines(self, format='markdown'):
        report = ''
        sections = dict(self.line_ids._fields['state']._description_selection(self.env))
        for line_state, subtitle in sections.items():
            lines = self.line_ids.filtered(lambda x: x.external_ref and x.state == line_state)
            if lines:
                report += _(
                    "### %(subtitle)s\n"
                    "External IDs: %(external_refs)s\n\n", 
                    subtitle=subtitle,
                    external_refs=' ' . join(set(lines.mapped("external_ref"))),
                )

                for line in lines.filtered('message'):
                    report += " - " + line._display() + "\n"
        return _convert_markdown(report, format)

    #===== API response =====#
    def _get_api_response(self) -> dict:
        """ Prepare data the returned by the API """
        report_data = self._get_report_data()
        mapped_ids, to_review, failed = {}, {}, {}
        for model, mapped_lines in report_data.items():
            mapped_ids[model] = {
                line.external_ref: line.record_id
                for lines in mapped_lines.values()
                for line in lines
                if line.external_ref and line.record_id
            }
            to_review[model] = list(set(mapped_lines["info"].mapped("external_ref")))
            failed[model] = list(set(mapped_lines["error"].mapped("external_ref")))

        response = {
            'logger_id': self.id, # technical ID of API call (storing log details in Odoo)
            'state': self.state, # values: 'success', 'info', 'warning', 'error'
            'state_text': self.state_text, # same as 'state' but in natural language
            'report': self._generate_report("plain"),
            'mapped_ids': mapped_ids,
            'to_review': to_review,
            'failed': failed,
        }
        _logger.debug(f"[API import] Response: {response}")
        return response
    
    def _get_report_data(self):
        """ :return: like
            {
                "account.move": {
                    "success": recordset of import.api.line,
                    "info": ...,
                    "error": ...,
                },
                "res.partner": {
                    ...
                },
                "account.payment": {
                    ...
                }
            }
        """
        self.ensure_one()
        Line = self.env["import.api.line"]
        states_default = {state: Line for state, _ in Line._fields['state'].selection}
        res = {}
        for line in self.line_ids:
            res.setdefault(line.model, states_default.copy())
            res[line.model][line.state] |= line
        return res
    
    #===== Button =====#
    def action_toggle_verified_all(self):
        for logger in self:
            lines = logger.line_ids
            if logger._get_is_verified():
                lines.verified = False
            else:
                lines.verified = True
    def _get_is_verified(self):
        self.ensure_one()
        lines = self.line_ids
        if not lines:
            return False
        return not bool(lines.filtered(lambda x: x.state != 'success' and not x.verified))
    
    def action_replay(self):
        for logger in self:
            if not logger.model in self.env:
                raise exceptions.ValidationError(_("Unknown model"))
            self.line_ids.active = False
            self.date_last_call = fields.Datetime.now()
            Model = self.env[logger.model]
            Model.import_api(
                payload_arg={
                    'config': json.loads(logger.config or ''),
                    'data': json.loads(logger.data or ''),
                },
                logger=logger,
            )
    
    def action_open_lines(self):
        """ Smart button to log lines """
        context_add = {"default_logger_id": self.id}
        if self._context.get("previous_line"):
            context_add.update({
                "search_default_inactive": True,
                "active_test": False,
            })
        
        xml_id = "base_import_api.import_api_line_action"
        action = self.env.ref(xml_id).read([])[0]
        action.update({
            "context": self._context | context_add,
            "domain": [("logger_id", "=", self.id)],
        })
        return action
    
    def action_open_records(self):
        """ Smart button to imported records """
        lines = self.with_context(active_test=False).line_ids
        action = {
            'name': _("Imported %(model_descr)s", model_descr = self.model_description),
            'type': 'ir.actions.act_window',
            'res_model': self.model,
            'view_mode': 'list,form',
            'context': self._context,
            'domain': [("id", "in", lines.mapped("record_id"))]
        }
        return action

def _convert_markdown(text, output_format):
    if output_format == 'markdown':
        return text
    else:
        try:
            from markdown import Markdown
        except ImportError:
            _logger.error(
                "Cannot convert report in HTML because of missing "
                "python dependency 'markdown'."
            )
            return text
        
        # patch Markdown to support 'plain'
        # https://stackoverflow.com/questions/761824/python-how-to-convert-markdown-formatted-text-to-text
        if output_format == "plain":
            from io import StringIO
            def unmark_element(element, stream=None):
                if stream is None:
                    stream = StringIO()
                if element.text:
                    stream.write(element.text)
                for sub in element:
                    unmark_element(sub, stream)
                if element.tail:
                    stream.write(element.tail)
                return stream.getvalue()
            Markdown.output_formats["plain"] = unmark_element
        
        md = Markdown(output_format=output_format, extensions=["sane_lists", "nl2br"])
        if output_format == "plain":
            md.stripTopLevelTags = False
        
        return md.convert(text)
