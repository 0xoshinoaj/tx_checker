#!/usr/bin/env python3
"""
RPC 測試工具
讀取 config.toml 中所有 networks.*.rpc，逐一測試連線可用性與回應時間。
"""

import sys
import time
from typing import Dict, List, Tuple

import requests
from utils.console import COLOR_GREEN, COLOR_RED, COLOR_YELLOW, color_text, print_error, print_warn

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def load_config(path: str = "config.toml") -> Dict:
    """讀取 TOML 配置檔"""
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print_error(f"✗ 找不到配置文件: {path}")
        sys.exit(1)
    except Exception as e:
        print_error(f"✗ 讀取配置文件失敗: {e}")
        sys.exit(1)


def test_single_rpc(rpc_url: str, timeout_sec: float) -> Tuple[bool, str, float]:
    """
    測單一 RPC
    回傳: (成功/失敗, 訊息, 耗時秒數)
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1,
    }

    start = time.perf_counter()
    try:
        resp = requests.post(rpc_url, json=payload, timeout=timeout_sec)
        elapsed = time.perf_counter() - start
        resp.raise_for_status()

        data = resp.json()
        if "error" in data:
            msg = data["error"].get("message", "未知RPC錯誤")
            return False, f"RPC錯誤: {msg}", elapsed

        result = data.get("result")
        if not isinstance(result, str) or not result.startswith("0x"):
            return False, "回傳格式異常（缺少有效區塊高度）", elapsed

        block_num = int(result, 16)
        return True, f"區塊高度 {block_num}", elapsed

    except requests.exceptions.Timeout:
        elapsed = time.perf_counter() - start
        return False, "請求超時", elapsed
    except requests.exceptions.RequestException as e:
        elapsed = time.perf_counter() - start
        return False, f"連線錯誤: {e}", elapsed
    except ValueError as e:
        elapsed = time.perf_counter() - start
        return False, f"解析錯誤: {e}", elapsed


def main() -> None:
    cfg = load_config("config.toml")
    settings = cfg.get("settings", {})
    timeout_sec = float(settings.get("rpc_test_timeout", 8))
    networks = cfg.get("networks", {})

    if not networks:
        print_error("✗ config.toml 未找到 networks 設定")
        sys.exit(1)

    print_warn(f"🧪 開始測試 config.toml 內所有 RPC（timeout={timeout_sec}s）")
    print("-" * 72)

    total = 0
    ok = 0
    failed = 0

    for net_name, net_cfg in networks.items():
        rpc_list: List[str] = net_cfg.get("rpc", [])
        enabled = net_cfg.get("enabled", False)
        if not rpc_list:
            continue

        status = "enabled" if enabled else "disabled"
        print(f"\n{color_text(f'[{net_name}] ({status})', COLOR_YELLOW)}")

        for idx, rpc_url in enumerate(rpc_list, start=1):
            total += 1
            success, message, elapsed = test_single_rpc(rpc_url, timeout_sec)
            elapsed_ms = int(elapsed * 1000)
            if success:
                ok += 1
                print(color_text(f"  ✓ ({idx}/{len(rpc_list)}) {rpc_url} | {elapsed_ms}ms | {message}", COLOR_GREEN))
            else:
                failed += 1
                print(color_text(f"  ✗ ({idx}/{len(rpc_list)}) {rpc_url} | {elapsed_ms}ms | {message}", COLOR_RED))

    print("\n" + "=" * 72)
    print("RPC 測試摘要")
    print("=" * 72)
    print(f"總數: {total}")
    print(color_text(f"成功: {ok}", COLOR_GREEN))
    print(color_text(f"失敗: {failed}", COLOR_RED))

    if failed > 0:
        print_warn("\n提示：可先移除/替換失敗率高的 RPC，再執行 tx_checker.py。")


if __name__ == "__main__":
    main()

