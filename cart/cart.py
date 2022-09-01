from decimal import Decimal

from account.models import *
from app.models import *


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
            if product.discount_percentage:
                self.cart[product_id] = {
                    "price": str(
                        product.price - (product.price * product.discount_percentage / 100)
                    ),
                    "qty": int(qty),
                    "currency": str(product.currency.symbol),
                }
            else:
                self.cart[product_id] = {
                    "price": str(
                        product.price
                    ),
                    "qty": int(qty),
                    "currency": str(product.currency.symbol),
                }
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids, in_stock=True)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]["product"] = product

        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = int(item["price"] * item["qty"])
            yield item

    def __len__(self):
        return sum(item["qty"] for item in self.cart.values())

    def get_total_price(self):
        return int(
            sum(Decimal(item["price"]) * item["qty"] for item in self.cart.values())
        )

    def get_grand_total(self, coupon_percentage):
        return int(
            sum(Decimal(item["price"]) * item["qty"] for item in self.cart.values())
            - (
                sum(Decimal(item["price"]) * item["qty"] for item in self.cart.values())
                * Decimal((coupon_percentage / 100))
            )
        )

    def get_product_qty(self, product):
        product_id = str(product)
        if product_id in self.item:
            return int(
                self.item[product_id]["qty"] * Decimal(self.item[product_id]["price"])
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

    def store_check(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_store = [product.store for product in products]
        result = all(store == products_store[0] for store in products_store)
        if result:
            return True
        else:
            return False

    def get_store_name(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        if products:
            a_store_name = [product.store for product in products]
            result = all(store == a_store_name[0] for store in a_store_name)
            if result:
                return Store.objects.get(store_name=a_store_name[0])

    def get_cart_products(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        return products

    def get_currency_symbol(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        currency = [product.currency.symbol for product in products]
        if currency:
            return currency[0]

    def get_currency_code(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        currency = [product.currency.code for product in products]
        if currency:
            return currency[0]

    def clear(self):
        del self.session["skey"]
        self.session.modified = True
