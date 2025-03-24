import psycopg2
conn = psycopg2.connect(
    dbname="MyPostgreSQLDb",
    user="Renat",
    password="Renatik",
    host="localhost",
    port="3000"
)

curs = conn.cursor()
curs.execute('SELECT version();')

print(f"Postgre version is ", curs.fetchone())

curs.close()
conn.close()
class Market:
    def __init__(self, name, price, days):
        self.name = name
        self.price = price
        self.days = days
    def show_prices(self):
        print(f"Цена за {self.name} будет состалять {self.price} рублей, придет оно через {self.days} дней")
    

class ElectroMarket(Market):
    def __init__(self, name, price, days, guarantee):
        super().__init__(name, price, days)
        self.guarantee = guarantee
    def show_guarantee(self):
        print(f"Гарантия на товар {self.name} будет составлять {self.guarantee} дней с {self.days} дня покупки")

milk = Market("молоко",200, 10)
milk.show_prices()

phone = ElectroMarket('Iphone 5s','500$','1','10')
phone.show_guarantee()

