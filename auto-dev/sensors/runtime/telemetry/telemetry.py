#!/usr/bin/env python3
"""
Telemetry - 全链路可观测系统
日志、追踪、指标三位一体

功能:
- 结构化日志记录
- 调用链追踪
- 指标采集与聚合
- 异常监控
"""

import os
import sys
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from collections import defaultdict
import threading
import uuid


class TelemetryLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TelemetryEvent:
    """遥测事件"""

    def __init__(
        self,
        name: str,
        level: str,
        category: str,
        message: str,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict] = None,
        error: Optional[Dict] = None
    ):
        self.name = name
        self.level = level
        self.category = category
        self.message = message
        self.trace_id = trace_id or generate_trace_id()
        self.span_id = span_id or generate_span_id()
        self.parent_span_id = parent_span_id
        self.duration_ms = duration_ms
        self.metadata = metadata or {}
        self.error = error
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "level": self.level,
            "category": self.category,
            "message": self.message,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
            "error": self.error,
            "timestamp": self.timestamp
        }


class Telemetry:
    """全链路可观测系统"""

    def __init__(self, service_name: str, log_dir: Optional[Path] = None):
        self.service_name = service_name
        self.log_dir = log_dir or Path.home() / ".auto-dev" / "telemetry"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self._events: List[TelemetryEvent] = []
        self._metrics: Dict[str, List[float]] = defaultdict(list)
        self._current_span: Optional[str] = None
        self._span_stack: List[str] = []
        self._lock = threading.Lock()

        # 当前 trace
        self._trace_id = generate_trace_id()

    def start_trace(self, name: str, metadata: Optional[Dict] = None) -> str:
        """开始追踪"""
        trace_id = self._trace_id
        span_id = generate_span_id()
        parent_span_id = self._current_span

        self._current_span = span_id
        self._span_stack.append(span_id)

        self.log(
            name=f"{name}.start",
            level=TelemetryLevel.INFO,
            category="trace",
            message=f"Started: {name}",
            span_id=span_id,
            parent_span_id=parent_span_id,
            metadata=metadata
        )

        return span_id

    def end_trace(self, span_id: str, duration_ms: Optional[float] = None):
        """结束追踪"""
        if self._span_stack and self._span_stack[-1] == span_id:
            self._span_stack.pop()

        if self._span_stack:
            self._current_span = self._span_stack[-1]
        else:
            self._current_span = None

        self.log(
            name=f"{span_id}.end",
            level=TelemetryLevel.INFO,
            category="trace",
            message=f"Ended: {span_id}",
            span_id=span_id,
            duration_ms=duration_ms
        )

    def log(
        self,
        name: str,
        level: str,
        category: str,
        message: str,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict] = None,
        error: Optional[Dict] = None
    ):
        """记录事件"""
        event = TelemetryEvent(
            name=name,
            level=level,
            category=category,
            message=message,
            trace_id=self._trace_id,
            span_id=span_id or self._current_span,
            parent_span_id=parent_span_id,
            duration_ms=duration_ms,
            metadata=metadata,
            error=error
        )

        with self._lock:
            self._events.append(event)

        # 写入日志文件
        self._write_to_file(event)

    def record_metric(self, name: str, value: float, unit: str = "count"):
        """记录指标"""
        with self._lock:
            self._metrics[name].append(value)

    def increment(self, name: str, value: float = 1):
        """递增计数器"""
        self.record_metric(name, value)

    def gauge(self, name: str, value: float):
        """设置仪表值"""
        with self._lock:
            self._metrics[name] = [value]

    def get_metrics_summary(self) -> Dict[str, Dict]:
        """获取指标摘要"""
        summary = {}
        with self._lock:
            for name, values in self._metrics.items():
                if values:
                    summary[name] = {
                        "count": len(values),
                        "sum": sum(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "last": values[-1]
                    }
        return summary

    def get_events(
        self,
        level: Optional[str] = None,
        category: Optional[str] = None,
        trace_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """获取事件列表"""
        with self._lock:
            events = self._events.copy()

        if level:
            events = [e for e in events if e.level == level]
        if category:
            events = [e for e in events if e.category == category]
        if trace_id:
            events = [e for e in events if e.trace_id == trace_id]

        return [e.to_dict() for e in events[-limit:]]

    def _write_to_file(self, event: TelemetryEvent):
        """写入日志文件"""
        try:
            # 按日期分目录
            date_str = datetime.now().strftime("%Y-%m-%d")
            category_dir = self.log_dir / event.category
            category_dir.mkdir(exist_ok=True)

            log_file = category_dir / f"{date_str}.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
        except Exception:
            pass  # 忽略写入错误

    def flush(self):
        """刷新缓冲"""
        with self._lock:
            self._events.clear()

    def get_trace_tree(self, trace_id: Optional[str] = None) -> Dict:
        """构建追踪树"""
        tid = trace_id or self._trace_id
        events = self.get_events(trace_id=tid, limit=1000)

        # 按 span_id 分组
        spans = {}
        for e in events:
            sid = e["span_id"]
            if sid not in spans:
                spans[sid] = {
                    "span_id": sid,
                    "parent_span_id": e.get("parent_span_id"),
                    "name": e["name"],
                    "events": []
                }
            spans[sid]["events"].append(e)

        return {"trace_id": tid, "spans": list(spans.values())}


# 全局单例
_telemetry: Optional[Telemetry] = None


def get_telemetry() -> Telemetry:
    """获取全局遥测实例"""
    global _telemetry
    if _telemetry is None:
        _telemetry = Telemetry("auto-dev")
    return _telemetry


def generate_trace_id() -> str:
    """生成追踪ID"""
    return f"trace-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"


def generate_span_id() -> str:
    """生成跨度ID"""
    return f"span-{uuid.uuid4().hex[:12]}"


# 便捷函数
def log_event(name: str, level: str, category: str, message: str, **kwargs):
    """记录事件"""
    get_telemetry().log(name, level, category, message, **kwargs)


def trace(name: str, metadata: Optional[Dict] = None):
    """追踪上下文管理器"""
    telemetry = get_telemetry()
    span_id = telemetry.start_trace(name, metadata)
    start_time = time.time()
    try:
        yield span_id
    except Exception as e:
        log_event(
            name=f"{name}.error",
            level=TelemetryLevel.ERROR,
            category="error",
            message=str(e),
            span_id=span_id,
            error={
                "type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )
        raise
    finally:
        duration = (time.time() - start_time) * 1000
        telemetry.end_trace(span_id, duration)


# 指标采集装饰器
def metric(name: str, unit: str = "count"):
    """指标采集装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                get_telemetry().increment(f"{name}.success", 1)
                return result
            except Exception as e:
                get_telemetry().increment(f"{name}.error", 1)
                raise
            finally:
                duration = (time.time() - start_time) * 1000
                get_telemetry().record_metric(f"{name}.duration_ms", duration)
        return wrapper
    return decorator
