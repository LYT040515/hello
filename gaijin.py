import streamlit as st
import os
from fastai.vision.all import *
import pathlib
import sys
import pandas as pd
import random

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
    pred, pred_idx, probs = learn_inf.predict(image)
    st.write(f"预测结果: {pred}; 概率: {probs[pred_idx]:.04f}")
    
    # 加载景点数据
    def load_scenicspots_from_excel(filename):
        # 使用pandas的read_excel函数读取Excel文件
        df = pd.read_excel(filename)
        scenicspots = df['scenicspot'].tolist()
        return scenicspots

    # 调用函数并传入文件名
    scenicspots = load_scenicspots_from_excel(os.path.join(path, "title.xlsx"))
    ratings = {}

    # 假设预测结果是某个景点的名称，使用这个信息来推荐景点
    # 这里只是一个示例，实际应用中可能需要更复杂的逻辑来处理预测结果
    if pred in scenicspots:
        recommended_scenicspots = [pred]
    else:
        recommended_scenicspots = random.sample(scenicspots, 3)

    # 使用Session State来存储推荐的景点
    if 'initial_recommended_scenicspots' not in st.session_state:
        st.session_state.initial_recommended_scenicspots = recommended_scenicspots

    # 显示推荐的景点
    st.write("推荐的景点:")
    for i, scenicspot in enumerate(st.session_state.initial_recommended_scenicspots):
        st.write(f"{i+1}. {scenicspot}")
        rating = st.slider(f"Rate this scenicspot ({i+1})", 0, 5, 3)
        ratings[scenicspot] = rating

    # 计算并显示用户满意度
    total_ratings = sum(ratings.values())
    num_ratings = len(ratings)
    satisfaction = total_ratings / num_ratings if num_ratings > 0 else 0
    st.write(f"本次推荐的满意度为: {satisfaction:.2f}/5")

    # 根据用户评分推荐五个新景点
    if st.button("推荐新的景点"):
        rated_scenicspots = set(ratings.keys())  # 使用已评分的景点作为集合
        remaining_scenicspots = [scenicspot for scenicspot in scenicspots if scenicspot not in rated_scenicspots]
        new_recommended_scenicspots = random.sample(remaining_scenicspots, 5)

        # 使用Session State来存储新的推荐景点
        if 'new_recommended_scenicspots' not in st.session_state:
            st.session_state.new_recommended_scenicspots = new_recommended_scenicspots

        # 显示新的推荐景点并获取评分
        for scenicspot in st.session_state.new_recommended_scenicspots:
            try:
                rating = st.slider(f"Rate this scenicspot ({scenicspot})", 0, 5, 3)
                ratings[scenicspot] = rating
            except Exception as e:
                st.error(f"An error occurred: {e}")
                # 如果发生错误，可以在这里记录或者处理异常
                # 例如，可以记录错误到日志文件，或者显示一个用户友好的错误消息

# 创建一个提交推荐的评分的按钮
if st.button("Submit Recommended Ratings"):
    # 使用Session State中的推荐景点来计算用户对推荐的景点的平均评分
    new_recommended_scenicspots = st.session_state.new_recommended_scenicspots
    new_ratings = {scenicspot: ratings[scenicspot] for scenicspot in new_recommended_scenicspots}
    avg_recommended_score = sum(new_ratings.values()) / len(new_ratings)

    # 计算百分比
    percentage_score = (avg_recommended_score / 5) * 100

    # 显示结果
    st.write(f"You rated the recommended scenicspots {percentage_score:.2f}% of the total possible score.")
