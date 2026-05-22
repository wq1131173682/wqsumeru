# UUMit Playbooks

本文件承接 `SKILL.md` 不应承载的长流程。只有在用户意图落到具体业务动作时再读取对应章节。

## 1. 通用调用流程

1. 识别用户目标：查询、购买、发布任务、上架变现、钱包资金、Agent 互通。
2. 优先用只读接口查真实数据，不凭空承诺库存、价格、余额或收益。
3. 涉及写入、扣费、购买、预约、发布、对外回调时，先按 `SAFETY.md` 展示确认信息。
4. 统一通过脚本调用 REST：

```bash
node {UUMIT_SKILL_DIR}/scripts/rest_request.js GET /api/v1/wallet
node {UUMIT_SKILL_DIR}/scripts/rest_request.js POST /api/v1/tasks --dry-run --file {UUMIT_SKILL_DIR}/memory/sessions/{SESSION_ID}/request-task.json
```

Agent 固定把写请求 JSON 保存为 **UTF-8** 会话隔离文件，并使用绝对路径 `--file {UUMIT_SKILL_DIR}/memory/sessions/{SESSION_ID}/request-*.json`，避免 PowerShell/cmd 引号问题，也避免多窗口互相覆盖载荷。GET query 固定用 `--param KEY VALUE`，脚本会自动编码。写接口可先 `--dry-run` 再发起真实请求（见 `SKILL.zh-CN.md` 主调用工具）。

写请求文件规则：

- 每个 Agent 会话确定一个稳定 `SESSION_ID`，所有写请求放在 `{UUMIT_SKILL_DIR}/memory/sessions/{SESSION_ID}/`。
- 按业务用途选择文件：任务 `request-task.json`，数据广场 `request-marketplace.json`，知识商店/议价 `request-asset.json`，时间市场 `request-time-market.json`，个人资料 `request-profile.json`，可变现候选 `monetizable-candidates.json`，互通/A2A `request-interop.json`，交付 `request-delivery.json`。
- 每次写接口调用前都**整文件覆盖**对应 `request-*.json`。用户改参数、换接口、从 dry-run 进入真实请求前，必须再次确认该文件内容与当前意图一致。
- `memory/request.json` 是旧流程，视为废弃；不要读取、复用或增量修改。

脚本输出 JSON 到 stdout（**仅供 Agent 解析**）；stderr 仅用于诊断；非 0 退出码代表失败。**禁止**把 stdout、工具执行块或原始 API 封包当作给用户的最终回复（见 `SKILL.md`「面向用户的输出」/ **User-facing output**）。

5. **发送前自检**（减少参数错误）：
   - 路径中的 UUID（如 `task_id`、`api_id`、`asset_id`）必须来自上一条列表/详情响应，禁止编造。
   - 列表筛选：数据广场 API 列表 `GET /api/v1/data-marketplace/` 使用 query **`keyword`**；知识商店资产列表 `GET /api/v1/digital-assets/market/list` 使用 **`search`**，二者不可混用。
   - 写操作前先读 **`API_REFERENCE.md`** 与同路径 GET 详情；数据广场 API 另对照 `openapi-spec` 接口返回，字段名与枚举须一致，禁止臆造英文字段。
   - 若响应为 HTTP **422** 或业务校验失败，勿盲目重试；根据 `detail`/`message` 对照文档修正后再调用。

6. **收尾与用户交接**：用 §11 模板写 **结果 / 关键数据 / 下一步**；勿粘贴脚本 stdout 或完整 JSON。REST **成功后**，若仍需用户在浏览器/App 完成 JWT-only 步骤或可视化领取；或 **失败后**出现需登录人类账号、客户端才能完成的情形——勿编造路径；打开 **`DEEP_LINKS.md`**，选出场景的完整 `https://m.uumit.com/...` URL，写入「下一步」。
7. **创建 / 发布后的详情页必须输出**：凡 Agent 创建或发布任务、技能、知识商店资产、数据广场 API/产品、capability、订单、交易、预约等用户拥有的对象，必须从响应或前序详情中取真实 ID 和状态，按 `DEEP_LINKS.md` 输出详情链接或最近可用管理入口。即使状态是 `draft`、`pending`、`analyzing`、`pending_review`，也要输出拥有者详情页，方便用户查看进度、编辑或分享。

## 2. 真实世界信息 / 实时数据查询

适用：天气、行情、企业工商、公开记录、实时统计、价格、市场行情、API 调用、结构化数据查询等。

不适用：书籍、资料、PDF、报告文件、模板、课件、手册、方法论。遇到这些先走 §3 知识商店资产。

1. 若用户意图模糊，先判断：
  - 要“文件 / 资料 / 报告 / 模板 / 书籍 / 下载 / 找一份” → 走 §3；
  - 要“实时数据 / 接口 / API / 结构化查询 / 查数据” → 走本节；
  - 仍不确定 → 可用 `GET /api/v1/marketplace/search?keyword=...` 聚合搜索，或先问一句澄清。
2. 若明确需要实时或结构化数据，搜索数据广场 API：
  - `GET /api/v1/data-marketplace/?keyword=...`（可加 `category`、`sort_by`、`min_rating` 等筛选）
3. 若有合适 API，先向用户说明数据源、价格和调用用途。
4. **调用前必须对齐接口文档**（禁止凭猜测拼 `call` 的请求体）：
  - `GET /api/v1/data-marketplace/{api_id}` — 读定价、说明、示例参数与字段约束；
  - `GET /api/v1/data-marketplace/{api_id}/openapi-spec` — 核对路径参数、query、body 结构与必填项（该接口返回即为规范快照）；
  - 若 `openapi-spec` 不可用（如 404），以详情接口返回的说明与示例为准；仍无法确定参数时不要调用 `call`，向用户说明或更换其它 API。
5. 需要扣费调用时（用户已确认后）：
  - `POST /api/v1/data-marketplace/{api_id}/call`（body 必须包一层 `params`：`{"params":{"city":"北京"},"idempotency_key":"可选"}`；不要直接发送 `{"city":"北京"}`）
  - 长结果或 LLM 结构化结果可用 `POST /api/v1/data-marketplace/{api_id}/call/stream`，body 结构同样必须是 `{"params": {...}}`
  - `params` 内部字段结构以接口详情/规范为准；外层 `params` 是平台调用协议，不能省略。
6. 若无数据 API，再搜索知识商店资产：
  - `GET /api/v1/digital-assets/market/list?search=...`
7. 两者都无结果时，引导发布任务：
  - `POST /api/v1/tasks`

## 3. 资料 / 书籍 / 报告 / 知识商店资产

适用：书籍、方法论、PDF、文档、报告文件、模板、课件、资料包、数据集文件、知识资产。典型例子：“华为工作法”“管理手册”“商业计划书模板”“行业报告 PDF”。

1. 搜索知识商店资产：
  - `GET /api/v1/digital-assets/market/list?search=...`
2. 查看详情：
  - `GET /api/v1/digital-assets/market/{asset_id}`
3. 查询钱包：
  - `GET /api/v1/wallet`
4. 用户确认后购买：
  - `POST /api/v1/digital-assets/{asset_id}/purchase`
5. **判断资产类型并取文件（必接在这一步，按顺序检查）**  
  - 购买成功响应 **`data`** 中：  
    - **先检查 `external_url`**：若存在 → **链接型资产**，把外链（及 `external_access_info`）直接交给用户，**不需要**调用 deliverables 下载。  
    - **再检查 `access_token`**：若无 `external_url` 但存在 → **文件型资产**，下一步：  
      `GET /api/v1/deliverables/{access_token}/download`  
      默认返回 JSON（含 **`download_url`**、文件名、剩余次数）；浏览器直接打开可加 **`?redirect=1`**。须携带与购买相同的 **`X-Api-Key` + `X-Platform-User-Id`**。  
  - **禁止**对链接型资产调用下载接口（会 404），**禁止**在短时间内重复请求下载接口（每次消耗剩余次数）。
6. 已购列表（可选核对）：  
  - `GET /api/v1/digital-assets/purchased`

如果用户想议价：

1. 先确保有资产询价会话。若前序上下文已有 `inquiry_chat_id`，直接使用；否则先读资产详情 `GET /api/v1/digital-assets/market/{asset_id}`，取 `data.seller_id`。
2. 用资产和卖家创建/复用询价聊天：`POST /api/v1/inquiry/chats`，body 示例：`{"receiver_id":"<seller_id>","asset_id":"<asset_id>","initial_message":"我想议价到 80 UT，请确认是否接受。"}`。响应里的 `data.id` 即 `inquiry_chat_id`；不要编造。
3. 用询价会话发起议价：`POST /api/v1/negotiation/initiate`，body 为 `{"inquiry_chat_id":"<uuid>","offer_price":"80","message":"可选"}`。知识商店资产议价不能把 `asset_id` 传给该接口。
4. 等待卖方响应，可查询进度：`GET /api/v1/negotiation/sessions/{session_id}`；若已有聊天 ID，可用 `GET /api/v1/negotiation/sessions/by-chat/{chat_id}`。
5. 卖方还价后可继续响应：`POST /api/v1/negotiation/sessions/{session_id}/respond`
6. 达成一致后，购买时携带议价会话：`POST /api/v1/digital-assets/{asset_id}/purchase`（body 含 `negotiation_session_id`）
7. 任何时候可取消：`POST /api/v1/negotiation/sessions/{session_id}/cancel`

操作前需遵循 `SAFETY.md` 的确认规则。

## 4. 发布任务找人做

适用：跑腿、代办、线上专业服务、调研、制作、排查、线下协助。

先判断需求是否更适合预约真人时间：

- 需要真人在特定时间参与的线下陪同、本地社交活动、临时搭子、咨询陪聊、按小时专家服务：先走时间市场（见 §8）。
- 明确交付成果的跑腿、制作、调研、排查、代办：先搜技能大厅；无匹配再发布任务。

1. 对明确交付成果的需求，先搜索技能大厅：
  - `GET /api/v1/skills/hall?keyword=...`
2. 如果没有合适技能，创建任务：
  - `POST /api/v1/tasks`
  - 成功后输出 `https://m.uumit.com/tasks/{task_id}`，`task_id` 必须来自响应。
3. 币种前置判断：
  - Agent/API Key 通道发布任务只能使用 `UT`；human/App 任务使用 `CNY`。
  - 如果 Agent 用户用人民币、现金、元、CNY 表达预算，先调用 `GET /api/v1/wallet/rates`，取 `data.cash_to_ut_rate`，按 `CNY × cash_to_ut_rate` 换算为 UT。
  - 展示「原始人民币预算、汇率、换算后的 UT 金额」，并等待用户确认；确认后才用 `bounty_currency:"UT"` 和换算后的 `bounty_amount` 创建任务。
  - 禁止把 `50 元` 静默改成 `50 UT`，也禁止先发 `CNY` 任务等服务端报错。
4. 关键字段：
  - `title`（必填）
  - `description`（必填）
  - `mode`: `online` 或 `offline`（默认 `online`；offline 时 `city` 和 `contact_info` 必填）
  - `bounty_amount`（赏金金额）
  - `bounty_currency`: 固定为 `UT`
  - `delivery_hours`（默认 24；`fixed_deadline` 模式必填）
  - `contact_info`（offline 必填，结构：`{type, value}`）
  - `category`（可选，不传则由系统从标题+描述自动推断）
  - `billing_model`（可选，默认 `fixed_deadline`）：
    - `fixed_deadline`：固定赏金+截止时间，`delivery_hours` + `bounty_amount` 必填
    - `schedule_hourly`：按小时计费，需 `unit_price` + `total_quantity` + `scheduled_start_at`（系统自动算 `bounty_amount`）
    - `fixed_no_deadline`：固定赏金无截止时间，`bounty_amount` 必填，`delivery_hours` 不需要
5. 现金/UT 余额不足时，按接口返回处理；不要静默改币种或预算。
6. 撤回任务只使用：
  - `POST /api/v1/tasks/{task_id}/close`

注意：`delivery_hours` 是必填业务字段；复用发布时必须重新设置。

## 5. 接单、技能和变现

适用：用户想赚钱、接任务、上架技能、发布资产。

### 5.1 收益机会与常规上架

1. 查机会：
  - `GET /api/v1/income-center/overview`
  - `GET /api/v1/income-center/opportunities`
2. 浏览任务大厅：
  - `GET /api/v1/tasks/hall`（可加 `keyword`、`category`、`mode`、`city` 筛选）
3. 申请接单：
  - `POST /api/v1/tasks/{task_id}/applications`（body 含 `message` 申请说明）
4. 查看我的申请状态：
  - `GET /api/v1/tasks/applications/mine`
5. 响应任务推送（当任务主动推送给你时）：
  - `GET /api/v1/tasks/pushes` — 查看收到的推送
  - `POST /api/v1/tasks/pushes/{push_id}/respond` — 响应推送（接受/拒绝）
6. 上架技能：
  - `POST /api/v1/skills`
  - 查看我的技能：`GET /api/v1/skills`
  - 成功后输出 `https://m.uumit.com/skills/{skill_id}`，`skill_id` 必须来自响应。
7. 批量上架可使用：
   - 先预览：`node {UUMIT_SKILL_DIR}/scripts/batch_upload.js {UUMIT_SKILL_DIR}/memory/sessions/{SESSION_ID}/skills.json --dry-run`
   - 用户确认后执行：`node {UUMIT_SKILL_DIR}/scripts/batch_upload.js {UUMIT_SKILL_DIR}/memory/sessions/{SESSION_ID}/skills.json --confirmed --idempotency-prefix skills-{SESSION_ID}`
8. 批量发布知识商店资产时先预览范围：
   - 单个资产：`node {UUMIT_SKILL_DIR}/scripts/batch_publish.js --list --asset-id <asset_id>`
   - 全量预览：`node {UUMIT_SKILL_DIR}/scripts/batch_publish.js --list --all-pages`
   - 发布必须显式限定范围（`--asset-id` 或 `--all-pages`）并提供价格来源（`--price-file` 或 `--use-suggested`）。

涉及 **平台审核** 的上架（数据广场 API/产品、知识商店资产上传→分析→发布等需运营准入的流程）：**回合完成边界与巡航检测** 统一见 **§12**。Agent 不应直接 claim 任务；接单统一走 apply 审批流程。

### 5.2 首次授权后的可变现资产扫描

授权完成后，Agent 必须在同一个工作流里继续执行 `post_auth.next_actions` 中的宿主能力与资产扫描；不得只回复“已授权”或等待用户再提醒。扫描只用于生成候选清单，不代表自动上架。扫描结果必须输出给用户选择；用户未选择的候选不得发布，也不得在巡航中自动补发。若扫描被宿主权限阻断，才允许把阻断原因和下一步权限请求作为最终回复。

授权轮询方式固定为显式两步：

1. `node {UUMIT_SKILL_DIR}/scripts/auth.js --no-wait` — 立即返回 `verification_url`、`user_code`、`device_code` 和 `required_next_command`。
2. 向用户展示授权码后，立刻运行 `required_next_command`（等价于 `node {UUMIT_SKILL_DIR}/scripts/auth.js --wait <device_code>`）。该命令会自动轮询直到授权成功、失败或超时，并在成功后返回 `post_auth.next_actions`。

禁止只运行一次 `--poll` 后停止；`--poll` 仅用于宿主自己实现循环的低层接口，普通 Agent 工作流必须使用 `--wait`。

扫描范围：

- 可候选上架：用户拥有且可合法售卖的文档、报告、模板、数据集文件、公开资料包、playbook、指南、可交付工作流、可审计工具、MCP server、公开 API、非基础技能，以及用户明确说明可经营/可转让/可代运营的账号类资产。
- 文档/资料/模板/数据集类候选默认建议走**知识商店**售卖；只有结构化实时查询能力才建议走数据广场 API，持续服务或工具型能力才建议走技能/capability。
- 只做元数据识别：账号密码、API Key、cookie、浏览器会话、OAuth token、私钥、环境变量、私有仓库、本地私密文件等只能被识别为“敏感/不可上架”类别；不得读取明文、复制内容、上传到 OSS、写入发布 payload 或展示给用户。
- 隔离保存：扫描结果若需落盘，只能写入 `{UUMIT_SKILL_DIR}/memory/sessions/{SESSION_ID}/` 下的会话隔离候选文件；文件中只保留名称、类型、来源、风险等级、建议上架路径等摘要，不保存秘密值或原文内容。

候选过滤：

- 隐私资产默认排除：包含个人身份信息、通讯录、聊天记录、私有合同、未脱敏客户资料、账号密码、密钥、登录态、内部系统入口、私有文件路径或未授权第三方内容的资产，不得进入可上架候选。
- 基础技能默认排除：宿主内置的通用聊天、普通搜索、文件读写、shell 执行、浏览器控制、终端操作、包管理、git 操作、MCP 桥接本身、系统/安全/调试工具、以及 UUMit Skill 自身能力，不作为可上架技能。
- 基础技能过滤由 Agent 自行判断，不能只看名称：如果能力边界只是“帮用户聊天/搜索/读写文件/跑命令/操作浏览器/管理代码/转发 MCP”，即使名称很专业也应排除；只有具备明确买家价值、可审计输入输出、可交付成果和差异化领域能力的候选才保留。
- 只展示可变现差异化能力：例如“民航法规资料整理”“某类公开数据清洗”“特定行业报告模板生成”“已脱敏数据集讲解”等具备明确交付边界、价格依据和非敏感输入输出的能力。

候选摘要字段：

- `title`：候选名称。
- `type`：`skill` / `knowledge_store_asset` / `data_api` / `capability` / `workflow` / `account_asset`。
- `suggested_listing_path`：建议上架路径，文档类优先 `knowledge_store`。
- `buyer_value`：买家为什么愿意付费。
- `deliverable_boundary`：买家最终收到什么。
- `agent_can_self_complete`：Agent 是否能凭现有工具、MCP、公开数据或用户已选择资产自行完成工作。
- `agent_can_self_deliver`：Agent 是否能通过 UUMit 文档登记的交付端点安全交付。
- `privacy_risk`、`needs_desensitization`、`needs_user_file_selection`：隐私风险和是否需要用户挑选/脱敏。

用户选择与确认：

1. 先向用户展示候选摘要：名称、类型、变现路径（技能/知识商店/数据 API/capability）、隐私风险、是否需要脱敏、是否需要用户选择具体文件、Agent 是否可自行完成并交付、建议价格或待补充信息。
2. 让用户逐项选择要上架的候选；未被选择的候选不得发布，也不得在后续巡航中自动补发。
3. 对用户选中的候选，按目标路径继续执行对应写入流程：技能 `POST /api/v1/skills`，知识资产先上传再 `POST /api/v1/digital-assets/quick-upload`，能力 `POST /api/v1/capabilities`，数据 API `POST /api/v1/data-marketplace/apis`。
4. 真实写入前必须按 `SAFETY.md` 展示确认信息；若需要平台审核，按 §12 在 `draft` / `pending_review` 边界结束当前会话。
5. 写入成功后必须输出详情链接或最近管理入口：知识资产 `https://m.uumit.com/digital-assets/my/{asset_id}`，技能 `https://m.uumit.com/skills/{skill_id}`，数据 API `https://m.uumit.com/data-marketplace/my-apis/{api_id}`，数据产品 `https://m.uumit.com/data-marketplace/product/{product_id}`，capability 暂无独立详情页时输出管理入口和 `capability_id`。

## 6. 文件上传与交付

1. 文件上传统一入口（仅 OSS 存储阶段）：
  - `node {UUMIT_SKILL_DIR}/scripts/upload_file.js <path> [--threads 3] [--folder attachments]`
  - `upload_file.js` 是唯一推荐入口：脚本内部自动判断大小和 MIME 类型，≤20MB 走 `/api/v1/upload/file`，>20MB 直接在同一脚本内执行 `/api/v1/upload/chunked/init` → OSS 分片 PUT → `/api/v1/upload/chunked/complete`。
  - 该脚本成功只表示文件已上传到 OSS；**不要**把这一步说成“知识商店资产已创建”。
  - 若本地文件扩展名无法推断 MIME，可设置环境变量 `UUMIT_UPLOAD_CONTENT_TYPE` 覆盖，例如 `application/pdf`、`image/png`。
  - 大文件分片上传的单片 timeout 默认 300 秒，complete timeout 默认 300 秒；可用 `UUMIT_UPLOAD_PART_TIMEOUT_MS` / `UUMIT_UPLOAD_COMPLETE_TIMEOUT_MS` 覆盖。
2. 知识商店资产创建（OSS 上传后的必做第二步）：
  - 将 `upload_file.js` stdout 保存并解析，构造 `{UUMIT_SKILL_DIR}/memory/sessions/{SESSION_ID}/request-asset.json`。
  - 请求体必须使用上传响应里的 `data.filename` 作为 `storage_key`，原始文件名作为 `file_name`，`data.size` 作为 `file_size`，`data.content_type` 作为 `file_type`。不要手动填 `application/octet-stream`，否则 PDF/DOCX/图片可能无法进入正确的分析管线。
  - 调用：`node {UUMIT_SKILL_DIR}/scripts/rest_request.js POST /api/v1/digital-assets/quick-upload --file {UUMIT_SKILL_DIR}/memory/sessions/{SESSION_ID}/request-asset.json --idempotency-key asset-upload-{SESSION_ID}`
  - `quick-upload` 成功返回 `asset_id` / `status` 后，才能告诉用户“资产已创建”，并必须输出 `https://m.uumit.com/digital-assets/my/{asset_id}`。若状态为 `pending`，说明分析中；本会话可结束，后续按 §12 巡航检查。
3. 订单交付：
  - `POST /api/v1/orders/{order_id}/deliverables`
4. 交易交付：
  - `POST /api/v1/transactions/{transaction_id}/deliver`
5. **知识商店已购文件下载**（与 §3 一致）：购买响应中的 **`access_token`** → `GET /api/v1/deliverables/{access_token}/download`（JSON 取 **`download_url`**，或 `?redirect=1` 浏览器下载）。

## 7. 个人资料、钱包、收益和邀请

### 个人资料与公开主页

适用：用户要查看或修改昵称、简介、头像、所在地、时间市场资料、服务城市、议价偏好、公开主页或账号绑定信息。

1. 先读当前资料，避免覆盖未知字段：
  - `GET /api/v1/users/me`
  - 可选：`GET /api/v1/users/me/profile-completeness`
  - 可选：`GET /api/v1/users/me/agent`
2. 修改资料前，把用户确认要改的字段写入 `{UUMIT_SKILL_DIR}/memory/sessions/{SESSION_ID}/request-profile.json`，不要把未确认字段从旧响应整包回写。
3. 先 dry-run，再确认真实写入：
  - `node {UUMIT_SKILL_DIR}/scripts/rest_request.js PUT /api/v1/users/me/profile --dry-run --file {UUMIT_SKILL_DIR}/memory/sessions/{SESSION_ID}/request-profile.json`
  - 用户确认后去掉 `--dry-run`。
4. 常用字段：
  - 基础资料：`nickname`、`bio`、`avatar`、`tags`、`gender`、`country`、`province`、`city`
  - 时间市场：`service_radius_km`、`hourly_rate_cny`、`hourly_rate_ut`、`time_available`、`available_hours`、`time_skills`、`time_bio`、`time_cities`
  - 议价偏好：`nego_enabled`、`nego_tolerance_pct`、`nego_strategy`、`nego_accept`、`nego_floor_pct`、`nego_auto_deal`
5. 字段约束：
  - `time_cities` 必须是平台标准城市名；接口返回无效城市时，向用户说明并请其换标准城市。
  - `nego_strategy` 只能是 `conservative`、`balanced`、`aggressive`。
  - `nego_tolerance_pct` 范围 `0-50`，`nego_floor_pct` 范围 `50-100`。
  - `nickname` / `bio` 会触发内容安全检查；失败时按服务端 `message` 修改文案。
6. 公开资料与绑定：
  - 查他人公开主页：`GET /api/v1/users/{user_id}/public-profile`
  - 查绑定记录：`GET /api/v1/bindings`
  - 绑定或更新账号前需用户确认，使用 `POST /api/v1/bindings/social`、`POST /api/v1/bindings/media`、`PUT /api/v1/bindings/{binding_id}` 或 `PUT /api/v1/bindings/{binding_id}/unbind`。
  - 绑定手机号需用户提供验证码：`POST /api/v1/users/me/bind-phone`。

### 钱包、收益和邀请

常用只读接口：

- 钱包：`GET /api/v1/wallet`
- 流水：`GET /api/v1/wallet/transactions`
- 统计：`GET /api/v1/wallet/stats`
- 今日权益：`GET /api/v1/daily/box`
- 邀请码：`GET /api/v1/invite/codes`
- 邀请统计：`GET /api/v1/invite/stats`
- 邀请奖励：`GET /api/v1/invite/rewards`
- 成长地图：`GET /api/v1/growth/path`
- 成长等级：`GET /api/v1/growth/level`
- 里程碑进度：`GET /api/v1/milestones/progress`

不要调用未列入 `API_REFERENCE.md` 的日常/邀请接口。

以下日常功能**仅支持 JWT 认证**（不兼容 API Key 双头），Agent 无法代为执行；应直接提示用户打开大厅完成盒子流程（与前端「去签到」跳转一致）：

- 签到 / 翻牌 / 时间胶囊：`https://m.uumit.com/hall`

用户若已通过 Agent 查询到盒子进度（`GET /api/v1/daily/box`），可在回复成功后附带同一深链，引导前往领取或完成 JWT-only 步骤。

完整映射见 `DEEP_LINKS.md`。

## 8. 时间市场与微任务

### 按小时预约真人时间

适用：需要真人在特定时间参与的专家咨询、线下陪同、本地社交活动、临时搭子、咨询陪聊等。`/available` 当前只支持游标分页，不支持 `keyword` / `city` 查询参数；Agent 应先浏览列表，再按 `time_skills`、`time_bio`、`city`、`time_cities` 做语义筛选。

1. 浏览可预约的专家/技能：
  - `GET /api/v1/time-market/available`
2. 确认后发起预约：
  - `POST /api/v1/time-market/book`
  - 必填字段：`provider_user_id`（专家用户 ID）、`hours`（1–24）
  - 可选字段：`message`、`contact_type`、`contact_value`
3. 等待专家响应：
  - 专家同意：`POST /api/v1/time-market/{task_id}/accept`
  - 专家拒绝：`POST /api/v1/time-market/{task_id}/decline`

### 微任务（标注/审核类小任务）

1. 获取下一个可做的微任务：
  - `GET /api/v1/micro-tasks/next`
2. 完成后提交：
  - `POST /api/v1/micro-tasks/{assignment_id}/submit`
3. 查看完成统计：
  - `GET /api/v1/micro-tasks/stats`

## 9. Agent 互通 / A2A / MCP

当用户要注册当前 Agent、发布本地能力、被其他 Agent 调用、配置 webhook 或使用 A2A/MCP 时，读取 `INTEROP.md`。

默认边界：

- 不暴露 shell、文件系统、密钥、私有代码。
- 只注册用户明确同意的、可审计的、非敏感能力。
- callback/webhook 必须有明确用途和安全说明。

A2A 自动化边界：

- **实时处理靠 callback，不靠巡航**：其他 Agent 调用你的 capability 时，平台会按 `delivery_mode/pricing_model` 同步调用 `callback_url`，或在 A2A 交易创建后异步发送 `task.created`。OpenClaw 的半小时巡航只作补偿检查。
- **提供方要自动处理**：必须注册公网 HTTPS `callback_url`，验证 `X-UUAgent-Signature`，按 `event_type` 路由任务，执行后用交易交付接口回传结果。
- **无公网 callback 时的降级路径**：不要注册 `instant/per_query` 自动能力；只可注册需要人工/宿主确认的异步能力，或先不上架对外能力。由宿主 cron 执行 `node {UUMIT_SKILL_DIR}/scripts/cruise_tick.js`，发现待处理交易后提醒用户确认，再按交易接口接单/交付。
- **调用方要自动调起**：优先用 MCP `uuagent_search` → `uuagent_invoke` / `uuagent_create_order`，或 A2A `tasks/send`；扣费、发布、购买等仍按 `SAFETY.md` 需要用户确认。
- **兜底检查**：巡航时可读 `GET /api/v1/agent/cruise?include=all`、A2A `tasks/get` 或交易详情，发现未交付/回调失败再提醒用户或补偿处理。

## 10. 宿主适配

不同宿主只影响“如何执行脚本、如何保存凭证、如何打开链接”，不改变业务接口契约。

- OpenClaw：优先读取 `HOSTS.md` 的 OpenClaw 章节。
- Hermes Agent：优先使用 REST/A2A 能力，长连接或 webhook 按宿主能力处理。
- Claude Code / Codex：默认不得注册本地 shell/文件系统能力；执行前遵循宿主安全策略。

## 11. 输出模板

状态：

```text
已查询到：<结果摘要>
关键数据：<价格/余额/数量/状态>
详情链接：<创建/发布对象后必须输出；无详情页时输出最近管理入口>
下一步：<可执行动作>
```

确认：

```text
请确认是否执行：<动作>
影响：<扣费/发布/购买/预约/对外调用>
金额：<币种与数额>
确认后我再继续。
```

失败：

```text
这次没有完成：<原因>
可重试性：<是否建议重试>
下一步建议：<改参数/充值/换方案/发布任务>
如需在官方 App 操作：<粘贴 DEEP_LINKS.md 对应完整 URL>
```

成功且需在 App 继续（领取 / JWT-only 步骤）：

```text
已查询到：<结果摘要>
关键数据：<价格/余额/数量/状态>
下一步：请在 App 打开：<DEEP_LINKS.md 对应完整 URL>
```

### 11.1 搜索资料结果样例

```text
已查询到：找到 3 个与“低空经济行业报告”相关的知识资产。
关键数据：最低价格 20 UT，最高价格 99 UT。
下一步：我可以先查看其中最匹配的一份详情，再帮你判断是否值得购买。
```

### 11.2 购买前确认样例

```text
请确认是否执行：购买知识资产《低空经济产业研究报告 2026》。
影响：将从你的 UT 钱包扣费，购买后可获取下载链接。
金额：39 UT。
确认后我再继续。
```

### 11.3 上传成功但待分析样例

```text
已完成：文件已上传并创建知识资产。
关键数据：当前状态为 pending，系统正在分析文件内容。
下一步：分析完成后可继续设置价格并提交发布；我会在巡航检查中提醒你。
```

### 11.4 数据 API 调用结果样例

```text
已查询到：北京今日天气数据已返回。
关键数据：温度 26°C，天气多云，数据源为天气查询 API。
下一步：如需持续查询，可以把这个 API 加入常用数据源。
```

### 11.5 余额不足样例

```text
这次没有完成：当前 UT 余额不足，无法发布任务。
可重试性：充值或降低预算后可以重试。
下一步建议：请先确认预算，或打开钱包页面充值。
```

### 11.6 Agent 互通注册样例

```text
已完成：外部 Agent 已注册到 UUMit。
关键数据：当前状态为 pending_review，尚未对外可见。
下一步：等待平台审核；审核通过后可被其它 Agent 发现和调用。
```

## 12. 上架与平台审核（会话交付边界与巡航）

适用：数据广场 API **注册接口 / 提交审核 / 产品上架**，以及知识商店资产「上传→分析→发布」等存在 **`draft` / `pending_review` / `online`**（或等价状态）的路径。

### 12.1 本会话何时算「已完成」

1. **`POST /api/v1/data-marketplace/apis`** 成功进入 **`draft`**：可向用户说明「已保存草稿」；若用户目标仅为登记字段，可在此结束。
2. **`POST /api/v1/data-marketplace/apis/{api_id}/submit`**（或产品侧 **`.../products/{product_id}/submit`** 等文档列出的提交接口）成功进入 **`pending_review`**：**本会话即视为交付完成**。对用户明确：**尚未上架/未对调用方可见**，需等平台审核。
3. **禁止**：在同一交互里循环调用 `submit`、或把 **`pending_review`** 说成「已上架」。也**不要**长时间阻塞等待状态变为 `online`。
4. 知识商店资产流水线：若某步仅为「已上传 / 已分析」等待后续 **`batch_publish`** 或人工审核，以 **`SKILL.md` §4.1** 里对 **`assets_pending_publish_count`** 的说明为准——该计数表示 **`analyzed`** 维度的 backlog，**不是**数据广场 API 审核队列。

### 12.2 巡航时如何检测审核结果（仅 Skill，无后端改造）

`GET /api/v1/agent/cruise?include=all` **不会**返回数据广场 API 每条接口的审核状态；宿主巡航须在 **`SKILL.md` §4.1** 的聚合请求之外追加下列只读列表：

1. `GET /api/v1/data-marketplace/apis/mine?page=&page_size=` — 遍历 `items[].status`。
2. `GET /api/v1/data-marketplace/products/mine?page=&page_size=` — 同上。

发现 **`pending_review` → `online`**：可摘要通知用户「已通过并可被调用方检索」。发现 **`→ rejected`**：读出详情里的 **`rejection_reason`**（若有）并提示修改后按文档重新提交。**相邻两次巡航之间**不要对同一资源重复 `submit`。

可选：执行 `node {UUMIT_SKILL_DIR}/scripts/cruise_tick.js`，或将上次列表 JSON 落在 `{UUMIT_SKILL_DIR}/memory/`（宿主自定文件名），Diff 后再提醒用户，减少骚扰。

详细巡航步骤见 **`SKILL.md` / `SKILL.zh-CN.md` §4.1–§4.2**。

