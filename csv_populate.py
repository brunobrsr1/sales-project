import csv
import random
from datetime import datetime, timedelta
from faker import Faker
import os

# Initialize Faker
fake = Faker()

def create_csv_files(categories=20, suppliers=50, sales_reps=25, customers=10000, products=5000, sales=20000):
    """Generate CSV files for bulk import"""
    print("🚀 Generating CSV files for bulk import...")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # 1. Generate Categories
    print("📁 Generating categories.csv...")
    categories_list = [
        'Electronics', 'Clothing', 'Home & Garden', 'Sports & Outdoors', 
        'Books', 'Health & Beauty', 'Toys & Games', 'Automotive',
        'Food & Beverages', 'Office Supplies', 'Pet Supplies', 'Music',
        'Movies & TV', 'Kitchen & Dining', 'Furniture', 'Tools',
        'Jewelry', 'Shoes', 'Baby Products', 'Art & Crafts'
    ]
    
    with open('data/categories.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i, category in enumerate(categories_list[:categories]):
            writer.writerow([i+1, category, f"Products related to {category.lower()}", datetime.now()])
    
    # 2. Generate Suppliers
    print("🏢 Generating suppliers.csv...")
    with open('data/suppliers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in range(suppliers):
            writer.writerow([
                i+1,
                fake.company(),
                fake.company_email(),
                fake.phone_number()[:20],
                fake.address()[:200],
                fake.city()[:50],
                fake.country()[:50],
                random.choice([1, 1, 1, 0]),  # 75% active
                datetime.now()
            ])
    
    # 3. Generate Sales Representatives
    print("👥 Generating sales_reps.csv...")
    territories = ['North', 'South', 'East', 'West', 'Central', 'Northeast', 
                  'Southeast', 'Northwest', 'Southwest', 'Online']
    
    with open('data/sales_reps.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in range(sales_reps):
            hire_date = fake.date_between(start_date='-5y', end_date='today')
            writer.writerow([
                i+1,
                fake.first_name(),
                fake.last_name(),
                fake.email(),
                fake.phone_number()[:20],
                hire_date,
                round(random.uniform(0.02, 0.10), 4),
                random.choice(territories),
                random.choice([1, 1, 1, 0]),
                datetime.now()
            ])
    
    # 4. Generate Customers
    print(f"👤 Generating customers.csv ({customers:,} records)...")
    with open('data/customers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in range(customers):
            reg_date = fake.date_time_between(start_date='-2y', end_date='now')
            writer.writerow([
                i+1,
                fake.first_name(),
                fake.last_name(),
                fake.email(),
                fake.phone_number()[:20],
                fake.street_address()[:100],
                fake.postcode()[:20],
                fake.city()[:70],
                fake.country()[:50],
                reg_date,
                random.choice([1, 1, 1, 0])
            ])
            
            if (i + 1) % 1000 == 0:
                print(f"   Generated {i + 1:,} customers...")
    
    # 5. Generate Products
    print(f"📦 Generating products.csv ({products:,} records)...")
    with open('data/products.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in range(products):
            cost = round(random.uniform(5.0, 200.0), 2)
            price = round(cost * random.uniform(1.3, 3.0), 2)
            
            writer.writerow([
                i+1,
                fake.catch_phrase()[:100],
                f"SKU-{i+1:06d}",
                random.randint(1, categories),
                random.randint(1, suppliers),
                price,
                cost,
                random.randint(0, 500),
                random.randint(5, 50),
                fake.text(max_nb_chars=200).replace('\n', ' '),
                random.choice([1, 1, 1, 0]),
                datetime.now(),
                datetime.now()
            ])
            
            if (i + 1) % 500 == 0:
                print(f"   Generated {i + 1:,} products...")
    
    # 6. Generate Sales and Sale Items
    print(f"💰 Generating sales data ({sales:,} sales)...")
    payment_methods = ['cash', 'credit_card', 'debit_card', 'check', 'online']
    payment_statuses = ['paid', 'paid', 'paid', 'pending', 'refunded']
    
    sales_data = []
    sale_items_data = []
    
    for i in range(sales):
        sale_id = i + 1
        sale_date = fake.date_time_between(start_date='-1y', end_date='now')
        customer_id = random.randint(1, customers)
        rep_id = random.randint(1, sales_reps) if random.random() > 0.3 else None
        
        # Generate sale items first to calculate totals
        num_items = random.randint(1, 5)
        subtotal = 0
        
        for _ in range(num_items):
            product_id = random.randint(1, products)
            quantity = random.randint(1, 3)
            unit_price = round(random.uniform(10.0, 200.0), 2)
            discount_percent = random.choice([0, 0, 0, 5, 10, 15])
            line_total = round(quantity * unit_price * (1 - discount_percent/100), 2)
            subtotal += line_total
            
            sale_items_data.append([
                len(sale_items_data) + 1,  # sale_item_id
                sale_id,
                product_id,
                quantity,
                unit_price,
                discount_percent,
                line_total
            ])
        
        # Calculate sale totals
        tax_amount = round(subtotal * 0.08, 2)
        total_amount = subtotal + tax_amount
        
        sales_data.append([
            sale_id,
            customer_id,
            sale_date,
            subtotal,
            tax_amount,
            0,  # discount_amount
            total_amount,
            random.choice(payment_methods),
            random.choice(payment_statuses),
            rep_id,
            fake.sentence() if random.random() > 0.7 else None,
            datetime.now(),
            datetime.now()
        ])
        
        if (i + 1) % 1000 == 0:
            print(f"   Generated {i + 1:,} sales...")
    
    # Write sales data
    with open('data/sales.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(sales_data)
    
    # Write sale items data
    with open('data/sale_items.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(sale_items_data)
    
    print("✅ CSV files generated successfully!")
    print(f"📁 Generated files in 'data/' directory:")
    print(f"   categories.csv ({categories} records)")
    print(f"   suppliers.csv ({suppliers} records)")
    print(f"   sales_reps.csv ({sales_reps} records)")
    print(f"   customers.csv ({customers:,} records)")
    print(f"   products.csv ({products:,} records)")
    print(f"   sales.csv ({sales:,} records)")
    print(f"   sale_items.csv ({len(sale_items_data):,} records)")

def generate_sql_import_script():
    """Generate SQL script to import CSV files"""
    print("📝 Generating import_data.sql script...")
    
    sql_script = """
-- SQL Script to Import CSV Data
-- Run this script in MySQL after generating CSV files

-- Disable foreign key checks and autocommit for faster imports
SET FOREIGN_KEY_CHECKS = 0;
SET AUTOCOMMIT = 0;

-- Clear existing data (optional)
TRUNCATE TABLE sale_items;
TRUNCATE TABLE sales;
TRUNCATE TABLE products;
TRUNCATE TABLE customers;
TRUNCATE TABLE categories;
TRUNCATE TABLE suppliers;
TRUNCATE TABLE sales_representatives;

-- Import Categories
LOAD DATA INFILE 'C:/Users/bruno/Documents/sales-project/data/categories.csv'
INTO TABLE categories
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
(category_id, category_name, description, created_at);

-- Import Suppliers
LOAD DATA INFILE 'C:/Users/bruno/Documents/sales-project/data/suppliers.csv'
INTO TABLE suppliers
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
(supplier_id, supplier_name, contact_email, contact_phone, address, city, country, is_active, created_at);

-- Import Sales Representatives
LOAD DATA INFILE 'C:/Users/bruno/Documents/sales-project/data/sales_reps.csv'
INTO TABLE sales_representatives
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
(rep_id, first_name, last_name, email, phone, hire_date, commission_rate, territory, is_active, created_at);

-- Import Customers
LOAD DATA INFILE 'C:/Users/bruno/Documents/sales-project/data/customers.csv'
INTO TABLE customers
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
(customer_id, first_name, last_name, email, phone, address_line, postal_code, city, country, registration_date, is_active);

-- Import Products
LOAD DATA INFILE 'C:/Users/bruno/Documents/sales-project/data/products.csv'
INTO TABLE products
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
(product_id, product_name, product_code, category_id, supplier_id, price, cost, stock_quantity, min_stock_level, description, is_active, created_at, updated_at);

-- Import Sales
LOAD DATA INFILE 'C:/Users/bruno/Documents/sales-project/data/sales.csv'
INTO TABLE sales
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
(sale_id, customer_id, sale_date, subtotal, tax_amount, discount_amount, total_amount, payment_method, payment_status, sales_rep_id, notes, created_at, updated_at);

-- Import Sale Items
LOAD DATA INFILE 'C:/Users/bruno/Documents/sales-project/data/sale_items.csv'
INTO TABLE sale_items
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
(sale_item_id, sale_id, product_id, quantity, unit_price, discount_percent, line_total);

-- Re-enable foreign key checks and commit
COMMIT;
SET FOREIGN_KEY_CHECKS = 1;
SET AUTOCOMMIT = 1;

-- Show import results
SELECT 'categories' as table_name, COUNT(*) as record_count FROM categories
UNION ALL
SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL
SELECT 'sales_representatives', COUNT(*) FROM sales_representatives
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sales', COUNT(*) FROM sales
UNION ALL
SELECT 'sale_items', COUNT(*) FROM sale_items;

SELECT 'Total Revenue (Paid Orders)' as metric, CONCAT('$', FORMAT(SUM(total_amount), 2)) as value
FROM sales WHERE payment_status = 'paid';
"""
    
    with open('import_data.sql', 'w') as f:
        f.write(sql_script)
    
    print("✅ Generated import_data.sql")
    print("💡 To use this method:")
    print("   1. Run: python csv_populate.py")
    print("   2. Update file paths in import_data.sql")
    print("   3. Run: mysql -u username -p sales_db < import_data.sql")

if __name__ == "__main__":
    # Generate massive amounts of data quickly
    create_csv_files(
        categories=20,
        suppliers=100,
        sales_reps=50,
        customers=50000,    # 50K customers
        products=10000,     # 10K products  
        sales=100000        # 100K sales
    )
    
    generate_sql_import_script()
    
    print("\n🎉 CSV generation complete!")
    print("🚀 This method is 10-50x faster for large datasets!")
