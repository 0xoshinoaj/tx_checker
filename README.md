# 區塊鏈交易查詢工具 🔍

這個專案是用於查詢多個區塊鏈網絡上的地址交易數量。從文本檔導入地址，並將結果導出為 JSON、CSV、XLSX 等格式。

## 功能

- 支持多個區塊鏈網路（Ethereum、BSC、Polygon、Arbitrum、Optimism 等，也可自行添加需要的網路）
- 從 `addresses.txt` 文件導入地址
- 使用隨機選擇的 RPC 節點進行查詢，提高穩定性（可自行添加）
- 可選擇是否使用代理查詢（`use_proxy = true/false`）
- 支持代理輪換策略（rotate 或 random）
- 智能代理故障轉移機制
- 分批查詢與並行查詢，性能提升 5-10 倍
- 批量查詢結果自動保存到多種格式（JSON、CSV、XLSX）
- 詳細的錯誤提示與智能重試機制

## 安裝（macOS）

1. 克隆此倉庫：
   ```
   git clone https://github.com/0xoshinoaj/tx_checker.git
   cd 1021-tx_checker
   ```

2. （選擇性）指定 Python 版本（若你使用 pyenv）：
   ```
   pyenv local 3.10.0
   ```

3. 創建並啟用虛擬環境：
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

4. 安裝所需套件：
   ```
   python -m pip install -r requirements.txt
   ```

## 配置

1. 編輯 `config.toml` 文件，選擇要查詢的網絡並配置相關參數（節錄）：
   ```toml
   [networks."Ethereum主網"]
   enabled = true
   rpc = [
     "https://eth.llamarpc.com",
     "https://rpc.ankr.com/eth",
   ]

   [settings]
   import_file = "addresses.txt"
   output_formats = ['json', 'csv', 'xlsx']
   use_proxy = true
   proxy_file = "proxy.txt"
   proxy_rotation_strategy = "rotate"
   batch_size = 30
   batch_delay = 5.0
   concurrent_requests = 10
   ```

   **主要配置說明：**
   - `enabled` - 是否啟用該網絡（true/false）
   - `rpc` - RPC 節點列表，可自行添加或刪除，但無法留白
   - `import_file` - 輸入檔案名稱
   - `output_formats` - 輸出格式（'json', 'csv', 'xlsx'）
   - `use_proxy` - 是否使用代理
   - `proxy_rotation_strategy` - 代理輪換策略（'rotate' 或 'random'）
   - `batch_size` - 每批查詢的地址數
   - `batch_delay` - 批次間延遲時間（秒）
   - `concurrent_requests` - 並行查詢數

2. 將要查詢的地址添加到 `addresses.txt` 文件，每行一個地址：
   ```
   0x1f9090aaE28b8a3dCeaDf281B0F12828e676c326
   0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb
   0xabcdefabcdefabcdefabcdefabcdefabcdefabcd
   ```

   **注意事項：**
   - 支持帶或不帶 `0x` 前綴的地址
   - 可以添加註釋行（以 `#` 開頭）
   - 空行會自動跳過

3. 若你要使用代理，將 `proxy-Sample.txt` 改名為 `proxy.txt`，並在 `config.toml` 設定 `use_proxy = true`。代理格式如下：
   ```
   IP:PORT:USER:PASS
   223.27.113.36:12323:14a00881c83ad:89ced83a60
   192.168.1.1:8080:user:pass
   ```

## 執行

運行主程式：
   ```
   python tx_checker.py
   ```

查詢完成後，結果會輸出到 `results.json`、`results.csv`、`results.xlsx`（根據 `config.toml` 中的 `output_formats` 設置）。

## 輸出格式

**JSON 格式 (`results.json`)：**
```json
{
  "0x1f9090aaE28b8a3dCeaDf281B0F12828e676c326": 1234,
  "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb": 5678
}
```

**CSV 格式 (`results.csv`)：**

| JSON格式 | 地址 | 交易數 |
|---|---|---|
| 0x1f9090...e676c326: 1234 | 0x1f9090...e676c326 | 1234 |
| 0x742d35...f1bEb: 5678 | 0x742d35...f1bEb | 5678 |

**XLSX 格式 (`results.xlsx`)：**
與 CSV 相同的表格結構，帶美化的標題格式。

## 配置場景

根據不同的查詢場景選擇配置：

**場景1：高速查詢（推薦用於代理充足的場景）**
```toml
batch_size = 50
batch_delay = 2.0
concurrent_requests = 15
# 300 個地址約 1 分鐘完成
```

**場景2：穩定性優先（RPC限制嚴格）**
```toml
batch_size = 20
batch_delay = 5.0
concurrent_requests = 5
# 300 個地址約 3-5 分鐘完成
```

**場景3：極速模式（代理多且穩定）**
```toml
batch_size = 100
batch_delay = 1.0
concurrent_requests = 20
# 300 個地址約 30 秒完成
```

## 代理功能詳解

### 代理輪換策略

**Rotate（循環）- 推薦使用**
```toml
proxy_rotation_strategy = "rotate"
```
- 循環使用代理列表中的代理
- 適合代理數量較多的場景
- 可以均衡分散請求

**Random（隨機）**
```toml
proxy_rotation_strategy = "random"
```
- 隨機選擇代理
- 適合減少檢測的場景

### 重試機制

工具內置智能重試機制：

1. **代理錯誤重試** - 如果代理連接失敗，自動嘗試下一個代理（靜默重試）
2. **連接超時重試** - 超時時自動重試（靜默重試）
3. **回退機制** - 如果所有代理都失敗，可選擇直接連接（如果 `proxy_fallback_no_proxy = true`）
4. **失敗提示** - 只有當所有重試都失敗後，才顯示最終的錯誤信息

## 錯誤排查

### 1. "找不到文件: addresses.txt"
- 確保 `addresses.txt` 文件在項目根目錄

### 2. "連接超時"
- 檢查 RPC URL 是否正確
- 檢查代理是否有效
- 增加 `proxy_timeout` 值

### 3. "代理錯誤"
- 確認代理格式是否正確：`IP:PORT:USER:PASS`
- 檢查代理是否支持 HTTPS
- 嘗試增加 `proxy_retry_times`

### 4. "不支持的網絡"
- 檢查 `config.toml` 中選擇的網絡是否啟用（`enabled = true`）
- 確認網絡在 `[networks]` 中定義

### 5. 無效的地址格式
- 確保地址是有效的以太坊地址格式
- 地址長度應該是 42 個字符（包括 `0x`）

## 進階用法

### 查詢不同網絡上的地址

```python
from tx_checker import TxChecker

checker = TxChecker(network='bsc', use_proxy=True)
tx_count = checker.get_transaction_count('0x...')
```

### 禁用代理

在 `config.toml` 中設定：
```toml
use_proxy = false
```

## 注意事項 ⚠️

1. **RPC 限制**：某些 RPC 提供商可能有速率限制，使用代理輪換可以幫助繞過
2. **代理質量**：建議使用可靠的代理服務商，確保代理穩定性
3. **地址安全**：此工具只讀取地址信息，不涉及任何資金操作
4. **隱私考量**：使用代理時，請注意代理服務商的隱私政策
5. **法律合規**：在使用代理前，請確保符合當地法律法規

## 依賴

- `requests` - HTTP 請求庫
- `openpyxl` - Excel 文件處理
- `tomli` - Python < 3.11 的 TOML 解析（3.11+ 內置）

## 許可

MIT License

## 貢獻

歡迎提交問題和改進建議！

---

**最後更新**：2026-04-24
