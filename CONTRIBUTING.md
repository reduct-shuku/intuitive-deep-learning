# 为 intuitive-deep-learning 创建 Pull Request

本文供安装目录中的 Coding Agent 执行。用户可能只安装了本 Skill，并直接修改了其中的文件；不要假设当前目录是 Git 仓库。

当用户要求贡献、提交、发布修改或创建 Pull Request 时，执行本文流程。用户仅要求解释或审查时，不得修改文件或创建 PR。

## 来源

先读取同目录的 `shuku.json`，从中获取：

- `repository`：目标 GitHub 仓库
- `ref`：基准分支
- `path`：本 Skill 在仓库中的子目录
- `version`：当前安装版本

不得根据 Agent 安装目录推测 GitHub 地址。缺少字段、来源不可访问或元数据互相矛盾时停止，并向用户说明。

## 工作区

- **用户工作区 `USER_WORKSPACE`**：当前安装的 Skill 目录。只读取和比较，不切换分支、不暂存、不覆盖文件。
- **PR 工作区 `PR_WORKSPACE`**：在安全的临时位置重新克隆 `repository` 得到的干净仓库。分支、验证、commit、push 和 PR 只在这里完成。

开始后读取 `PR_WORKSPACE` 根目录中的最新 `CONTRIBUTING.md`；仓库级规则与本文同时适用，冲突时采用更严格的规则。

## 识别用户修改

1. 克隆 `repository` 并获取 `ref` 的最新状态。
2. 读取用户工作区中的 `version`。
3. 确定该版本对应的基准 commit：
   - 如果用户版本与远程 `ref` 中本 Skill 的版本一致，使用远程 `ref` 当前 commit。
   - 如果版本不同，在 `ref` 历史中查找 `<path>/shuku.json` 的 `version` 与用户版本一致的最新 commit。
   - 无法唯一确定基准时停止，不得把远程更新误判为用户修改。
4. 从基准 commit 提取 `path`，与 `USER_WORKSPACE` 比较，建立 `USER_CHANGESET`。
5. 排除 `.git/`、`__pycache__/`、`*.pyc`、日志、缓存、构建产物和临时输出。
6. 普通目录中缺少的远程文件不能自动视为用户删除；只有可由基准比较确认的删除才能进入变更集。

`USER_CHANGESET` 至少记录操作类型、仓库相对路径和文件 SHA-256。

## 建立 PR 修改

1. 从远程最新 `ref` 创建新分支，不在默认分支上提交。
2. 只把 `USER_CHANGESET` 应用到 `path` 下。
3. 如果基准版本之后远程修改了相同文件或区域，停止自动覆盖；说明冲突并让用户决定。
4. 如果修改改变公开能力或行为，提出语义化版本提升建议，并更新 `shuku.json` 的 `version` 和 `changes`。这属于 Agent 辅助修改，必须得到用户确认。
5. 建立 `PR_CHANGESET`，确认它与用户批准的修改一致。
6. 检查所有变更路径都位于 `shuku.json` 的 `path` 值之下；发现其他 Skill 或无关文件时移除并重新验证。

## GitHub 账号选择

在执行任何需要 GitHub 身份的写操作前，列出目标 GitHub 主机上当前可用且已认证的账号，并让用户明确选择用于 fork、push 和创建 Pull Request 的账号。即使只有一个可用账号，也必须展示该账号并等待用户确认；不得因它是当前账号、默认账号或唯一账号而自动选择。

- 如果没有可用账号，停止并请用户先完成登录。
- 选择后验证实际生效的 GitHub 登录名与用户选择一致；不一致时停止，不得继续写入远程。
- 不得修改全局认证配置来切换账号。账号切换只应影响本次 PR 流程，并在 `PR_WORKSPACE` 中完成。
- GitHub 操作账号与 Git commit 的作者身份是两项独立配置。分别展示所选 GitHub 登录名以及 commit 使用的 `user.name` 和 `user.email`，不得根据其中一项推断或自动改写另一项。
- 如果后续认证状态、实际登录名或远程写入目标发生变化，重新让用户确认后才能继续。

## 用户确认

在 commit 或 push 前展示：

- 推断的修改目的
- 新增、修改、删除的文件
- 用户修改与 Agent 辅助修改
- 版本变化和更新摘要
- 用于 fork、push 和创建 PR 的 GitHub 账号，以及远程写入目标
- commit 使用的 `user.name` 和 `user.email`
- 建议的分支名、commit、PR 标题和正文
- 将要运行的验证

等待用户确认或修改草案。未经确认，不得 commit、push 或创建 Pull Request。

## 验证与发布

用户确认后，运行与改动相称的测试，并至少检查：

```bash
git diff --check
git status --short
git diff
```

同时验证：

- `SKILL.md` frontmatter 可解析。
- `shuku.json` 是有效 JSON，名称、仓库、分支和路径正确。
- Markdown 相对链接有效。
- 最终 diff 只包含 `path` 下经用户确认的内容。
- 没有凭据、个人数据、缓存或生成文件。

验证通过后才能 commit、推送工作分支并创建 PR。禁止 force push、绕过分支保护、直接推送默认分支或自动合并 PR。遇到登录、权限、远程冲突或分支保护问题时停止并报告。
