import io
from dataclasses import dataclass

import pandas as pd
import streamlit as st


POINT_WEIGHTS = {
    "sales": 40,
    "deliveries": 30,
    "rating": 20,
    "attendance": 10,
}


BADGE_RULES = {
    "Sales Streak": lambda r: r["sales_ratio"] >= 1.0,
    "Delivery Hero": lambda r: r["delivery_ratio"] >= 0.98,
    "Customer Champion": lambda r: r["customer_rating"] >= 4.8,
    "Reliability Pro": lambda r: r["attendance_pct"] >= 98,
    "All-Rounder": lambda r: r["performance_index"] >= 90,
}


@dataclass
class RewardTier:
    name: str
    min_points: int
    reward: str


REWARD_TIERS = [
    RewardTier("Bronze", 0, "Digital kudos + team mention"),
    RewardTier("Silver", 80, "Gift card raffle entry"),
    RewardTier("Gold", 90, "Priority shift preference"),
    RewardTier("Platinum", 100, "Performance bonus + feature spotlight"),
]


def load_data(uploaded_file: io.BytesIO | None) -> pd.DataFrame:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv("data/sample_kpis.csv")

    required_cols = {
        "employee_id",
        "employee_name",
        "team",
        "month",
        "sales_target",
        "sales_achieved",
        "deliveries_target",
        "deliveries_on_time",
        "customer_rating",
        "attendance_pct",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    df["month"] = pd.to_datetime(df["month"])
    return df


def assign_level(points: float) -> str:
    if points >= 95:
        return "Level 5 - Elite"
    if points >= 90:
        return "Level 4 - Expert"
    if points >= 80:
        return "Level 3 - Advanced"
    if points >= 70:
        return "Level 2 - Rising"
    return "Level 1 - Rookie"


def reward_from_points(points: float) -> RewardTier:
    tier = REWARD_TIERS[0]
    for candidate in REWARD_TIERS:
        if points >= candidate.min_points:
            tier = candidate
    return tier


def generate_nudge(row: pd.Series) -> str:
    prompts: list[str] = []
    if row["sales_ratio"] < 0.9:
        prompts.append("Focus on high-intent leads and close one additional deal this week.")
    if row["delivery_ratio"] < 0.95:
        prompts.append("Prioritize route planning at shift start to improve on-time delivery.")
    if row["customer_rating"] < 4.5:
        prompts.append("Use the 30-second closeout script to boost service consistency.")
    if row["attendance_pct"] < 95:
        prompts.append("Set attendance reminders to keep your streak active.")

    if not prompts:
        return "Outstanding month—maintain momentum and mentor one teammate."
    return " ".join(prompts[:2])


def apply_gamification(df: pd.DataFrame) -> pd.DataFrame:
    scored = df.copy()
    scored["sales_ratio"] = (scored["sales_achieved"] / scored["sales_target"]).clip(upper=1.2)
    scored["delivery_ratio"] = (scored["deliveries_on_time"] / scored["deliveries_target"]).clip(upper=1.1)

    scored["points_sales"] = scored["sales_ratio"] * POINT_WEIGHTS["sales"]
    scored["points_delivery"] = scored["delivery_ratio"] * POINT_WEIGHTS["deliveries"]
    scored["points_rating"] = (scored["customer_rating"] / 5) * POINT_WEIGHTS["rating"]
    scored["points_attendance"] = (scored["attendance_pct"] / 100) * POINT_WEIGHTS["attendance"]
    scored["performance_index"] = (
        scored[["points_sales", "points_delivery", "points_rating", "points_attendance"]].sum(axis=1).round(2)
    )

    scored["badges"] = scored.apply(
        lambda r: ", ".join([name for name, rule in BADGE_RULES.items() if rule(r)]) or "Getting Started",
        axis=1,
    )
    scored["level"] = scored["performance_index"].apply(assign_level)
    scored["reward_tier"] = scored["performance_index"].apply(lambda p: reward_from_points(p).name)
    scored["reward"] = scored["performance_index"].apply(lambda p: reward_from_points(p).reward)
    scored["nudge"] = scored.apply(generate_nudge, axis=1)
    return scored


def build_dashboard(scored: pd.DataFrame) -> None:
    st.set_page_config(page_title="Gamified Performance Feedback Agent", layout="wide")
    st.title("🎮 Gamified Performance Feedback Agent")
    st.caption("Real-time KPI feedback for delivery and sales frontline teams")

    teams = ["All"] + sorted(scored["team"].unique().tolist())
    selected_team = st.sidebar.selectbox("Team", teams)

    month_options = sorted(scored["month"].dt.strftime("%Y-%m").unique().tolist())
    selected_month = st.sidebar.selectbox("Month", month_options, index=len(month_options) - 1)

    view = scored.copy()
    if selected_team != "All":
        view = view[view["team"] == selected_team]
    view = view[view["month"].dt.strftime("%Y-%m") == selected_month]

    if view.empty:
        st.warning("No records found for selected filters.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Performance Index", f"{view['performance_index'].mean():.1f}")
    c2.metric("Top Score", f"{view['performance_index'].max():.1f}")
    c3.metric("Employees Tracked", f"{view['employee_id'].nunique()}")
    c4.metric("Avg Customer Rating", f"{view['customer_rating'].mean():.2f}")

    st.subheader("🏆 Interactive Leaderboard")
    leaderboard = (
        view.sort_values("performance_index", ascending=False)[
            [
                "employee_name",
                "team",
                "performance_index",
                "level",
                "badges",
                "reward_tier",
            ]
        ]
        .reset_index(drop=True)
    )
    leaderboard.index = leaderboard.index + 1
    st.dataframe(leaderboard, use_container_width=True)

    st.subheader("📈 KPI Performance Breakdown")
    perf = view[["employee_name", "sales_ratio", "delivery_ratio", "customer_rating", "attendance_pct"]].copy()
    perf["sales_ratio"] = (perf["sales_ratio"] * 100).round(1)
    perf["delivery_ratio"] = (perf["delivery_ratio"] * 100).round(1)
    perf = perf.set_index("employee_name")
    st.bar_chart(perf[["sales_ratio", "delivery_ratio", "attendance_pct"]])

    st.subheader("🎯 Personalized Nudges & Rewards")
    feedback = view[["employee_name", "performance_index", "reward", "nudge"]].sort_values(
        "performance_index", ascending=False
    )
    for _, row in feedback.iterrows():
        with st.expander(f"{row['employee_name']} · Score {row['performance_index']:.1f}"):
            st.markdown(f"**Reward:** {row['reward']}")
            st.markdown(f"**Nudge:** {row['nudge']}")

    st.subheader("📊 Engagement Analytics Snapshot")
    analytics = view.assign(
        high_engagement=lambda d: d["performance_index"] >= 85,
        badge_count=lambda d: d["badges"].str.split(",").str.len(),
    )
    summary = pd.DataFrame(
        {
            "Metric": [
                "High-engagement share",
                "Avg badges earned",
                "Needs coaching (<75 score)",
            ],
            "Value": [
                f"{(analytics['high_engagement'].mean() * 100):.1f}%",
                f"{analytics['badge_count'].mean():.2f}",
                int((analytics["performance_index"] < 75).sum()),
            ],
        }
    )
    st.table(summary)


def main() -> None:
    st.sidebar.header("Data Ingestion")
    uploaded = st.sidebar.file_uploader("Upload KPI CSV", type=["csv"])

    try:
        df = load_data(uploaded)
        scored = apply_gamification(df)
        build_dashboard(scored)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load dashboard: {exc}")


if __name__ == "__main__":
    main()
