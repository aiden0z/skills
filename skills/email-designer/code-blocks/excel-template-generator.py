"""
Excel Template Generator — Generate & Load Excel Data Templates
================================================================
Two responsibilities:
1. Generate: Create an Excel template from section definitions (crystallization)
2. Load: Read data from a filled Excel template (production mode)

Dependencies: openpyxl (auto-installed by deps-checker.py)
"""

import re
from pathlib import Path
from typing import Dict, List

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.comments import Comment
    from openpyxl.utils import get_column_letter
except ImportError:
    raise ImportError(
        "openpyxl is required for Excel template generation. "
        "Install it with: pip install openpyxl"
    )


# ---------- Markup Processing ----------

MARKUP_COLORS = {
    "black": "#374151",
    "red": "#b91c1c",
    "green": "#059669",
    "orange": "#d97706",
    "blue": "#2563eb",
}


def process_markup(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    html = text
    for color_name, color_hex in MARKUP_COLORS.items():
        pattern = rf"<({color_name})>(.+?)</\1>"
        html = re.sub(
            pattern,
            lambda m: f'<span style="color:{MARKUP_COLORS[m.group(1)]}">{m.group(2)}</span>',
            html, flags=re.DOTALL,
        )
    html = re.sub(
        r'<a\s+href=["\'](.+?)["\']\s*>(.+?)</a>',
        r'<a href="\1" style="color:#2563eb; text-decoration:underline;">\2</a>',
        html, flags=re.DOTALL,
    )
    html = html.replace("\r\n", "<br>").replace("\n", "<br>")
    return html


def process_cell_value(value) -> str:
    if value is None:
        return ""
    return process_markup(str(value).strip())


# ---------- Styles ----------

HEADER_FONT = Font(name="Microsoft YaHei", size=11, bold=True, color="FFFFFF")
HEADER_FILL_GREEN = PatternFill(start_color="059669", end_color="059669", fill_type="solid")
HEADER_FILL_BLUE = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
HEADER_FILL_PURPLE = PatternFill(start_color="7C3AED", end_color="7C3AED", fill_type="solid")
HEADER_FILL_ORANGE = PatternFill(start_color="EA580C", end_color="EA580C", fill_type="solid")
HEADER_FILL_RED = PatternFill(start_color="DC2626", end_color="DC2626", fill_type="solid")

DATA_FONT = Font(name="Microsoft YaHei", size=10)
EXAMPLE_FONT = Font(name="Microsoft YaHei", size=10, color="6B7280")
WRAP_ALIGNMENT = Alignment(wrap_text=True, vertical="top")
THIN_BORDER = Border(
    left=Side(style="thin", color="E5E7EB"),
    right=Side(style="thin", color="E5E7EB"),
    top=Side(style="thin", color="E5E7EB"),
    bottom=Side(style="thin", color="E5E7EB"),
)
SHEET_FILLS = [HEADER_FILL_BLUE, HEADER_FILL_PURPLE, HEADER_FILL_ORANGE,
               HEADER_FILL_RED, HEADER_FILL_GREEN]


# ---------- Generate ----------

def generate_template(sections: List[Dict], output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    wb.remove(wb.active)
    ws_instructions = wb.create_sheet("填写说明")
    _build_instructions_sheet(ws_instructions, sections)
    for i, section in enumerate(sections):
        ws = wb.create_sheet(section["name"])
        fill = SHEET_FILLS[i % len(SHEET_FILLS)]
        _build_data_sheet(ws, section, fill)
    wb.save(output_path)
    wb.close()
    return str(Path(output_path).resolve())


def _build_instructions_sheet(ws, sections: List[Dict]):
    ws.sheet_properties.tabColor = "059669"
    ws["A1"] = "📖 邮件模板填写说明"
    ws["A1"].font = Font(name="Microsoft YaHei", size=14, bold=True)
    ws.merge_cells("A1:C1")
    ws["A3"] = "本 Excel 文件用于填写邮件内容数据。每个 Sheet 对应邮件中的一个内容区域。"
    ws["A3"].font = DATA_FONT
    ws.merge_cells("A3:C3")
    row = 5
    ws.cell(row=row, column=1, value="Sheet 名称").font = Font(name="Microsoft YaHei", size=10, bold=True)
    ws.cell(row=row, column=2, value="对应区域").font = Font(name="Microsoft YaHei", size=10, bold=True)
    ws.cell(row=row, column=3, value="说明").font = Font(name="Microsoft YaHei", size=10, bold=True)
    row += 1
    for section in sections:
        ws.cell(row=row, column=1, value=section["name"]).font = DATA_FONT
        ws.cell(row=row, column=2, value=section["description"]).font = DATA_FONT
        note = "单行数据" if section.get("single_row") else "多行数据（可增减行）"
        ws.cell(row=row, column=3, value=note).font = DATA_FONT
        row += 1
    row += 1
    for section in sections:
        ws.cell(row=row, column=1, value=f"📝 {section['name']} 字段说明").font = Font(
            name="Microsoft YaHei", size=11, bold=True)
        row += 1
        for col_def in section["columns"]:
            required_mark = "（必填）" if col_def.get("required") else "（可选）"
            ws.cell(row=row, column=1, value=col_def["name"]).font = DATA_FONT
            ws.cell(row=row, column=2, value=f'{col_def["description"]}{required_mark}').font = DATA_FONT
            ws.cell(row=row, column=3, value=f'示例: {col_def.get("example", "")}').font = EXAMPLE_FONT
            row += 1
        row += 1
    ws.cell(row=row, column=1, value="🎨 内容标记语法").font = Font(
        name="Microsoft YaHei", size=11, bold=True)
    row += 1
    for label, example in [
        ("加粗", "<strong>文本</strong>"),
        ("红色文本", "<red>文本</red>（警告、紧急）"),
        ("绿色文本", "<green>文本</green>（成功、正向）"),
        ("蓝色文本", "<blue>文本</blue>（信息、链接）"),
        ("橙色文本", "<orange>文本</orange>（关注、待观察）"),
        ("链接", '<a href="https://example.com">点击查看</a>'),
    ]:
        ws.cell(row=row, column=1, value=label).font = DATA_FONT
        ws.cell(row=row, column=2, value=example).font = DATA_FONT
        row += 1
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 50
    ws.column_dimensions["C"].width = 40


def _build_data_sheet(ws, section: Dict, header_fill: PatternFill):
    ws.sheet_properties.tabColor = header_fill.start_color.rgb[-6:]
    columns = section["columns"]
    for col_idx, col_def in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_def["name"])
        cell.font = HEADER_FONT
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = THIN_BORDER
        required_mark = "（必填）" if col_def.get("required") else "（可选）"
        cell.comment = Comment(
            f'{col_def["description"]}{required_mark}\n示例: {col_def.get("example", "")}',
            "Email Designer",
        )
        if "validation" in col_def and col_def["validation"]:
            dv = DataValidation(
                type="list",
                formula1='"' + ",".join(col_def["validation"]) + '"',
                allow_blank=not col_def.get("required", False),
            )
            dv.error = f"请从下拉列表中选择{col_def['name']}的值"
            dv.errorTitle = "无效值"
            ws.add_data_validation(dv)
            col_letter = get_column_letter(col_idx)
            dv.add(f"{col_letter}2:{col_letter}100")
    num_examples = 1 if section.get("single_row") else 3
    for row_idx in range(2, 2 + num_examples):
        for col_idx, col_def in enumerate(columns, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=col_def.get("example", ""))
            cell.font = EXAMPLE_FONT
            cell.alignment = WRAP_ALIGNMENT
            cell.border = THIN_BORDER
    for col_idx, col_def in enumerate(columns, start=1):
        max_len = max(len(col_def["name"]), len(str(col_def.get("example", ""))), 10)
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = min(max_len + 4, 50)
    ws.freeze_panes = "A2"


# ---------- Load ----------

def load_excel_data(excel_path: str) -> Dict[str, List[Dict]]:
    wb = load_workbook(excel_path, data_only=True)
    data = {}
    for sheet_name in wb.sheetnames:
        if sheet_name == "填写说明":
            continue
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(min_row=1, values_only=False))
        if not rows:
            continue
        headers = [cell.value for cell in rows[0] if cell.value is not None]
        if not headers:
            continue
        sheet_data = []
        for row in rows[1:]:
            values = [cell.value for cell in row[:len(headers)]]
            if all(v is None or str(v).strip() == "" for v in values):
                continue
            row_dict = {}
            for header, value in zip(headers, values):
                row_dict[header] = process_cell_value(value)
            sheet_data.append(row_dict)
        data[sheet_name] = sheet_data
    wb.close()
    return data
