import streamlit as st
from site_chrome import (
    render_site_chrome,
    render_support_categories,
)

st.set_page_config(layout="wide")
st.session_state.setdefault("cart", {})


def show_home() -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("Meet who we are:")
            st.image("assets/collections/miez_co.png", width="stretch")
            st.caption("Our story page is coming soon.")
    with col2:
        with st.container(border=True):
            st.subheader("Meet our collections:")
            st.image("assets/collections/miez_co.png", width="stretch")
            st.page_link(
                collections_page,
                label="Shop our collections",
                icon=":material/arrow_forward:",
                width="stretch",
            )
    with col3:
        with st.container(border=True):
            st.subheader("Contact us:")
            st.image("assets/collections/miez_co.png", width="stretch")
            st.page_link(
                contactFAQ_page,
                label="FAQ and Contact",
                icon=":material/arrow_forward:",
                width="stretch",
            )
    render_support_categories()
# Configure all pages.
home_page = st.Page(
    show_home,
    title="Home",
    icon=":material/home:",
    default=True,
)
collections_page = st.Page(
    "pages/1_Collections.py",
    title="Collections",
    icon=":material/collections_bookmark:",
)
products_page = st.Page(
    "pages/4_Products.py",
    title="Products",
    icon=":material/collections:",
)
account_page = st.Page(
    "pages/2_Customer_Account.py",
    title="Sign in / Sign up",
    icon=":material/account_circle:",
)
cart_page = st.Page(
    "pages/8_Customer_cart.py",
    title=(
        f"Cart ({sum(item['quantity'] for item in st.session_state.get('cart', {}).values())})"
        if st.session_state.get("cart")
        else "Cart"
    ),
    icon=":material/shopping_cart:",
)
contactFAQ_page = st.Page(
    "pages/5_Contact_FAQ.py",
    title="Contact & FAQ",
    icon=":material/phone:",
)
admin_page = st.Page(
    "pages/3_Adm_Dashboard.py",
    title="Admin",
    url_path="Adm_Dashboard",
    icon=":material/dashboard:",
)

navigation = st.navigation(
    [
        home_page,
        collections_page,
        products_page,
        account_page,
        cart_page,
        contactFAQ_page,
        admin_page,
    ],
    position="hidden",
)

render_site_chrome(
    home_page,
    collections_page,
    products_page,
    account_page,
    contactFAQ_page,
)
navigation.run()
