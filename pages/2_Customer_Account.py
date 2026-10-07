import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import hashlib
import hmac
import os
import secrets
from streamlit.errors import StreamlitSecretNotFoundError
from site_chrome import render_support_categories

PASSWORD_ITERATIONS = 600_000
CUSTOMER_DB = Path(__file__).with_name("DBcustomers.csv")
CUSTOMER_CART_DB = Path(__file__).with_name("DBcustomer_carts.csv")
PASSWORD_SALT_COLUMN = "Password Salt"
PASSWORD_HASH_COLUMN = "Password Hash"
CUSTOMER_FIELDS = [
    "Date",
    "Name",
    "Email",
    "Phone",
    "Address",
    "Unit/Apartment number",
    "City",
    "State",
    "Postal Code",
    "Preferred Payment Method",
]
PRODUCTS = ["Notepad", "Notebook", "Bookmarker", "Sticker"]
PAYMENT_METHODS = ["Credit/debit card", "PayPal", "Venmo", "Zelle"]
CUSTOMER_CART_COLUMNS = ["Email", "Product", "Quantity"]
STRIPE_PRICE_ENV_VARS = {
    "Notepad": "STRIPE_PRICE_ID_BLOQUINHO",
    "Bookmarker": "STRIPE_PRICE_ID_MARCA_PAGINA",
    "Notebook": "STRIPE_PRICE_ID_CADERNO",
    "Sticker": "STRIPE_PRICE_ID_ADESIVOS",
}
COUNTRY_CALLING_CODES = [
    ("United States / Canada (+1)", "+1"),
    ("Brazil (+55)", "+55"),
    ("United Kingdom (+44)", "+44"),
    ("Mexico (+52)", "+52"),
    ("France (+33)", "+33"),
    ("Germany (+49)", "+49"),
    ("India (+91)", "+91"),
    ("Australia (+61)", "+61"),
    ("Japan (+81)", "+81"),
]


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return salt.hex(), password_hash.hex()


def password_matches(password: str, salt_hex: str, password_hash_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    _, candidate_hash = hash_password(password, salt)
    return hmac.compare_digest(candidate_hash, password_hash_hex)


def stripe_setting(name: str, stripe_secrets: dict) -> str | None:
    return os.environ.get(name) or stripe_secrets.get(name)

tabela_cliente = pd.read_csv(CUSTOMER_DB)
for column in (*CUSTOMER_FIELDS, PASSWORD_SALT_COLUMN, PASSWORD_HASH_COLUMN):
    if column not in tabela_cliente.columns:
        tabela_cliente[column] = ""

if CUSTOMER_CART_DB.exists():
    tabela_carrinho = pd.read_csv(CUSTOMER_CART_DB)
else:
    tabela_carrinho = pd.DataFrame(columns=CUSTOMER_CART_COLUMNS)

if st.session_state.get("logged_in_email"):
    logged_in_email = st.session_state["logged_in_email"]
    customer = tabela_cliente[
        tabela_cliente["Email"].astype(str).str.strip().str.casefold()
        == logged_in_email.casefold()
    ]
    if customer.empty:
        del st.session_state["logged_in_email"]
        st.rerun()

    customer = customer.iloc[0]
    st.success(f"Welcome, {customer['Name']}!")

    st.write("## Your registration information")
    profile_columns = st.columns(2)
    profile_fields = [
        ("Name", "Name"),
        ("Email", "Email"),
        ("Cellphone", "Phone"),
        ("Address", "Address"),
        ("Unit/Apartment", "Unit/Apartment number"),
        ("City", "City"),
        ("State", "State"),
        ("Postal code", "Postal Code"),
        ("Registration date", "Date"),
    ]
    for index, (label, field) in enumerate(profile_fields):
        value = customer[field]
        if pd.isna(value) or not str(value).strip():
            value = "Not provided"
        profile_columns[index % 2].write(f"**{label}:** {value}")

    st.write("## Preferred payment method")
    st.caption(
        "For card payments, card details are entered on Stripe's secure checkout "
        "page. This app does not collect or store card numbers or security codes."
    )
    with st.form("payment_method_form"):
        current_payment_method = customer["Preferred Payment Method"]
        payment_index = (
            PAYMENT_METHODS.index(current_payment_method)
            if current_payment_method in PAYMENT_METHODS
            else 0
        )
        preferred_payment_method = st.selectbox(
            "Choose a payment method for checkout",
            PAYMENT_METHODS,
            index=payment_index,
        )
        save_payment_method = st.form_submit_button("Save payment method")

    if save_payment_method:
        customer_rows = tabela_cliente.index[
            tabela_cliente["Email"].astype(str).str.strip().str.casefold()
            == logged_in_email.casefold()
        ]
        tabela_cliente.loc[customer_rows, "Preferred Payment Method"] = (
            preferred_payment_method
        )
        tabela_cliente.to_csv(CUSTOMER_DB, index=False)
        st.success("Preferred payment method saved.")
        st.rerun()

    st.write("## Your cart")
    st.caption(
        "Add products below. Prices have not been set in the catalog yet, so this cart "
        "does not calculate a total or process payment."
    )
    cart_rows = tabela_carrinho[
        tabela_carrinho["Email"].astype(str).str.strip().str.casefold()
        == logged_in_email.casefold()
    ]
    with st.form("add_to_cart_form"):
        product_to_add = st.selectbox("Product", PRODUCTS)
        quantity_to_add = st.number_input("Quantity", min_value=1, step=1)
        add_to_cart = st.form_submit_button("Add to cart")

    if add_to_cart:
        matching_cart_rows = tabela_carrinho.index[
            tabela_carrinho["Email"].astype(str).str.strip().str.casefold().eq(
                logged_in_email.casefold()
            )
            & tabela_carrinho["Product"].eq(product_to_add)
        ]
        if len(matching_cart_rows):
            row = matching_cart_rows[0]
            tabela_carrinho.at[row, "Quantity"] = (
                int(tabela_carrinho.at[row, "Quantity"]) + int(quantity_to_add)
            )
        else:
            new_cart_item = pd.DataFrame(
                [
                    {
                        "Email": logged_in_email,
                        "Product": product_to_add,
                        "Quantity": int(quantity_to_add),
                    }
                ]
            )
            tabela_carrinho = pd.concat(
                [tabela_carrinho, new_cart_item], ignore_index=True
            )
        tabela_carrinho.to_csv(CUSTOMER_CART_DB, index=False)
        st.rerun()

    cart_rows = tabela_carrinho[
        tabela_carrinho["Email"].astype(str).str.strip().str.casefold()
        == logged_in_email.casefold()
    ]
    if cart_rows.empty:
        st.info("Your cart is empty.")
    else:
        st.dataframe(
            cart_rows[["Product", "Quantity"]].reset_index(drop=True),
            hide_index=True,
            width="stretch",
        )
        cart_product_to_remove = st.selectbox(
            "Remove a product",
            cart_rows["Product"].tolist(),
            key="cart_product_to_remove",
        )
        remove_col, clear_col = st.columns(2)
        with remove_col:
            if st.button("Remove selected product"):
                tabela_carrinho = tabela_carrinho.drop(
                    cart_rows[cart_rows["Product"] == cart_product_to_remove].index
                )
                tabela_carrinho.to_csv(CUSTOMER_CART_DB, index=False)
                st.rerun()
        with clear_col:
            if st.button("Clear cart"):
                tabela_carrinho = tabela_carrinho.drop(cart_rows.index)
                tabela_carrinho.to_csv(CUSTOMER_CART_DB, index=False)
                st.rerun()

        if preferred_payment_method == "Credit/debit card":
            st.write("### Pay by card")
            if st.button("Continue to secure card checkout"):
                try:
                    stripe_secrets = st.secrets.get("stripe", {})
                except StreamlitSecretNotFoundError:
                    stripe_secrets = {}

                stripe_secret_key = stripe_setting(
                    "STRIPE_SECRET_KEY", stripe_secrets
                )
                stripe_price_ids = {
                    product: stripe_setting(environment_variable, stripe_secrets)
                    for product, environment_variable in STRIPE_PRICE_ENV_VARS.items()
                }
                missing_settings = []
                if not stripe_secret_key:
                    missing_settings.append("STRIPE_SECRET_KEY")
                for product in cart_rows["Product"].unique():
                    price_environment_variable = STRIPE_PRICE_ENV_VARS.get(product)
                    if (
                        price_environment_variable
                        and not stripe_price_ids.get(product)
                    ):
                        missing_settings.append(price_environment_variable)
                success_url = stripe_setting("STRIPE_SUCCESS_URL", stripe_secrets)
                cancel_url = stripe_setting("STRIPE_CANCEL_URL", stripe_secrets)
                if not success_url:
                    missing_settings.append("STRIPE_SUCCESS_URL")
                if not cancel_url:
                    missing_settings.append("STRIPE_CANCEL_URL")

                if missing_settings:
                    st.warning(
                        "Secure card checkout isn't configured yet. Set these "
                        "environment variables to enable it: "
                        + ", ".join(missing_settings)
                        + ". Create the product prices in Stripe and use their "
                        "Price IDs. Don't put card numbers or security codes here."
                    )
                else:
                    import stripe

                    stripe.api_key = stripe_secret_key
                    line_items = [
                        {
                            "price": stripe_price_ids[row["Product"]],
                            "quantity": int(row["Quantity"]),
                        }
                        for _, row in cart_rows.iterrows()
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
                        st.link_button(
                            "Open Stripe secure checkout", checkout_session.url
                        )

    if st.button("Log out"):
        del st.session_state["logged_in_email"]
        st.rerun()
else:
    st.html("""
        <style>
        .st-key-registration_form_style input,
        .st-key-registration_form_style textarea,
        .st-key-login_form_style input,
        .st-key-registration_form_style [data-testid="stTextInputRootElement"],
        .st-key-login_form_style [data-testid="stTextInputRootElement"] {
            background-color: #FAEBD7 !important;
            color: #B6322E !important;
        }

        .st-key-registration_form_style button[aria-label="Show password"],
        .st-key-registration_form_style button[aria-label="Hide password"],
        .st-key-login_form_style button[aria-label="Show password"],
        .st-key-login_form_style button[aria-label="Hide password"] {
            color: #B6322E !important;
        }

        .st-key-registration_form_style [data-testid="stDateInputField"],
        .st-key-registration_form_style [data-testid="stSelectbox"] [role="group"] {
            background-color: #FAEBD7 !important;
        }

        .st-key-registration_form_style [data-testid="stDateInputField"] *,
        .st-key-registration_form_style [data-baseweb="select"] *,
        .st-key-registration_form_style [data-testid="stSelectbox"] input,
        .st-key-registration_form_style [data-testid="stSelectbox"] button,
        .st-key-registration_form_style [data-testid="stSelectbox"] svg,
        .st-key-registration_form_style [data-testid="stSelectbox"] svg path,
        .st-key-login_form_style input::placeholder {
            color: #B6322E !important;
        }

        .st-key-registration_form_style [data-testid="stDateInput"] input[type="date"] {
            color-scheme: light;
        }
        </style>
    """)
    col1, col2 = st.columns(2)

    with col1:
        st.write("## Create an account")
        with st.container(key="registration_form_style"):
            with st.form("register_form"):
                registration_date = st.date_input("Date", value=pd.Timestamp("today"), format="DD/MM/YYYY")
                name = st.text_input("Name")
                registration_email = st.text_input("Email", type="email")
                phone_col1, phone_col2 = st.columns([1, 2])
                with phone_col1:
                    country_calling_code = st.selectbox("Country code", COUNTRY_CALLING_CODES, format_func=lambda option: option[0],)[1]
                with phone_col2:
                    phone = st.text_input("Cellphone number")
                    address = st.text_input("Address")
                    address2 = st.text_input("House/Unit/Apartment number")
                    city = st.text_input("City")
                    state = st.text_input("State")
                    postal_code = st.text_input("Postal Code")
                    registration_password = st.text_input("Password", type="password")
                    confirm_password = st.text_input("Confirm password", type="password")
                    register = st.form_submit_button("Register")

        if register:
            email = registration_email.strip().casefold()
            if not name.strip() or not email or not phone.strip() or not address or not address2 or not city or not state or not postal_code or not registration_password:
                st.error("Please complete all field.")
            elif len(registration_password) < 8:
                st.error("Password must be at least 8 characters long.")
            elif registration_password != confirm_password:
                st.error("The passwords do not match.")
            else:
                matching_rows = tabela_cliente.index[
                    tabela_cliente["Email"].astype(str).str.strip().str.casefold()
                    == email
                ]
                if len(matching_rows) and pd.notna(
                    tabela_cliente.at[matching_rows[0], PASSWORD_HASH_COLUMN]
                ) and tabela_cliente.at[matching_rows[0], PASSWORD_HASH_COLUMN]:
                    st.error("An account with this email already exists.")
                else:
                    salt, password_hash = hash_password(registration_password)
                    if len(matching_rows):
                        # Existing CSV customers can set a password without creating a duplicate.
                        row = matching_rows[0]
                        tabela_cliente.at[row, PASSWORD_SALT_COLUMN] = salt
                        tabela_cliente.at[row, PASSWORD_HASH_COLUMN] = password_hash
                        tabela_cliente.at[row, "Date"] = registration_date
                        tabela_cliente.at[row, "Name"] = name.strip()
                        tabela_cliente.at[row, "Phone"] = (
                            f"{country_calling_code} {phone.strip()}"
                        )
                        tabela_cliente.at[row, "Address"] = address.strip()
                        tabela_cliente.at[row, "Unit/Apartment number"] = (
                            address2.strip()
                        )
                        tabela_cliente.at[row, "City"] = city.strip()
                        tabela_cliente.at[row, "State"] = state.strip()
                        tabela_cliente.at[row, "Postal Code"] = postal_code.strip()
                        message = "Password set for your existing customer account."
                    else:
                        new_customer = {
                            "Date": registration_date,
                            "Name": name.strip(),
                            "Email": email,
                            "Phone": f"{country_calling_code} {phone.strip()}",
                            "Address": address.strip(),
                            "Unit/Apartment number": address2.strip(),
                            "City": city.strip(),
                            "State": state.strip(),
                            "Postal Code": postal_code.strip(),
                            PASSWORD_SALT_COLUMN: salt,
                            PASSWORD_HASH_COLUMN: password_hash,
                        }
                        tabela_cliente = pd.concat(
                            [tabela_cliente, pd.DataFrame([new_customer])],
                            ignore_index=True,
                        )
                        message = "You are registered and can now log in."
                    tabela_cliente.to_csv(CUSTOMER_DB, index=False)
                    st.success(message)

    with col2:
        st.write("## Already a customer?")
        with st.container(key="login_form_style"):
            with st.form("login_form"):
                login_email = st.text_input("Email", type="email", key="login_email")
                login_password = st.text_input(
                    "Password", type="password", key="login_password"
                )
                login = st.form_submit_button("Login")

        if login:
            email = login_email.strip().casefold()
            matching_customer = tabela_cliente[
                tabela_cliente["Email"].astype(str).str.strip().str.casefold()
                == email
            ]
            if matching_customer.empty:
                st.error("Invalid email or password.")
            else:
                customer = matching_customer.iloc[0]
                salt = customer[PASSWORD_SALT_COLUMN]
                password_hash = customer[PASSWORD_HASH_COLUMN]
                if (
                    pd.isna(salt)
                    or pd.isna(password_hash)
                    or not salt
                    or not password_hash
                    or not password_matches(login_password, salt, password_hash)
                ):
                    st.error("Invalid email or password.")
                else:
                    st.session_state["logged_in_email"] = email
                    st.rerun()

render_support_categories()
