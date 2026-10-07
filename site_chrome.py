import base64
from pathlib import Path
import streamlit as st
from cart_ui import show_cart_dialog


def _render_site_header() -> None:
    image_data = base64.b64encode(
        Path("assets/Miez e co_header.png").read_bytes()
    ).decode("ascii")
    st.html(f"""
        <div style="
            background-image:
                linear-gradient(rgba(0, 0, 0, 0.25), rgba(0, 0, 0, 0.25)),
                url('data:image/png;base64,{image_data}');
            background-size: cover;
            background-position: top;
            width: 100vw;
            max-width: none;
            margin-left: calc(50% - 50vw);
            margin-top: -60px;
            min-height: 600px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 0;
            text-align: center;
        ">
        </div>
        """)

def _render_navigation_bar(
    home_page,
    collections_page,
    products_page,
    account_page,
    contact_page,
) -> None:
    logo_image = base64.b64encode(
        Path("assets/cat_front.png").read_bytes()
    ).decode("ascii")

    st.html("""
        <style>
        .stMainBlockContainer div:has(> .st-key-top_navigation) {
            position: sticky;
            top: 0;
            z-index: 1000;
            width: 100vw;
            max-width: 100vw;
            margin-left: calc(50% - 50vw);
            margin-top: -6rem;
            box-sizing: border-box;
            padding: 0.5rem 1rem;
            background-color: var(--background-color, #2b3036);
        }
        </style>
        """)
    with st.container(key="top_navigation"):
        logo_nav, main_nav, cart_nav = st.columns(
                [0.45, 3.8, 5.8],
            vertical_alignment="center",
        )
        with logo_nav:
            st.html(f"""
                <a href="/Adm_Dashboard" aria-label="Open admin dashboard">
                    <img
                        src="data:image/png;base64,{logo_image}"
                        alt="Miez & co."
                        style="display:block;width:44px;height:44px;object-fit:contain;"
                    >
                </a>
                """)

        with main_nav:
            with st.container(
                horizontal=True,
                horizontal_alignment="left",
                wrap=False,
            ):
                st.page_link(home_page, width="content")
                st.page_link(collections_page, width="content")
                st.page_link(products_page, width="content")

        with cart_nav:
            cart_quantity = sum(
                item["quantity"]
                for item in st.session_state.get("cart", {}).values()
            )
            with st.container(
                horizontal=True,
                horizontal_alignment="right",
                vertical_alignment="center",
                gap="small",
                wrap=False,
            ):
                if st.button(
                    "Cart",
                    icon=":material/shopping_cart:",
                    key="open_cart_dialog",
                    width="content",
                ):
                    st.session_state["cart_dialog_open"] = True
                if cart_quantity:
                    st.html(f"""
                        <span style="
                            display: inline-flex;
                            align-items: center;
                            justify-content: center;
                            min-width: 1.5rem;
                            height: 1.5rem;
                            padding: 0 0.35rem;
                            box-sizing: border-box;
                            border-radius: 0.35rem;
                            background-color: #f8e3c6;
                            color: #b42318;
                            font-weight: 700;
                            line-height: 1;
                        ">{cart_quantity}</span>
                        """)
                st.page_link(account_page, width="content")
                st.page_link(contact_page, width="content")
            if st.session_state.get("cart_dialog_open"):
                show_cart_dialog()


def render_site_chrome(
    home_page,
    collections_page,
    products_page,
    account_page,
    contact_page,
) -> None:
    _render_navigation_bar(
        home_page,
        collections_page,
        products_page,
        account_page,
        contact_page,
    )
    _render_site_header()


def render_support_categories() -> None:
    st.html("""
        <style>
        .st-key-site_footer {
            position: relative;
            isolation: isolate;
            padding: 1rem 0;
        }
        .st-key-site_footer::before {
            content: "";
            position: absolute;
            z-index: -1;
            left: 50%;
            top: 0;
            bottom: 0;
            width: 100vw;
            transform: translateX(-50%);
            box-sizing: border-box;
            background-color: #24282e;
            border-top: 1px solid rgba(248, 227, 198, 0.45);
        }
        .stMainBlockContainer {
            padding-bottom: 0 !important;
            overflow-x: clip;
        }
        </style>
        """)
    with st.container(key="site_footer"):
        col1, col2 = st.columns(2)
        with col1:
            st.header("Support")
            st.subheader("If you need assistance, you've come to the right place!")
            st.page_link(
                "pages/5_Contact_FAQ.py",
                label="Contact || FAQ || Terms and Conditions",
                icon=":material/arrow_forward:",
                width="stretch",
            )
        with col2:
            st.header("Collections")
            st.subheader("Explore our product collections:")
            st.page_link(
                "pages/1_Collections.py",
                label="Miez & co.",
                icon=":material/arrow_forward:",
                width="stretch",
            )
            st.page_link(
                "pages/1_Collections.py",
                label="Halloween",
                icon=":material/arrow_forward:",
                width="stretch",
            )
            st.page_link(
                "pages/1_Collections.py",
                label="Personalized",
                icon=":material/arrow_forward:",
                width="stretch",
            )
