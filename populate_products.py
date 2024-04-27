import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarique_perfumes.settings')
django.setup()

from tarique_perfumes_app.models import Product

def populate_products():
    products_data = [
        {
            'name': 'Product 1',
            'description': 'Description of Product 1',
            'price_retail': 50.99,
            'price_wholesale': 40.00,
            'size': 'Small',
            'fragrance_notes': 'Notes of vanilla and sandalwood',
            'image_url': 'https://example.com/product1.jpg',
            'in_stock_retail': True,
            'in_stock_wholesale': True,
            'sku': 'SKU123',
            'weight': 0.5,
            'dimension': '5x5x10 cm',
            'manufacturing_date': '2023-01-01',
            'expiry_date': '2024-12-31',
            'is_active': True,
            'average_rating': None,  # You can add random ratings if needed
        },
        {
            'name': 'Product 2',
            'description': 'Description of Product 2',
            'price_retail': 45.50,
            'price_wholesale': 35.00,
            'size': 'Medium',
            'fragrance_notes': 'Notes of rose and jasmine',
            'image_url': 'https://example.com/product2.jpg',
            'in_stock_retail': True,
            'in_stock_wholesale': True,
            'sku': 'SKU456',
            'weight': 1.0,
            'dimension': '8x8x15 cm',
            'manufacturing_date': '2022-12-01',
            'expiry_date': '2024-11-30',
            'is_active': True,
            'average_rating': None,
        }
    ]

    for data in products_data:
        Product.objects.create(**data)

if __name__ == '__main__':
    populate_products()
