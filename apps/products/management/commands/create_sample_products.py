from django.core.management.base import BaseCommand
from apps.products.models import ProductCategory, Product


class Command(BaseCommand):
    help = 'Crea productos de prueba basados en el diseño del mockup'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando categorías y productos de prueba...')

        # Crear categorías
        categories_data = [
            {'name': 'Computadoras', 'slug': 'computadoras', 'icon': 'fas fa-laptop', 'order': 1},
            {'name': 'Redes', 'slug': 'redes', 'icon': 'fas fa-network-wired', 'order': 2},
            {'name': 'Impresoras', 'slug': 'impresoras', 'icon': 'fas fa-print', 'order': 3},
            {'name': 'Servidores', 'slug': 'servidores', 'icon': 'fas fa-server', 'order': 4},
            {'name': 'Almacenamiento', 'slug': 'almacenamiento', 'icon': 'fas fa-hdd', 'order': 5},
            {'name': 'Accesorios', 'slug': 'accesorios', 'icon': 'fas fa-keyboard', 'order': 6},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = ProductCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'[+] Categoria creada: {category.name}'))
            else:
                self.stdout.write(f'  Categoria ya existe: {category.name}')

        # Crear productos
        products_data = [
            {
                'category': 'computadoras',
                'name': 'Laptop Empresarial',
                'slug': 'laptop-empresarial',
                'short_description': 'Equipos de alto rendimiento para trabajo profesional',
                'full_description': 'Laptop empresarial con procesador Intel Core i7, 16GB RAM, SSD 512GB, perfecta para trabajo profesional y multitarea exigente.',
                'price': 2000000,
                'sku': 'LAP-EMP-001',
                'stock': 10,
                'icon': 'fas fa-laptop',
                'active': True,
                'featured': True,
            },
            {
                'category': 'redes',
                'name': 'Router Empresarial',
                'slug': 'router-empresarial',
                'short_description': 'Conectividad de alta velocidad y seguridad',
                'full_description': 'Router empresarial de alto rendimiento con soporte para VPN, firewall integrado y gestión centralizada.',
                'price': 300000,
                'sku': 'ROU-EMP-001',
                'stock': 15,
                'icon': 'fas fa-router',
                'active': True,
                'featured': False,
            },
            {
                'category': 'impresoras',
                'name': 'Impresora Multifuncional',
                'slug': 'impresora-multifuncional',
                'short_description': 'Impresión, escaneo y copiado profesional',
                'full_description': 'Impresora multifuncional láser con capacidad de impresión, escaneo, copiado y fax. Ideal para oficinas.',
                'price': 1500000,
                'sku': 'IMP-MUL-001',
                'stock': 8,
                'icon': 'fas fa-print',
                'active': True,
                'featured': True,
            },
            {
                'category': 'servidores',
                'name': 'Servidor Rack',
                'slug': 'servidor-rack',
                'short_description': 'Soluciones de almacenamiento empresarial',
                'full_description': 'Servidor rack de 2U con procesadores Xeon, 64GB RAM, almacenamiento SAS, ideal para virtualización y aplicaciones empresariales.',
                'price': 1200000,
                'sku': 'SER-RAC-001',
                'stock': 5,
                'icon': 'fas fa-server',
                'active': True,
                'featured': False,
            },
            {
                'category': 'almacenamiento',
                'name': 'Disco Duro SSD',
                'slug': 'disco-duro-ssd',
                'short_description': 'Almacenamiento rápido y confiable',
                'full_description': 'SSD NVMe de 1TB con velocidades de lectura/escritura ultrarrápidas. Ideal para upgrade de laptops y desktops.',
                'price': 500000,
                'sku': 'SSD-NVM-001',
                'stock': 20,
                'icon': 'fas fa-hdd',
                'active': True,
                'featured': False,
            },
            {
                'category': 'accesorios',
                'name': 'Periféricos de Oficina',
                'slug': 'perifericos-oficina',
                'short_description': 'Teclados, ratones y accesorios',
                'full_description': 'Kit de periféricos inalámbricos incluyendo teclado y mouse ergonómico, ideal para trabajo de oficina prolongado.',
                'price': 200000,
                'sku': 'ACC-PER-001',
                'stock': 30,
                'icon': 'fas fa-keyboard',
                'active': True,
                'featured': False,
            },
        ]

        for prod_data in products_data:
            category_slug = prod_data.pop('category')
            prod_data['category'] = categories[category_slug]

            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults=prod_data
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'[+] Producto creado: {product.name}'))
            else:
                self.stdout.write(f'  Producto ya existe: {product.name}')

        self.stdout.write(self.style.SUCCESS('\nProductos de prueba creados exitosamente!'))
        self.stdout.write(f'Total categorías: {ProductCategory.objects.count()}')
        self.stdout.write(f'Total productos: {Product.objects.count()}')
