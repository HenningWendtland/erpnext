import frappe


def execute():
	"""Backfill `allocated_gross_amount` on child rows that carry advance allocations.

	Pre-existing rows have no linked Advance Taxes, so gross equals `allocated_amount`.
	Without this backfill, `total_advance` (now summed off gross with a net fallback)
	would still be correct, but reposts that re-derive gross from current taxes
	could diverge. Backfilling once lets every downstream code path read gross
	unconditionally.
	"""
	tables = (
		"Payment Entry Reference",
		"Sales Invoice Advance",
		"Purchase Invoice Advance",
	)
	for table in tables:
		if not frappe.db.has_column(table, "allocated_gross_amount"):
			continue

		frappe.db.sql(
			f"""
			UPDATE `tab{table}`
			SET allocated_gross_amount = allocated_amount
			WHERE allocated_gross_amount IS NULL OR allocated_gross_amount = 0
			"""
		)
