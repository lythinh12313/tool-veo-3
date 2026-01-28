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
    ar_option = st.selectbox("Tỉ lệ khung hình:", ["16:9", "9:16", "1:1"])
    st.info("Sử dụng Endpoint: generateVideos")

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
            # --- THAY ĐỔI QUAN TRỌNG: ENDPOINT GENERATE_VIDEOS ---
            # Model ID chuẩn thường là 'veo-3' hoặc 'veo-3-generate-001'
            model_id = "veo-3" 
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateVideos?key={api_key}"
            headers = {'Content-Type': 'application/json'}

            # Cấu trúc Payload dành riêng cho Video
            payload = {
                "video_prompt": {
                    "text": prompt
                },
                "generation_config": {
                    "aspect_ratio": ar_option
                }
            }

            # Nếu có ảnh tham chiếu
            if uploaded_file:
                img_base64 = image_to_base64(Image.open(uploaded_file))
                payload["video_prompt"]["image"] = {
                    "mime_type": "image/jpeg",
                    "data": img_base64
                }

            with st.status("📡 Đang gửi yêu cầu tạo video...") as status:
                response = requests.post(url, headers=headers, json=payload)
                res_data = response.json()

                if response.status_code == 200:
                    st.success("Yêu cầu đã được gửi thành công!")
                    # Veo sẽ trả về một Operation (vì tạo video mất nhiều thời gian)
                    if "name" in res_data:
                        op_name = res_data["name"]
                        st.info(f"Đang xử lý (Mã số: {op_name}). Vui lòng đợi...")
                        
                        # Vòng lặp kiểm tra trạng thái (Polling)
                        check_url = f"https://generativelanguage.googleapis.com/v1beta/{op_name}?key={api_key}"
                        
                        while True:
                            check_res = requests.get(check_url).json()
                            if check_res.get("done"):
                                if "error" in check_res:
                                    st.error(f"Lỗi render: {check_res['error']['message']}")
                                    break
                                
                                # Nếu xong, lấy link video
                                video_uri = check_res.get("response", {}).get("video", {}).get("uri")
                                st.video(video_uri)
                                st.balloons()
                                break
                            time.sleep(10) # Đợi 10 giây mỗi lần kiểm tra
                    else:
                        st.json(res_data)
                else:
                    # Nếu model 'veo-3' không được tìm thấy, thử với 'veo-3.1-generate-preview'
                    error_msg = res_data.get('error', {}).get('message', '')
                    if "not found" in error_msg.lower():
                        st.warning("Đang thử lại với Model ID thay thế...")
                        # Bạn có thể thay đổi model_id ở đây nếu cần test
                    st.error(f"Lỗi API: {error_msg}")

        except Exception as e:
            st.error(f"Lỗi kết nối: {str(e)}")