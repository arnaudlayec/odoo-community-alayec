# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, users, new_test_user

class TestBaseImportApi(TransactionCase):
    """ This class is a mixin of test methods """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # users
        group_name = "base_import_api.group_import_api_manager"
        cls.user_api = new_test_user(cls.env, "api_user", groups=group_name)
        cls.human_user = new_test_user(cls.env, "Human User", groups=group_name)
        # import a payload
        payload = {"config": {}}
        cls.response = cls.env['import.api.mixin'].with_user(cls.user_api).import_api(payload)
        # simulate import of a record
        cls.logger = cls.env['import.api.call'].with_user(cls.user_api).browse(
            cls.response.get("logger_id")
        )
        record = cls.user_api # random record
        cls.parsed_inv = {
            "external_id": "EXT001",
            "chatter_msg": ["Test message"],
        }
        cls.logger._flush_lines(cls.parsed_inv, record)
        # views
        cls.env['ir.config_parameter'].set_param(
            'import_api.readonly_records', True,
        )

    @users("api_user")
    def test_api_call_and_response(self):
        """ Test very basic call:
            - default config
            - format of API response
        """
        # config
        self.assertEqual(self.logger.company_id, self.env.company)
        # response
        self.assertEqual(self.response.get("state"), "error")
    
    @users("api_user")
    def test_logger_logics(self):
        """ Test logger's:
            - flush lines
            - state & verified computation
            - init and finish
            - replay
            - report & tranpose of chatter_msg
        """
        # flushed lines
        self.assertEqual(self.logger.line_ids.message, "Test message")

        # verified
        self.assertEqual(self.logger.state, "error") # none line imported
        self.logger.line_ids.action_toggle_verified()
        self.assertEqual(self.logger.state, "verified")

        # init & finish
        message = self.env['mail.message'].search(
            [('model', '=', 'import.api.call'), ('res_id', '=', self.logger.id)],
        )
        self.assertIn(self.human_user.partner_id, message.notified_partner_ids)

        # replay
        self.logger.action_replay()
        lines = self.logger.with_context(active_test=False).line_ids
        self.assertEqual(set(lines.mapped('active')), {False})

        # report
        self.assertTrue(self.logger.report)
    
    def test_front_end(self):
        """ Test:
            1. readonly fields
            2. view inheritance (form, tree, search)
        """
        # 1.
        ApiMixin = self.env['import.api.mixin'].with_context(test_mode=True)
        readonly_fields = all([
            attrs['readonly'] for attrs in ApiMixin.fields_get().values()
        ])
        self.assertTrue(readonly_fields)

        # 2.
        arch = ApiMixin.get_view(view_type="list")['arch'].decode("utf-8")
        self.assertTrue('<field name="external_ref"' in arch)
