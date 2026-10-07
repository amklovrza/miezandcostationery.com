import streamlit as st
from site_chrome import render_support_categories

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.subheader("Miez & co.")
        st.image("assets/collections/miez_co.png", width="stretch")
        st.page_link(
            "pages/4_Products.py",
            label="Shop this collection",
            icon=":material/arrow_forward:",
            width="stretch",
            query_params={"collection": "Miez & co."},
        )

    with st.container(border=True):
        st.subheader("Birthday")
        st.image("assets/miez_co.png", width="stretch")
        st.page_link(
            "pages/4_Products.py",
            label="COMMING SOON",
            icon=":material/arrow_forward:",
            width="stretch",
            query_params={"collection": "Birthday"},
        )

    with st.container(border=True):
            st.subheader("Easter")
            st.image("assets/miez_co.png", width="stretch")
            st.page_link(
                "pages/4_Products.py",
                label="COMMING SOON",
                icon=":material/arrow_forward:",
                width="stretch",
                query_params={"collection": "Easter"},
            )

with col2:
    with st.container(border=True):
        st.subheader("Halloween")
        st.image("assets/collections/halloween_stickers.png", width="stretch")
        st.page_link(
            "pages/4_Products.py",
            label="Shop this collection",
            icon=":material/arrow_forward:",
            width="stretch",
            query_params={"collection": "Halloween"},
        )

    with st.container(border=True):
        st.subheader("Christmas")
        st.image("assets/miez_co.png", width="stretch")
        st.page_link(
            "pages/4_Products.py",
            label="COMMING SOON",
            icon=":material/arrow_forward:",
            width="stretch",
            query_params={"collection": "Christmas"},
        )

    with st.container(border=True):
            st.subheader("Valentines")
            st.image("assets/miez_co.png", width="stretch")
            st.page_link(
                "pages/4_Products.py",
                label="COMMING SOON",
                icon=":material/arrow_forward:",
                width="stretch",
                query_params={"collection": "Valentines"},
            )

with col3:
    with st.container(border=True):
        st.subheader("Personalized")
        st.image("assets/miez_co.png", width="stretch")
        st.page_link("pages/4_Products.py", 
                     label="Shop this collection", 
                     icon=":material/arrow_forward:", 
                     width="stretch", 
                     query_params={"collection": "Personalized"}
        )

    with st.container(border=True):
        st.subheader("Back to school")
        st.image("assets/miez_co.png", width="stretch")
        st.page_link(
            "pages/4_Products.py",
            label="COMMING SOON",
            icon=":material/arrow_forward:",
            width="stretch",
            query_params={"collection": "Back to school"},
        )

    with st.container(border=True):
        st.subheader("Limited edition kits")
        st.image("assets/miez_co.png", width="stretch")
        st.page_link(
            "pages/4_Products.py",
            label="COMMING SOON",
            icon=":material/arrow_forward:",
            width="stretch",
            query_params={"collection": "Limited edition kits"},
        )

render_support_categories()