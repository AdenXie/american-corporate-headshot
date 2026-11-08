# 示例工作流

以下为流程演示，不含真实照片、图片调用或视觉质检结论。使用时以本人原照和用户要求替换示例观察。

## A. 蓝色影棚：本人原照与其他人的样板

用户：“用我的照片做金融求职头像，参考这张蓝底样板。保留眼镜，不打领带，做一张。”

1. 实际查看本人照片；记录能看清的五官、原有表情、脸部角度和眼镜。样板人物只参考蓝色细纹理、棚拍光、服装和构图，不能借用脸。
2. 选择 `studio-blue`；用户不打领带的偏好覆盖风格默认。默认头至上胸构图，脸保持与原照接近的角度，避免为了摆正而重绘五官。仅在身份不受影响时轻调表情。
3. 确认真实的参考编辑工具能力和处理授权；将原照作为身份参考。支持局部编辑或蒙版时，主要编辑背景与服装，保护脸部结构，需要时可局部轻调表情。生成一张。
4. 对照原照检查五官、眼镜、头发、肤色与衣领，再检查影棚背景和光线。身份明显漂移时不推荐；可使用原照和实际发现的问题作一次针对性修复。
5. 交付真实图片，说明本人需确认相似度；只有实际制作并查看圆裁预览时才报告检查过。

离线计划示例：复制 `examples/request.json` 到 `private/request.json`；实际看图之后才填写 `source_reviewed: true` 和观察到的 `identity_notes`，授权覆盖目标服务时才将 `provider_processing_authorized` 设为 true。复制并据实填写能力记录。

```bash
python scripts/prompt_studio.py --request private/request.json --capabilities private/capabilities.json --out runs/plan.json
```

脚本只生成计划，不发送或读取图片。宿主再将完整提示词与本人原照传给已授权的编辑工具。

## B. 中性极简：只有视觉输入、没有图片编辑工具

用户：“我能让你看照片，但你只能输出文字。想要像个人主页一样自然的浅灰背景。”

实际看图后可交付一份完整英文提示词，将可见特征和具体偏好写入；以下仅为模板，不代表已分析真实照片。

```text
Edit my attached identity photo into one natural professional studio portrait. My photo is the sole identity source: preserve my recognizable facial proportions, eye and brow shapes and spacing, nose, lips, face shape, hairline, hair, skin tone, apparent age and natural asymmetry. Keep my head angle close to the original rather than rebuilding my face. Preserve glasses and permanent marks if present. Do not infer features hidden in my photo.

Use a soft warm-gray or off-white background with a gentle gradient and some negative space, understated professional clothing, and soft directional light with natural facial depth and skin texture. Keep a relaxed closed-mouth expression close to the original. Frame from the head through the upper chest with comfortable headroom, or follow my requested composition. For a profile avatar, leave room for a centered circular crop.

Prioritize the background, clothing and lighting; protect facial structure with selective editing if supported, allowing a small local expression change when needed. Avoid identity drift, changed facial proportions or age, invented teeth, waxy skin, malformed features, obvious cutout edges, text, logos and watermarks.
```

告诉用户上传同一原图到参考图编辑入口，再粘贴提示词；若成品尚未生成或查看，明确写明，不声称完成质检。

## C. 无法查看原照或成品

原照不可见时，请用户提供可访问的清晰照片；只可提供标记为未分析原图的通用提示词，不得猜测其身份特征。成品不可见时不编造视觉质检；用户已同意接受未审查草稿时，交付真实附件并标注尚未视觉质检。

## D. 预设与旧 ID

`studio-blue` 为默认蓝色纹理影棚，`studio-neutral` 为中性极简影棚。原来的五个 ID 仍可作为别名输入，映射见 `styles/presets.json`。可用以下命令查看及生成计划：

```bash
python scripts/prompt_studio.py --list-styles
python scripts/prompt_studio.py --request private/request.json --capabilities examples/capabilities/vision-only.json --format prompt --out runs/edit-prompt.txt
```

三张候选需显式设置 `candidate_count: 3`；前两张是选定风格，第三张是相邻风格。所有结果仍需原照与本人终审。
