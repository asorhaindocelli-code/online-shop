from flask import Flask, render_template, request, redirect, url_for, abort, session
from setup_database import get_db_connection

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/products")
def products():
    search = request.args.get("search", "")
    sort = request.args.get("sort", "")

    conn = get_db_connection()
    query = "SELECT * FROM Product"
    parameters = []

    if search:
        query += " WHERE name LIKE ?"
        parameters.append("%" + search + "%")

    if sort == "name":
        query += " ORDER BY name ASC"
    elif sort == "price_low":
        query += " ORDER BY price ASC"
    elif sort == "price_high":
        query += " ORDER BY price DESC"


    products = conn.execute(query, parameters).fetchall()
    conn.close()

    return render_template("products.html", products=products,search=search, sort=sort)

@app.route("/add_product", methods=["GET","POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        stock = request.form["stock"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO Product (name, description, price, stock) VALUES (?, ?, ?, ?)",
            (name, description, price, stock)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("products"))

    return render_template("add_product.html")

@app.route("/edit_product/<int:id>",methods=["GET","POST"])
def edit_product(id):
    conn = get_db_connection()

    product = conn.execute(
        "SELECT * FROM Product WHERE productID = ?",
        (id,)
    ).fetchone()

    if request.method =="POST":
        name= request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        stock = request.form["stock"]

        conn.execute(
            "UPDATE Product SET name = ?, description = ?, price = ?, stock = ? WHERE productID = ?",
            (name, description, price, stock, id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("products"))

    conn.close()
    return render_template("edit_product.html", product=product)

@app.route("/delete_product/<int:id>")
def delete_product(id):
    conn = get_db_connection()

    conn. execute(
        "DELETE FROM Product WHERE productID = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("products"))

@app.route("/product/<int:id>")
def product_detail(id):
    conn = get_db_connection()

    product = conn.execute(
        "SELECT * FROM Product WHERE productID = ?",
        (id,)
    ).fetchone()

    conn.close()

    if product is None:
        abort(404)

    return render_template("product_detail.html", product=product)

@app.route("/add_to_basket/<int:id>")
def add_to_basket(id):
    basket = session.get("basket", {})

    product_id = str(id)

    if product_id in basket:
        basket[product_id] = basket[product_id] +1
    else:
        basket[product_id] = 1

    session["basket"] = basket
    return redirect(url_for("basket"))

@app.route("/basket")
def basket():
    basket = session.get("basket", {})
    basket_items = []
    total = 0

    conn = get_db_connection()

    for product_id, quantity in basket.items():
        product = conn.execute(
            "SELECT * FROM Product WHERE productID = ?",
            (product_id,)
        ).fetchone()

        if product:
            subtotal = product["price"] * quantity
            total = total + subtotal

            basket_items.append({
                "productID": product["productID"],
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
                "subtotal": subtotal
            })

        conn.close()
        return render_template("basket.html",basket_items=basket_items,total=total)
    @app.route("/remove_from_basket/<int:id>")
    def remove_from_basket(id):
        basket = session.get("basket", {})
        product_id = str(id)

        if product_id in basket:
            basket.pop(product_id)

        session["basket"] = basket
        return redirect(url_for("basket"))




if __name__ == "__main__":
    app.run(debug=True)