import streamlit as st
import requests
import time
import base64
from PIL import Image
import io

st.set_page_config(page_title="Veo 3 Pro Studio", page_icon="🎬")

st.title("🎬 Veo 3 Video Studio")

with st.sidebar:
    st.header("⚙️ Cài đặt")
    api_key = st.text_input("Google API Key:", type="password")
    # Đổi lại giá trị đơn giản để API dễ nhận diện
    ar_option = st.selectbox("Tỉ lệ khung hình:", ["16:9", "9:16", "1:1"])
    st.info("Lưu ý: Đảm bảo tài khoản của bạn đã được cấp quyền sử dụng Veo 3.")

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

prompt = st.text_area("Mô tả video:", placeholder="Ví dụ: Cinematic drone shot of a tropical island...")
uploaded_file = st.file_uploader("Ảnh tham chiếu (Tùy chọn):", type=['jpg', 'jpeg', 'png'])

if st.button("🚀 Bắt đầu tạo Video", use_container_width=True):
    if not api_key:
        st.error("Vui lòng nhập API Key!")
    elif not prompt:
        st.warning("Vui lòng nhập mô tả!")
    else:
        try:
            # Endpoint chuẩn cho Gemini/Veo API Studio
            url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-generate-preview:generateContent?key={api_key}"
            headers = {'Content-Type': 'application/json'}

            parts = [{"text": prompt}]
            if uploaded_file:
                img_base64 = image_to_base64(Image.open(uploaded_file))
                parts.append({"inline_data": {"mime_type": "image/jpeg", "data": img_base64}})

            # Cấu trúc Payload chuẩn hóa lại
            payload = {
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "aspectRatio": ar_option # Gửi "16:9", "9:16" hoặc "1:1"
                }
            }

            with st.status("📡 Đang gửi yêu cầu...") as status:
                response = requests.post(url, headers=headers, json=payload)
                res_data = response.json()

                if response.status_code != 200:
                    # Nếu lỗi vẫn ở 'aspectRatio', mình sẽ thử gửi lại không có config
                    st.write("Đang thử lại với cấu hình tối giản...")
                    simple_payload = {"contents": [{"parts": parts}]}
                    response = requests.post(url, headers=headers, json=simple_payload)
                    res_data = response.json()

                if response.status_code == 200:
                    st.success("Yêu cầu đã được chấp nhận!")
                    # Veo trả về một chuỗi phản hồi chứa Video hoặc Operation
                    st.json(res_data) # Hiển thị để kiểm tra cấu trúc trả về
                else:
                    st.error(f"Lỗi API: {res_data.get('error', {}).get('message', 'Không xác định')}")

        except Exception as e:
            st.error(f"Lỗi: {str(e)}")

st.caption("Nếu API trả về JSON thành công, mình sẽ viết thêm hàm giải mã Video từ JSON đó cho bạn!")