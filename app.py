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


LEVEL_THEME = {
    "Level 1 - Rookie": "#8FA7C7",
    "Level 2 - Rising": "#5BD2FF",
    "Level 3 - Advanced": "#6BFFA2",
    "Level 4 - Expert": "#FFD166",
    "Level 5 - Elite": "#00F5A0",
}


def inject_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg1: #020816;
                --bg2: #091d3a;
                --card: rgba(19, 35, 65, 0.78);
                --line: rgba(91, 210, 255, 0.45);
                --txt: #e7f0ff;
                --muted: #9fb6d4;
                --aqua: #33d6ff;
                --lime: #57f287;
                --warn: #ffd166;
            }
            .stApp {
                background: radial-gradient(circle at 15% 0%, #123f70 0%, var(--bg2) 35%, var(--bg1) 85%);
                color: var(--txt);
            }
            .block-container {
                padding-top: 1.2rem;
                padding-bottom: 2rem;
                max-width: 1400px;
            }
            .portal-title {
                font-size: 3.2rem;
                font-weight: 900;
                letter-spacing: 1px;
                margin: 0;
                color: var(--txt);
                text-transform: uppercase;
            }
            .portal-title span { color: var(--aqua); }
            .card {
                background: linear-gradient(120deg, rgba(22,39,70,0.86), rgba(15,27,49,0.82));
                border: 1px solid var(--line);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                box-shadow: 0 10px 28px rgba(0,0,0,.32);
                margin-bottom: 0.7rem;
            }
            .hero {
                display: flex;
                gap: 1rem;
                align-items: center;
                margin-bottom: .8rem;
            }
            .avatar {
                width: 86px;
                height: 86px;
                border-radius: 50%;
                border: 3px solid var(--aqua);
                background: linear-gradient(145deg,#1e3f6f,#09172b);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
            }
            .hero-name { font-size: 2rem; font-weight: 800; margin:0; }
            .hero-level { color: var(--muted); font-size: 1rem; font-weight: 700; margin:0; text-transform: uppercase; }
            .kpi-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0,1fr));
                gap: .8rem;
            }
            .kpi-card h4 { margin:0; color: var(--muted); font-size: 0.95rem; text-transform: uppercase; }
            .kpi-card .value { margin-top: .45rem; font-size: 2rem; font-weight: 800; color: var(--txt); }
            .kpi-card .delta-up { color: var(--lime); font-weight: 700; }
            .kpi-card .delta-down { color: #ff8585; font-weight: 700; }
            .section-title {
                margin: .2rem 0 .7rem;
                text-transform: uppercase;
                color: #dbe9ff;
                letter-spacing: .4px;
                font-weight: 800;
            }
            .nudge {
                border: 1px solid rgba(159,182,212,.35);
                border-radius: 12px;
                padding: .72rem .8rem;
                margin-bottom: .55rem;
                background: rgba(9, 20, 38, 0.55);
            }
            .achievement {
                display: inline-block;
                margin: .25rem .4rem .25rem 0;
                padding: .35rem .75rem;
                border-radius: 999px;
                border: 1px solid rgba(91,210,255,.5);
                color: #d8f5ff;
                font-size: .86rem;
                font-weight: 700;
                background: rgba(9,27,49,.62);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
        prompts.append("🔥 Delivery Dash: Close one extra high-intent sale before shift end for +50 XP.")
    if row["delivery_ratio"] < 0.95:
        prompts.append("📦 Route Boost: Reorder early stops to raise your on-time streak today.")
    if row["customer_rating"] < 4.5:
        prompts.append("🛡️ Streak Saver: Use the 30-second closeout script to protect your rating.")
    if row["attendance_pct"] < 95:
        prompts.append("📅 Attendance Quest: Keep a 5-day attendance streak to unlock bonus points.")

    if not prompts:
        return "⭐ Elite Quest: Sustain momentum and mentor a teammate this week for bonus recognition."
    return " ".join(prompts[:2])


def apply_gamification(df: pd.DataFrame) -> pd.DataFrame:
    scored = df.copy()
    scored["sales_ratio"] = (scored["sales_achieved"] / scored["sales_target"]).clip(upper=1.2)
    scored["delivery_ratio"] = (scored["deliveries_on_time"] / scored["deliveries_target"]).clip(upper=1.1)

    scored["points_sales"] = scored["sales_ratio"] * POINT_WEIGHTS["sales"]
    scored["points_delivery"] = scored["delivery_ratio"] * POINT_WEIGHTS["deliveries"]
    scored["points_rating"] = (scored["customer_rating"] / 5) * POINT_WEIGHTS["rating"]
    scored["points_attendance"] = (scored["attendance_pct"] / 100) * POINT_WEIGHTS["attendance"]
    scored["performance_index"] = scored[
        ["points_sales", "points_delivery", "points_rating", "points_attendance"]
    ].sum(axis=1).round(2)

    scored["badges"] = scored.apply(
        lambda r: ", ".join([name for name, rule in BADGE_RULES.items() if rule(r)]) or "Getting Started",
        axis=1,
    )
    scored["level"] = scored["performance_index"].apply(assign_level)
    scored["reward_tier"] = scored["performance_index"].apply(lambda p: reward_from_points(p).name)
    scored["reward"] = scored["performance_index"].apply(lambda p: reward_from_points(p).reward)
    scored["nudge"] = scored.apply(generate_nudge, axis=1)

    scored = scored.sort_values(["month", "performance_index"], ascending=[True, False])
    scored["rank"] = scored.groupby("month")["performance_index"].rank(method="first", ascending=False).astype(int)
    scored["xp_points"] = (scored["performance_index"] * 150).round().astype(int)
    scored["streak_days"] = (
        7
        + (scored["delivery_ratio"] * 7).round().astype(int)
        + (scored["attendance_pct"] > 97).astype(int) * 3
    )
    return scored


def render_hero(player: pd.Series, team_rank: int, total_players: int) -> None:
    level_color = LEVEL_THEME.get(player["level"], "#5BD2FF")
    progress = min(player["performance_index"] / 100, 1.0)
    st.markdown(
        f"""
        <div class='card'>
            <div class='hero'>
                <div class='avatar'>🏃</div>
                <div>
                    <p class='hero-name'>{player['employee_name']}</p>
                    <p class='hero-level' style='color:{level_color};'>{player['level']}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(progress)

    m1, m2, m3 = st.columns(3)
    m1.markdown(f"<div class='card'><h4 class='section-title'>Points</h4><div class='value'>{player['xp_points']:,} XP</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='card'><h4 class='section-title'>Current Rank</h4><div class='value'>#{team_rank}/{total_players}</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='card'><h4 class='section-title'>Streak</h4><div class='value'>{player['streak_days']} days</div></div>", unsafe_allow_html=True)


def render_portal(scored: pd.DataFrame) -> None:
    st.markdown("<h1 class='portal-title'>Performance <span>Portal</span></h1>", unsafe_allow_html=True)

    teams = ["All"] + sorted(scored["team"].unique().tolist())
    selected_team = st.sidebar.selectbox("Team", teams)
    month_options = sorted(scored["month"].dt.strftime("%Y-%m").unique().tolist())
    selected_month = st.sidebar.selectbox("Month", month_options, index=len(month_options) - 1)

    view = scored[scored["month"].dt.strftime("%Y-%m") == selected_month].copy()
    if selected_team != "All":
        view = view[view["team"] == selected_team]

    if view.empty:
        st.warning("No records found for selected filters.")
        return

    hero_col, side_col = st.columns([1.35, 1], gap="large")
    top_player = view.sort_values("performance_index", ascending=False).iloc[0]

    with hero_col:
        render_hero(top_player, int(top_player["rank"]), len(view))

    with side_col:
        st.markdown("<div class='kpi-grid'>", unsafe_allow_html=True)
        sales_pct = top_player["sales_ratio"] * 100
        delivery_pct = top_player["delivery_ratio"] * 100
        rating = top_player["customer_rating"]
        st.markdown(
            f"<div class='card kpi-card'><h4>Average Delivery Time</h4><div class='value'>{max(15, 40 - int(delivery_pct/4))} min</div><div class='delta-up'>↑ better this month</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='card kpi-card'><h4>Sales Conversions</h4><div class='value'>{sales_pct/12:.1f}%</div><div class='delta-up'>↑ {sales_pct-95:.1f}%</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='card kpi-card'><h4>Customer Rating</h4><div class='value'>{rating:.1f}</div><div class='delta-up'>/ 5 stars</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([1.6, 1], gap="large")

    with left:
        st.markdown("<div class='card'><h3 class='section-title'>Leaderboard</h3>", unsafe_allow_html=True)
        leaderboard = view.sort_values("performance_index", ascending=False).copy()
        leaderboard["badge_icon"] = leaderboard["reward_tier"].map(
            {"Platinum": "🏆", "Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}
        )
        show = leaderboard[["rank", "employee_name", "xp_points", "reward_tier", "badge_icon"]]
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'><h3 class='section-title'>Weekly Engagement Trend</h3>", unsafe_allow_html=True)
        trend = view.sort_values("performance_index", ascending=False)[["employee_name", "xp_points"]].copy()
        trend = trend.set_index("employee_name")
        st.line_chart(trend)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'><h3 class='section-title'>Active Quests & Nudges</h3>", unsafe_allow_html=True)
        for _, row in leaderboard.head(3).iterrows():
            st.markdown(
                f"<div class='nudge'><strong>{row['employee_name']}:</strong> {row['nudge']}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'><h3 class='section-title'>Recent Achievements</h3>", unsafe_allow_html=True)
        top_badges = ", ".join(leaderboard.iloc[0]["badges"].split(",")[:3])
        for badge in [b.strip() for b in top_badges.split(",") if b.strip()]:
            st.markdown(f"<span class='achievement'>{badge}</span>", unsafe_allow_html=True)
        milestone_ratio = min(top_player["deliveries_on_time"] / max(top_player["deliveries_target"], 1), 1.0)
        st.progress(milestone_ratio)
        st.caption(
            f"Next Badge Milestone: {top_player['deliveries_on_time']}/{top_player['deliveries_target']} deliveries"
        )
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="Performance Portal", layout="wide")
    inject_theme()
    st.sidebar.header("Data Ingestion")
    uploaded = st.sidebar.file_uploader("Upload KPI CSV", type=["csv"])

    try:
        df = load_data(uploaded)
        scored = apply_gamification(df)
        render_portal(scored)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load dashboard: {exc}")


if __name__ == "__main__":
    main()
