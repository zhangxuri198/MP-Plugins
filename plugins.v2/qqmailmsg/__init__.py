from typing import Any, List, Dict, Tuple

from app.core.event import eventmanager, Event
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType, NotificationType

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests

def send_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email, subject, body, image_url=None):
    # 创建邮件消息对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject  # 设置邮件标题

    # 邮件正文部分（文本内容）
    msg.attach(MIMEText(body, 'plain'))

    # 如果提供了图片 URL，则下载并添加图片附件
    if image_url:
        try:
            # 通过 URL 获取图片内容
            response = requests.get(image_url)
            response.raise_for_status()  # 如果请求失败会抛出异常
            img_data = response.content

            # 创建图片附件
            img = MIMEImage(img_data)
            img.add_header('Content-ID', '<image1>')  # 可以在邮件正文中引用图片
            msg.attach(img)
        except requests.exceptions.RequestException as e:
            logger.warn(f"下载图片时发生错误: {e}")

    # 连接到SMTP服务器并发送邮件
    server = None
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # 启动 TLS 安全连接
        server.login(sender_email, sender_password)  # 登录到SMTP服务器
        server.sendmail(sender_email, recipient_email, msg.as_string())  # 发送邮件
        logger.info("邮件发送成功！")
    except Exception as e:
        logger.error(f"邮件发送失败: {e}")
    finally:
        # 优雅地关闭连接
        if server:
            try:
                server.quit()  # 或者使用 server.close()
            except Exception as e:
                logger.warn(f"关闭 SMTP 连接时发生错误: {e}")

class QQMailMsg(_PluginBase):
    # 插件名称
    plugin_name = "邮件消息通知"
    # 插件描述
    plugin_desc = "支持使用邮件发送消息通知。"
    # 插件图标
    plugin_icon = "Wecom_A.png"
    # 插件版本
    plugin_version = "1.0"
    # 插件作者
    plugin_author = "zhangxuri198"
    # 作者主页
    author_url = "https://github.com/zhangxuri198"
    # 插件配置项ID前缀
    plugin_config_prefix = "qqmailmsg_"
    # 加载顺序
    plugin_order = 28
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _msgtypes = []
    _smtp_server = None
    _smtp_port = None
    _sender_email = None
    _sender_password = None
    _recipient_email = None

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled")
            self._smtp_server = config.get("smtp_server")
            self._smtp_port = config.get("smtp_port")
            self._sender_email = config.get("sender_email")
            self._sender_password = config.get("sender_password")
            self._recipient_email = config.get("recipient_email")
            self._msgtypes = config.get("msgtypes") or []

    def get_state(self) -> bool:
        return (self._enabled
                and (True if self._smtp_server else False)
                and (True if self._smtp_port else False)
                and (True if self._sender_email else False)
                and (True if self._sender_password else False)
                and (True if self._recipient_email else False))

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        # 编历 NotificationType 枚举，生成消息类型选项
        MsgTypeOptions = []
        for item in NotificationType:
            MsgTypeOptions.append({
                "title": item.value,
                "value": item.name
            })
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'multiple': True,
                                            'chips': True,
                                            'model': 'msgtypes',
                                            'label': '消息类型',
                                            'items': MsgTypeOptions
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'smtp_server',
                                            'label': 'smtp服务器',
                                            'placeholder': 'smtp.qq.com',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'smtp_port',
                                            'label': 'smtp服务器端口',
                                            'placeholder': '587',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'sender_email',
                                            'label': '发送者',
                                            'placeholder': '',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'sender_password',
                                            'label': '密码',
                                            'placeholder': '',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'recipient_email',
                                            'label': '接收者',
                                            'placeholder': '',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                ]
            }
        ], {
            "enabled": False,
            'smtp_server': 'smtp.qq.com',
            'smtp_port': '587',
            'sender_email': '',
            'sender_password': '',
            'recipient_email': '',
            'subject': '',
            'body': '',
        }

    def get_page(self) -> List[dict]:
        pass

    @eventmanager.register(EventType.NoticeMessage)
    def send(self, event: Event):
        """
        消息发送事件
        """
        if not self.get_state():
            return

        if not event.event_data:
            return

        msg_body = event.event_data
        # 渠道
        channel = msg_body.get("channel")
        if channel:
            return
        # 类型
        msg_type: NotificationType = msg_body.get("type")
        # 标题
        title = msg_body.get("title")
        # 文本
        text = msg_body.get("text")
        # 图像
        image = msg_body.get("image")

        if not title and not text:
            logger.warn("标题和内容不能同时为空")
            return

        if (msg_type and self._msgtypes
                and msg_type.name not in self._msgtypes):
            logger.info(f"消息类型 {msg_type.value} 未开启消息发送")
            return

        smtp_server = self._smtp_server
        smtp_port = self._smtp_port
        sender_email = self._sender_email
        sender_password = self._sender_password
        recipient_email = self._recipient_email

        send_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email, title, text,
                   image)

    def stop_service(self):
        """
        退出插件
        """
        pass
