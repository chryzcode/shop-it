from decimal import Decimal

from app.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("skey")
        if "skey" not in request.session:
            cart = self.session["skey"] = {}
        self.cart = cart

    def add(self, product, qty):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]["qty"] = qty
        else:
            self.cart[product_id] = {"price": str(product.price - (product.price * product.discount_percentage / 100)), "qty": int(qty)}
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids, in_stock=True)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]["product"] = product

        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["qty"]
            yield item

    def __len__(self):
        return sum(item["qty"] for item in self.cart.values())

    def get_total_price(self): 
        return sum(Decimal(item["price"]) * item["qty"] for item in self.cart.values() )

    def get_grand_total(self, coupon_percentage):
        return sum(Decimal(item["price"]) * item["qty"] for item in self.cart.values()) - (
                sum(Decimal(item["price"]) * item["qty"] for item in self.cart.values()) * Decimal((coupon_percentage / 100))
            )   
        

    # return the sum of an item quantity
    def get_product_qty(self, product):
        product_id = str(product)
        if product_id in self.item:
            return self.item[product_id]["qty"] * Decimal(
                self.item[product_id]["price"]
            )

    def delete(self, product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    

    def update(self, product, qty, cartitemqty):
        product_id = str(product)

        if product_id in self.cart:
            self.cart[product_id]["qty"] = qty
            self.cart[product_id]["cartitemqty"] = cartitemqty
        self.save()

    def save(self):
        self.session.modified = True

    def cart_products_store_name(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_store = [ product.created_by for product in products ]
        return products_store

    # delete all session
    def clear(self):
        del self.session["skey"]
        self.session.modified = True
