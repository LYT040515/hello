import streamlit as st
import os
from fastai.vision.all import *
import pathlib
import sys

# 根据不同的操作系统设置正确的pathlib.Path
if sys.platform == "win32":
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath
else:
    temp = pathlib.WindowsPath
    pathlib.WindowsPath = pathlib.PosixPath

# 获取当前文件所在的文件夹路径
path = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(path,"scenic spot.pkl")

# 加载模型
learn_inf = load_learner(model_path)

# 恢复pathlib.Path的原始值
if sys.platform == "win32":
    pathlib.PosixPath = temp
else:
    pathlib.WindowsPath = temp

st.title("叮咚！景点照片请上传～")
st.write("上传一张图片，应用将预测对应的景点名称。")

# 允许用户上传图片
uploaded_file = st.file_uploader("选择一张照片...",
                                 type=["jpg",
                                      "jpeg",
                                      "png"]
                                 )

# 如果用户已上传图片
if uploaded_file is not None:
    # 显示上传的图片
    image = PILImage.create(uploaded_file)
    st.image(image,
             caption="上传的照片",
             use_column_width=True)
    
    # 获取预测的标签
    pred, pred_idx, probs = learn_inf.predict(image )
    st.write(f"预测结果: {pred}; 概率: {probs[pred_idx]:.04f}")
