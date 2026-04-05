from __future__ import annotations

import io
import re

import pandas as pd
import streamlit as st

from db import (
    fetch_all_orders,
    fetch_all_teacher_classes,
    fetch_archived_quarter_set,
    set_quarter_archived,
    update_orders_admin_fulfillment,
    update_orders_statuses,
)

from procuregix.config import (
    ADMIN_CLASS_ORDER_STATUSES,
    ADMIN_ORDER_FULFILLMENT_OPTIONS,
    LEGACY_QUARTER_LABEL,
    SELECTABLE_QUARTERS,
)
from procuregix.utils.formatting import line_total, parse_created_display, stable_key

from procuregix.ui.admin.instructor_accounts import run_admin_instructor_accounts_form
from procuregix.ui.admin.sidebar import (
    ADMIN_NAV_ALL_ORDERS,
    ADMIN_NAV_ARCHIVE,
    ADMIN_NAV_CLASSES,
    ADMIN_NAV_INSTRUCTOR,
)
from procuregix.ui.styles import (
    inject_admin_quarter_workspace_typography,
    inject_class_expander_heading_styles,
)


def _quarter_tab_key(q: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", q.lower()).strip("_") or "q"


def _classes_for_quarter(teacher_rows: list[dict], quarter_key: str) -> list[dict]:
    if quarter_key == LEGACY_QUARTER_LABEL:
        return [r for r in teacher_rows if not (r.get("quarter") or "").strip()]
    return [r for r in teacher_rows if (r.get("quarter") or "").strip() == quarter_key]


def _admin_status_select_options(status_series: pd.Series) -> tuple[str, ...]:
    """Canonical admin statuses first; append sorted legacy values present in data."""
    base = list(ADMIN_CLASS_ORDER_STATUSES)
    seen = set(base)
    extras: list[str] = []
    for x in status_series.astype(str).str.strip().str.lower().unique():
        if x and x not in seen:
            extras.append(x)
            seen.add(x)
    extras.sort()
    return tuple(base + extras)


def _render_class_orders_section(class_name: str, class_df: pd.DataFrame) -> None:
    if class_df.empty:
        st.info("No order line items for this class yet.")
        return

    class_df = class_df.copy()
    class_df["line_total"] = class_df.apply(line_total, axis=1)
    class_df["created_display"] = class_df["created_at"].map(parse_created_display)

    display_cols = [
        "id",
        "created_display",
        "order_group_id",
        "team_number",
        "cfo_name",
        "provider",
        "item_name",
        "quantity",
        "unit_price",
        "line_total",
        "link_url",
        "notes",
        "status",
        "admin_fulfillment",
    ]
    rename = {
        "created_display": "Submitted (UTC)",
        "order_group_id": "Order group",
        "team_number": "Team #",
        "cfo_name": "CFO",
        "item_name": "Item",
        "unit_price": "Unit price",
        "line_total": "Line total",
        "link_url": "Purchase link",
        "status": "Status",
        "admin_fulfillment": "Admin: ongoing / completed",
    }
    status_options = _admin_status_select_options(class_df["status"])
    allowed_status_save = frozenset(status_options)

    def _split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        ong = df[df["admin_fulfillment"].astype(str).str.lower() != "completed"].copy()
        done = df[df["admin_fulfillment"].astype(str).str.lower() == "completed"].copy()
        return ong, done

    ongoing_df, completed_df = _split(class_df)

    sk = stable_key(class_name, "admcls")

    st.markdown("### Ongoing")
    if ongoing_df.empty:
        st.caption("No line items marked ongoing.")
        editor_on = None
    else:
        base_on = ongoing_df[display_cols].rename(columns=rename)
        editor_on = st.data_editor(
            base_on,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True, format="%d"),
                "Submitted (UTC)": st.column_config.TextColumn(disabled=True),
                "Order group": st.column_config.TextColumn(disabled=True),
                "Team #": st.column_config.NumberColumn(disabled=True, format="%d"),
                "CFO": st.column_config.TextColumn(disabled=True),
                "provider": st.column_config.TextColumn("Provider", disabled=True),
                "Item": st.column_config.TextColumn(disabled=True),
                "quantity": st.column_config.NumberColumn("Qty", disabled=True, format="%.2f"),
                "Unit price": st.column_config.NumberColumn(disabled=True, format="$%.2f"),
                "Line total": st.column_config.NumberColumn(disabled=True, format="$%.2f"),
                "Purchase link": st.column_config.LinkColumn(disabled=True),
                "notes": st.column_config.TextColumn(disabled=True),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=status_options,
                    required=True,
                ),
                "Admin: ongoing / completed": st.column_config.SelectboxColumn(
                    "Admin: ongoing / completed",
                    options=ADMIN_ORDER_FULFILLMENT_OPTIONS,
                    required=True,
                ),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key=f"adm_fulf_on_{sk}",
        )

    st.markdown("### Completed")
    if completed_df.empty:
        st.caption("No line items marked completed yet.")
        editor_co = None
    else:
        base_co = completed_df[display_cols].rename(columns=rename)
        editor_co = st.data_editor(
            base_co,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True, format="%d"),
                "Submitted (UTC)": st.column_config.TextColumn(disabled=True),
                "Order group": st.column_config.TextColumn(disabled=True),
                "Team #": st.column_config.NumberColumn(disabled=True, format="%d"),
                "CFO": st.column_config.TextColumn(disabled=True),
                "provider": st.column_config.TextColumn("Provider", disabled=True),
                "Item": st.column_config.TextColumn(disabled=True),
                "quantity": st.column_config.NumberColumn("Qty", disabled=True, format="%.2f"),
                "Unit price": st.column_config.NumberColumn(disabled=True, format="$%.2f"),
                "Line total": st.column_config.NumberColumn(disabled=True, format="$%.2f"),
                "Purchase link": st.column_config.LinkColumn(disabled=True),
                "notes": st.column_config.TextColumn(disabled=True),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=status_options,
                    required=True,
                ),
                "Admin: ongoing / completed": st.column_config.SelectboxColumn(
                    "Admin: ongoing / completed",
                    options=ADMIN_ORDER_FULFILLMENT_OPTIONS,
                    required=True,
                ),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key=f"adm_fulf_co_{sk}",
        )

    if st.button(
        "Save changes",
        type="primary",
        key=f"adm_fulf_save_{sk}",
    ):
        id_to_old_f = dict(zip(class_df["id"].astype(int), class_df["admin_fulfillment"].astype(str)))
        id_to_old_s = dict(
            zip(class_df["id"].astype(int), class_df["status"].astype(str).str.strip().str.lower())
        )
        f_updates: list[tuple[int, str]] = []
        s_updates: list[tuple[int, str]] = []
        col_f = "Admin: ongoing / completed"
        col_s = "Status"

        def _collect_rows(ed: pd.DataFrame | None) -> None:
            if ed is None or ed.empty:
                return
            for _, row in ed.iterrows():
                oid = int(row["id"])
                new_f = str(row[col_f]).strip().lower()
                if new_f in ADMIN_ORDER_FULFILLMENT_OPTIONS:
                    old_f = str(id_to_old_f.get(oid, "")).strip().lower()
                    if old_f != new_f:
                        f_updates.append((oid, new_f))
                new_s = str(row[col_s]).strip().lower()
                if new_s in allowed_status_save:
                    old_s = str(id_to_old_s.get(oid, "")).strip().lower()
                    if old_s != new_s:
                        s_updates.append((oid, new_s))

        _collect_rows(editor_on)
        _collect_rows(editor_co)
        if not f_updates and not s_updates:
            st.info("No changes to save.")
        else:
            if f_updates:
                update_orders_admin_fulfillment(f_updates)
            if s_updates:
                update_orders_statuses(s_updates)
            parts = []
            if f_updates:
                parts.append(f"{len(f_updates)} ongoing/completed")
            if s_updates:
                parts.append(f"{len(s_updates)} status")
            st.success(f"Saved: {', '.join(parts)}.")
            st.rerun()


def _render_quarter_workspace(
    quarter_label: str,
    *,
    teacher_rows: list[dict],
    orders_df: pd.DataFrame,
    archived_set: set[str],
    show_archive_controls: bool,
    show_restore: bool,
) -> None:
    classes = _classes_for_quarter(teacher_rows, quarter_label)
    qk = _quarter_tab_key(quarter_label)

    with st.container(key=f"pgx_admin_qw_{qk}"):
        if quarter_label == LEGACY_QUARTER_LABEL:
            st.markdown(
                "These classes were created before terms were required. New classes must pick a quarter."
            )
        elif show_restore:
            st.markdown(
                f"Archived quarter **{quarter_label}**. Expand a class to review orders or restore the term."
            )

        if not classes:
            st.info("No classes for this term yet.")
            return

        names = [str(c["class_name"]) for c in classes]
        for i, cn in enumerate(names):
            card_sk = stable_key(cn, "admqcard")
            # Archived quarter view: all class cards start collapsed. Active terms: first card open.
            expand_default = (not show_restore) and (i == 0)
            with st.expander(cn, expanded=expand_default):
                if show_archive_controls and quarter_label in SELECTABLE_QUARTERS:
                    if st.button(
                        "Archive quarter (hide from main tabs)",
                        key=f"adm_archive_do_{qk}_{card_sk}",
                        use_container_width=True,
                    ):
                        set_quarter_archived(quarter_label, archived=True)
                        st.success(f"Archived **{quarter_label}**. Open it anytime from **Archive** in the sidebar.")
                        st.rerun()
                if show_restore and quarter_label in archived_set:
                    if st.button(
                        "Restore quarter to main dashboard",
                        key=f"adm_unarchive_do_{qk}_{card_sk}",
                        use_container_width=True,
                    ):
                        set_quarter_archived(quarter_label, archived=False)
                        st.success(f"Restored **{quarter_label}**.")
                        st.rerun()

                match = [x for x in teacher_rows if x["class_name"] == cn]
                t = match[0] if match else {}
                st.markdown(f"### Instructor: **{t.get('teacher_name', '—')}**")
                st.markdown(f"### Budget: **${float(t.get('budget_usd', 0)):,.2f}**")
                cdf = orders_df[orders_df["class_name"] == cn] if not orders_df.empty else pd.DataFrame()
                _render_class_orders_section(cn, cdf)


def _render_classic_master_table_and_export(orders_df: pd.DataFrame) -> None:
    if orders_df.empty:
        st.info("No orders to export.")
        return
    df = orders_df.copy()
    df["line_total"] = df.apply(line_total, axis=1)
    df["created_display"] = df["created_at"].map(parse_created_display)
    class_names = sorted(df["class_name"].unique())
    status_filter_opts = sorted(
        set(ADMIN_CLASS_ORDER_STATUSES)
        | {str(x).strip().lower() for x in df["status"].unique() if str(x).strip()}
    )
    fc, fs, fp = st.columns(3)
    with fc:
        class_pick = st.multiselect(
            "Class",
            class_names,
            default=[],
            key="adm_mstr_class",
            help="Leave empty to include all classes.",
        )
    with fs:
        status_pick = st.multiselect(
            "Status",
            status_filter_opts,
            default=[],
            key="adm_mstr_stat",
            help="Leave empty to include all statuses.",
        )
    with fp:
        prov_opts = sorted(df["provider"].unique())
        prov_pick = st.multiselect(
            "Provider",
            prov_opts,
            default=[],
            key="adm_mstr_prov",
            help="Leave empty to include all providers.",
        )

    mask = pd.Series(True, index=df.index)
    if class_pick:
        mask &= df["class_name"].isin(class_pick)
    if status_pick:
        mask &= df["status"].isin(status_pick)
    if prov_pick:
        mask &= df["provider"].isin(prov_pick)
    filtered = df.loc[mask].copy()
    if filtered.empty:
        st.warning("No rows match the current filters.")
        return

    show_cols = [
        "id",
        "created_display",
        "class_name",
        "team_number",
        "cfo_name",
        "provider",
        "item_name",
        "quantity",
        "unit_price",
        "line_total",
        "link_url",
        "notes",
        "status",
        "admin_fulfillment",
    ]
    st.dataframe(
        filtered[show_cols].rename(
            columns={
                "created_display": "Submitted (UTC)",
                "admin_fulfillment": "Ongoing/Completed",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    export_df = filtered[
        [
            "id",
            "created_at",
            "class_name",
            "team_number",
            "cfo_name",
            "provider",
            "item_name",
            "quantity",
            "unit_price",
            "line_total",
            "link_url",
            "notes",
            "status",
            "admin_fulfillment",
        ]
    ]
    csv_buf = io.StringIO()
    export_df.to_csv(csv_buf, index=False)
    st.download_button(
        label="Download data as CSV",
        data=csv_buf.getvalue(),
        file_name="procuregix_orders.csv",
        mime="text/csv",
        key="adm_csv_dl",
    )


def _render_admin_archive_page(
    *,
    teacher_rows: list[dict],
    orders_df: pd.DataFrame,
    archived_set: set[str],
) -> None:
    st.subheader("Archive")
    st.markdown(
        "Open an archived quarter to review classes and orders, or restore it to the term tabs on **Classes**."
    )
    arch_list = sorted(archived_set & set(SELECTABLE_QUARTERS))
    if not arch_list:
        st.info(
            "No archived terms yet. Use **Archive quarter** on **Classes** when a past quarter should leave the main tab bar."
        )
        return
    pick = st.selectbox("Quarter", arch_list, key="admin_archived_quarter_pick")
    _render_quarter_workspace(
        pick,
        teacher_rows=teacher_rows,
        orders_df=orders_df,
        archived_set=archived_set,
        show_archive_controls=False,
        show_restore=True,
    )


def _render_admin_classes_page(
    *,
    teacher_rows: list[dict],
    orders_df: pd.DataFrame,
    archived_set: set[str],
) -> None:
    st.subheader("Classes")
    quarters_with_classes: set[str] = set()
    for r in teacher_rows:
        q = (r.get("quarter") or "").strip()
        if q:
            quarters_with_classes.add(q)

    legacy_exists = any(not (r.get("quarter") or "").strip() for r in teacher_rows)
    main_quarters = [
        q
        for q in SELECTABLE_QUARTERS
        if q not in archived_set and q in quarters_with_classes
    ]
    tab_labels = list(main_quarters)
    if legacy_exists:
        tab_labels.append(LEGACY_QUARTER_LABEL)

    if not tab_labels:
        st.info(
            "No terms with classes on the dashboard yet. After instructors create a class and choose a quarter, "
            "that term shows up as a tab here. Use **Archive** in the sidebar for hidden quarters, or **All orders** for export."
        )
        return

    tabs = st.tabs(tab_labels)
    for tab, label in zip(tabs, tab_labels):
        with tab:
            _render_quarter_workspace(
                label,
                teacher_rows=teacher_rows,
                orders_df=orders_df,
                archived_set=archived_set,
                show_archive_controls=True,
                show_restore=False,
            )


def _render_admin_all_orders_page(orders_df: pd.DataFrame) -> None:
    st.subheader("All orders")
    st.caption("Optional filters narrow the table and export; leave all empty to show every line item.")
    _render_classic_master_table_and_export(orders_df)


def run_admin_dashboard() -> None:
    if "admin_view" not in st.session_state:
        st.session_state.admin_view = "orders"

    if st.session_state.get("admin_view") == "student_accounts":
        st.session_state.admin_view = "orders"
    if st.session_state.get("admin_view") == "instructor_accounts":
        st.session_state.admin_menu_choice = ADMIN_NAV_INSTRUCTOR
        st.session_state.admin_view = "orders"

    menu = str(st.session_state.get("admin_menu_choice") or ADMIN_NAV_CLASSES)
    if menu == "notifications":
        st.session_state.admin_menu_choice = ADMIN_NAV_CLASSES
        menu = ADMIN_NAV_CLASSES

    if menu == ADMIN_NAV_INSTRUCTOR:
        run_admin_instructor_accounts_form()
        return

    teacher_rows = fetch_all_teacher_classes()
    rows = fetch_all_orders()
    orders_df = pd.DataFrame(rows) if rows else pd.DataFrame()
    if not orders_df.empty and "admin_fulfillment" not in orders_df.columns:
        orders_df["admin_fulfillment"] = "ongoing"

    archived_set = fetch_archived_quarter_set()

    if menu in (ADMIN_NAV_CLASSES, ADMIN_NAV_ARCHIVE):
        inject_class_expander_heading_styles()
        inject_admin_quarter_workspace_typography()

    if menu == ADMIN_NAV_CLASSES:
        _render_admin_classes_page(
            teacher_rows=teacher_rows,
            orders_df=orders_df,
            archived_set=archived_set,
        )
    elif menu == ADMIN_NAV_ARCHIVE:
        _render_admin_archive_page(
            teacher_rows=teacher_rows,
            orders_df=orders_df,
            archived_set=archived_set,
        )
    elif menu == ADMIN_NAV_ALL_ORDERS:
        _render_admin_all_orders_page(orders_df)
    else:
        st.session_state.admin_menu_choice = ADMIN_NAV_CLASSES
        st.rerun()
