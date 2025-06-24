# Recipe Details Finder

A Python application that leverages the Spoonacular API to search for recipes and display detailed information including ingredients, instructions, and nutritional data.

## Project Overview

This project demonstrates working with complex nested JSON data structures through the Spoonacular API. Users can search for recipes and view detailed information including ingredients with measurements and step-by-step cooking instructions.

## Features

- Recipe search functionality
- Detailed ingredient lists with measurements
- Step-by-step cooking instructions
- Error handling for API responses
- Clean and formatted output display

## Prerequisites

- Python 3.8+
- Spoonacular API key (sign up at [Spoonacular's website](https://spoonacular.com/food-api))

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd recipe-details-finder
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Spoonacular API key:
```
SPOONACULAR_API_KEY=your_api_key_here
```

## Project Structure

```
recipe-details-finder/
├── .env                  # Stores API key
├── .gitignore           # Git ignore file
├── requirements.txt     # Project dependencies
├── README.md           # Project documentation
├── PROGRESS.md         # Development progress tracking
├── main.py            # Main application entry point
└── src/
    ├── __init__.py    # Makes src a Python package
    ├── api_client.py  # API interaction functions
    └── data_parser.py # JSON response parsing functions
```

## Usage

1. Ensure your virtual environment is activated
2. Run the main script:
```bash
python main.py
```
3. Follow the prompts to search for recipes

## Development Progress

See [PROGRESS.md](PROGRESS.md) for detailed development progress and upcoming features.

## Error Handling

The application includes robust error handling for:
- API connection issues
- Invalid API keys
- No results found
- Malformed JSON responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 