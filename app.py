import streamlit as st
import spacy
from spacy import displacy
import pandas as pd

# ---------------------- 页面配置 ----------------------
st.set_page_config(
    page_title="句法透视仪",
    page_icon="🔍",
    layout="wide"
)

# ---------------------- 自动下载spaCy模型 ----------------------
@st.cache_resource
def load_spacy_model():
    """加载spaCy模型，如果未安装则自动下载"""
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        import subprocess
        import sys
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")
    return nlp

nlp = load_spacy_model()

# ---------------------- 核心功能函数 ----------------------
def get_dep_analysis(text):
    """依存句法分析与可视化"""
    doc = nlp(text)
    html = displacy.render(doc, style="dep", jupyter=False)
    return doc, html

def extract_core_args(doc):
    """提取核心论元（Root, nsubj, dobj, pobj）"""
    core_args = []
    for token in doc:
        if token.dep_ in ["ROOT", "nsubj", "dobj", "pobj"]:
            core_args.append({
                "依存关系": token.dep_,
                "词": token.text,
                "词性": token.pos_,
                "头节点": token.head.text
            })
    return pd.DataFrame(core_args)

def get_constituent_structure(doc):
    """简化版成分句法结构（用缩进文本模拟）"""
    def traverse(token, indent=0):
        result = []
        result.append("  " * indent + f"({token.tag_} {token.text})")
        for child in token.children:
            if child.dep_ not in ["punct"]:
                result.extend(traverse(child, indent + 1))
        return result
    root = next(token for token in doc if token.head == token)
    return "\n".join(traverse(root))

# ---------------------- 主界面 ----------------------
st.title("🔍 句法透视仪 - 依存vs成分双视角")
input_text = st.text_input(
    "输入句子",
    value="The boy saw the man with the telescope."
)

if st.button("分析句法结构"):
    doc, dep_html = get_dep_analysis(input_text)
    
    tab1, tab2 = st.tabs(["依存关系", "成分结构"])
    
    with tab1:
        st.header("依存句法图")
        st.components.v1.html(dep_html, height=500)
        
        st.header("核心论元提取")
        args_df = extract_core_args(doc)
        st.dataframe(args_df, use_container_width=True)
    
    with tab2:
        st.header("简化成分句法树")
        st.code(get_constituent_structure(doc), language="text")

st.markdown("---")
st.markdown("© 2025 NLP 课程实验 | 句法透视仪")
