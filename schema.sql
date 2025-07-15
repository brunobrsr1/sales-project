-- Create the database
CREATE DATABASE IF NOT EXISTS sales_db;
USE sales_db;

-- Customers table
CREATE TABLE customers (
  customer_id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  phone VARCHAR(20),
  address_line VARCHAR(100),
  postal_code VARCHAR(20),
  city VARCHAR(70),
  country VARCHAR(50),
  registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,

  -- Indexes for performance
  INDEX idx_customer_email (email),
  INDEX idx_customer_name (last_name, first_name),
  INDEX idx_customer_city (city)
);

-- Categories Table
CREATE TABLE categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(50) NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suppliers Table
CREATE TABLE suppliers (
  supplier_id INT AUTO_INCREMENT PRIMARY KEY,
  supplier_name VARCHAR(100) NOT NULL,
  contact_email VARCHAR(100),
  contact_phone VARCHAR(20),
  address VARCHAR(200),
  city VARCHAR(50),
  country VARCHAR(50),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales Representatives Table
CREATE TABLE sales_representatives (
  rep_id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  phone VARCHAR(20),
  hire_date DATE,
  commission_rate DECIMAL(5, 4) DEFAULT 0.0000 CHECK (commission_rate >= 0 AND commission_rate <= 1),
  territory VARCHAR(100),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_rep_email (email),
  INDEX idx_rep_name (last_name, first_name)
);

-- Products table
CREATE TABLE products(
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  product_name VARCHAR(100) NOT NULL,
  product_code VARCHAR(50) UNIQUE,
  category_id INT,
  supplier_id INT,
  price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
  cost DECIMAL(10, 2) CHECK (cost >= 0),
  stock_quantity INT DEFAULT 0 CHECK (stock_quantity >= 0),
  min_stock_level INT DEFAULT 5,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (category_id) REFERENCES categories(category_id),
  FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),

  -- Indexes for performance
  INDEX idx_product_name (product_name),
  INDEX idx_product_code (product_code),
  INDEX idx_product_category (category_id),
  INDEX idx_product_price (price)
);

-- Sales Table
CREATE TABLE sales(
  sale_id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0 CHECK (subtotal >= 0),
  tax_amount DECIMAL(10, 2) DEFAULT 0 CHECK (tax_amount >= 0),
  discount_amount DECIMAL(10, 2) DEFAULT 0 CHECK (discount_amount >= 0),
  total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
  payment_method ENUM('cash', 'credit_card', 'debit_card', 'check', 'online') DEFAULT 'cash',
  payment_status ENUM('pending', 'paid', 'refunded', 'cancelled') DEFAULT 'pending',
  sales_rep_id INT,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (sales_rep_id) REFERENCES sales_representatives(rep_id),

  -- Indexes for performance
  INDEX idx_sale_date (sale_date),
  INDEX idx_sale_customer (customer_id),
  INDEX idx_sale_status (payment_status),
  INDEX idx_sale_total (total_amount)
);

-- Sales Items Table
CREATE TABLE sale_items(
  sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
  sale_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL CHECK (quantity > 0),
  unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
  discount_percent DECIMAL(5, 2) DEFAULT 0 CHECK (discount_percent >= 0 AND discount_percent <= 100),
  line_total DECIMAL(10, 2) NOT NULL CHECK (line_total >= 0),
  
  FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  
  -- Indexes for performance
  INDEX idx_sale_items_sale (sale_id),
  INDEX idx_sale_items_product (product_id)
);

-- Create triggers to automatically update totals
DELIMITER //

CREATE TRIGGER update_sale_total
AFTER INSERT ON sale_items
FOR EACH ROW
BEGIN
  UPDATE sales
  SET subtotal = (
    SELECT SUM(line_total)
    FROM sale_items
    WHERE sale_id = NEW.sale_id
  ),
  total_amount = subtotal + tax_amount - discount_amount
  WHERE sale_id = NEW.sale_id;
END//

CREATE TRIGGER update_sale_total_on_update
AFTER UPDATE ON sale_items
FOR EACH ROW
BEGIN
  UPDATE sales
  SET subtotal = (
    SELECT SUM(line_total)
    FROM sale_items
    WHERE sale_id = NEW.sale_id
  ),
  total_amount = subtotal + tax_amount - discount_amount
  WHERE sale_id = NEW.sale_id;
END//

CREATE TRIGGER update_sale_total_on_delete
AFTER DELETE ON sale_items
FOR EACH ROW
BEGIN
  UPDATE sales
  SET subtotal = COALESCE((
    SELECT SUM(line_total)
    FROM sale_items
    WHERE sale_id = OLD.sale_id
  ), 0),
  total_amount = subtotal + tax_amount - discount_amount
  WHERE sale_id = OLD.sale_id;
END//

DELIMITER ;

-- Create useful views for reporting
CREATE VIEW sales_summary AS
SELECT 
  s.sale_id,
  s.sale_date,
  CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
  c.email AS customer_email,
  c.city AS customer_city,
  CONCAT(sr.first_name, ' ', sr.last_name) AS sales_rep_name,
  s.subtotal,
  s.tax_amount,
  s.discount_amount,
  s.total_amount,
  s.payment_method,
  s.payment_status,
  COUNT(si.sale_item_id) AS item_count
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
LEFT JOIN sales_representatives sr ON s.sales_rep_id = sr.rep_id
LEFT JOIN sale_items si ON s.sale_id = si.sale_id
GROUP BY s.sale_id, s.sale_date, c.first_name, c.last_name, c.email, c.city, 
         sr.first_name, sr.last_name, s.subtotal, s.tax_amount, s.discount_amount, 
         s.total_amount, s.payment_method, s.payment_status;

CREATE VIEW product_sales_summary AS
SELECT 
  p.product_id,
  p.product_name,
  p.product_code,
  cat.category_name,
  sup.supplier_name,
  p.price AS current_price,
  p.stock_quantity,
  p.min_stock_level,
  COALESCE(SUM(si.quantity), 0) AS total_sold,
  COALESCE(SUM(si.line_total), 0) AS total_revenue,
  COALESCE(AVG(si.unit_price), 0) AS avg_selling_price,
  CASE 
    WHEN p.stock_quantity = 0 THEN 'OUT_OF_STOCK'
    WHEN p.stock_quantity <= p.min_stock_level THEN 'LOW_STOCK'
    ELSE 'IN_STOCK'
  END AS stock_status
FROM products p
LEFT JOIN categories cat ON p.category_id = cat.category_id
LEFT JOIN suppliers sup ON p.supplier_id = sup.supplier_id
LEFT JOIN sale_items si ON p.product_id = si.product_id
WHERE p.is_active = TRUE
GROUP BY p.product_id, p.product_name, p.product_code, cat.category_name, 
         sup.supplier_name, p.price, p.stock_quantity, p.min_stock_level;

CREATE VIEW customer_summary AS
SELECT 
  c.customer_id,
  CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
  c.email,
  c.phone,
  c.city,
  c.country,
  c.registration_date,
  COUNT(s.sale_id) AS total_orders,
  COALESCE(SUM(s.total_amount), 0) AS total_spent,
  COALESCE(AVG(s.total_amount), 0) AS avg_order_value,
  MAX(s.sale_date) AS last_purchase_date,
  CASE 
    WHEN MAX(s.sale_date) >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY) THEN 'ACTIVE'
    WHEN MAX(s.sale_date) >= DATE_SUB(CURRENT_DATE, INTERVAL 90 DAY) THEN 'RECENT'
    WHEN MAX(s.sale_date) IS NOT NULL THEN 'INACTIVE'
    ELSE 'NEW'
  END AS customer_status
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id AND s.payment_status = 'paid'
WHERE c.is_active = TRUE
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.phone, 
         c.city, c.country, c.registration_date;

-- Additional useful views
CREATE VIEW low_stock_products AS
SELECT 
  p.product_id,
  p.product_name,
  p.product_code,
  cat.category_name,
  p.stock_quantity,
  p.min_stock_level,
  (p.min_stock_level - p.stock_quantity) AS stock_deficit
FROM products p
LEFT JOIN categories cat ON p.category_id = cat.category_id
WHERE p.is_active = TRUE 
  AND p.stock_quantity <= p.min_stock_level
ORDER BY stock_deficit DESC;

CREATE VIEW sales_rep_performance AS
SELECT 
  sr.rep_id,
  CONCAT(sr.first_name, ' ', sr.last_name) AS rep_name,
  sr.territory,
  sr.commission_rate,
  COUNT(s.sale_id) AS total_sales,
  COALESCE(SUM(s.total_amount), 0) AS total_revenue,
  COALESCE(AVG(s.total_amount), 0) AS avg_sale_amount,
  COALESCE(SUM(s.total_amount * sr.commission_rate), 0) AS total_commission_earned,
  MAX(s.sale_date) AS last_sale_date
FROM sales_representatives sr
LEFT JOIN sales s ON sr.rep_id = s.sales_rep_id AND s.payment_status = 'paid'
WHERE sr.is_active = TRUE
GROUP BY sr.rep_id, sr.first_name, sr.last_name, sr.territory, sr.commission_rate
ORDER BY total_revenue DESC;

-- Create some useful stored procedures
DELIMITER //

CREATE PROCEDURE GetCustomerPurchaseHistory(IN customer_id_param INT)
BEGIN
  SELECT 
    s.sale_id,
    s.sale_date,
    s.total_amount,
    s.payment_status,
    GROUP_CONCAT(
      CONCAT(p.product_name, ' (', si.quantity, ')')
      SEPARATOR ', '
    ) AS products_purchased
  FROM sales s
  JOIN sale_items si ON s.sale_id = si.sale_id
  JOIN products p ON si.product_id = p.product_id
  WHERE s.customer_id = customer_id_param
  GROUP BY s.sale_id, s.sale_date, s.total_amount, s.payment_status
  ORDER BY s.sale_date DESC;
END//

CREATE PROCEDURE UpdateProductStock(
  IN product_id_param INT, 
  IN quantity_change INT
)
BEGIN
  DECLARE current_stock INT;
  
  SELECT stock_quantity INTO current_stock 
  FROM products 
  WHERE product_id = product_id_param;
  
  IF (current_stock + quantity_change) >= 0 THEN
    UPDATE products 
    SET stock_quantity = stock_quantity + quantity_change,
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = product_id_param;
  ELSE
    SIGNAL SQLSTATE '45000' 
    SET MESSAGE_TEXT = 'Insufficient stock for this operation';
  END IF;
END//

DELIMITER ;

