"""让 Planner 在用户要求时向指定 QQ 群发送普通文字。"""
from maibot_sdk import MaiBotPlugin, Tool
from maibot_sdk.types import ToolParameterInfo, ToolParamType

ADAPTER = 'maibot-team.snowluma-adapter.'

class GroupMessenger(MaiBotPlugin):
    async def on_load(self):
        self.ctx.logger.info('跨聊天群消息工具已加载：list_message_groups / send_group_message')

    async def on_unload(self):
        pass

    async def on_config_update(self, new_config):
        pass

    async def groups(self):
        result = await self.ctx.api.call(ADAPTER + 'adapter.napcat.group.get_group_list')
        if not isinstance(result, list):
            raise ValueError('无法读取机器人已加入的群列表，请检查 SnowLuma 适配器')
        return [{'group_id': str(g['group_id']), 'group_name': str(g.get('group_name') or '')}
                for g in result if isinstance(g, dict) and str(g.get('group_id') or '').isascii()
                and str(g.get('group_id') or '').isdigit()]

    @Tool('list_message_groups', description='查询机器人已加入的QQ群名和群号。用户让你去某个群发言而目标不明确时查询；不能猜测目标群。', parameters=[])
    async def list_message_groups(self, **kwargs):
        try:
            return {'success': True, 'groups': await self.groups()}
        except Exception as exc:
            return {'success': False, 'error': str(exc)}

    @Tool('send_group_message', description=(
        '当用户明确要求你去指定QQ群发言、传话或道歉时，向该群发送你组织好的普通文字消息。'
        '私聊中也可调用。target为群号或群名，message为完整发言内容。'
        '用户没说明哪个群时先查询list_message_groups并询问用户，不要猜测。'
        '必须真正调用本工具并根据success反馈；失败或未确认时不能声称已经发送，也不要自动重发。'),
        parameters=[ToolParameterInfo(name='target', param_type=ToolParamType.STRING, description='目标QQ群号或群名', required=True),
                    ToolParameterInfo(name='message', param_type=ToolParamType.STRING, description='要以机器人身份发送的完整文字', required=True)])
    async def send_group_message(self, target='', message='', **kwargs):
        if not isinstance(target, str) or not target.strip():
            return {'success': False, 'error': '请明确目标群号或群名'}
        if not isinstance(message, str) or not message.strip() or len(message) > 4000:
            return {'success': False, 'error': '消息必须是1至4000字的非空文字'}
        target = target.strip()
        try:
            groups = await self.groups()
            exact = [g for g in groups if target in (g['group_id'], g['group_name'])]
            matches = ([g for g in groups if g['group_id'] == target] if target.isascii() and target.isdigit()
                       else exact or [g for g in groups if target in g['group_name']])
            if len(matches) != 1:
                return {'success': False, 'error': '没有唯一匹配的群，请用户明确群号；尚未发送', 'candidates': matches}
            group = matches[0]
            response = await self.ctx.api.call(ADAPTER + 'adapter.napcat.message.send_msg', params={
                'message_type': 'group', 'group_id': int(group['group_id']),
                'message': [{'type': 'text', 'data': {'text': message.strip()}}]})
            if not isinstance(response, dict) or response.get('success') is False:
                return {'success': False, 'error': str(response), 'content': '发送未确认，请勿自动重发'}
            if response.get('status', 'ok') != 'ok' or response.get('retcode', 0) not in (0, 1):
                return {'success': False, 'error': str(response), 'content': '适配器报告发送失败'}
            data = response.get('data')
            mid = data.get('message_id') if isinstance(data, dict) else None
            if not mid or str(mid) == '0':
                return {'success': False, 'error': '未收到有效消息回执，消息可能迟到，请勿自动重发'}
            return {'success': True, **group, 'message_id': str(mid), 'content': '适配器已确认群消息发送成功'}
        except Exception as exc:
            return {'success': False, 'error': str(exc), 'content': '未确认发送，请勿声称成功或自动重发'}

def create_plugin():
    return GroupMessenger()




