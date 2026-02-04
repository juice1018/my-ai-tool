import streamlit as st
import pandas as pd
import re

# --- 核心檢查邏輯 ---

def check_rules(row):
    errors = []
    product_name = str(row.get('商品名稱', ''))
    content = str(row.get('商品詳情', ''))
    size_val = row.get('尺寸數值', 0)  # 假設 Excel 有一欄是尺寸

    # 規範二：數字與中文中間要空格
    # 邏輯：檢查是否存在 中文+數字 或 數字+中文 但中間沒空格
    if re.search(r'[\u4e00-\u9fa5][0-9]|[0-9][\u4e00-\u9fa5]', product_name):
        errors.append({
            "類型": "格式錯誤",
            "原始內容": product_name,
            "描述": "數字與中文中間缺少空格",
            "建議修正": "請在數字與中文間加入空格"
        })

    # 規範三：長寬高超過 43cm，超取欄位檢查
    delivery_type = str(row.get('超取欄位', ''))
    if size_val > 43 and delivery_type != 'X':
        errors.append({
            "類型": "數據嚴重錯誤",
            "原始內容": f"尺寸 {size_val}cm / 超取欄位: {delivery_type}",
            "描述": "長寬高超過 43cm，超取欄位必須填寫 X",
            "建議修正": "將超取欄位改為 X"
        })

    # 規格一致性比對 (例如 ml/g)
    name_specs = re.findall(r'(\d+)\s*(ml|g|cm|kg)', product_name, re.I)
    for val, unit in name_specs:
        if val not in content:
            errors.append({
                "類型": "數據不符",
                "原始內容": f"品名標示 {val}{unit}",
                "描述": f"商品詳情內文中未找到對應的數值 {val}",
                "建議修正": "請核對品名與內文規格是否一致"
            })

    return errors

# --- Streamlit 網頁介面 ---

st.title("🛍️ 商品文案自動審稿工具")
st.subheader("請上傳您的商品清單 Excel")

uploaded_file = st.file_uploader("選擇 Excel 檔案", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("已讀取資料：", df.head())
    
    if st.button("開始審核"):
        all_errors = []
        for index, row in df.iterrows():
            row_errors = check_rules(row)
            all_errors.extend(row_errors)
        
        if all_errors:
            st.error("發現以下錯誤：")
            error_df = pd.DataFrame(all_errors)
            st.table(error_df)
        else:
            st.success("審核完畢，未發現明顯錯誤！")