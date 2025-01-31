from typing import Union

import aiohttp

from .base import *
from .protect import protector
from ..errors import *


class FriendMixin(WechatAPIClientBase):
    async def accept_friend(self, scene: int, v1: str, v2: str) -> bool:
        """
        接受好友请求

        - 主动添加好友单天上限如下所示：1小时内上限为 5个，超过上限时，无法发出好友请求，也收不到好友请求。
        - 新账号：5/天
        - 注册超过7天：10个/天
        - 注册满3个月\&\&近期登录过该电脑：15/天
        - 注册满6个月\&\&近期经常登录过该电脑：20/天
        - 注册满6个月\&\&近期频繁登陆过该电脑：30/天
        - 注册1年以上\&\&一直登录：50/天
        - 上一次通过好友到下一次通过间隔20-40s
        - 收到加人申请，到通过好友申请（每天最多通过300个好友申请），间隔30s+（随机时间）

        :param scene: 来源 在消息的xml获取
        :param v1: v1key
        :param v2: v2key
        :return:
        """
        if not self.wxid:
            raise UserLoggedOut("请先登录")
        elif not self.ignore_protect and protector.check(14400):
            raise BanProtection("登录新设备后4小时内请不要操作以避免风控")

        async with aiohttp.ClientSession() as session:
            json_param = {"Wxid": self.wxid, "Scene": scene, "V1": v1, "V2": v2}
            response = await session.post(f'http://{self.ip}:{self.port}/AcceptFriend', json=json_param)
            json_resp = await response.json()

            if json_resp.get("Success"):
                return True
            else:
                self.error_handler(json_resp)

    async def get_contact(self, wxid: Union[str, list[str]]) -> Union[dict, list[dict]]:
        """
        获取联系人信息
        :param wxid: 联系人wxid, 可以是多个wxid在list里，也可查询chatroom
        :return: dict or list[dict]
        """
        if not self.wxid:
            raise UserLoggedOut("请先登录")

        if isinstance(wxid, list):
            wxid = ",".join(wxid)

        async with aiohttp.ClientSession() as session:
            json_param = {"Wxid": self.wxid, "RequestWxids": wxid}
            response = await session.post(f'http://{self.ip}:{self.port}/GetContact', json=json_param)
            json_resp = await response.json()

            if json_resp.get("Success"):
                contact_list = json_resp.get("Data").get("ContactList")
                if len(contact_list) == 1:
                    return contact_list[0]
                else:
                    return contact_list
            else:
                self.error_handler(json_resp)

    async def get_contract_detail(self, wxid: Union[str, list[str]], chatroom: str = "") -> dict:
        """
        获取联系人详情
        :param wxid: 联系人wxid
        :param chatroom: 群聊wxid
        :return: dict (dict of contact detail)
        """
        if not self.wxid:
            raise UserLoggedOut("请先登录")

        if isinstance(wxid, list):
            wxid = ",".join(wxid)

        async with aiohttp.ClientSession() as session:
            json_param = {"Wxid": self.wxid, "RequestWxids": wxid, "Chatroom": chatroom}
            response = await session.post(f'http://{self.ip}:{self.port}/GetContractDetail', json=json_param)
            json_resp = await response.json()

            if json_resp.get("Success"):
                return json_resp.get("Data").get("ContactList")[0]
            else:
                self.error_handler(json_resp)

    async def get_contract_list(self) -> list:
        """
        获取联系人列表
        :return: list[dict] (list of contact)
        """
        if not self.wxid:
            raise UserLoggedOut("请先登录")

        async with aiohttp.ClientSession() as session:
            json_param = {"Wxid": self.wxid, "CurrentWxcontactSeq": 0, "CurrentChatroomContactSeq": 0}
            response = await session.post(f'http://{self.ip}:{self.port}/GetContractList', json=json_param)
            json_resp = await response.json()

            if json_resp.get("Success"):
                return json_resp.get("Data").get("ContactUsernameList")
            else:
                self.error_handler(json_resp)

    async def get_nickname(self, wxid: str) -> str:
        """
        获取用户昵称
        :param wxid: 用户wxid
        :return: str
        """
        data = await self.get_contract_detail(wxid)
        try:
            return data.get("NickName").get("string")
        except:
            return ""
