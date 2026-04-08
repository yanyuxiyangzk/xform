#!/usr/bin/env python3
"""
Notification Operations - 通知模块

支持Discord webhook通知

功能:
- Discord webhook通知
- 可配置的通知事件
- 静默模式（webhook未配置时）

用法:
  python notification_ops.py test                      # 发送测试消息
  python notification_ops.py send <event> <message>   # 发送消息
  python notification_ops.py daily-summary            # 发送日报
  python notification_ops.py config [--enable]        # 配置通知
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
STATE_DIR = AUTO_DEV_BASE / "self-improving"
CONFIG_FILE = STATE_DIR / "notification-config.json"

# 默认配置
DEFAULT_CONFIG = {
    "enabled": False,
    "webhook_url": "",
    "notify_on": [
        "pipeline_complete",
        "pipeline_blocked",
        "stuck_detected",
        "daily_summary"
    ],
    "mention_on_error": True,
    "mention_role_id": None  # Discord role ID to mention
}


class NotificationOps:
    """通知操作类"""

    def __init__(self):
        STATE_DIR.mkdir(exist_ok=True)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return DEFAULT_CONFIG.copy()

    def _save_config(self):
        """保存配置"""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def is_enabled(self) -> bool:
        """检查通知是否启用"""
        return self.config.get("enabled", False) and bool(self.config.get("webhook_url"))

    def should_notify(self, event_type: str) -> bool:
        """检查是否应发送此类型的通知"""
        if not self.is_enabled():
            return False
        notify_list = self.config.get("notify_on", [])
        return event_type in notify_list

    def _build_payload(self, content: str, embed: Dict = None) -> Dict:
        """构建Discord payload"""
        payload = {
            "content": content,
            "embeds": []
        }

        if embed:
            payload["embeds"].append(embed)

        return payload

    def _send_webhook(self, payload: Dict) -> Tuple[bool, str]:
        """发送webhook请求"""
        if not self.is_enabled():
            return False, "Notification disabled or webhook not configured"

        webhook_url = self.config.get("webhook_url")

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                webhook_url,
                data=data,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 204:
                    return True, "Message sent successfully"
                else:
                    return False, f"Unexpected response: {response.status}"

        except urllib.error.HTTPError as e:
            return False, f"HTTP error: {e.code}"
        except urllib.error.URLError as e:
            return False, f"URL error: {e.reason}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def notify(self, event_type: str, message: str, details: Dict = None) -> Tuple[bool, str]:
        """
        发送通知

        Args:
            event_type: 事件类型
            message: 消息内容
            details: 额外详情

        Returns:
            (success: bool, message: str)
        """
        if not self.should_notify(event_type):
            return False, f"Not configured to notify on: {event_type}"

        # 构建内容
        content = f"**[{event_type}]** {message}"

        # 添加mention
        if self.config.get("mention_on_error") and "error" in event_type.lower():
            role_id = self.config.get("mention_role_id")
            if role_id:
                content = f"<@{role_id}> {content}"

        # 构建embed
        embed = None
        if details:
            embed = {
                "title": "Details",
                "color": self._get_color_for_event(event_type),
                "fields": []
            }

            for key, value in details.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)[:100]
                embed["fields"].append({
                    "name": key,
                    "value": str(value)[:100],
                    "inline": True
                })

            embed["footer"] = {
                "text": f"Auto-Dev | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }

        payload = self._build_payload(content, embed)
        return self._send_webhook(payload)

    def _get_color_for_event(self, event_type: str) -> int:
        """获取事件对应的颜色"""
        colors = {
            "pipeline_complete": 0x00FF00,    # 绿色
            "pipeline_blocked": 0xFF0000,     # 红色
            "stuck_detected": 0xFF6600,       # 橙色
            "error": 0xFF0000,               # 红色
            "daily_summary": 0x0099FF,       # 蓝色
            "warning": 0xFFAA00              # 黄色
        }
        return colors.get(event_type, 0x888888)

    def send_test(self) -> Tuple[bool, str]:
        """发送测试消息"""
        return self.notify(
            "test",
            "Auto-Dev notification test",
            {"test": "ok", "timestamp": datetime.now().isoformat()}
        )

    def send_pipeline_complete(self, pipeline_id: str, duration: str = None) -> Tuple[bool, str]:
        """发送Pipeline完成通知"""
        return self.notify(
            "pipeline_complete",
            f"Pipeline {pipeline_id} completed",
            {"pipeline_id": pipeline_id, "duration": duration}
        )

    def send_pipeline_blocked(self, pipeline_id: str, reason: str) -> Tuple[bool, str]:
        """发送Pipeline阻塞通知"""
        return self.notify(
            "pipeline_blocked",
            f"Pipeline {pipeline_id} blocked: {reason}",
            {"pipeline_id": pipeline_id, "reason": reason}
        )

    def send_stuck_detected(self, task_id: str, reason: str) -> Tuple[bool, str]:
        """发送Stuck检测通知"""
        return self.notify(
            "stuck_detected",
            f"Stuck task detected: {task_id}",
            {"task_id": task_id, "reason": reason}
        )

    def send_daily_summary(self, stats: Dict) -> Tuple[bool, str]:
        """发送日报"""
        return self.notify(
            "daily_summary",
            "Auto-Dev Daily Summary",
            stats
        )

    def configure(self, enable: bool = None, webhook_url: str = None,
                 notify_on: List[str] = None, mention_role_id: str = None):
        """配置通知"""
        if enable is not None:
            self.config["enabled"] = enable

        if webhook_url is not None:
            self.config["webhook_url"] = webhook_url

        if notify_on is not None:
            self.config["notify_on"] = notify_on

        if mention_role_id is not None:
            self.config["mention_role_id"] = mention_role_id

        self._save_config()

        print("[OK] Configuration saved")
        print(f"  Enabled: {self.config['enabled']}")
        print(f"  Webhook configured: {bool(self.config.get('webhook_url'))}")
        print(f"  Notify on: {', '.join(self.config.get('notify_on', []))}")

    def get_status(self) -> Dict:
        """获取配置状态"""
        return {
            "enabled": self.config.get("enabled", False),
            "webhook_configured": bool(self.config.get("webhook_url")),
            "notify_on": self.config.get("notify_on", []),
            "mention_on_error": self.config.get("mention_on_error", True),
            "mention_role_id": self.config.get("mention_role_id")
        }


def main():
    parser = argparse.ArgumentParser(description="Notification Operations - 通知模块")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # test命令
    subparsers.add_parser("test", help="发送测试消息")

    # send命令
    send_parser = subparsers.add_parser("send", help="发送消息")
    send_parser.add_argument("event", help="事件类型")
    send_parser.add_argument("message", help="消息内容")

    # daily-summary命令
    subparsers.add_parser("daily-summary", help="发送日报")

    # config命令
    config_parser = subparsers.add_parser("config", help="配置通知")
    config_parser.add_argument("--enable", action="store_true", help="启用通知")
    config_parser.add_argument("--disable", action="store_true", help="禁用通知")
    config_parser.add_argument("--webhook", help="设置webhook URL")
    config_parser.add_argument("--notify-on", nargs="+", help="设置通知事件类型")

    # status命令
    subparsers.add_parser("status", help="查看通知状态")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ops = NotificationOps()

    if args.command == "test":
        success, msg = ops.send_test()
        print(f"[{'OK' if success else 'FAIL'}] {msg}")
        sys.exit(0 if success else 1)

    elif args.command == "send":
        success, msg = ops.notify(args.event, args.message)
        print(f"[{'OK' if success else 'FAIL'}] {msg}")
        sys.exit(0 if success else 1)

    elif args.command == "daily-summary":
        stats = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "pipelines_completed": 0,
            "tasks_completed": 0,
            "errors": 0
        }
        success, msg = ops.send_daily_summary(stats)
        print(f"[{'OK' if success else 'FAIL'}] {msg}")
        sys.exit(0 if success else 1)

    elif args.command == "config":
        enable = None
        if args.enable:
            enable = True
        elif args.disable:
            enable = False

        webhook = args.webhook
        notify_on = args.notify_on

        ops.configure(enable=enable, webhook_url=webhook, notify_on=notify_on)

    elif args.command == "status":
        status = ops.get_status()
        print("\n[NOTIFICATION STATUS]")
        print("=" * 50)
        print(f"Enabled:          {status['enabled']}")
        print(f"Webhook configured: {status['webhook_configured']}")
        print(f"Notify on:        {', '.join(status['notify_on']) or 'none'}")
        print(f"Mention on error: {status['mention_on_error']}")
        print(f"Mention role ID:  {status['mention_role_id'] or 'not set'}")


if __name__ == "__main__":
    main()
