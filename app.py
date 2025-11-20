"""
Production Order Tracker (Internship Project)
Author: [Your Name]
Created: September 2025
Purpose: To explore AI-assisted development of a simple MES-like system
Built using: Python, Flask, SQLite, Bootstrap
"""

from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'some-secret-key'  # Needed for session storage

# --- Translations (English + German) ---
translations = {
    'en': {
        'title': 'Production Order Tracker',
        'subtitle': 'Track production orders and update their status in real time',
        'toggle_dark': 'Toggle Dark Mode',
        'add_order': 'Add New Order',
        'item_name': 'Item Name',
        'quantity': 'Quantity',
        'status': 'Status',
        'created': 'Created',
        'actions': 'Actions',
        'add': 'Add',
        'search': 'Search item...',
        'order_list': 'Order List',
        'delete_confirm': 'Are you sure you want to delete this order?',
        'yes_delete': 'Yes, Delete',
        'cancel': 'Cancel',
        'success': 'Order added successfully!',
        'previous': 'Previous',
        'next': 'Next',
        'order_by': 'Order By',
        'date_newest': 'Date (Newest)',
        'date_oldest': 'Date (Oldest)',
        'quantity_asc': 'Quantity (Low → High)',
        'quantity_desc': 'Quantity (High → Low)',
        'status_asc': 'Status (A → Z)',
        'status_desc': 'Status (Z → A)',
        'status_labels': {
            'Pending': 'Pending',
            'In Progress': 'In Progress',
            'Completed': 'Completed'
        }
    },
    'de': {
        'title': 'Produktionsauftrag Verfolgung',
        'subtitle': 'Verfolgen Sie Produktionsaufträge und aktualisieren Sie deren Status in Echtzeit',
        'toggle_dark': 'Dunkelmodus umschalten',
        'add_order': 'Neuen Auftrag hinzufügen',
        'item_name': 'Artikelname',
        'quantity': 'Menge',
        'status': 'Status',
        'created': 'Erstellt',
        'actions': 'Aktionen',
        'add': 'Hinzufügen',
        'search': 'Artikel suchen...',
        'order_list': 'Auftragsliste',
        'delete_confirm': 'Möchten Sie diesen Auftrag wirklich löschen?',
        'yes_delete': 'Ja, löschen',
        'cancel': 'Abbrechen',
        'success': 'Auftrag erfolgreich hinzugefügt!',
        'previous': 'Zurück',
        'next': 'Weiter',
        'order_by': 'Sortieren nach',
        'date_newest': 'Datum (neueste)',
        'date_oldest': 'Datum (älteste)',
        'quantity_asc': 'Menge (aufsteigend)',
        'quantity_desc': 'Menge (absteigend)',
        'status_asc': 'Status (A → Z)',
        'status_desc': 'Status (Z → A)',
        'status_labels': {
            'Pending': 'Ausstehend',
            'In Progress': 'In Bearbeitung',
            'Completed': 'Abgeschlossen'
        }
    }
}


# --- Initialize the database ---
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  item TEXT NOT NULL,
                  quantity INTEGER NOT NULL,
                  status TEXT NOT NULL,
                  created_at TEXT NOT NULL)''')
    conn.commit()
    conn.close()


# --- Homepage: Show all orders ---
@app.route('/')
def index():
    lang = session.get('lang', 'en')
    t = translations[lang]

    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 15
    offset = (page - 1) * per_page

    # Sorting setup
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    valid_sort_fields = ['created_at', 'quantity', 'status']
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'
    if sort_order not in ['asc', 'desc']:
        sort_order = 'desc'

    conn = sqlite3.connect('orders.db')
    c = conn.cursor()

    # Count total orders
    c.execute("SELECT COUNT(*) FROM orders")
    total_orders = c.fetchone()[0]
    total_pages = (total_orders + per_page - 1) // per_page

    # Fetch orders with sorting
    query = f"SELECT * FROM orders ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"
    c.execute(query, (per_page, offset))
    orders = c.fetchall()
    conn.close()

    # Determine visible pages (e.g. pagination with ellipsis)
    if total_pages <= 7:
        visible_pages = list(range(1, total_pages + 1))
    else:
        visible_pages = ['...']
        if page > 2:
            visible_pages = [1, '...']
        for p in range(page - 1, page + 2):
            if 1 <= p <= total_pages:
                visible_pages.append(p)
        if page < total_pages - 1:
            visible_pages += ['...', total_pages]

    return render_template('index.html',
                           orders=orders,
                           t=t,
                           lang=lang,
                           current_page=page,
                           total_pages=total_pages,
                           visible_pages=visible_pages,
                           sort_by=sort_by,
                           sort_order=sort_order)





# --- Add a new order ---
@app.route('/add', methods=['POST'])
def add_order():
    item = request.form['item']
    quantity = request.form['quantity']
    status = 'Pending'
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (item, quantity, status, created_at) VALUES (?, ?, ?, ?)",
              (item, quantity, status, created_at))
    conn.commit()
    conn.close()
    return redirect('/?success=true')


# --- Update order status ---
@app.route('/update/<int:order_id>', methods=['POST'])
def update_status(order_id):
    new_status = request.form['status']

    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()
    return redirect('/')


# --- Delete an order by ID ---
@app.route('/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return redirect('/')


# --- Set Language ---
@app.route('/set-language', methods=['POST'])
def set_language():
    session['lang'] = request.form['language']
    return redirect('/')


# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    total_orders = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    pending_orders = conn.execute("SELECT COUNT(*) FROM orders WHERE status = 'Pending'").fetchone()[0]
    completed_orders = conn.execute("SELECT COUNT(*) FROM orders WHERE status = 'Completed'").fetchone()[0]
    most_frequent_item = conn.execute('''
        SELECT item_name, COUNT(*) as count
        FROM orders
        GROUP BY item_name
        ORDER BY count DESC
        LIMIT 1
    ''').fetchone()
    conn.close()

    return render_template(
        'dashboard.html',
        total_orders=total_orders,
        pending_orders=pending_orders,
        completed_orders=completed_orders,
        most_frequent_item=most_frequent_item
    )

# --- Run the app ---
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
