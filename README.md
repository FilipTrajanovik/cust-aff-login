# Trump Finance

A comprehensive cryptocurrency management platform built with Django, featuring customer account management, crypto wallets, trading capabilities, and AI-powered news analysis.

## Features

### Manager Dashboard
- **Customer Management**: Create, edit, view, and delete customer accounts
- **Professional Interface**: Modern card-based design with responsive layout
- **Search Functionality**: Filter customers by username, email, or phone
- **Secure Authentication**: Manager-specific login system
- **Account Verification**: Track customer eligibility and cashout status

### Customer Portal
- **Personal Dashboard**: View account balance and crypto holdings
- **Multi-Currency Support**: Bitcoin, Ethereum, XRP, and Stellar
- **Crypto Wallets**: Individual wallet management for each cryptocurrency
- **Live Price Charts**: Real-time cryptocurrency price tracking
- **Portfolio Analytics**: Track total portfolio value and performance

### Crypto Trading Features
- **Currency Conversion**: Exchange between different cryptocurrencies
- **P2P Transfers**: Send crypto to other platform users
- **Transaction History**: Track all transfers and conversions
- **Fee Structure**: Transparent 10% conversion fees
- **Real-time Rates**: Live market price integration

### AI-Powered News
- **Personalized Feed**: News filtered by user's crypto holdings
- **AI Summarization**: Intelligent article summaries
- **Multi-Source Aggregation**: News from various crypto sources
- **Interactive Interface**: Click-to-summarize functionality

## Technology Stack

- **Backend**: Django 4.x with Python
- **Frontend**: Bootstrap 5.3, HTML5, CSS3, JavaScript
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **APIs**: CoinGecko API for crypto prices, News API for articles
- **Authentication**: Django built-in authentication system
- **Styling**: Custom CSS with glassmorphism effects and modern gradients

## Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/trump-finance.git
   cd trump-finance
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   NEWS_API_KEY=your_news_api_key
   COINGECKO_API_KEY=your_coingecko_api_key  # Optional
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load Sample Data** (Optional)
   ```bash
   python manage.py loaddata fixtures/sample_data.json
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

## Project Structure

```
trump-finance/
├── custLogin/                 # Main Django app
│   ├── migrations/           # Database migrations
│   ├── templates/           # HTML templates
│   │   ├── base.html           # Base template
│   │   ├── manager_login.html  # Manager authentication
│   │   ├── manager_dashboard.html
│   │   ├── customer_login.html
│   │   ├── crypto_dashboard.html
│   │   ├── crypto_wallets.html
│   │   ├── crypto_profile.html
│   │   ├── crypto_transfer.html
│   │   ├── crypto_convert.html
│   │   └── crypto_news.html
│   ├── static/              # Static files
│   │   └── images/          # Logo and background images
│   ├── models.py            # Database models
│   ├── views.py             # View controllers
│   ├── forms.py             # Form definitions
│   ├── urls.py              # URL routing
│   └── utils.py             # Utility functions
├── trumpFinance/            # Project settings
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI configuration
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
└── README.md               # This file
```

## Models

### Customer
- Username, email, phone, address
- Balance and cashout eligibility
- Manager relationship
- Password management

### ManagerProfile
- Linked to Django User model
- Customer relationship management

### UserWallet
- Individual crypto wallets per customer
- Balance tracking for each cryptocurrency

### Cryptocurrency
- Supported currencies (BTC, ETH, XRP, XLM)
- Current USD values
- Market data integration

### CryptoTransfer & CryptoConvert
- Transaction history tracking
- Fee calculation and recording

## API Integration

### CoinGecko API
- Real-time cryptocurrency prices
- Historical market data
- Price chart generation

### News API
- Crypto-related news articles
- Source filtering and aggregation
- Content summarization integration

## Security Features

- CSRF protection on all forms
- Password hashing with Django's built-in system
- Session-based authentication
- Manager-level access controls
- Secure password storage and handling

## Customization

### Styling
- Custom CSS with Trump Finance branding
- Glassmorphism and modern design elements
- Fully responsive design
- Dark theme with gold accents

### Adding New Cryptocurrencies
1. Add currency to `Cryptocurrency` model
2. Update conversion logic in views
3. Add appropriate styling and icons
4. Configure API integration

## Deployment

### Production Checklist
- [ ] Set `DEBUG = False` in settings
- [ ] Configure proper database (PostgreSQL recommended)
- [ ] Set up static file serving
- [ ] Configure environment variables
- [ ] Set up SSL certificates
- [ ] Configure allowed hosts
- [ ] Set up backup systems

### Environment Variables
```env
SECRET_KEY=production_secret_key
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost/dbname
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
NEWS_API_KEY=your_production_news_api_key
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Write docstrings for complex functions
- Maintain responsive design principles
- Test on multiple screen sizes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub



## Acknowledgments

- Bootstrap for responsive design framework
- Font Awesome for icons
- CoinGecko for cryptocurrency data
- News API for article aggregation
- Django community for excellent documentation

## Version History

### v1.0.0 (Current)
- Initial release
- Complete manager and customer portals
- Crypto wallet functionality
- AI-powered news integration
- Responsive design implementation

---

**Note**: This is a demonstration project. Ensure proper security auditing before deploying to production environments.