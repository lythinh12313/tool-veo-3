import google.generativeai as genai
import time

# 1. Cấu hình API
genai.configure(api_key="YOUR_API_KEY")

# 2. Gửi lệnh tạo video
operation = genai.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Một phi hành gia đang đi bộ trên bề mặt sao Hỏa, phong cách điện ảnh, 4k",
    config={"aspect_ratio": "16:9"}
)

# 3. Chờ đợi kết quả
while not operation.done:
    print("Đang tạo video... vui lòng đợi...")
    time.sleep(10)

# 4. Lưu kết quả
video = operation.result()
video.save("mars_walking.mp4")
print("Video đã được lưu thành công!")import streamlit as st
import google.generativeai as genai
import time
import os

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Veo 3 Video Generator", page_icon="🎬", layout="wide")

st.title("🎬 Veo 3 Video Generator")
st.markdown("Công cụ tạo video chuyên nghiệp từ văn bản sử dụng Google Veo 3.")

# --- SIDEBAR: CẤU HÌNH API & THÔNG SỐ ---
with st.sidebar:
    st.header("Cài đặt")
    api_key = st.text_input("Nhập Google API Key:", type="password")
    
    st.divider()
    
    aspect_ratio = st.selectbox(
        "Tỉ lệ khung hình:",
        options=["16:9", "9:16", "1:1"],
        index=0
    )
    
    fps = st.select_slider("Khung hình (FPS):", options=[24, 30, 60], value=24)
    
    resolution = st.selectbox(
        "Độ phân giải:",
        options=["720p", "1080p"],
        index=0
    )

# --- GIAO DIỆN CHÍNH ---
prompt = st.text_area(
    "Mô tả video bạn muốn tạo:",
    placeholder="Ví dụ: Một chú mèo máy đang bay giữa thành phố tương lai, phong cách anime, ánh sáng neon rực rỡ...",
    height=150
)

if st.button("🚀 Bắt đầu tạo Video", use_container_width=True):
    if not api_key:
        st.error("Vui lòng nhập API Key ở thanh bên trái!")
    elif not prompt:
        st.warning("Vui lòng nhập mô tả video!")
    else:
        try:
            # Cấu hình AI
            genai.configure(api_key=api_key)
            
            with st.status("🤖 Đang kết nối với Veo 3...", expanded=True) as status:
                # Gửi yêu cầu tạo video
                st.write("Đang gửi prompt và phân tích...")
                operation = genai.generate_videos(
                    model="veo-3.1-generate-preview", # Hoặc model mới nhất bạn có quyền truy cập
                    prompt=prompt,
                    config={
                        "aspect_ratio": aspect_ratio,
                        "fps": fps
                    }
                )
                
                # Vòng lặp chờ video hoàn thành
                start_time = time.time()
                while not operation.done:
                    elapsed = int(time.time() - start_time)
                    st.write(f"Đang xử lý video... ({elapsed} giây)")
                    time.sleep(5)
                
                status.update(label="✅ Hoàn tất!", state="complete", expanded=False)

            # Lấy kết quả
            video_result = operation.result()
            
            # Hiển thị và lưu video
            st.success("Video của bạn đã sẵn sàng!")
            video_file_name = f"video_{int(time.time())}.mp4"
            video_result.save(video_file_name)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.video(video_file_name)
            
            with col2:
                st.info("Chi tiết file:")
                st.write(f"Tên file: `{video_file_name}`")
                with open(video_file_name, "rb") as file:
                    st.download_button(
                        label="📥 Tải video về máy",
                        data=file,
                        file_name=video_file_name,
                        mime="video/mp4"
                    )
                    
        except Exception as e:
            st.error(f"Đã xảy ra lỗi: {str(e)}")

# --- CHÂN TRANG ---
st.divider()
st.caption("Lưu ý: Thời gian tạo video có thể kéo dài từ 1-3 phút tùy thuộc vào độ phức tạp của prompt.")import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import io

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Veo 3 Pro Studio", page_icon="🎬", layout="wide")

st.title("🎬 Veo 3 Video Studio (Image-to-Video)")
st.markdown("Tải ảnh lên để làm nguồn cảm hứng hoặc mô tả bằng văn bản để tạo video.")

# --- SIDEBAR: CẤU HÌNH ---
with st.sidebar:
    st.header("⚙️ Cấu hình")
    api_key = st.text_input("Google API Key:", type="password")
    
    st.divider()
    aspect_ratio = st.selectbox("Tỉ lệ:", ["16:9", "9:16", "1:1"])
    resolution = st.selectbox("Độ phân giải:", ["720p", "1080p"])
    
    st.info("💡 Mẹo: Dùng ảnh tham chiếu giúp AI giữ đúng phong cách nhân vật/bối cảnh.")

# --- GIAO DIỆN CHÍNH ---
col_input, col_preview = st.columns([1, 1])

with col_input:
    prompt = st.text_area("Mô tả video của bạn:", height=100)
    
    # Tính năng mới: Tải ảnh tham chiếu
    uploaded_file = st.file_uploader("Tải ảnh tham chiếu (Tùy chọn):", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Ảnh tham chiếu của bạn", use_container_width=True)

# --- NÚT TẠO VIDEO ---
if st.button("🚀 Bắt đầu tạo Video", use_container_width=True):
    if not api_key:
        st.error("Vui lòng nhập API Key!")
    elif not prompt:
        st.warning("Vui lòng nhập mô tả!")
    else:
        try:
            genai.configure(api_key=api_key)
            
            with st.status("🤖 Veo 3 đang xử lý...", expanded=True) as status:
                # Chuẩn bị dữ liệu đầu vào
                input_data = [prompt]
                
                # Nếu có ảnh, thêm ảnh vào danh sách đầu vào
                if uploaded_file:
                    st.write("Đang tải ảnh lên hệ thống...")
                    # Chuyển đổi file tải lên thành đối tượng PIL Image để gửi đi
                    input_data.append(img)
                
                st.write("Đang tạo video dựa trên dữ liệu của bạn...")
                
                # Gọi API Veo 3
                operation = genai.generate_videos(
                    model="veo-3.1-generate-preview",
                    prompt=input_data, # Gửi cả list gồm [prompt, image]
                    config={
                        "aspect_ratio": aspect_ratio,
                    }
                )
                
                # Chờ đợi (Polling)
                start_time = time.time()
                while not operation.done:
                    elapsed = int(time.time() - start_time)
                    st.write(f"Đang xử lý... ({elapsed} giây)")
                    time.sleep(5)
                
                status.update(label="✅ Hoàn tất!", state="complete")

            # Hiển thị kết quả
            video_result = operation.result()
            video_file_name = f"veo_output_{int(time.time())}.mp4"
            video_result.save(video_file_name)
            
            st.success("Tạo video thành công!")
            st.video(video_file_name)
            
            with open(video_file_name, "rb") as file:
                st.download_button("📥 Tải video về máy", data=file, file_name=video_file_name)
                    
        except Exception as e:
            st.error(f"Lỗi: {str(e)}")
            st.info("Lưu ý: Đảm bảo Model ID 'veo-3.1-generate-preview' khả dụng với tài khoản của bạn.")# Tự động thu gọn sidebar trên màn hình nhỏ của điện thoại
st.set_page_config(
    page_title="Veo 3 Mobile",
    page_icon="🎬",
    initial_sidebar_state="collapsed" 
)