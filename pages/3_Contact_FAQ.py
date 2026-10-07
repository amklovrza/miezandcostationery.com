from site_chrome import render_support_categories
import streamlit as st
import base64
import pandas as pd
from pathlib import Path
from site_chrome import render_support_categories

MESSAGES_DB = "pages/DBmessages.csv"
tabela_mensagens = pd.read_csv(MESSAGES_DB)
your_name = tabela_mensagens["Name"]
your_email = tabela_mensagens["Email"]
your_phone = tabela_mensagens["Phone"]
your_message = tabela_mensagens["Message"]

# HTML WITH COLORS
st.html("""
    <style>
    .st-key-contact_form input,
    .st-key-contact_form textarea {
        background-color: #f8e3c6 !important;
        color: #b42318 !important;
        -webkit-text-fill-color: #b42318 !important;
        caret-color: #b42318 !important;
    }
    </style>
""")

# database de mensagens
tabela_mensagens = pd.read_csv(MESSAGES_DB)
nome_cliente = tabela_mensagens["Name"]
email_cliente = tabela_mensagens["Email"]
telefone_cliente = tabela_mensagens["Phone"]
mensagem = tabela_mensagens["Message"]

col1, col2 = st.columns(2)
with col1:
    st.header("Contact Us")
    st.write("Have questions? We're here to help!")
    with st.container(key="contact_form"):
        nome_cliente = st.text_input("Your Name")
        email_cliente = st.text_input("Your Email")
        telefone_cliente = st.text_input("Your Phone number")
        mensagem = st.text_area("Your Message", height=100)
        botao_customer_message = st.button("Send Message")
    if botao_customer_message:
        nova_mensagem = [nome_cliente, email_cliente, telefone_cliente, mensagem]
        tabela_mensagens.loc[len(tabela_mensagens)] = nova_mensagem
        tabela_mensagens.to_csv(MESSAGES_DB, index=False)
        st.success("Message sent successfully!")


with col2:
    st.header("Frequently Asked Questions")
    st.write("Find answers to common questions about our products and services:")
    st.markdown("- **How do I track my order?**", unsafe_allow_html=True)
    st.markdown("- **What is your return policy?**", unsafe_allow_html=True)
    st.markdown("- **Do you offer international shipping?**", unsafe_allow_html=True)

render_support_categories()