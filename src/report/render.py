"""Minimal HTML report renderer."""

from __future__ import annotations


def render_report(summary: dict) -> str:
    plate_rows = []
    rerun_items = []
    global_counts = summary.get("global_counts", {})
    for plate in summary.get("plates", []):
        plate_rows.append(
            "<tr>"
            f"<td>{plate['plate_id']}</td>"
            f"<td>{plate['well_total']}</td>"
            f"<td>{plate['pass_count']}</td>"
            f"<td>{plate['review_count']}</td>"
            f"<td>{plate['rerun_count']}</td>"
            f"<td>{plate['plate_status']}</td>"
            "</tr>"
        )
        if int(plate.get("rerun_count", 0)) > 0:
            rerun_items.append(
                "<li>"
                f"{plate['plate_id']}: rerun_count={plate['rerun_count']}, "
                f"ntc_contamination_count={plate.get('ntc_contamination_count', 0)}, "
                f"replicate_discordance_count={plate.get('replicate_discordance_count', 0)}"
                "</li>"
            )
    rows = "".join(plate_rows)
    rerun_html = "<ul>" + "".join(rerun_items) + "</ul>" if rerun_items else "<p>No rerun-triggering flags detected.</p>"
    return (
        "<html><head><title>qPCR HMM QC Report</title></head><body>"
        "<h1>qPCR HMM QC Summary</h1>"
        "<h2>Overview</h2>"
        f"<p>Pass={global_counts.get('pass', 0)} | Review={global_counts.get('review', 0)} | Rerun={global_counts.get('rerun', 0)}</p>"
        "<h2>Per-Plate Summary</h2>"
        "<table border='1'>"
        "<tr><th>Plate</th><th>Total</th><th>Pass</th><th>Review</th><th>Rerun</th><th>Status</th></tr>"
        f"{rows}</table>"
        "<h2>Rerun Rationale</h2>"
        f"{rerun_html}</body></html>"
    )
