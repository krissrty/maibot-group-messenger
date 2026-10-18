import importlib.util
import pathlib
import unittest
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[1]

class MessengerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('messenger', ROOT / 'plugin.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.plugin = module.create_plugin()
        self.calls = []
        self.response = {'status': 'ok', 'retcode': 0, 'data': {'message_id': '123'}}
        async def call(name, **kwargs):
            self.calls.append((name, kwargs))
            if name.endswith('get_group_list'):
                return [{'group_id': 12345, 'group_name': '姐妹群'}, {'group_id': 67890, 'group_name': '姐妹群二号'}]
            return self.response
        self.plugin._ctx = SimpleNamespace(api=SimpleNamespace(call=call))

    async def test_send_uses_explicit_group_and_text_segment(self):
        result = await self.plugin.send_group_message('12345', '你好[CQ:at,qq=all]')
        self.assertTrue(result['success'])
        payload = self.calls[-1][1]['params']
        self.assertEqual(payload['message_type'], 'group')
        self.assertEqual(payload['group_id'], 12345)
        self.assertEqual(payload['message'], [{'type': 'text', 'data': {'text': '你好[CQ:at,qq=all]'}}])

    async def test_ambiguous_name_does_not_send(self):
        result = await self.plugin.send_group_message('姐妹', '你好')
        self.assertFalse(result['success'])
        self.assertEqual(len(self.calls), 1)

    async def test_exact_name_resolves(self):
        result = await self.plugin.send_group_message('姐妹群', '你好')
        self.assertTrue(result['success'])
        self.assertEqual(result['group_id'], '12345')

    async def test_nonmember_group_does_not_send(self):
        self.assertFalse((await self.plugin.send_group_message('99999', '你好'))['success'])
        self.assertEqual(len(self.calls), 1)

    async def test_failed_or_unconfirmed_delivery_is_not_success(self):
        for response in (None, {'success': False, 'error': '拒绝'}, {'status': 'failed', 'retcode': 100}, {'status': 'ok', 'data': {}}):
            self.response = response
            self.assertFalse((await self.plugin.send_group_message('12345', '你好'))['success'])

    async def test_empty_text_does_not_call_adapter(self):
        self.assertFalse((await self.plugin.send_group_message('12345', '  '))['success'])
        self.assertEqual(self.calls, [])

if __name__ == '__main__':
    unittest.main()
