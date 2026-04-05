# --- Reference lists (edit to match your program roster and suppliers) ---
CFO_NAMES = [
    "Alex Rivera",
    "Jordan Kim",
    "Sam Patel",
    "Taylor Chen",
    "Riley Martinez",
    "Casey Nguyen",
    "Morgan Lee",
    "Jamie Wilson",
]

PROVIDERS = [
    "Amazon",
    "McMaster-Carr",
    "DigiKey",
    "SparkFun",
    "Adafruit",
    "Grainger",
    "Local vendor / cash reimbursement",
    "Other (see notes)",
]

CLASSES = ["Class 1", "Class 2"]


def selectable_academic_quarters(*, start_year: int = 2026, num_years: int = 3) -> list[str]:
    """Fixed catalog of terms (no free-form year picker). Order: Spring → Summer → Fall → Winter per year."""
    seasons = ("Spring", "Summer", "Fall", "Winter")
    out: list[str] = []
    for y in range(start_year, start_year + num_years):
        for s in seasons:
            out.append(f"{s} {y}")
    return out


# Teachers may only assign classes to these quarters (edit start_year/num_years to extend the window).
SELECTABLE_QUARTERS: list[str] = selectable_academic_quarters()

# DB / UI label for classes created before quarters existed
LEGACY_QUARTER_LABEL = "Legacy (no quarter assigned)"

STATUSES = [
    "pending",
    "approved",
    "ordered",
    "received",
    "rejected",
    "backordered",
    "returned_refunded",
    "archived",
]

# Admin class / All orders UI: workflow status dropdown (teacher flows still use STATUSES above).
ADMIN_CLASS_ORDER_STATUSES = [
    "pending",
    "approved",
    "ordered",
    "backordered",
    "arrived",
    "needs_return",
    "verified",
    "cancelled",
]

# Admin-only: procurement tracking separate from line workflow `status`
ADMIN_ORDER_FULFILLMENT_ONGOING = "ongoing"
ADMIN_ORDER_FULFILLMENT_COMPLETED = "completed"
ADMIN_ORDER_FULFILLMENT_OPTIONS = [
    ADMIN_ORDER_FULFILLMENT_ONGOING,
    ADMIN_ORDER_FULFILLMENT_COMPLETED,
]

NEED_ATTENTION_STATUSES = frozenset({"rejected", "backordered", "returned_refunded"})

# Student dashboard: status cell backgrounds (raw DB value -> CSS color)
STUDENT_STATUS_BG = {
    "pending": "#fff9c4",
    "approved": "#c8e6c9",
    "rejected": "#ffcdd2",
    "ordered": "#bbdefb",
    "received": "#e0e0e0",
    "archived": "#eceff1",
    "backordered": "#ffe0b2",
    "returned_refunded": "#e1bee7",
    "arrived": "#e0e0e0",
    "needs_return": "#ffe0b2",
    "verified": "#c8e6c9",
    "cancelled": "#ffcdd2",
}
