# streamlit_app.py
import streamlit as st

def get_file_content_as_string(file_path):
    with open(file_path, 'r', encoding="UTF-8") as file:
        return file.read()

def main():
    readme_text = st.markdown(get_file_content_as_string("README.md"))

if __name__ == "__main__":
    main()
