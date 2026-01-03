# E-Commerce CRM Chatbot

A conversational AI chatbot for e-commerce customer support, built with FastAPI, SQLite, Flask, and integrated with a local LLM (Ollama/Phi-3).

## Features

### 🤖 AI-Powered Conversations
- **Intent Detection**: Sophisticated pattern matching for common e-commerce queries
- **LLM Integration**: Uses Ollama with Phi-3 for natural language understanding
- **Context Awareness**: Provides responses based on user orders, cart, and product data

### 🛍️ Product Management
- Browse complete product catalog with descriptions and ratings
- Search products by name and description
- Filter products by category
- View product details (price, stock, description)
- Stock availability checking

### 🛒 Shopping & Cart
- Add products to cart with stock validation
- Remove items from cart
- View cart with calculated totals
- Cart persistence per session

### 📦 Order Management
- View order history
- Track order status
- Return and refund requests
- Order-related inquiries

### 👤 User Management
- User authentication with secure password hashing (SHA256)
- Session management
- Support for multiple users

### 🗄️ Database
- SQLite database with 7 tables:
  - users
  - products
  - orders
  - cart_items
  - addresses
  - reviews
  - (extensible for more features)

## Supported User Intents

- **Greetings**: hi, hello, hey
- **Farewells**: bye, thank you
- **Product Browsing**: show products, browse, what products
- **Product Search**: search for, find, do you have
- **Product Details**: price, cost, details, description
- **Cart Management**: show cart, add to cart, remove, clear cart
- **Orders**: my orders, order status, track order
- **Returns/Refunds**: return, refund
- **Support**: complaint, issue, customer care, human agent

## Architecture

```
fastapi_backend/          # Backend API server
├── main.py               # FastAPI app & endpoints
├── database.py           # SQLite ORM & models
├── intents.py            # Intent detection
├── llm_client.py         # LLM integration (Ollama)
├── models.py             # Pydantic models
├── users_db.py           # User auth helpers
├── carts.py              # Cart operations
├── products_data.py      # Product utilities
└── seed_db.py            # Database seeding

flask_ui/                 # Frontend
├── app.py                # Flask server
└── templates/
    ├── login.html        # Login page
    └── chat.html         # Chat interface
```

## Setup & Installation

### Prerequisites
- Python 3.9+
- Ollama with Phi-3 model (for LLM features)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Initialize Database
```bash
python fastapi_backend/seed_db.py
```

This creates a database with:
- 3 sample users
- 6 sample products (Electronics, Accessories, Footwear)
- 5 sample orders

### Start the Backend
```bash
uvicorn fastapi_backend.main:app --reload --port 8000
```

### Start the Frontend
In a separate terminal:
```bash
cd flask_ui
python app.py
```

The UI will be available at `http://localhost:5000`

## Sample User Credentials

| Email | Password | Name |
|-------|----------|------|
| m25ai1060@iitj.ac.in | 12345 | Sowmya |
| raj.patel@example.com | password123 | Raj Patel |
| priya.sharma@example.com | secure_pass | Priya Sharma |

## API Endpoints

### Authentication
- `POST /login` - User login

### Chat
- `POST /chat` - Send message to chatbot

### Products
- `GET /products` - Get all products
- `GET /products/search?query=...` - Search products
- `GET /products/category/{category}` - Filter by category
- `GET /products/top-rated` - Get top-rated products
- `GET /products/{id}` - Get product details

### Cart
- `POST /cart/add` - Add to cart (with stock check)
- `POST /cart/remove` - Remove from cart
- `GET /health` - Health check

## Environment Variables

```
FASTAPI_URL=http://127.0.0.1:8000        # Backend URL (for Flask)
OLLAMA_URL=http://localhost:11434/api/generate  # LLM endpoint
LLM_MODEL=phi3:mini                       # LLM model name
DB_PATH=crm_chatbot.db                    # Database file path
```

## Example Conversations

### Product Browsing
```
User: "What products do you have?"
Bot: "Available products:
  - Wireless Earbuds X2 — ₹1,499 (⭐ 0)
  - Nike Running Shoes — ₹2,999 (⭐ 0)
  [...]"
```

### Search
```
User: "Do you have any speakers?"
Bot: "Found 1 product(s) matching 'speakers':
  - Bluetooth Speaker — ₹1,999"
```

### Cart Management
```
User: "Add Wireless Earbuds to my cart"
Bot: "Added Wireless Earbuds X2 to cart"

User: "Show my cart"
Bot: "Your cart:
  - Wireless Earbuds X2 × 1 — ₹1,499

Total: ₹1,499"
```

### Order Tracking
```
User: "Where is my order?"
Bot: "Your orders:
  - ORD001 — Delivered
  - ORD002 — Out for Delivery"
```

## Future Enhancements

- [ ] Payment gateway integration
- [ ] Real-time order tracking with geolocation
- [ ] Personalized product recommendations
- [ ] Wishlist functionality
- [ ] Review system with ratings
- [ ] Multi-language support
- [ ] Email notifications
- [ ] Loyalty program
- [ ] Admin dashboard
- [ ] Analytics & reporting

## Technologies Used

- **Backend**: FastAPI, Python 3.9+
- **Frontend**: Flask, HTML, CSS, JavaScript
- **Database**: SQLite3
- **LLM**: Ollama + Phi-3
- **Authentication**: SHA256 password hashing

## License

MIT