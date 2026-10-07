# Terminal -> pip install streamlit pandas plotly
import streamlit as st
from cart_ui import add_to_cart
from site_chrome import render_support_categories

st.session_state.setdefault("cart", {})

PRODUCTS = [
    {
        "id": "personalized_notebook_grey_wolf",
        "name": "Grey wolf notebook",
        "collection": "Personalized",
        "image": "assets/products/notebook_personalized.png",
        "price": 20.00,
    },
    {
        "id": "personalized_notebook_otter",
        "name": "Otter notebook",
        "collection": "Personalized",
        "image": "assets/products/notebook_personalized2.png",
        "price": 20.00,
    },
    {   "id": "Miez_notebook", 
        "name": "Notebook", 
        "collection": "Miez & co.", 
        "image": "assets/products/notebook_miez1.png",
        "price": 20.00
    },
    {
        "id": "Miez_notebook_recipe",
        "name": "Notebook Recipe",
        "collection": "Miez & co.",
        "image": "assets/products/recipe1.png",
        "price": 20.00
    },
    {
        "id": "Miez_notebook_recipe2",
        "name": "Notebook Recipe²",
        "collection": "Miez & co.",
        "image": "assets/products/recipe_2.png",
        "price": 20.00
    },
    {
        "id": "personalized_notepad_bear",
        "name": "Bear notepad",
        "collection": "Personalized",
        "image": "assets/products/notepad_personalized1.png",
        "price": 20.00,
    },
    {
        "id": "personalized_notepad_otter",
        "name": "Otter notepad",
        "collection": "Personalized",
        "image": "assets/products/notepad_personalized2a.png",
        "price": 20.00,
    },
    {
        "id": "Miez_notepad_cat",
        "name": "Notepad",
        "collection": "Miez & co.",
        "image": "assets/products/mini_notepad_cozy.png",
        "price": 20.00
    },
    {
        "id": "Halloween_notepad",
        "name": "Vampire Notepad",
        "collection": "Halloween",
        "image": "assets/products/mini_notepad_miez1.png",
        "price": 20.00
    },
    {
        "id": "Japan_notepad",
        "name": "Japan Notepad",
        "collection": "Miez & co.",
        "image": "assets/products/mini_notepad3a.png",
        "price": 20.00
    },
    {
        "id": "Croissant_notepad",
        "name": "Croissant Notepad",
        "collection": "Miez & co.",
        "image": "assets/products/mini_notepad4a.png",
        "price": 20.00
    },
    {
        "id": "Sleepy_notepad",
        "name": "Sleepy Notepad",
        "collection": "Miez & co.",
        "image": "assets/products/mini_notepad5a.png",
        "price": 20.00
    },
    {
        "id": "Ghost_notepad",
        "name": "Ghost Notepad",
        "collection": "Halloween",
        "image": "assets/products/mini_notepad6a.png",
        "price": 20.00
    },
    {
        "id": "Halloween_stickers",
        "name": "Halloween Stickers",
        "collection": "Halloween",
        "image": "assets/products/halloween_stickers2a.png",
        "price": 20.00
    },
]

PRODUCTS_BY_ID = {product["id"]: product for product in PRODUCTS}

@st.dialog("Product details")
def show_product_details(product_id):
    product = PRODUCTS_BY_ID[product_id]
    st.image(product["image"], width="stretch")
    st.write(f"**{product['name']}**")
    st.caption(f"Collection: {product['collection']}")
    st.write(f"Unit price: ${product['price']:.2f}")
    quantity = st.number_input(
        "Quantity",
        min_value=1,
        step=1,
        key=f"product_quantity_{product_id}",
    )
    st.write(f"Total: ${product['price'] * quantity:.2f}")

    if st.button(
        "Add to cart",
        key=f"add_to_cart_{product_id}",
        type="primary",
    ):
        add_to_cart(
            product_id,
            product["name"],
            product["price"],
            quantity,
        )
        st.rerun(scope="app")


# Shows which collection is currently being displayed.
collection_filter = st.query_params.get("collection", "All collections")
collection_options = sorted({product["collection"] for product in PRODUCTS})
if collection_filter not in collection_options and collection_filter != "All collections":
    collection_options.append(collection_filter)
filter_options = ["All collections", *collection_options]

selected_collection = st.segmented_control(
    "Filter by collection",
    options=filter_options,
    default=collection_filter,
    key=f"product_collection_filter_{collection_filter}",
)
if selected_collection is None or selected_collection == "All collections":
    st.query_params.pop("collection", None)
    collection_filter = "All collections"
else:
    st.query_params["collection"] = selected_collection
    collection_filter = selected_collection

if collection_filter == "All collections":
    st.caption("Showing all products")
else:
    st.caption(f"Showing products in the **{collection_filter}** collection")

visible_products = [
    product
    for product in PRODUCTS
    if collection_filter == "All collections"
    or product["collection"] == collection_filter
]

if visible_products:
    columns = st.columns(3)
    for index, product in enumerate(visible_products):
        with columns[index % 3]:
            with st.container(border=True):
                st.image(product["image"], width="stretch")
                if st.button(
                    "View product",
                    key=f"view_{product['id']}",
                    width="stretch",
                ):
                    show_product_details(product["id"])
                st.subheader(product["name"])
                st.caption(f"Collection: {product['collection']}")
else:
    st.info(f"There are no products in the {collection_filter} collection yet.")

render_support_categories()
