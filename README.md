# 📦 Supply Chain Stock Optimization App

A comprehensive Streamlit application for optimizing inventory levels in supply chain management using proven techniques like EOQ (Economic Order Quantity), Reorder Point (ROP), and Safety Stock calculations.

## Features

### 🎯 Single Product Analysis
- Calculate optimal order quantities using EOQ formula
- Determine reorder points and safety stock levels
- Visualize inventory levels over time
- Analyze cost breakdowns (ordering vs. holding costs)
- Customize service levels and demand variability

### 📊 Multi-Product Comparison
- Compare optimization results across multiple products
- Side-by-side analysis of EOQ, ROP, and costs
- Visual comparisons with interactive charts

### 🔬 Scenario Analysis
- Test sensitivity to parameter changes
- Analyze impact of demand, costs, and service levels
- Make data-driven decisions with what-if scenarios

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Input Parameters

### Demand & Lead Time
- **Annual Demand**: Total units needed per year
- **Lead Time**: Days between ordering and receiving stock
- **Demand Std Dev**: Daily demand variability (standard deviation)

### Cost Parameters
- **Ordering Cost**: Fixed cost per order placement ($)
- **Holding Cost Rate**: Annual cost to hold inventory (% of unit cost)
- **Unit Cost**: Price per unit ($)
- **Stockout Cost**: Cost of running out of stock ($)

### Service Level
- Target percentage of demand met from stock (90-99%)
- Higher service levels require more safety stock

## Optimization Formulas

### Economic Order Quantity (EOQ)
```
EOQ = √((2 × D × S) / H)
```
where:
- D = Annual demand
- S = Ordering cost per order
- H = Holding cost per unit per year

### Reorder Point (ROP)
```
ROP = (Average daily demand × Lead time) + Safety stock
```

### Safety Stock
```
Safety Stock = Z × σ_L
```
where:
- Z = Z-score for desired service level
- σ_L = Standard deviation during lead time

## Example Use Cases

1. **Manufacturing**: Optimize raw material inventory
2. **Retail**: Manage product stock levels across stores
3. **E-commerce**: Balance fulfillment speed vs. storage costs
4. **Wholesale**: Determine optimal bulk ordering quantities

## Technology Stack

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Plotly**: Interactive visualizations
- **SciPy**: Statistical calculations

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── optimization.py        # Inventory optimization algorithms
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Tips for Best Results

1. **Accurate Data**: Use historical data for demand and costs
2. **Service Level**: Balance between customer satisfaction and inventory costs
3. **Lead Time**: Include safety margins for supplier reliability
4. **Review Regularly**: Update parameters as business conditions change

## License

This project is open source and available for educational and commercial use.

## Contributing

Feel free to fork, modify, and enhance this application for your specific needs.

---

Built with ❤️ using Streamlit | Optimizing supply chains since 2026
