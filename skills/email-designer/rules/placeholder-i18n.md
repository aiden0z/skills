# Placeholder Internationalization

Agent MUST detect the user's conversation language and use matching placeholders.

## Chinese (zh)
- Title: 在此输入标题
- Subtitle: 在此输入副标题
- Body text: 在此输入正文内容
- Image alt: 在此插入图片
- Table header: 列标题
- Table cell: 表格内容
- Footer copyright: 版权所有 © 2026 公司名称
- Footer unsubscribe: 退订链接
- CTA button: 点击查看详情
- Section title: 章节标题

## English (en)
- Title: Enter Title Here
- Subtitle: Enter Subtitle Here
- Body text: Enter body content here
- Image alt: Insert image here
- Table header: Column Header
- Table cell: Table content
- Footer copyright: Copyright © 2026 Company Name
- Footer unsubscribe: Unsubscribe
- CTA button: Learn More
- Section title: Section Title

## Japanese (ja)
- Title: タイトルを入力
- Subtitle: サブタイトルを入力
- Body text: 本文を入力してください
- Image alt: 画像を挿入
- Table header: 列ヘッダー
- Table cell: テーブル内容
- Footer copyright: 著作権 © 2026 会社名
- Footer unsubscribe: 配信停止
- CTA button: 詳細を見る
- Section title: セクションタイトル

## Agent Behavior
1. Detect user's conversation language from their messages
2. Use the corresponding placeholder set when generating HTML
3. If language not listed above, use English as default
4. User can explicitly request a specific language for placeholders
