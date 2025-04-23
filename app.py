import streamlit as st
from PIL import Image
import qrcode
import uuid
import os
from io import BytesIO

# Streamlit app setup
st.set_page_config(page_title="QR to PDF Scanner", layout="wide")
st.title("QR to PDF Scanner")

# Function to generate PDF from images
def images_to_pdf(images, output_filename):
    if not images:
        return None
    
    # Convert all images to RGB
    rgb_images = [img.convert('RGB') for img in images]
    
    # Save first image and append others
    pdf_bytes = BytesIO()
    rgb_images[0].save(
        pdf_bytes,
        format='PDF',
        save_all=True,
        append_images=rgb_images[1:],
        quality=100
    )
    pdf_bytes.seek(0)
    return pdf_bytes

# Main app logic
def main():
    tab1, tab2 = st.tabs(["Generate QR", "Upload Images"])
    
    with tab1:
        # Generate QR Code
        session_id = str(uuid.uuid4())[:8]
        session_url = f"https://your-streamlit-app-url.com/?session_id={session_id}"
        
        qr_img = qrcode.make(session_url)
        st.image(qr_img.get_image(), caption="Scan this QR to upload images")
        st.code(session_url)
        
    with tab2:
        # Upload Images
        session_id = st.experimental_get_query_params().get("session_id", [""])[0]
        
        if not session_id:
            st.warning("Please scan the QR code or enter a session ID")
            session_id = st.text_input("Or enter session ID manually:")
            
        if session_id:
            uploaded_files = st.file_uploader(
                "Upload images to convert to PDF",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                images = []
                for file in uploaded_files:
                    try:
                        img = Image.open(file)
                        images.append(img)
                        st.success(f"Processed: {file.name}")
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {e}")
                
                if images:
                    if st.button("Generate PDF"):
                        with st.spinner("Creating PDF..."):
                            pdf_bytes = images_to_pdf(images, f"{session_id}.pdf")
                            
                        st.success("PDF generated successfully!")
                        st.download_button(
                            label="Download PDF",
                            data=pdf_bytes,
                            file_name=f"{session_id}.pdf",
                            mime="application/pdf"
                        )

if __name__ == "__main__":
    main()