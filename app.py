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
    model_choice = st.selectbox("Chọn Model:", ["veo-3.1-generate-preview", "veo-3"])
    st.info("Lấy Key tại: aistudio.google.com")

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

prompt = st.text_area("Mô tả video:", placeholder="Ví dụ: Cảnh hoàng hôn trên biển, sóng vỗ rì rào...")
uploaded_file = st.file_uploader("Ảnh tham chiếu (Tùy chọn):", type=['jpg', 'jpeg', 'png'])

if st.button("🚀 Bắt đầu tạo Video", use_container_width=True):
    if not api_key:
        st.error("Vui lòng nhập API Key!")
    elif not prompt:
        st.warning("Vui lòng nhập mô tả!")
    else:
        try:
            # Endpoint chuẩn cho Video Generation
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_choice}:generateVideos?key={api_key}"
            headers = {'Content-Type': 'application/json'}

            payload = {
                "video_prompt": {"text": prompt},
                "generation_config": {"aspect_ratio": "16:9"}
            }
            if uploaded_file:
                img_b64 = image_to_base64(Image.open(uploaded_file))
                payload["video_prompt"]["image"] = {"mime_type": "image/jpeg", "data": img_b64}

            with st.status("📡 Đang gửi yêu cầu...") as status:
                response = requests.post(url, headers=headers, json=payload)
                
                # KIỂM TRA PHẢN HỒI TRƯỚC KHI ĐỌC JSON
                if response.status_code != 200:
                    st.error(f"Lỗi hệ thống (Mã {response.status_code})")
                    try:
                        st.write(response.json())
                    except:
                        st.write(response.text) # Hiển thị lỗi dạng văn bản nếu không phải JSON
                    st.stop()

                res_data = response.json()
                if "name" in res_data:
                    op_name = res_data["name"]
                    st.info(f"Đang render video... (Mã: {op_name})")
                    
                    # Vòng lặp kiểm tra trạng thái
                    check_url = f"https://generativelanguage.googleapis.com/v1beta/{op_name}?key={api_key}"
                    while True:
                        check_res = requests.get(check_url).json()
                        if check_res.get("done"):
                            if "error" in check_res:
                                st.error(f"Lỗi render: {check_res['error']['message']}")
                                break
                            video_uri = check_res.get("response", {}).get("video", {}).get("uri")
                            st.video(video_uri)
                            st.success("Tạo video thành công!")
                            break
                        time.sleep(10)
                else:
                    st.warning("Phản hồi không chứa mã tiến trình. Vui lòng kiểm tra quyền truy cập Veo 3.")
                    st.json(res_data)

        except Exception as e:
            st.error(f"Lỗi kết nối: {str(e)}")