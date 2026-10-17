# 示例工作流

以下是流程演示，不含真实照片、实际图片调用或视觉质检结论。文中的观察需要在使用时由真实原图替换。

## A. 有视觉输入和参考图编辑工具

用户：“这是我的照片，用于金融实习申请。保留眼镜，不打领带，做三张。”

1. 实际看图，检查清晰度；记录可见轮廓、眼镜、发际线和原有表情。确定 Wall Street / Finance，用户偏好覆盖预设的可选领带。
2. 根据当前工具文档填写真实能力记录。照片将送往哪个服务、现有授权是否覆盖，均应在提交前清楚。先查预算，不自动启动额外付费服务。
3. 计划 C1、C2 为 Finance，C3 为 Classic；初始最多三次，修复最多两次，合计最多五次。用户若只同意两次调用，则只规划两张初始候选，不另加修复。
4. 用原图编辑。C2 若出现翻领粘连且身份相似，可使用修复模板只改翻领；如果 C3 明显换脸，拒绝推荐，不靠后期锐化掩盖。
5. 实际查看原图、成品、可用的圆形预览，逐项填写质检记录；只交付真实附件。最终由用户确认最像本人的一张。

配置方式：把 `examples/request.json` 复制到 `private/request.json`，只有实际看图后才填 `source_reviewed: true` 和真实的 `identity_notes`。授权覆盖目标服务时才将 `provider_processing_authorized` 设为 true。把示例能力记录复制到 `private/capabilities.json` 并替换为实际工具信息。

```bash
python scripts/prompt_studio.py --request private/request.json --capabilities private/capabilities.json --out runs/plan.json
```

这条命令只生成计划，不触发图片工具。宿主读取 `candidate_variants`，将每个完整提示词与原图映射到真实接口，逐张生成和质检。

## B. 只有视觉输入，没有图片输出工具

用户：“我能让你看照片，但你只能输出文字。做 Consulting 风格。”

实际看图后可交付下面这种完整提示词。此例没有原图可看，因此保留通用身份说明，不能当作已完成分析的真实案例。

```text
Edit the attached photo of me into a photorealistic professional head-and-shoulders portrait in the Consulting / MBB Polished style. Use my attached original as the sole authority for identity. Preserve my recognizable face shape, eye spacing, nose, lips, jawline, hairline, skin tone, actual apparent age, and natural asymmetry. Keep my glasses and permanent identifying marks where present. Do not infer or redesign details hidden in the reference.

Use an understated fitted blazer over a simple light shirt or blouse, a clean warm-gray seamless background, and a gentle natural smile. Keep the original expression if a broader smile would require inventing unseen teeth. Turn the shoulders slightly while keeping the face toward the lens and eyes looking at the camera. Use bright soft studio light with gentle facial depth and realistic catchlights, retaining natural pores and fine expression lines.

Compose one square portrait, ideally 1024 by 1024 pixels if supported, with the entire head, visible ears and chin comfortably inside a centered circular-avatar area. Leave breathing room above the hair and around the face; crop through shoulder margins instead of the head. Keep hands outside the frame. Return a single photograph without logos, text, borders or a collage.

Avoid identity drift, facial reshaping, skin whitening, age changes, forced symmetry, mismatched gaze, duplicated pupils, fused teeth, distorted ears or hairline, glasses merging with skin, waxy skin, melted collars or lapels, harsh dramatic shadows, overexposure, glamour filters, busy office scenery and fake company affiliation.
```

使用说明：

1. 在支持参考图编辑的图像工具上传同一原图，确认它已经进入编辑请求。
2. 将整段英文粘贴到编辑提示词中。此版本已合并负面约束；若工具有独立负面字段，可使用 `prompts/negative.txt`。
3. 先试一张，检查身份和五官，再考虑增加候选。参数只用该工具文档支持的选项，不凭空填写参考强度。
4. 将结果带回可看图的环境进行审查；若领口出现问题，再用以下修复语句，并同时附上原图和候选图。

```text
If inspection reveals a malformed collar: repair only the malformed shirt collar in the attached candidate. Use the original photo as the identity reference. Preserve the face, expression, hair, glasses, lighting, background, pose and all unaffected clothing. Return one corrected photograph; do not redesign the face.
```

应明确告知用户：本次交付提示词，尚未生成或检查成品照片。修复语句为条件式示例，没有断言成品确实存在领口问题。

## C. 看不到照片

用户：“按我的脸型推荐商务头像”，但照片不可访问。

回复应说明尚未看到原图，请用户提供清晰照片。可以先解释五种风格或提供通用模板，但不能说“你的脸型适合深色西装”，也不能将 `source_reviewed` 写成 true。

## D. 生成成功但无法检查返回图片

先尝试宿主允许的打开方式；不可访问时不编造质检。若用户已同意接受未审查草稿，交付工具真实返回的附件或允许链接，标注“未视觉质检”，请用户带回可查看的图片。不得因为工具返回 success 就宣称身份一致或没有瑕疵。

## E. 所有五种风格的提示词

在 `examples/request.json` 的副本中把 `style` 设为任一预设 ID，生成完整提示词：

```bash
python scripts/prompt_studio.py --list-styles
python scripts/prompt_studio.py --request private/request.json --capabilities examples/capabilities/vision-only.json --format prompt --out runs/edit-prompt.txt
```

`styles/presets.json` 包含每种风格的完整英文摄影方向。生成器将它与身份、构图、皮肤和负面约束合并；不需要另装提示词框架。未真实看图的示例会明确标注未分析原图。
