# Payment Schedule Generator

A CLI tool that generates weekend/holiday payment schedule tables based on business rules for benefit payment processing.

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Generate payment schedule tables using the command line:

```bash
# Generate full year table
python payment_schedule_generator.py --table 109 --year 2015

# Generate specific month by number
python payment_schedule_generator.py --table 109 --year 2015 --month 3

# Generate specific month by name
python payment_schedule_generator.py --table 109 --year 2015 --month Mar
python payment_schedule_generator.py --table 109 --year 2015 --month March
```

### Arguments

- `--table`: Table number (currently supports `109`)
- `--year`: Year to generate schedule for (e.g., `2015`)
- `--month`: Optional. Month number (1-12) or name (Jan, January, etc.)

## Business Rules

Based on documented rules for Table 109 (Weekend/Holiday Table in Arrears):
- Payment dates calculated by subtracting 2 working days from run date
- Weekend handling: Use Friday's payment date
- Holiday handling: Use previous working day's payment date
- Cross-month payment dates supported
