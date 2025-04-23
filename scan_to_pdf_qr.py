import os
import uuid
from PIL import Image
import qrcode
import streamlit as st

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def main():
    st.title("Scan to PDF with QR Code")
    
    # Create a new session when the app starts or refreshes
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.images = []
    
    # Generate QR code URL (using Streamlit's URL)
    session_url = f"{st.experimental_get_query_params().get('url', [''])[0]}/?session_id={st.session_state.session_id}"
    
    # Display QR code
    st.subheader("Scan this QR code to upload images:")
    qr_img = qrcode.make(session_url)
    st.image(qr_img.get_image(), caption="Scan to upload images", width=200)
    
    # File uploader
    st.subheader("Or upload images directly:")
    uploaded_files = st.file_uploader(
        "Choose images to convert to PDF",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.session_state.images = []
        for file in uploaded_files:
            try:
                img = Image.open(file).convert('RGB')
                st.session_state.images.append(img)
                st.success(f"Processed: {file.name}")
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")
    
    # Generate PDF button
    if st.button("Generate PDF") and st.session_state.images:
        pdf_path = os.path.join(UPLOAD_FOLDER, f"{st.session_state.session_id}.pdf")
        try:
            st.session_state.images[0].save(
                pdf_path,
                save_all=True,
                append_images=st.session_state.images[1:],
                quality=100
            )
            
            # Offer PDF download
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download PDF",
                    data=f,
                    file_name="scanned_document.pdf",
                    mime="application/pdf"
                )
            
            # Clean up
            os.remove(pdf_path)
        except Exception as e:
            st.error(f"Failed to generate PDF: {str(e)}")

if __name__ == '__main__':
    main()
