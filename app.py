import streamlit as st
import pandas as pd
import re

# 頁面標題
st.title("🛍️ 商品文案自動審稿工具")

def extract_ml(text):
    """從文字中抓取所有數字+ml的組合，例如 450ml"""
    return re.findall(r'(\d+)\s*ml', str(text).lower())

uploaded_file = st.file_uploader("請上傳您的商品清單 Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("已讀取資料（前5筆）：", df.head())
    
    if st.button("開始審核"):
        errors = []
        
        # 自動尋找可能的欄位名稱
        cols = df.columns.tolist()
        name_col = next((c for c in cols if "品名" in c or "公式" in c), None)
        
        if not name_col:
            st.error("找不到包含『品名』或『公式』的欄位，請檢查 Excel 標題。")
        else:
            for index, row in df.iterrows():
                content = str(row[name_col])
                # 抓取該列中所有的 ml 數值
                ml_values = extract_ml(content)
                
                # 如果同一列出現兩個以上不同的 ml 數值，就代表有誤
                if len(set(ml_values)) > 1:
                    errors.append({
                        "行數": index + 2, # Excel 行號
                        "類型": "數據嚴重錯誤",
                        "原始內容": content,
                        "發現數值": "、".join(set(ml_values)) + " ml",
                        "描述": f"同一格內發現多種容量數值（{', '.join(set(ml_values))}），請檢查是否標示不一。"
                    })

            if errors:
                st.error(f"發現 {len(errors)} 個錯誤！")
                st.table(pd.DataFrame(errors))
            else:
                st.success("審核完畢，未發現明顯錯誤！")