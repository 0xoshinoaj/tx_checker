# 更新日誌

## [1.3.0] - 2026-04-25

### 新增功能
- 新增 `test_rpc.py`，可獨立測試 `config.toml` 中所有 RPC 的可用性、回應時間與區塊高度。
- 主程式新增缺檔互動建立流程：若 `import_file` / `proxy_file` 不存在，可詢問是否由 `addresses-Sample.txt` / `proxy-Sample.txt` 複製建立。

### 改進
- 新增 `debug` 模式切換：`true` 顯示完整錯誤，`false` 顯示精簡錯誤訊息。
- 錯誤與結果輸出加入終端顏色標記（紅/黃/綠），提升可讀性。
- 新增失敗地址分輪重試機制：後續輪次只重試失敗地址，直到成功或達到設定條件。
- 新增重試相關配置：`retry_delay_seconds`、`retry_failed_wallets`、`retry_until_all_success`、`max_retry_rounds`、`retry_round_delay`。
- 輸出檔改為統一寫入 `output/`，資料夾不存在時自動建立。
- 輸出檔命名改為 `tx_results_YYYYMMDD_HHMMSS`。
- CSV 輸出改為兩欄格式：`地址`、`交易數`。

## [1.2.0] - 2026-04-24

### 新增功能
- 配置文件改為讀取 `config.toml`，移除 `config.py` 流程。
- 支持多個區塊鏈網路（Ethereum、BSC、Polygon、Arbitrum、Optimism 等）
- 支持自訂 RPC 端點並可自行添加更多網路

### 改進
- 新增 Python 3.9+ TOML 相容支持（3.11+ 用 `tomllib`，舊版使用 `tomli`）
- 使用隨機選擇的 RPC 節點進行查詢，提高穩定性
- 改善輸出格式配置，支持 JSON、CSV、XLSX 多格式輸出
- 增強代理支持系統（rotate/random 輪換策略）
- 優化批量查詢功能與並行查詢性能

## [1.1.0] - 2025-10-21

### 新增功能
- 完整的代理支持系統
  - 支持多個代理輪換（rotate/random）
  - 代理 IP:Port:Username:Password 格式
  - 智能代理故障轉移

- **分批查詢功能**
  - `BATCH_SIZE` - 可配置每批查詢的地址數
  - `BATCH_DELAY` - 批次間延遲時間
  - 均勻分散負擔，避免 RPC 速率限制
  - 支持大規模地址批量查詢（100+ 個地址）

- **並行查詢功能**（性能提升）
  - `CONCURRENT_REQUESTS` - 每批內的並行查詢數
  - 使用多線程同時發送多個 RPC 請求
  - 查詢速度提升 5-10 倍
  - 結果實時顯示，不再卡頓

- **多格式輸出**（新增）
  - 支持同時輸出 JSON、CSV、XLSX 格式
  - 一鍵生成多種數據格式

### 改進
- **優化日誌輸出** - 代理重試時不再顯示中間信息
  - 只在所有重試都失敗後才顯示錯誤
  - 輸出更清爽，不被重試消息污染
  - 成功查詢立即顯示結果

- **增強重試機制**
  - 支持可配置的重試次數（`PROXY_RETRY_TIMES`）
  - 支持代理失敗後直接連接（`PROXY_FALLBACK_NO_PROXY`）
  - 自動統計代理錯誤次數

## [1.0.0] - 2025-10-21

### 初始版本
- 支持多個區塊鏈網絡
- 批量查詢功能
- JSON 結果導出
