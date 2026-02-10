# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime, html2plaintext
from markupsafe import Markup

import json
import re

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
        default='[]',
    )
    report = fields.Html(
        string='Detailed report',
        help='Using Markdown syntax for formatting',
        compute='_compute_report',
        readonly=True,
    )
    date_last_call = fields.Datetime(
        string="Last import date",
        readonly=True,
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
    )
    to_verify_line_count = fields.Integer(
        string="Log lines to verify",
        compute='_compute_counts',
    )
    previous_line_count = fields.Integer(
        string="Previous import log lines",
        compute='_compute_counts',
    )
    record_count = fields.Integer(
        string="Imported",
        compute="_compute_counts",
        help="Odoo records with an External Ref. imported by this API call. "
             "It can be higher than the exact number of really imported records, "
             "because it catches duplicates (like previsouly imported records "
             "having identical External Refs. than the ones imported by this API call).",
    )

    #===== Compute =====#
    @api.depends("model", "create_date")
    def _compute_display_name(self):
        for logger in self:
            name = logger.model_description
            if logger.date_last_call:
                date = format_datetime(self.env, logger.date_last_call)
                name = "[%s] %s" % (name, date)
            logger.display_name = name

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
            elif any(x in states for x in ["error", "warning"]):
                state = 'warning'
            # all lines imported, some with message
            elif "info" in states:
                state = 'info'
            # defaut: all lines imported, no review needed
            else:
                state = 'success'
            
            # 'verified': overrides the previous one
            if lines and state in ("error", "warning", "info") and self._is_all_verified():
                state = 'verified'
            
            logger.state = state
    
    @api.depends('state')
    def _compute_state_text(self):
        states = {
            "success": _("All records imported successfully, with no further information."),
            "info": _("Records imported, some with informative note."),
            "warning": _(
                "Partially successful imports: some records had defect "
                "during import or some failed."
            ),
            "error": _("General failure: no record imported."),
            "verified": _("Some issues, all handle by a real user."),
        }
        for logger in self:
            logger.state_text = states[logger.state]

    @api.depends("line_ids", "line_ids.active", "line_ids.record_id",)
    def _compute_counts(self):
        for logger in self:
            logger.line_count = len(logger.line_ids)
            logger.to_verify_line_count = len(
                logger.line_ids.filtered(lambda x: not x.verified)
            )

            all_lines = logger.with_context(active_test=False).line_ids
            logger.previous_line_count = len(all_lines.filtered(lambda x: not x.active))

            if logger.model in self.env:
                record_lines = all_lines.filtered(lambda x: x.model == logger.model and x.external_ref)
                domain = [("external_ref", "in", record_lines.mapped("external_ref"))]
                logger.record_count = self.env[logger.model].search_count(domain)
            else:
                logger.record_count = 0

    #===== Logics =====#
    @api.model
    def _init(self, model, payload):
        """ Create logger and add subscribers """
        logger = self.create({
            'company_id': self.env.company.id,
            'config': payload.get('config', {}),
            'data': payload.get('data', {}),
            'model': model,
            "date_last_call": self.env.cr.now(), # like create_date
        })
        # followers
        group = self.env.ref("base_import_api.group_import_api_user")
        logger.message_subscribe(group.users.partner_id.ids)
        return logger
    
    def _finish(self):
        """ 1. Set `record_id` on lines with created records
            2. Notify followers
        """
        # Set record_id
        for model, lines in self._get_lines_by_model().items():
            external_refs = lines.mapped("external_ref")
            domain = [
                ("external_ref", "in", external_refs),
                ("create_date", ">=", self.date_last_call), # to ignore already existing records 
            ]
            mapped_refs = {
                x["external_ref"]: x["id"]
                for x in self.env[model].search_read(domain, ["external_ref"])
            }
            for line in lines:
                line.record_id = mapped_refs.get(line.external_ref)

        # Notify to followers
        report = Markup(self._generate_report("html", with_body=False))
        self.message_post(body=report)

    def _get_lines_by_model(self):
        lines_by_model = {}
        for line in self.line_ids:
            if line.external_ref:
                lines_by_model.setdefault(line.model, self.env["import.api.line"])
                lines_by_model[line.model] |= line
        return lines_by_model
    
    #===== Lines =====#
    def _add_line(
        self, message='', parsed_dict={}, record=None, capture_msg=False,
        state=None, field='', value=None,
        flush=False,
    ):
        """ :option flush: should be True if record is not created
            :option capture_msg: if given, last item will be merged with `message`
        """
        vals = {
            "logger_id": self.id,
            "external_ref": parsed_dict.get("external_ref"),
            'message': message,
            'field': field,
            'value': value or parsed_dict.get(field),
            "model": record._name if record else self.model,
            "record_id": record and record.id,
        }
        if capture_msg and parsed_dict["chatter_msg"]:
            vals["message"] += "\n" + parsed_dict["chatter_msg"].pop()
        if state:
            vals["state"] = state

        line = self.env['import.api.line'].create(vals)
        _logger.info(f"[API import] {line._display()}")
        
        if flush:
            self._flush_lines(parsed_dict, record)
        
        return line
    
    def _add_line_warning(self, *args, **kwargs):
        """ Same than `_add_line` but `state` to "warning" """
        kwargs["state"] = "warning"
        self._add_line(*args, **kwargs)

    def _add_line_success(
            self, parsed_dict, record, capture_msg, *args, **kwargs
        ):
        """ Same than `_add_line` but `message` arg is always the same
            (and `state` to "success")
        """
        kwargs["state"] = "success"
        message = (
            _("%s created", record._description if record else _("Record"))
            + (_(", ID %d", record.id) if record else "")
        )
        self._add_line(message, parsed_dict, record, capture_msg, *args, **kwargs,)
    
    def _flush_lines(self, parsed_dict, record):
        """ Design to be called at the end of record import work
            (in `bio.post_create_or_update()`).

            It reconciles `chatter_msg` and `logger.line_ids` by:
             1. flushing `chatter_msg` into `logger.line_ids`
                (e.g. for "info" level-msg added via `business_document_import` methods)
             2. posting to the chatter the `logger.line_ids` not in `chatter_msg`
                (e.g. for "warning" level-msg added by this module)
            3. If no `chatter_msg`, it logs 1 empty success line to save `record_id`
        """
        if record:
            _lambda = lambda x: x.model == record._name and x.record_id == record.id
        else:
            external_ref = parsed_dict.get("external_ref")
            _lambda = external_ref and (lambda x: x.external_ref == str(external_ref))
        record_lines = bool(_lambda) and self.line_ids.filtered(_lambda)
        api_messages = [line for line in record_lines.read(["state", "message"])] if record_lines else []
        # 1.
        chatter_msg = parsed_dict.get("chatter_msg", [])
        if chatter_msg:
            for message in chatter_msg:
                message = message.strip()
                if message:
                    self._add_line(html2plaintext(message), parsed_dict)
        # 2.
        if record and api_messages:
            for line in api_messages:
                msg = f"<strong class=\"text-{line["state"]}\">{line["message"]}</strong>"
                record.message_post(body=Markup(msg.replace("\n", "<br />")))
        # 3.
        if not chatter_msg and not record_lines:
            # 'success' records: create an empty log line to keep it trace
            self._add_line_success(parsed_dict, record, capture_msg=False)
        
    #===== Report =====#
    @api.depends('line_ids.record_id', 'line_ids.message')
    def _compute_report(self):
        for logger in self:
            logger.report = Markup(logger._generate_report('html'))
    
    def _generate_report(self, format='html', with_body=True):
        """ :option format: 'html' or 'markdown' (default) """
        if not self.line_ids:
            return _("No report available.")
        else:
            report = f"# {self.display_name}\n"

            # Global lines
            global_lines = self.line_ids.filtered(lambda x: x.state == "global")
            if global_lines:
                report += _(
                    "## Global messages\n%s",
                    "\n" . join(global_lines.mapped("message"))
                )

            # Per model
            states = dict(self.line_ids._fields['state']._description_selection(self.env))
            for model, lines in self._get_lines_by_model().items():
                # Title (new model)
                report += _(
                    "## %(model_description)s (%(res_model)s)\n",
                    model_description=(
                        self.env[model]._description
                        if model in self.env else _("Unknown model")
                    ),
                    res_model=model,
                )

                if with_body:
                    report += _("### Summary\n")

                # Summary
                counts = {
                    state: len(set(lines.filtered(lambda x: x.state == state).mapped("external_ref")))
                    for state in states
                }
                report += _(
                    "\n"
                    "* %(success)d successful record(s), imported with no note\n"
                    "* %(warning)d imported record(s), with defect requiring user review\n"
                    "* %(info)d imported record(s), with informative note\n"
                    "* %(failed)d import(s) failed\n",
                    success=counts["success"],
                    warning=counts["warning"],
                    info=counts["info"],
                    failed=counts["error"],
                )

                if with_body:
                    for line_state, state in states.items():
                        lines = self.line_ids.filtered(lambda x: x.external_ref and x.state == line_state)
                        if lines:
                            # External Refs
                            external_refs = set(lines.mapped("external_ref"))
                            if external_refs:
                                report += _(
                                    "### External Refs of \"%(state)s\" records\n"
                                    "%(external_refs)s\n\n",
                                    state=state,
                                    external_refs=' ' . join(external_refs),
                                )

                            # Messages
                            lines_message = lines.filtered('message')
                            if lines_message:
                                report += _(
                                    "### Log of \"%(state)s\" lines\n"
                                    "\n- %(messages)s",
                                    state=state,
                                    messages="\n- " . join([line._display() for line in lines_message])
                                )
            return _convert_markdown(report, format)
    
    #===== API response =====#
    def _get_api_response(self, config) -> dict:
        """ Prepare the data returned by the API
            {
                "logger_id": 1,
                    // Technical ID of the API call details in Odoo (model `import.api.call`)
                "state": "success",
                    // values: 'success', 'info', 'warning', 'error'
                "state_text": "All records imported successfully, with no further information.",
                    // Same as "state", but in natural language
                "report": "...",
                    // Full rich-text report, without formatting by default (plain)
                    (other supported format: Markdown or HTML)
                "records":
                {
                    "account.move": { // Invoices
                        "mapping": {"EXT001": 10, "EXT002": 12, "EXT003": 13, ...},
                            // Correspondance between External Ref. -> and Odoo ID
                        "success": ["EXT001" ...],
                            // Imported successfully with no note
                        "info": ["EXT002", ...],
                            // Imported with note, user *SHOULD* review the data in Odoo
                        "warning": ["EXT003", ...],
                            // Imported with defect, user *MUST* review the data in Odoo
                        "error": ...,
                            // Not imported at all
                    },
                    "res.partner": { // Contacts
                        "mapping": {...},
                        ...
                    },
                    "account.payment": { // Payments
                        ...
                    }
                }
            }
        """
        response = {
            'logger_id': self.id, # technical ID of API call (storing log details in Odoo)
            'state': self.state, # 
            'state_text': self.state_text, # same as 'state' but in natural language
            'report': self._generate_report(config.get("api_report_format")), # report, by default without formatting
            'records': self._get_api_response_records(),
        }
        _logger.debug(f"[API import] Response: {response}")
        return response
    
    def _get_api_response_records(self):
        self.ensure_one()
        res = {}
        states = self.env["import.api.line"]._fields['state'].selection
        default_key = {"mapping": {}} | {state: [] for state, _ in states}
        for line in self.line_ids:
            res.setdefault(line.model, default_key.copy())
            if line.record_ref:
                res[line.model][line.state].append(line.record_ref)
            if line.record_id:
                res[line.model]["mapping"][line.record_ref] = line.record_id
        return res

    #===== Button =====#
    def action_toggle_verified_all(self):
        for logger in self:
            lines = logger.line_ids
            if logger._is_all_verified():
                lines.verified = False
            else:
                lines.verified = True
    def _is_all_verified(self):
        self.ensure_one()
        lines = self.line_ids
        if not lines:
            return False
        return not bool(lines.filtered(lambda x: x.state != 'success' and not x.verified))
    
    def action_replay(self):
        for logger in self:
            if not logger.model in self.env:
                raise exceptions.ValidationError(_("Unknown model"))
            pattern = re.compile('//.+') # to remove JSON comments
            payload_arg = {
                "config": json.loads(pattern.sub('', logger.config or '')),
                "data": json.loads(pattern.sub('', logger.data or ''))
            }
            payload_arg["config"]["api_raise_exception"] = True # since actionned by user

            self.line_ids.active = False
            self.date_last_call = self.env.cr.now()
            
            Model = self.env[logger.model]
            Model.import_api(payload_arg, logger)
    
    def action_reset(self):
        lines = self.with_context(active_test=False).line_ids.sorted("model")
        mapped_ids = self._get_reset_record_ids(lines)
        for model, ids in mapped_ids.items():
            _logger.info("===== Model to reset: %s =====" % model)
            if not model in self.env:
                _logger.warning("Skipping %s: not existing anymore", model)
                continue

            Model = self.env[model]
            records = Model.browse(ids).exists()
            if not records:
                _logger.warning("Skipping %s: no imported records to reset", model)
                continue
            else:
                _logger.info("%d imported records to reset" % len(records))

            # reset one by one
            reset_method = self._get_reset_method
            for record in records:
                _logger.debug("Deleting %s" % record.display_name)
                reset_method(record)

    @api.model
    def _get_reset_record_ids(self, lines):
        """ Extension point, e.g. for reordering logic:
            reset 1 model before the other
        """
        mapped_ids = {}
        for line in lines.read(["model", "record_id"]):
            if line["model"] and line["record_id"]:
                record_ids = mapped_ids.setdefault(line["model"], set())
                record_ids.add(line["record_id"])
        return mapped_ids

    @api.model
    def _get_reset_method(self, record):
        """ Extension point for pre-processing before unlink
            Example: `button_draft` on `account.move`, then unlink
        """
        if record._name == "account.move" and record.state == "posted":
            record.button_draft()
        record.unlink()
    
    def action_open_lines(self):
        """ Smart button to log lines """
        context_add = {
            "default_logger_id": self.id,
            "search_default_unverified": True,
        }
        if self._context.get("previous_line"):
            context_add.update({
                "search_default_inactive": True,
                "active_test": False,
            })
        
        return {
            "type": "ir.actions.act_window",
            "name": _("API call line"),
            "res_model": "import.api.line",
            "view_mode": "list,form",
            "context": self._context | context_add,
            "domain": [("logger_id", "=", self.id)],
        }
    
    def action_open_records(self):
        """ Smart button to imported records """
        self = self.with_context(active_test=False)
        action = {
            'name': _("Imported %s", self.model_description),
            'type': 'ir.actions.act_window',
            'res_model': self.model,
            'view_mode': 'list,form',
            'context': self._context,
            'domain': [
                ("external_ref", "in", self.line_ids.filtered("external_ref").mapped("external_ref"))
            ]
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
