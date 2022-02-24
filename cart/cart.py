

class Cart():
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('skey')
        if 'skey' not in request.session:
            cart = self.session['skey'] = {}
        self.cart = cart

    def add(self, product, qty):
        product_id = product.id
        if product_id not in self.cart:
            self.cart[product_id] = {'price': float(product.price), 'qty':int(qty)}
        self.session.modified = True