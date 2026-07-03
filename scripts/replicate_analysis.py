"""Reproduce the key statistics from the WTI geopolitical risk analysis.

The original analysis was performed in Excel (pivot tables, frequency
distributions, descriptive statistics). This script independently
reproduces the headline results from the raw data in
data/wti_daily_prices.csv using pandas and scipy.

Usage:
    python scripts/replicate_analysis.py
"""

from pathlib import Path

import pandas as pd
from scipy import stats

DATA = Path(__file__).resolve().parents[1] / "data" / "wti_daily_prices.csv"
REGIME_ORDER = [
    "De-escalation",
    "Policy Uncertainty",
    "Geopolitical Tension",
    "Military Escalation",
]


def main() -> None:
    df = pd.read_csv(DATA, parse_dates=["Date"])
    daily = df.dropna(subset=["Daily Chg(%)"])

    print("=" * 68)
    print("WTI Crude Oil Geopolitical Risk Analysis — replication")
    print(f"{len(df)} trading days, {df['Date'].min():%b %Y} – {df['Date'].max():%b %Y}")
    print("=" * 68)

    print("\nAverage price change by regime (%):")
    summary = df.groupby("Event Category")[
        ["3-Day Chg(%)", "7-Day Chg (%)", "30-Day Chg (%)"]
    ].mean().reindex(REGIME_ORDER)
    print(summary.round(2).to_string())

    print("\nDaily price-change volatility by regime:")
    vol = daily.groupby("Event Category")["Daily Chg(%)"].agg(["count", "mean", "std"])
    print(vol.reindex(REGIME_ORDER).round(2).to_string())

    esc = daily.loc[daily["Event Category"] == "Military Escalation", "Daily Chg(%)"]
    pol = daily.loc[daily["Event Category"] == "Policy Uncertainty", "Daily Chg(%)"]

    print("\nMilitary Escalation vs. Policy Uncertainty (daily % change):")
    print(f"  sigma = {esc.std():.1f}% vs {pol.std():.1f}%  (~{esc.std() / pol.std():.1f}x)")
    print(f"  Share of escalation days with |move| > 2%: {(esc.abs() > 2).mean():.1%}")

    lev_stat, lev_p = stats.levene(esc, pol)
    print(f"  Levene variance test: W = {lev_stat:.2f}, p = {lev_p:.2e}")

    t_stat, t_p = stats.ttest_ind(esc, pol, equal_var=False)
    print(f"  Welch t-test on daily means: t = {t_stat:.2f}, p = {t_p:.3f}")
    print(
        "\n  Interpretation: the regimes differ significantly in VOLATILITY\n"
        "  (variance), while mean daily returns alone are too noisy to\n"
        "  separate — the return signal emerges over 7- and 30-day windows."
    )


if __name__ == "__main__":
    main()
