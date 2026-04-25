#!/usr/bin/env python3
"""
RPC 測試工具
讀取 config.toml 中所有 networks.*.rpc，逐一測試連線可用性與回應時間。
"""

import sys
import time
from typing import Dict, List, Tuple

import requests

try:
    import tomllib
except ImportError:
    import tomli as tomllib


COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"


def load_config(path: str = "config.toml") -> Dict:
    """讀取 TOML 配置檔"""
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"{COLOR_RED}✗ 找不到配置文件: {path}{COLOR_RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{COLOR_RED}✗ 讀取配置文件失敗: {e}{COLOR_RESET}")
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
        print(f"{COLOR_RED}✗ config.toml 未找到 networks 設定{COLOR_RESET}")
        sys.exit(1)

    print(f"{COLOR_YELLOW}🧪 開始測試 config.toml 內所有 RPC（timeout={timeout_sec}s）{COLOR_RESET}")
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
        print(f"\n{COLOR_YELLOW}[{net_name}] ({status}){COLOR_RESET}")

        for idx, rpc_url in enumerate(rpc_list, start=1):
            total += 1
            success, message, elapsed = test_single_rpc(rpc_url, timeout_sec)
            elapsed_ms = int(elapsed * 1000)
            if success:
                ok += 1
                print(
                    f"{COLOR_GREEN}  ✓ ({idx}/{len(rpc_list)}) {rpc_url} | {elapsed_ms}ms | {message}{COLOR_RESET}"
                )
            else:
                failed += 1
                print(
                    f"{COLOR_RED}  ✗ ({idx}/{len(rpc_list)}) {rpc_url} | {elapsed_ms}ms | {message}{COLOR_RESET}"
                )

    print("\n" + "=" * 72)
    print("RPC 測試摘要")
    print("=" * 72)
    print(f"總數: {total}")
    print(f"{COLOR_GREEN}成功: {ok}{COLOR_RESET}")
    print(f"{COLOR_RED}失敗: {failed}{COLOR_RESET}")

    if failed > 0:
        print(f"\n{COLOR_YELLOW}提示：可先移除/替換失敗率高的 RPC，再執行 tx_checker.py。{COLOR_RESET}")


if __name__ == "__main__":
    main()

