import streamlit as st
import google.generativeai as genai
import time
from PIL import Image

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(
    page_title="Veo 3 Pro Studio", 
    page_icon="🎬", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🎬 Veo 3 Video Studio")
st.markdown("Công cụ tạo video AI chuyên nghiệp chạy trên Android.")

# --- SIDEBAR: CẤU HÌNH ---
with st.sidebar:
    st.header("⚙️ Cài đặt")
    api_key = st.text_input("Google API Key:", type="password")
    st.divider()
    aspect_ratio = st.selectbox("Tỉ lệ khung hình:", ["16:9", "9:16", "1:1"])
    st.info("Lấy API Key tại: aistudio.google.com")

# --- GIAO DIỆN CHÍNH ---
col1, col2 = st.columns([1, 1])

with col1:
    prompt = st.text_area("Mô tả video của bạn:", height=150, placeholder="Ví dụ: Một con rồng băng đang bay qua dãy Himalaya...")
    uploaded_file = st.file_uploader("Tải ảnh tham chiếu (Tùy chọn):", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Ảnh đã tải lên", use_container_width=True)

# --- NÚT TẠO VIDEO ---
if st.button("🚀 Bắt đầu tạo Video", use_container_width=True):
    if not api_key:
        st.error("Vui lòng nhập API Key ở menu bên trái!")
    elif not prompt:
        st.warning("Vui lòng nhập mô tả video!")
    else:
        try:
            genai.configure(api_key=api_key)
            
            with st.status("🤖 Veo 3 đang xử lý...", expanded=True) as status:
                input_data = [prompt]
                if uploaded_file:
                    input_data.append(img)
                
                st.write("Đang gửi yêu cầu tới server Google...")
                # Sử dụng phương thức khởi tạo model trước khi gọi tạo video
model = genai.GenerativeModel("veo-3.1-generate-preview")
operation = model.generate_content(
    input_data,
    # Cấu hình cho Veo thường nằm trong công cụ này nếu API chính thức cập nhật
)
# Lưu ý: Nếu Veo 3 vẫn đang ở bản giới hạn, 
# hãy dùng lệnh trực tiếp từ genai nhưng đảm bảo thư viện đã update ở Bước 1.
                )
                
                start_time = time.time()
                while not operation.done:
                    elapsed = int(time.time() - start_time)
                    st.write(f"Đang xử lý video... ({elapsed} giây)")
                    time.sleep(10)
                
                status.update(label="✅ Đã xong!", state="complete")

            # Hiển thị kết quả
            video_result = operation.result()
            video_file_name = f"veo_video_{int(time.time())}.mp4"
            video_result.save(video_file_name)
            
            st.success("Video đã tạo thành công!")
            st.video(video_file_name)
            
            with open(video_file_name, "rb") as file:
                st.download_button("📥 Tải về điện thoại", data=file, file_name=video_file_name)
                    
        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")