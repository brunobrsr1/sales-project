import mysql.connector
import random
from datetime import datetime, timedelta
from faker import Faker
import sys

# Initialize Faker for generating realistic data
fake = Faker()

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Change this to your MySQL username
    'password': 'Bebepatas1331',  # Change this to your MySQL password
    'database': 'sales_db'
}

def connect_to_database():
    """Establish connection to MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connected to database successfully!")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error connecting to database: {err}")
        sys.exit(1)

def clear_existing_data(cursor):
    """Clear existing data from all tables (optional)"""
    print("🧹 Clearing existing data...")
    
    # Disable foreign key checks temporarily
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    tables = ['sale_items', 'sales', 'products', 'customers', 'categories', 
              'suppliers', 'sales_representatives']
    
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table}")
        print(f"   Cleared {table}")
    
    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print("✅ Data cleared successfully!")

def check_and_fix_duplicates(cursor):
    """Check for and report duplicate emails"""
    print("🔍 Checking for duplicate emails...")
    
    # Check customer email duplicates
    cursor.execute("""
        SELECT email, COUNT(*) as count 
        FROM customers 
        GROUP BY email 
        HAVING COUNT(*) > 1
    """)
    customer_dupes = cursor.fetchall()
    
    if customer_dupes:
        print(f"⚠️  Found {len(customer_dupes)} duplicate customer emails:")
        for email, count in customer_dupes[:5]:  # Show first 5
            print(f"   {email}: {count} occurrences")
        
        # Option to fix duplicates
        print("🔧 Removing duplicate customers (keeping the first one)...")
        cursor.execute("""
            DELETE c1 FROM customers c1
            INNER JOIN customers c2 
            WHERE c1.customer_id > c2.customer_id 
            AND c1.email = c2.email
        """)
        print(f"   Removed {cursor.rowcount} duplicate customers")
    
    # Check sales rep email duplicates
    cursor.execute("""
        SELECT email, COUNT(*) as count 
        FROM sales_representatives 
        GROUP BY email 
        HAVING COUNT(*) > 1
    """)
    rep_dupes = cursor.fetchall()
    
    if rep_dupes:
        print(f"⚠️  Found {len(rep_dupes)} duplicate sales rep emails:")
        for email, count in rep_dupes[:5]:
            print(f"   {email}: {count} occurrences")
        
        print("🔧 Removing duplicate sales reps (keeping the first one)...")
        cursor.execute("""
            DELETE r1 FROM sales_representatives r1
            INNER JOIN sales_representatives r2 
            WHERE r1.rep_id > r2.rep_id 
            AND r1.email = r2.email
        """)
        print(f"   Removed {cursor.rowcount} duplicate sales reps")
    
    if not customer_dupes and not rep_dupes:
        print("✅ No duplicate emails found!")

def populate_categories(cursor, count=20):
    """Populate categories table"""
    print(f"📁 Creating {count} product categories...")
    
    categories = [
        'Electronics', 'Clothing', 'Home & Garden', 'Sports & Outdoors', 
        'Books', 'Health & Beauty', 'Toys & Games', 'Automotive',
        'Food & Beverages', 'Office Supplies', 'Pet Supplies', 'Music',
        'Movies & TV', 'Kitchen & Dining', 'Furniture', 'Tools',
        'Jewelry', 'Shoes', 'Baby Products', 'Art & Crafts'
    ]
    
    for i, category in enumerate(categories[:count]):
        cursor.execute("""
            INSERT INTO categories (category_name, description) 
            VALUES (%s, %s)
        """, (category, f"Products related to {category.lower()}"))
    
    print(f"✅ Created {count} categories")

def populate_suppliers(cursor, count=50):
    """Populate suppliers table"""
    print(f"🏢 Creating {count} suppliers...")
    
    for i in range(count):
        cursor.execute("""
            INSERT INTO suppliers (supplier_name, contact_email, contact_phone, 
                                 address, city, country, is_active) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            fake.company(),
            fake.company_email(),
            fake.phone_number()[:20],
            fake.address()[:200],
            fake.city()[:50],
            fake.country()[:50],
            random.choice([True, True, True, False])  # 75% active
        ))
    
    print(f"✅ Created {count} suppliers")

def populate_sales_representatives(cursor, count=25):
    """Populate sales representatives table"""
    print(f"👥 Creating {count} sales representatives...")
    
    territories = ['North', 'South', 'East', 'West', 'Central', 'Northeast', 
                  'Southeast', 'Northwest', 'Southwest', 'Online']
    
    used_emails = set()
    
    for i in range(count):
        # Generate unique email for sales rep
        email = fake.email()
        attempts = 0
        while email in used_emails and attempts < 10:
            email = fake.email()
            attempts += 1
        
        # If still duplicate after 10 attempts, create a unique one
        if email in used_emails:
            email = f"salesrep{i+1}_{fake.random_int(1000, 9999)}@{fake.free_email_domain()}"
        
        used_emails.add(email)
        
        hire_date = fake.date_between(start_date='-5y', end_date='today')
        cursor.execute("""
            INSERT INTO sales_representatives (first_name, last_name, email, 
                                             phone, hire_date, commission_rate, 
                                             territory, is_active) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            fake.first_name(),
            fake.last_name(),
            email,
            fake.phone_number()[:20],
            hire_date,
            round(random.uniform(0.02, 0.10), 4),  # 2-10% commission
            random.choice(territories),
            random.choice([True, True, True, False])  # 75% active
        ))
    
    print(f"✅ Created {count} sales representatives")

def populate_customers(cursor, count=1000):
    """Populate customers table"""
    print(f"👤 Creating {count} customers...")
    
    used_emails = set()
    batch_size = 100
    
    for batch_start in range(0, count, batch_size):
        batch_end = min(batch_start + batch_size, count)
        batch_data = []
        
        for i in range(batch_start, batch_end):
            # Generate unique email
            email = fake.email()
            attempts = 0
            while email in used_emails and attempts < 10:
                email = fake.email()
                attempts += 1
            
            # If still duplicate after 10 attempts, create a unique one
            if email in used_emails:
                email = f"customer{i+1}_{fake.random_int(1000, 9999)}@{fake.free_email_domain()}"
            
            used_emails.add(email)
            
            reg_date = fake.date_time_between(start_date='-2y', end_date='now')
            batch_data.append((
                fake.first_name(),
                fake.last_name(),
                email,
                fake.phone_number()[:20],
                fake.street_address()[:100],
                fake.postcode()[:20],
                fake.city()[:70],
                fake.country()[:50],
                reg_date,
                random.choice([True, True, True, False])  # 75% active
            ))
        
        cursor.executemany("""
            INSERT INTO customers (first_name, last_name, email, phone, 
                                 address_line, postal_code, city, country, 
                                 registration_date, is_active) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, batch_data)
        
        print(f"   Created {batch_end} customers...")
    
    print(f"✅ Created {count} customers")

def populate_products(cursor, count=500):
    """Populate products table"""
    print(f"📦 Creating {count} products...")
    
    # Get category and supplier IDs
    cursor.execute("SELECT category_id FROM categories")
    category_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT supplier_id FROM suppliers WHERE is_active = TRUE")
    supplier_ids = [row[0] for row in cursor.fetchall()]
    
    batch_size = 50
    for batch_start in range(0, count, batch_size):
        batch_end = min(batch_start + batch_size, count)
        batch_data = []
        
        for i in range(batch_start, batch_end):
            cost = round(random.uniform(5.0, 200.0), 2)
            price = round(cost * random.uniform(1.3, 3.0), 2)  # 30-200% markup
            
            batch_data.append((
                fake.catch_phrase()[:100],  # product name
                f"SKU-{i+1:06d}",  # product code
                random.choice(category_ids) if category_ids else None,
                random.choice(supplier_ids) if supplier_ids else None,
                price,
                cost,
                random.randint(0, 500),  # stock quantity
                random.randint(5, 50),   # min stock level
                fake.text(max_nb_chars=200),  # description
                random.choice([True, True, True, False])  # 75% active
            ))
        
        cursor.executemany("""
            INSERT INTO products (product_name, product_code, category_id, 
                                supplier_id, price, cost, stock_quantity, 
                                min_stock_level, description, is_active) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, batch_data)
        
        print(f"   Created {batch_end} products...")
    
    print(f"✅ Created {count} products")

def populate_sales_and_items(cursor, sales_count=2000):
    """Populate sales and sale_items tables"""
    print(f"💰 Creating {sales_count} sales with items...")
    
    # Get active customers, products, and sales reps
    cursor.execute("SELECT customer_id FROM customers WHERE is_active = TRUE")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT product_id, price FROM products WHERE is_active = TRUE")
    products = cursor.fetchall()
    
    cursor.execute("SELECT rep_id FROM sales_representatives WHERE is_active = TRUE")
    rep_ids = [row[0] for row in cursor.fetchall()]
    
    if not customer_ids or not products:
        print("❌ No active customers or products found!")
        return
    
    payment_methods = ['cash', 'credit_card', 'debit_card', 'check', 'online']
    payment_statuses = ['paid', 'paid', 'paid', 'pending', 'refunded']  # More paid orders
    
    for i in range(sales_count):
        # Create sale
        sale_date = fake.date_time_between(start_date='-1y', end_date='now')
        tax_rate = 0.08  # 8% tax
        
        cursor.execute("""
            INSERT INTO sales (customer_id, sale_date, payment_method, 
                             payment_status, sales_rep_id, notes) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            random.choice(customer_ids),
            sale_date,
            random.choice(payment_methods),
            random.choice(payment_statuses),
            random.choice(rep_ids) if rep_ids and random.random() > 0.3 else None,
            fake.sentence() if random.random() > 0.7 else None
        ))
        
        sale_id = cursor.lastrowid
        
        # Add 1-5 items to each sale
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        subtotal = 0
        for product_id, base_price in selected_products:
            quantity = random.randint(1, 3)
            # Convert Decimal to float before calculation to avoid type errors
            base_price_float = float(base_price)
            # Add some price variation (±10%)
            unit_price = round(base_price_float * random.uniform(0.9, 1.1), 2)
            discount_percent = random.choice([0, 0, 0, 5, 10, 15])  # Most items no discount
            
            # Calculate line total
            line_total = round(quantity * unit_price * (1 - discount_percent/100), 2)
            subtotal += line_total
            
            cursor.execute("""
                INSERT INTO sale_items (sale_id, product_id, quantity, 
                                      unit_price, discount_percent, line_total) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (sale_id, product_id, quantity, unit_price, discount_percent, line_total))
        
        # Update sale totals (triggers will handle this, but let's set it manually too)
        tax_amount = round(subtotal * tax_rate, 2)
        total_amount = subtotal + tax_amount
        
        cursor.execute("""
            UPDATE sales 
            SET subtotal = %s, tax_amount = %s, total_amount = %s 
            WHERE sale_id = %s
        """, (subtotal, tax_amount, total_amount, sale_id))
        
        if (i + 1) % 200 == 0:
            print(f"   Created {i + 1} sales...")
    
    print(f"✅ Created {sales_count} sales with items")

def generate_sample_data(clear_data=True, 
                        categories=20, 
                        suppliers=50, 
                        sales_reps=25, 
                        customers=1000, 
                        products=500, 
                        sales=2000):
    """Main function to populate the database"""
    print("🚀 Starting database population...")
    print(f"📊 Will create: {categories} categories, {suppliers} suppliers, {sales_reps} reps, {customers} customers, {products} products, {sales} sales")
    
    conn = connect_to_database()
    cursor = conn.cursor()
    
    try:
        if clear_data:
            clear_existing_data(cursor)
        
        # Populate tables in dependency order
        populate_categories(cursor, categories)
        conn.commit()
        
        populate_suppliers(cursor, suppliers)
        conn.commit()
        
        populate_sales_representatives(cursor, sales_reps)
        conn.commit()
        
        populate_customers(cursor, customers)
        conn.commit()
        
        populate_products(cursor, products)
        conn.commit()
        
        populate_sales_and_items(cursor, sales)
        conn.commit()
        
        # Check for any duplicates that might have occurred
        check_and_fix_duplicates(cursor)
        conn.commit()
        
        print("\n🎉 Database population completed successfully!")
        print("\n📈 Summary:")
        
        # Show summary statistics
        cursor.execute("SELECT COUNT(*) FROM customers")
        print(f"   👤 Customers: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM products")
        print(f"   📦 Products: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM sales")
        print(f"   💰 Sales: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM sale_items")
        print(f"   📋 Sale Items: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT SUM(total_amount) FROM sales WHERE payment_status = 'paid'")
        total_revenue = cursor.fetchone()[0] or 0
        print(f"   💵 Total Revenue: ${total_revenue:,.2f}")
        
    except mysql.connector.IntegrityError as e:
        if "Duplicate entry" in str(e):
            print(f"⚠️  Duplicate entry error: {e}")
            print("💡 Try running with clear_data=True to clear existing data first")
        else:
            print(f"❌ Database integrity error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"❌ Error during population: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Customize these numbers based on your needs
    generate_sample_data(
        clear_data=True,    # Set to False if you want to add to existing data
        categories=20,      # Number of product categories
        suppliers=50,       # Number of suppliers
        sales_reps=25,      # Number of sales representatives
        customers=1000,     # Number of customers
        products=500,       # Number of products
        sales=2000          # Number of sales transactions
    )
