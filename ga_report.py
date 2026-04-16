#!/usr/bin/env python3
"""
Daily GA4 report for The Times of Climate Change.
Usage: python3 ga_report.py [--days 1]
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    Dimension, Metric, DateRange, FilterExpression,
    Filter, OrderBy
)

PROPERTY_ID = "530360067"
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "ga_credentials.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_FILE


def get_client():
    return BetaAnalyticsDataClient()


def date_range(days):
    end = datetime.today()
    start = end - timedelta(days=days - 1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def run_report(client, start_date, end_date, dimensions, metrics, order_by=None, limit=20, dimension_filter=None):
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        limit=limit,
    )
    if order_by:
        req.order_bys = order_by
    if dimension_filter:
        req.dimension_filter = dimension_filter
    return client.run_report(req)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=1, help="Number of days to report on (default: 1 = yesterday/today)")
    args = parser.parse_args()

    days = args.days
    start_date, end_date = date_range(days)
    label = "Today" if days == 1 else f"Last {days} days"

    print(f"\n🔦 Times of Climate Change — Daily GA Report")
    print(f"   {label}: {start_date} → {end_date}")

    client = get_client()

    # ── 1. Views by page ──────────────────────────────────────────
    section("1. Page Views")
    resp = run_report(
        client, start_date, end_date,
        dimensions=["pageTitle", "pagePath"],
        metrics=["screenPageViews"],
        order_by=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=15
    )
    print(f"  {'Views':<8} {'Page'}")
    print(f"  {'-'*8} {'-'*50}")
    total_views = 0
    for row in resp.rows:
        views = int(row.metric_values[0].value)
        title = row.dimension_values[0].value[:45]
        total_views += views
        print(f"  {views:<8} {title}")
    print(f"\n  TOTAL VIEWS: {total_views}")

    # ── 2. Avg session duration ───────────────────────────────────
    section("2. Average Time on Site")
    resp = run_report(
        client, start_date, end_date,
        dimensions=["date"],
        metrics=["averageSessionDuration", "sessions", "totalUsers"]
    )
    for row in resp.rows:
        secs = float(row.metric_values[0].value)
        sessions = row.metric_values[1].value
        users = row.metric_values[2].value
        mins, s = divmod(int(secs), 60)
        print(f"  Users: {users}  |  Sessions: {sessions}  |  Avg time: {mins}m {s:02d}s")

    # ── 3. Torchlight: started vs completed ──────────────────────
    section("3. Torchlight — Started vs Completed")
    resp_start = run_report(
        client, start_date, end_date,
        dimensions=["customEvent:puzzle_date"],
        metrics=["eventCount"],
        order_by=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="torchlight_start")
            )
        )
    )
    resp_complete = run_report(
        client, start_date, end_date,
        dimensions=["customEvent:puzzle_date"],
        metrics=["eventCount"],
        order_by=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="torchlight_complete")
            )
        )
    )
    starts = {r.dimension_values[0].value: int(r.metric_values[0].value) for r in resp_start.rows}
    completes = {r.dimension_values[0].value: int(r.metric_values[0].value) for r in resp_complete.rows}
    all_dates = sorted(set(list(starts.keys()) + list(completes.keys())), reverse=True)
    print(f"  {'Puzzle Date':<15} {'Started':<10} {'Completed':<12} {'Rate'}")
    print(f"  {'-'*15} {'-'*10} {'-'*12} {'-'*6}")
    for d in all_dates:
        s = starts.get(d, 0)
        c = completes.get(d, 0)
        pct = f"{c/s*100:.0f}%" if s > 0 else "—"
        print(f"  {d:<15} {s:<10} {c:<12} {pct}")

    # ── 4. Torchlight: Won vs Lost ────────────────────────────────
    section("4. Torchlight — Won vs Lost")
    resp_won = run_report(
        client, start_date, end_date,
        dimensions=["customEvent:won"],
        metrics=["eventCount"],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="torchlight_complete")
            )
        )
    )
    if resp_won.rows:
        for row in resp_won.rows:
            won = row.dimension_values[0].value
            count = row.metric_values[0].value
            emoji = "🏆" if won == "true" else "💀"
            print(f"  {emoji} {'Won' if won == 'true' else 'Lost'}: {count}")
    else:
        print(f"  No completions yet today.")

    # ── 5. Share button clicks ────────────────────────────────────
    section("5. Share Button Clicks")
    print("  Not yet tracked. (torchlight_share events not wired up)")

    # ── 6. Outbound link clicks ───────────────────────────────────
    section("6. Outbound Link Clicks")
    resp = run_report(
        client, start_date, end_date,
        dimensions=["linkUrl"],
        metrics=["eventCount"],
        order_by=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=10,
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="click")
            )
        )
    )
    if resp.rows:
        for row in resp.rows:
            url = row.dimension_values[0].value[:55]
            count = row.metric_values[0].value
            print(f"  {count:<6} {url}")
    else:
        print("  No outbound click data.")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
