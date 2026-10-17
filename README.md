# American Corporate Headshot / LinkedIn 商务头像 Skill

用本人自拍或半身照制作自然、可信、有棚拍质感的美式职业头像。适用于 LinkedIn、求职简历、个人网站等场景，提供五种摄影与着装预设。

项目包含可直接加载的 [SKILL.md](SKILL.md)、英文编辑模板、工具适配说明、视觉质检清单，以及一个无需第三方依赖的离线提示词生成器。它不捆绑图像模型，也不承诺零瑕疵或求职结果。

## 先弄清模型能力

**能看图、只能输出文字的视觉模型，不能独立生成照片。Skill 不能创造工具能力。**

- **Image Edit**：视觉模型分析照片，调用已授权的参考图编辑工具，再检查真实返回的图片，并在预算内修复。
- **Prompt Studio**：模型能看照片但没有编辑工具时，输出完整英文编辑提示词、负面约束和使用方法。用户将照片与提示词一起交给支持参考图编辑的图像工具。

如果连原图也看不到，只能给标记清楚的通用模板。仅有从文字生图能力不够，不能用新造的人脸冒充本人。图片生成后也不能因为接口成功就声称已完成视觉质检。

## 五种预设

| ID | 风格 | 摄影与着装方向 |
| --- | --- | --- |
| `classic-linkedin` | Classic LinkedIn Corporate | 默认通用；浅暖灰、简洁西装、自然微笑 |
| `wall-street-finance` | Wall Street / Finance | 深灰或蓝灰、深色正装、克制表情 |
| `consulting-mbb` | Consulting / MBB Polished | 干净暖灰、正式而温和、明亮柔光 |
| `big-tech-startup` | Big Tech / Startup Professional | 明亮背景、smart casual、放松自然 |
| `graduate-analyst` | Graduate / Analyst | 清爽、合身正装、友好表情 |

预设不会改变本人年龄、肤色、五官或身份表达。“MBB”“Wall Street”等名称只描述视觉方向，不表示所属机构、真实职级或学历。服装可按用户偏好调整，默认保留眼镜、宗教服饰、辅助设备和永久身份特征。

## 直接使用 Skill

先安装 [Git](https://git-scm.com/downloads)，然后按使用的工具复制一条命令到终端运行。以下命令均适用于 Windows PowerShell、macOS 和 Linux 终端；如果目标目录已存在，Git 会停止，不覆盖已有安装。

### Codex 一键安装

```sh
git clone --depth 1 https://github.com/AdenXie/american-corporate-headshot.git "$HOME/.agents/skills/american-corporate-headshot"
```

安装到 Codex 的用户级 Skill 目录，可在本机不同项目中使用；目录依据 [Codex 官方 Skill 说明](https://learn.chatgpt.com/docs/build-skills)。安装后若未出现，重新打开 Codex 会话，在 Skill 选择器中选择或输入 `$american-corporate-headshot`。

### Claude Code 一键安装

```sh
git clone --depth 1 https://github.com/AdenXie/american-corporate-headshot.git "$HOME/.claude/skills/american-corporate-headshot"
```

安装到 Claude Code 的用户级 Skill 目录，可在本机项目中使用；目录依据 [Claude Code 官方 Skill 说明](https://code.claude.com/docs/en/skills)。安装后输入 `/american-corporate-headshot`，若未出现则重新打开会话。这种本地安装不自动同步到云端会话。

### 开始制作头像

上传清晰的本人照片，然后说明用途、风格和允许修改的范围。例如在 Codex 中：

```text
使用 $american-corporate-headshot。照片是我本人，用于 LinkedIn 和金融实习申请。
请选择 Finance 风格，保留眼镜、不打领带、保持本人年龄。
先检查你能否查看原图、使用参考图编辑工具并查看结果。
工具和已有授权允许时，最多三张候选和两次修复；没有编辑工具就交付英文提示词。
```

Claude Code 中把首句改为 `/american-corporate-headshot`，其余要求可以照用。其他支持目录式 Skill 的宿主可加载整个仓库，保留相对路径；没有 Skill 安装机制时，提供 `SKILL.md` 及其引用的相关文件。

安装仅提供指令、模板和离线生成器，不会增加图像工具。Claude Code 或其他环境若只能看图并输出文字，就按 Prompt Studio 流程交付英文提示词；只有接入参考图编辑工具后才能生成本人头像。

## 离线 Prompt Studio 快速开始

需要 Python 3.10 或以上；仅用标准库，无需 API key。命令从仓库根目录运行。

```bash
python scripts/prompt_studio.py --list-styles
python scripts/prompt_studio.py --request examples/request.json --capabilities examples/capabilities/vision-only.json --out runs/plan.json
python scripts/prompt_studio.py --request examples/request.json --capabilities examples/capabilities/vision-only.json --format prompt --out runs/edit-prompt.txt
python -m unittest discover -s tests -v
```

`--out` 拒绝覆盖已有文件，重新运行时使用新文件名。JSON 输出包含模式、状态、完整提示词、候选提示词、预算和未执行声明；`--format prompt` 输出一份主提示词。默认三张候选为所选风格两张、相邻风格一张，第三张使用自己的完整风格提示词。

示例请求的 `source_reviewed` 和 `provider_processing_authorized` 均为 false，所以默认输出会等待原图分析，而不会声称执行条件已满足。实际使用时把请求复制到 `private/`，由能够看图的模型据实填写 `identity_notes` 和已看图状态；授权字段仅在真实授权覆盖目标服务时设为 true。`references` 是附件标签，不会自动加载文件。

能力文件同样由宿主检查工具后据实填写；示例能力文件不会发现或启用任何工具。未知布尔能力默认为 false，不接受字符串 `"true"`。生成器不读取照片、不联网、不调用编辑 API、不做图像质检。它的可运行范围是提示词组装与执行计划。

## 项目结构

```text
american-corporate-headshot/
  SKILL.md                       核心指令与双模式流程
  README.md                      使用与安装说明
  LICENSE                        AGPL-3.0 完整许可证
  agents/openai.yaml              可选的 Codex 展示元数据
  styles/presets.json             五种预设与相邻风格
  prompts/                       主编辑、负面约束、局部修复模板
  references/                    工具适配、质量审查、隐私授权
  examples/                      完整工作流、请求、能力示例、验收场景
  scripts/prompt_studio.py        离线提示词生成器
  tests/test_prompt_studio.py     路由、预算、输出状态与 CLI 测试
  .github/workflows/validate.yml  Windows / Linux 离线检查
```

## 质量与隐私

身份相似度优先，保留自然皮肤纹理与真实左右差异；审查五官、牙齿、耳朵、发际线、眼镜、领口、西装、光线、背景和头像裁切。方形 1024×1024 母图与约 96 px 圆形预览是建议工作尺寸，不是平台官方规格。

默认全任务最多五次图像调用，包括最多三次初始编辑和两次修复；失败提交也计数。遵守用户更小的预算。身份持续漂移、原图不清楚或预算耗尽时停止。详细规则见 [质量审查](references/quality-review.md)。无法 100% 保证零瑕疵，最终由本人确认是否像自己及是否适合使用。

原图、成品和私人任务记录不得提交 Git。仓库已忽略常见图片、`private/`、`inputs/`、`outputs/`、`runs/` 和 `.env`，但忽略规则不能清理已经提交的历史。发送照片到外部服务前，说明服务与用途，遵循已有授权。见 [隐私与授权](references/privacy.md)。

本版不含用户照片或真实生成样张，尚未做真实人物图片的端到端视觉验证。离线测试只能验证程序行为，不能证明人物身份一致或生成质量。想查看五种风格的真实效果，需要本人参考图和已授权的图像编辑环境。

## English overview

An identity-preserving corporate headshot skill with five style presets, reference-image editing workflows, visual QA, bounded repairs, and a vision-only Prompt Studio fallback. A vision model that only outputs text cannot produce images without an image tool. The included Python CLI is an offline prompt and plan composer, not an image generator. Keep personal photos out of Git and have the subject approve the final likeness.

## 开源许可证

Copyright (C) 2026 AdenXie。项目采用 [GNU Affero General Public License v3.0](LICENSE)，SPDX 标识为 `AGPL-3.0-only`。许可证适用于本仓库的代码、Skill 指令、提示词模板和文档；完整条款见 `LICENSE`。
