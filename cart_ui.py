import os

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


STRIPE_PRICE_ENV_VARS = {
    "personalized_notebook_grey_wolf": "STRIPE_PRICE_ID_NOTEBOOK_PERSONALIZED_GREY_WOLF",
    "personalized_notebook_otter": "STRIPE_PRICE_ID_NOTEBOOK_PERSONALIZED_OTTER",
    "personalized_notepad_bear": "STRIPE_PRICE_ID_NOTEPAD_PERSONALIZED_BEAR",
    "personalized_notepad_otter": "STRIPE_PRICE_ID_NOTEPAD_PERSONALIZED_OTTER",
    "personalized_bookmark_otter": "STRIPE_PRICE_ID_BOOKMARK_PERSONALIZED_OTTER",
    "personalized_bookmark_bear": "STRIPE_PRICE_ID_BOOKMARK_PERSONALIZED_BEAR",
    "personalized_bookmark_grey_wolf": "STRIPE_PRICE_ID_BOOKMARK_PERSONALIZED_GREY_WOLF",
    "miezandco_notebook_small": "STRIPE_PRICE_ID_NOTEBOOK_SMALL",
    "miezandco_notebook_medium": "STRIPE_PRICE_ID_NOTEBOOK_MEDIUM",
    "miezandco_notebook_recipe": "STRIPE_PRICE_ID_NOTEBOOK_RECIPE",
    "miezandco_notepad_A5": "STRIPE_PRICE_ID_NOTEPAD_A5",
    "miezandco_notepad_A6": "STRIPE_PRICE_ID_NOTEPAD_A6",
    "miezandco_notepad_grocery": "STRIPE_PRICE_ID_NOTEPAD_GROCERY",
    "miezandco_sticker": "STRIPE_PRICE_ID_STICKER",
    "miezandco_bookmark": "STRIPE_PRICE_ID_BOOKMARK",
    "halloween_notebook": "STRIPE_PRICE_ID_HALLOWEEN_NOTEBOOK",
    "halloween_notepad": "STRIPE_PRICE_ID_HALLOWEEN_NOTEPAD",
    "halloween_stickers": "STRIPE_PRICE_ID_HALLOWEEN_STICKERS",
    "halloween_bookmark": "STRIPE_PRICE_ID_HALLOWEEN_BOOKMARK",
}


def stripe_setting(name, stripe_secrets):
    return os.environ.get(name) or stripe_secrets.get(name)


def add_to_cart(product_id, name, unit_price, quantity):
    cart = st.session_state.setdefault("cart", {})
    item = cart.get(product_id)
    if item:
        item["quantity"] += quantity
    else:
        cart[product_id] = {
            "name": name,
            "unit_price": unit_price,
            "quantity": quantity,
        }


def remove_from_cart(product_id):
    st.session_state.cart.pop(product_id, None)
    st.rerun()


def adjust_cart_quantity(product_id, adjustment):
    item = st.session_state.cart.get(product_id)
    if item:
        item["quantity"] += adjustment
        st.rerun()


def close_cart_dialog():
    st.session_state["cart_dialog_open"] = False


@st.dialog("Your cart", width="large", on_dismiss=close_cart_dialog)
def show_cart_dialog():
    cart = st.session_state.setdefault("cart", {})
    if not cart:
        st.info("Your cart is empty.")
        return

    cart_total = 0.0
    for item_id, item in cart.items():
        item_total = item["unit_price"] * item["quantity"]
        cart_total += item_total
        with st.container(border=True):
            st.write(f"**{item['name']}**")
            st.write(f"Unit price: ${item['unit_price']:.2f}")
            quantity_columns = st.columns([1, 2, 1, 2])
            with quantity_columns[0]:
                st.button(
                    "-",
                    key=f"decrease_{item_id}",
                    disabled=item["quantity"] <= 1,
                    on_click=adjust_cart_quantity,
                    args=(item_id, -1),
                )
            with quantity_columns[1]:
                st.write(f"Quantity: {item['quantity']}")
            with quantity_columns[2]:
                st.button(
                    "+",
                    key=f"increase_{item_id}",
                    on_click=adjust_cart_quantity,
                    args=(item_id, 1),
                )
            with quantity_columns[3]:
                st.button(
                    "Remove",
                    key=f"remove_{item_id}",
                    on_click=remove_from_cart,
                    args=(item_id,),
                )
            st.write(f"Subtotal: ${item_total:.2f}")

    st.divider()
    st.write(f"**Total: ${cart_total:.2f}**")
    logged_in_email = st.session_state.get("logged_in_email")
    if not logged_in_email:
        st.info("Log in or create an account before checkout.")
        if st.button(
            "Log in or create an account",
            icon=":material/login:",
            key="cart_login",
        ):
            close_cart_dialog()
            st.switch_page("pages/2_Customer_Account.py")
        return

    if not st.button(
        "Continue to secure checkout",
        key="cart_checkout",
        icon=":material/lock:",
    ):
        return

    try:
        stripe_secrets = st.secrets.get("stripe", {})
    except StreamlitSecretNotFoundError:
        stripe_secrets = {}

    stripe_secret_key = stripe_setting("STRIPE_SECRET_KEY", stripe_secrets)
    success_url = stripe_setting("STRIPE_SUCCESS_URL", stripe_secrets)
    cancel_url = stripe_setting("STRIPE_CANCEL_URL", stripe_secrets)
    price_ids = {
        item_id: stripe_setting(environment_variable, stripe_secrets)
        for item_id, environment_variable in STRIPE_PRICE_ENV_VARS.items()
    }
    missing_settings = []
    if not stripe_secret_key:
        missing_settings.append("STRIPE_SECRET_KEY")
    for item_id in cart:
        if not price_ids.get(item_id):
            missing_settings.append(
                STRIPE_PRICE_ENV_VARS.get(
                    item_id, f"Stripe price ID for {item_id}"
                )
            )
    if not success_url:
        missing_settings.append("STRIPE_SUCCESS_URL")
    if not cancel_url:
        missing_settings.append("STRIPE_CANCEL_URL")

    if missing_settings:
        st.error(
            "Checkout isn't configured. Set these environment "
            "variables or Stripe secrets: "
            + ", ".join(missing_settings)
            + ". The Stripe Price ID must match the price shown "
            "in the catalog."
        )
        return

    import stripe

    stripe.api_key = stripe_secret_key
    line_items = [
        {
            "price": price_ids[item_id],
            "quantity": int(item["quantity"]),
        }
        for item_id, item in cart.items()
    ]
    try:
        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=line_items,
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=logged_in_email,
        )
    except stripe.StripeError as error:
        st.error(
            "Stripe couldn't start checkout: "
            + (error.user_message or str(error))
        )
    else:
        st.link_button("Open secure checkout", checkout_session.url)
