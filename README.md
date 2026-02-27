# Gamified Performance Feedback Agent

Streamlit-based agent that transforms monthly KPI data into a gamified feedback experience for frontline delivery and sales teams.

## Tech stack
- Python
- Streamlit
- Pandas

## Deliverables in this repo
1. **Gamified performance dashboard**: `app.py`
2. **Demo with sample KPI data**: `data/sample_kpis.csv`
3. **Reward system documentation**: `docs/reward_system.md`
4. **Engagement analytics report**: `reports/engagement_analytics_report.md`

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

Upload your own CSV from the sidebar or use the bundled sample file.

## Expected input columns
- `employee_id`
- `employee_name`
- `team`
- `month`
- `sales_target`
- `sales_achieved`
- `deliveries_target`
- `deliveries_on_time`
- `customer_rating`
- `attendance_pct`
