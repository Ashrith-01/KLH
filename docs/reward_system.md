# Reward System Documentation

## 1) Point model
Each employee gets a monthly **Performance Index (0–110 capped by metric caps)** calculated from weighted KPI components:

- Sales attainment ratio (`sales_achieved / sales_target`) × 40 points (capped at 120% attainment)
- On-time delivery ratio (`deliveries_on_time / deliveries_target`) × 30 points (capped at 110% attainment)
- Customer rating (`customer_rating / 5`) × 20 points
- Attendance (`attendance_pct / 100`) × 10 points

## 2) Badges
Badges are earned each month according to threshold rules:

- **Sales Streak**: sales ratio ≥ 1.00
- **Delivery Hero**: on-time delivery ratio ≥ 0.98
- **Customer Champion**: customer rating ≥ 4.8
- **Reliability Pro**: attendance ≥ 98%
- **All-Rounder**: performance index ≥ 90

If no badge condition is met, the employee gets `Getting Started`.

## 3) Levels
- **Level 1 - Rookie**: < 70
- **Level 2 - Rising**: 70–79.99
- **Level 3 - Advanced**: 80–89.99
- **Level 4 - Expert**: 90–94.99
- **Level 5 - Elite**: ≥ 95

## 4) Reward tiers
- **Bronze (0+)**: Digital kudos + team mention
- **Silver (80+)**: Gift card raffle entry
- **Gold (90+)**: Priority shift preference
- **Platinum (100+)**: Performance bonus + feature spotlight

The dashboard automatically chooses the highest eligible tier per employee for the selected month.

## 5) Nudges
Personalized nudges are generated from underperforming dimensions:

- Sales ratio < 0.90 → closing-focus prompt
- Delivery ratio < 0.95 → route-planning prompt
- Customer rating < 4.5 → service consistency prompt
- Attendance < 95% → attendance reminder

If all dimensions are healthy, employees receive a reinforcement nudge focused on sustained momentum and peer mentorship.
