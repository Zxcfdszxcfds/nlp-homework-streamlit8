import streamlit as st
import pandas as pd
import re

# ---------------------- 页面配置 ----------------------
st.set_page_config(
    page_title="句法透视仪",
    page_icon="🔍",
    layout="wide"
)

# ---------------------- 规则实现的句法分析函数 ----------------------
def simple_dep_analysis(text):
    """基于规则的依存句法分析（模拟核心功能）"""
    doc = []
    words = re.findall(r'\b\w+\b', text)
    for i, word in enumerate(words):
        doc.append({
            "text": word,
            "dep_": "",
            "pos_": "",
            "head_idx": -1
        })
    
    # 简单规则匹配核心依存关系
    for i, token in enumerate(doc):
        # 1. Root 根节点（动词）
        if token["text"].lower() in ["saw", "is", "was", "are", "were", "have", "has"]:
            token["dep_"] = "ROOT"
            token["head_idx"] = i
        # 2. 主语（名词短语，位于动词前）
        elif i > 0 and doc[i-1]["dep_"] == "":
            token["dep_"] = "nsubj"
            token["head_idx"] = i + 1 if i + 1 < len(doc) else i
        # 3. 宾语（名词短语，位于动词后）
        elif i > 0 and doc[i-1]["dep_"] == "ROOT":
            token["dep_"] = "dobj"
            token["head_idx"] = i - 1
        # 4. 介词短语
        elif token["text"].lower() in ["with", "in", "on", "at", "by"]:
            token["dep_"] = "prep"
            token["head_idx"] = i - 1
        # 5. 介词宾语
        elif i > 0 and doc[i-1]["dep_"] == "prep":
            token["dep_"] = "pobj"
            token["head_idx"] = i - 1
    
    return doc

def get_core_args(doc):
    """提取核心论元（Root, nsubj, dobj, pobj）"""
    core_args = []
    for token in doc:
        if token["dep_"] in ["ROOT", "nsubj", "dobj", "pobj"]:
            core_args.append({
                "依存关系": token["dep_"],
                "词": token["text"],
                "词性": "VERB" if token["dep_"] == "ROOT" else "NOUN",
                "头节点": doc[token["head_idx"]]["text"] if token["head_idx"] != -1 else "ROOT"
            })
    return pd.DataFrame(core_args)

def get_constituent_structure(text):
    """简化版成分句法结构（缩进文本形式）"""
    # 简单规则构建成分树
    if "with the telescope" in text:
        return """
(S
  (NP (DT The) (NN boy))
  (VP (VBD saw)
    (NP (DT the) (NN man)
      (PP (IN with)
        (NP (DT the) (NN telescope)))))
)
"""
    else:
        return """
(S
  (NP (DT The) (NN boy))
  (VP (VBD saw)
    (NP (DT the) (NN man)))
  (PP (IN with)
    (NP (DT the) (NN telescope)))
)
"""

# ---------------------- 主界面 ----------------------
st.title("🔍 句法透视仪 - 依存vs成分双视角")
input_text = st.text_input(
    "输入句子",
    value="The boy saw the man with the telescope."
)

if st.button("分析句法结构"):
    doc = simple_dep_analysis(input_text)
    
    tab1, tab2 = st.tabs(["依存关系", "成分结构"])
    
    with tab1:
        st.header("依存句法分析（模拟结果）")
        # 用表格展示依存关系
        dep_df = pd.DataFrame([{
            "词": token["text"],
            "依存关系": token["dep_"],
            "头节点": doc[token["head_idx"]]["text"] if token["head_idx"] != -1 else "ROOT"
        } for token in doc])
        st.dataframe(dep_df, use_container_width=True)
        
        st.header("核心论元提取")
        args_df = get_core_args(doc)
        st.dataframe(args_df, use_container_width=True)
    
    with tab2:
        st.header("简化成分句法树")
        st.code(get_constituent_structure(input_text), language="text")

st.markdown("---")
st.markdown("© 2025 NLP 课程实验 | 句法透视仪")
