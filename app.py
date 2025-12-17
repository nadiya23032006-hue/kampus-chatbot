import streamlit as st
import json
import requests
import os

st.set_page_config(page_title="Chatbot Kampus Nad")
st.title("Chatbot Kampus Nad")

# Load data TXT
txt_path = "data.txt"
if os.path.exists(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        txt_content = f.read()
else:
    txt_content = ""

# Load data JSON
json_path = "data.json"
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        # gabungkan semua value JSON jadi satu string
        if isinstance(json_data, dict):
            json_content = " ".join([str(v) for v in json_data.values()])
        elif isinstance(json_data, list):
            # misal list of dict
            json_content = " ".join([str(v) for item in json_data for v in (item.values() if isinstance(item, dict) else [item])])
        else:
            json_content = str(json_data)
else:
    json_content = ""

# Pilih sumber data
option = st.selectbox("Pilih sumber data:", ["TXT", "JSON"])

if option == "TXT":
    data_text = txt_content
elif option == "JSON":
    data_text = json_content

st.write("Data berhasil dimuat!" if data_text else "Tidak ada data.")

# Input user
user_input = st.text_input("Tanya sesuatu:")
if user_input and data_text:
    try:
        api_key = st.secrets["QWEN_API_KEY"]
    except KeyError:
        st.error("Token Qwen API belum diatur di Streamlit Secrets!")
        st.stop()

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"input": f"{data_text}\nUser: {user_input}"}

    response = requests.post("https://api.qwen.ai/generate", json=payload, headers=headers)

    if response.status_code == 200:
        answer = response.json().get("output", "")
        st.success(answer)
    else:
        st.error(f"Error API: {response.status_code} {response.text}")
