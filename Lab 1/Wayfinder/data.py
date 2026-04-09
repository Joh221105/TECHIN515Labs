"""
Wayfinder — resource records, validation, and search/filter logic.
"""

from __future__ import annotations

RESOURCE_KEYS: frozenset[str] = frozenset(
    {
        "name",
        "category",
        "location",
        "lat",
        "lon",
        "hours",
        "access",
        "description",
        "tags",
        "cost",
        "contact",
    }
)

RESOURCES: list[dict[str, object]] = [
    {
        "name": "GIX Makerspace",
        "category": "Makerspace",
        "location": "Steve Ballmer Building — Prototyping Lab (check door signage)",
        "hours": "Mon–Fri 9:00–21:00; weekends by reservation for capstone teams",
        "access": "GIX student/staff Husky Card tap; orientation required before solo use",
        "description": "Laser cutters, 3D printers, hand tools, and electronics benches for physical prototyping. Staff can help with machine training and material questions.",
        "tags": ["3d-printing", "laser", "electronics", "prototyping", "training"],
        "cost": "Included for enrolled students; specialty materials billed at cost",
        "contact": "makerspace@gix.uw.edu",
        "lat": 47.6197,
        "lon": -122.18545,
    },
    {
        "name": "Indoor bike storage",
        "category": "Transportation",
        "location": "Ground floor, secure card-access bike room near main entrance",
        "hours": "Building access hours (typically 7:00–22:00)",
        "access": "Husky Card; register your bike sticker at front desk once per quarter",
        "description": "Covered racks and repair stand with basic tools. Best for commuters using the Spring District / Link connections.",
        "tags": ["bike", "commuter", "storage", "sustainability"],
        "cost": "Free",
        "contact": None,
        "lat": 47.61958,
        "lon": -122.18515,
    },
    {
        "name": "Student free printing",
        "category": "Academic support",
        "location": "Copy alcove next to the student kitchen",
        "hours": "Mon–Fri 8:00–18:00 (toner restocked weekdays)",
        "access": "GIX netID login at the release station",
        "description": "Grayscale printing for course readings and posters up to tabloid size. Large format jobs go through the makerspace queue instead.",
        "tags": ["printing", "coursework", "netid"],
        "cost": "Free within fair-use quota; overages routed to department billing",
        "contact": "ithelp@gix.uw.edu",
        "lat": 47.61968,
        "lon": -122.18528,
    },
    {
        "name": "Quiet study room",
        "category": "Study space",
        "location": "Third floor, north wing — rooms 3xx (bookable pods)",
        "hours": "24/7 for students with building access",
        "access": "Reserve 2-hour blocks in the room tablet; no food, drinks with lids only",
        "description": "Small enclosed pods optimized for deep work, interviews, and timed assessments. White noise generators available at the desk.",
        "tags": ["quiet", "focus", "reservation", "interviews"],
        "cost": "Free",
        "contact": None,
        "lat": 47.61978,
        "lon": -122.1855,
    },
    {
        "name": "Collaborative studio",
        "category": "Study space",
        "location": "Second floor open studio overlooking the atrium",
        "hours": "Building access hours; after-hours for project teams on roster",
        "access": "Open seating; large tables first-come for teams of 3+",
        "description": "Writable walls, modular furniture, and portable monitors for design jams and sprint reviews. Nearby huddle rooms can be booked for calls.",
        "tags": ["teamwork", "whiteboards", "design", "sprint"],
        "cost": "Free",
        "contact": "frontdesk@gix.uw.edu",
        "lat": 47.61965,
        "lon": -122.18532,
    },
    {
        "name": "Graduate student lounge",
        "category": "Community",
        "location": "Fourth floor lounge with kitchenette and lockers",
        "hours": "24/7 graduate access",
        "access": "MSTI / related graduate programs; Husky Card tier 2",
        "description": "Microwave, fridge space, coffee fund jar, and bulletin board for rideshares. Respect quiet hours after 22:00.",
        "tags": ["lounge", "kitchen", "community", "msti"],
        "cost": "Free; coffee contributions optional",
        "contact": None,
        "lat": 47.61982,
        "lon": -122.18538,
    },
    {
        "name": "IT help desk",
        "category": "Technology",
        "location": "First floor service desk (shared with front-of-house)",
        "hours": "Mon–Fri 9:00–17:00; emergency pager after hours for classroom A/V",
        "access": "Walk-up or ticket; bring laptop and charger",
        "description": "Wi‑Fi troubleshooting, MFA resets, loaner adapters, and classroom hybrid kit checkouts.",
        "tags": ["wifi", "laptop", "av", "support", "tickets"],
        "cost": "Free for supported devices; replacement parts at UW rates",
        "contact": "ithelp@gix.uw.edu",
        "lat": 47.6196,
        "lon": -122.18522,
    },
    {
        "name": "Career services (GIX)",
        "category": "Career",
        "location": "Hybrid — coach office hours on-site Tuesdays; Zoom the rest of the week",
        "hours": "Coaching Tue 12:00–17:00 on campus; workshops announced on Slack #careers",
        "access": "Book via Handshake; MSTI students prioritized during recruiting season",
        "description": "Resume reviews, mock interviews, employer info sessions, and startup treks coordinated with Seattle and Bellevue partners.",
        "tags": ["jobs", "interviews", "handshake", "recruiting"],
        "cost": "Free for enrolled students",
        "contact": "gixcareers@uw.edu",
        "lat": 47.61963,
        "lon": -122.18518,
    },
]


def _assert_resources_well_formed() -> None:
    for _resource in RESOURCES:
        assert set(_resource.keys()) == RESOURCE_KEYS, (
            f"Resource {_resource.get('name', '?')!r} must have exactly keys {sorted(RESOURCE_KEYS)}"
        )
        _tags = _resource["tags"]
        assert isinstance(_tags, list) and all(isinstance(t, str) for t in _tags)
        _contact = _resource["contact"]
        assert _contact is None or isinstance(_contact, str)
        assert isinstance(_resource["lat"], (int, float))
        assert isinstance(_resource["lon"], (int, float))


_assert_resources_well_formed()

CATEGORY_OPTIONS: list[str] = ["All"] + sorted({str(r["category"]) for r in RESOURCES})


def search_resources(query: str, category: str) -> list[dict[str, object]]:
    """Filter ``RESOURCES`` by category and optional keyword substring."""

    def category_ok(resource: dict[str, object]) -> bool:
        if category == "All":
            return True
        return str(resource["category"]).strip() == category.strip()

    needle = query.strip().lower()
    if not needle:

        def keyword_ok(_resource: dict[str, object]) -> bool:
            return True

    else:

        def keyword_ok(resource: dict[str, object]) -> bool:
            tags_obj = resource["tags"]
            assert isinstance(tags_obj, list)
            tag_strs = " ".join(str(t) for t in tags_obj)
            haystack = " ".join(
                [
                    str(resource["name"]),
                    str(resource["description"]),
                    str(resource["category"]),
                    tag_strs,
                ]
            ).lower()
            return needle in haystack

    return [r for r in RESOURCES if category_ok(r) and keyword_ok(r)]
