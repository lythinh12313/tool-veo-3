import streamlit as st
import requests
import time
import base64
from PIL import Image
import io

# --- CẤU HÌNH ---
st.set_page_config(page_title="Veo 3 Direct API", page_icon="🎬", layout="wide")

st.title("🎬 Veo 3 Video Studio (Direct API)")

with st.sidebar:
    st.header("⚙️ Cấu hình")
    api_key = st.text_input("Google API Key:", type="password")
    aspect_ratio = st.selectbox("Tỉ lệ:", ["OUT_ASPECT_RATIO_16_9", "OUT_ASPECT_RATIO_9_16", "OUT_ASPECT_RATIO_1_1"])
    st.info("Sử dụng phương thức Request trực tiếp để tránh lỗi thư viện cũ.")

# --- HÀM HỖ TRỢ ---
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- GIAO DIỆN ---
prompt = st.text_area("Mô tả video:", placeholder="Mô tả chi tiết cảnh quay...")
uploaded_file = st.file_uploader("Ảnh tham chiếu (Tùy chọn):", type=['jpg', 'jpeg', 'png'])

if st.button("🚀 Tạo Video", use_container_width=True):
    if not api_key:
        st.error("Thiếu API Key!")
    elif not prompt:
        st.warning("Vui lòng nhập mô tả!")
    else:
        try:
            # 1. Chuẩn bị Endpoint và Header
            # Lưu ý: Endpoint này có thể thay đổi tùy theo vùng (region) của bạn
            url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-generate-preview:generateContent?key={api_key}"
            headers = {'Content-Type': 'application/json'}

            # 2. Chuẩn bị dữ liệu Payload
            parts = [{"text": prompt}]
            if uploaded_file:
                img = Image.open(uploaded_file)
                img_base64 = image_to_base64(img)
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_base64
                    }
                })

            payload = {
                "contents": [{"parts": parts}],
                "generation_config": {
                    "aspect_ratio": aspect_ratio
                }
            }

            # 3. Gửi yêu cầu
            with st.status("📡 Đang gửi yêu cầu tới Google Veo...") as status:
                response = requests.post(url, headers=headers, json=payload)
                res_data = response.json()

                if response.status_code != 200:
                    st.error(f"Lỗi API: {res_data.get('error', {}).get('message', 'Không rõ lỗi')}")
                    st.stop()

                # Kiểm tra xem có video trả về ngay không (hoặc là một Operation ID)
                # Lưu ý: Veo thường trả về một Operation để Polling
                st.write("Đang khởi tạo quá trình render...")
                
                # Cấu trúc phản hồi thực tế của Veo sẽ tùy thuộc vào việc bạn dùng Vertex hay AI Studio
                # Dưới đây là logic xử lý chung cho kết quả trả về
                if 'video' in str(res_data): 
                    st.success("Đã nhận được dữ liệu video!")
                    # (Logic xử lý hiển thị video từ bytes/URL ở đây)
                else:
                    st.json(res_data) # Hiển thị kết quả thô để bạn debug nếu cần
                    st.info("Yêu cầu đã được gửi. Nếu đây là tài khoản thử nghiệm, hãy kiểm tra tiến trình trong Google AI Studio.")

        except Exception as e:
            st.error(f"Lỗi kết nối: {str(e)}")

st.divider()
st.caption("Lưu ý: Veo 3 hiện vẫn đang trong giai đoạn Preview (thử nghiệm giới hạn).")