import streamlit as st
import json
import requests
import os

st.set_page_config(page_title="Chatbot Kampus Vokasi", layout="wide")
st.title("Chatbot Kampus Vokasi 💬")

# --- Load data TXT ---
txt_path = "data.txt"
if os.path.exists(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        txt_content = f.read()
else:
    txt_content = ""

# --- Load data JSON ---
json_path = "data.json"
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        if isinstance(json_data, dict):
            json_content = " ".join([str(v) for v in json_data.values()])
        elif isinstance(json_data, list):
            json_content = " ".join([str(v) for item in json_data for v in (item.values() if isinstance(item, dict) else [item])])
        else:
            json_content = str(json_data)
else:
    json_content = ""

# --- Pilih sumber data ---
option = st.selectbox("Pilih sumber data:", ["TXT", "JSON"])
data_text = txt_content if option == "TXT" else json_content
st.write("Data berhasil dimuat!" if data_text else "Tidak ada data.")

# --- Inisialisasi chat history ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Fungsi untuk request ke Hugging Face Inference API terbaru ---
def ask_qwen(prompt):
    api_key = st.secrets["QWEN_API_KEY"]
    url = "https://api-inference.huggingface.co/models/Qwen/Qwen-7B-Chat"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.3
        }
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=90)
        if res.status_code == 200:
            result = res.json()
            # HF Inference API mengembalikan list dengan field generated_text
            if isinstance(result, list) and "generated_text" in result[0]:
                return result[0]["generated_text"]
            else:
                return "AI tidak mengembalikan jawaban."
        else:
            return f"AI Error {res.status_code}: {res.text}"
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- Input user ---
user_input = st.text_input("Tanya sesuatu:")

if st.button("Kirim") and user_input.strip():
    if not data_text:
        st.error("Tidak ada data untuk dijadikan konteks.")
    else:
        # Gabungkan data + user input
        prompt = f"{data_text}\nUser: {user_input}"
        with st.spinner("AI sedang memproses..."):
            reply = ask_qwen(prompt)

        # Simpan ke chat history
        st.session_state.history.append({"user": user_input, "reply": reply})

# --- Tampilkan chat history ala Laravel ---
for chat in st.session_state.history:
    st.markdown(f"**Kamu:** {chat['user']}")
    st.markdown(f"**Bot:** {chat['reply']}")
    st.markdown("---")
