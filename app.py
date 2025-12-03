import flet as ft
from datetime import datetime

def main(page: ft.Page):
    # Optional: window sizing (ignored on web)
    try:
        page.window.width = 390
        page.window.height = 844
        page.window.resizable = False
    except Exception:
        # Some runtimes (e.g., web) ignore window properties; ignore errors
        pass

    page.title = "Expense Tracker"

    # ------- Compatibility for Colors across Flet versions -------
    if hasattr(ft, "Colors"):
        Colors = ft.Colors
    elif hasattr(ft, "colors"):
        Colors = ft.colors
    else:
        Colors = ft  # fallback (may require hex usage)
    # ------------------------------------------------------------

    # Data
    expenses: list[dict] = []
    income: list[dict] = []

    # --- UI placeholders ---
    dashboard_content = ft.Column(spacing=20)
    reports_content = ft.Column()
    expenses_list = ft.ListView(expand=True, spacing=10, padding=10)

    # --- Dashboard updater ---
    def update_dashboard():
        total_spent = sum(exp["amount"] for exp in expenses)
        total_received = sum(inc["amount"] for inc in income)
        balance = total_received - total_spent

        # Recent 3 expenses
        recent = expenses[-3:] if expenses else []

        dashboard_content.controls = [
            ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),

            # Cards row
            ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Money Received", size=14, color="white"),
                                ft.Text(f"${total_received:.2f}", size=20, weight=ft.FontWeight.BOLD, color="white"),
                            ],
                            spacing=5,
                        ),
                        width=120,
                        height=90,
                        padding=10,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[Colors.GREEN_400, Colors.GREEN_700],
                        ),
                        border_radius=ft.border_radius.all(10),
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Money Spent", size=14, color="white"),
                                ft.Text(f"${total_spent:.2f}", size=20, weight=ft.FontWeight.BOLD, color="white"),
                            ],
                            spacing=5,
                        ),
                        width=120,
                        height=90,
                        padding=10,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[Colors.RED_400, Colors.RED_700],
                        ),
                        border_radius=ft.border_radius.all(10),
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Balance", size=14, color="white"),
                                ft.Text(f"${balance:.2f}", size=20, weight=ft.FontWeight.BOLD, color="white"),
                            ],
                            spacing=5,
                        ),
                        width=120,
                        height=90,
                        padding=10,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[Colors.BLUE_400, Colors.BLUE_700],
                        ),
                        border_radius=ft.border_radius.all(10),
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),

            ft.Text("Recent Expenses:", size=18, weight=ft.FontWeight.BOLD),
            ft.Column([ft.Text(f"- {exp['description']}: ${exp['amount']:.2f}") for exp in recent]),
        ]
        page.update()

    # --- Expense input fields ---
    expense_amount = ft.TextField(
        label="Amount",
        hint_text="0.00",
        prefix_text="$",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=150,
        border_color=Colors.BLUE_400
    )

    expense_category = ft.Dropdown(
        label="Category",
        width=150,
        options=[
            ft.dropdown.Option("🍔 Food"),
            ft.dropdown.Option("🚗 Transport"),
            ft.dropdown.Option("🎬 Entertainment"),
            ft.dropdown.Option("🏠 Utilities"),
            ft.dropdown.Option("🛒 Shopping"),
            ft.dropdown.Option("🏥 Healthcare"),
            ft.dropdown.Option("✈️ Travel"),
            ft.dropdown.Option("📚 Education"),
            ft.dropdown.Option("💼 Business"),
            ft.dropdown.Option("❓ Other"),
        ],
        border_color=Colors.BLUE_400
    )

    expense_description = ft.TextField(
        label="Description",
        hint_text="What did you spend on?",
        width=200,
        border_color=Colors.BLUE_400
    )

    expense_date = ft.TextField(
        label="Date",
        hint_text="YYYY-MM-DD",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=150,
        border_color=Colors.BLUE_400
    )

    # --- Add / delete logic ---
    def update_total():
        total = sum(exp["amount"] for exp in expenses)
        total_expenses_text.value = f"Total: ${total:.2f}"
        page.update()

    total_expenses_text = ft.Text("Total: $0.00", size=18, weight=ft.FontWeight.BOLD)

    def update_expenses_list():
        expenses_list.controls.clear()

        if not expenses:
            expenses_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.MONEY_OFF, size=48, color=Colors.GREY_400),
                        ft.Text("No expenses yet", size=16, color=Colors.GREY_600),
                        ft.Text("Add your first expense above!", size=14, color=Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                    alignment=ft.alignment.center
                )
            )
        else:
            # reversed so newest first in UI
            for i, exp in enumerate(reversed(expenses)):
                # idx in original list
                idx_in_original = len(expenses) - 1 - i

                # emoji map (keyed by full category text)
                emoji_map = {
                    "🍔 Food": "🍔",
                    "🚗 Transport": "🚗",
                    "🎬 Entertainment": "🎬",
                    "🏠 Utilities": "🏠",
                    "🛒 Shopping": "🛒",
                    "🏥 Healthcare": "🏥",
                    "✈️ Travel": "✈️",
                    "📚 Education": "📚",
                    "💼 Business": "💼",
                    "❓ Other": "❓"
                }
                emoji = emoji_map.get(exp["category"], "💰")

                # Get readable category name (drop leading emoji + space if present)
                parts = exp["category"].split(" ")
                if len(parts) > 1:
                    category_name = " ".join(parts[1:])
                else:
                    category_name = exp["category"]

                # create delete handler bound to the current index
                def make_delete_handler(index):
                    return lambda e: delete_expense(index)

                expenses_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row([
                                ft.Row([
                                    ft.Text(emoji, size=20),
                                    ft.Column([
                                        ft.Text(
                                            f"{category_name}",
                                            weight=ft.FontWeight.BOLD,
                                            size=14
                                        ),
                                        ft.Text(
                                            exp["description"],
                                            size=12,
                                            color=Colors.GREY_600
                                        ),
                                        ft.Text(
                                            exp["date"],
                                            size=10,
                                            color=Colors.GREY_500
                                        ),
                                    ], spacing=2),
                                ], spacing=15),

                                ft.Row([
                                    ft.Text(
                                        f"${exp['amount']:.2f}",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=Colors.RED_600
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color=Colors.RED_400,
                                        icon_size=20,
                                        on_click=make_delete_handler(idx_in_original),
                                        tooltip="Delete expense"
                                    ),
                                ], spacing=5),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=15,
                            border_radius=10,
                        ),
                        elevation=2,
                    )
                )

        page.update()

    def delete_expense(index: int):
        if 0 <= index < len(expenses):
            expenses.pop(index)
            update_expenses_list()
            update_total()
            update_dashboard()
            # feedback
            page.snack_bar = ft.SnackBar(
                content=ft.Text("🗑️ Expense deleted!"),
                bgcolor=Colors.ORANGE_400
            )
            page.snack_bar.open = True
            page.update()

    def add_expense(e):
        if not expense_amount.value or not expense_category.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Please fill in amount and category!"),
                bgcolor=Colors.RED_400
            )
            page.snack_bar.open = True
            page.update()
            return

        try:
            amount = float(expense_amount.value)
        except Exception:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Please enter a valid amount!"),
                bgcolor=Colors.RED_400
            )
            page.snack_bar.open = True
            page.update()
            return

        new_expense = {
            "amount": amount,
            "category": expense_category.value,
            "description": expense_description.value or "No description",
            "date": expense_date.value or datetime.now().strftime("%Y-%m-%d")
        }
        expenses.append(new_expense)

        # Clear form
        expense_amount.value = ""
        expense_description.value = ""
        expense_category.value = None

        # Update UI
        update_expenses_list()
        update_total()
        update_dashboard()

        # feedback
        page.snack_bar = ft.SnackBar(
            content=ft.Text("✅ Expense added successfully!"),
            bgcolor=Colors.GREEN_400
        )
        page.snack_bar.open = True
        page.update()

    add_button = ft.ElevatedButton(
        "Add Expense",
        icon=ft.Icons.ADD_CIRCLE,
        color="white",
        bgcolor=Colors.BLUE_400,
        on_click=add_expense,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )

    # --- Expenses Page layout ---
    expenses_content = ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=Colors.BLUE_400),
                ft.Text("Expenses", size=24, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            padding=ft.padding.only(bottom=20)
        ),

        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Add New Expense", size=18, weight=ft.FontWeight.BOLD),

                    ft.ResponsiveRow([
                        ft.Container(expense_amount, col=6),
                        ft.Container(expense_category, col=6),
                    ]),

                    ft.ResponsiveRow([
                        ft.Container(expense_description, col=8),
                        ft.Container(expense_date, col=4),
                    ]),

                    ft.Container(
                        add_button,
                        alignment=ft.alignment.center_right,
                        padding=ft.padding.only(top=10)
                    )
                ], spacing=15),
                padding=20,
            ),
            elevation=3,
        ),

        ft.Container(
            content=ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Text("Total Spent:", size=16),
                            total_expenses_text,
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=15,
                    ),
                    color=Colors.BLUE_50,
                    elevation=1,
                ),

                ft.Row([
                    ft.Text("Your Expenses", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"({len(expenses)})", size=16, color=Colors.GREY_600),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Container(
                    content=expenses_list,
                    height=400,
                    border=ft.border.all(1, Colors.GREY_200),
                    border_radius=10,
                    padding=10,
                )
            ], spacing=15),
            padding=ft.padding.only(top=20)
        )
    ], scroll=ft.ScrollMode.ADAPTIVE)

    # --- Reports Page ---
    def update_reports_chart():
        # Safe early-exit if no expenses
        if not expenses:
            reports_content.controls = [
                ft.Text("Reports", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("No data available yet.", size=16, color=Colors.GREY_600),
            ]
            page.update()
            return

        # Aggregate totals per category (preserve order)
        categories_totals: dict[str, float] = {}
        for exp in expenses:
            categories_totals.setdefault(exp["category"], 0.0)
            categories_totals[exp["category"]] += exp["amount"]

        # Build bar groups: one group per category (x increments)
        bar_groups = []
        x_value = 0
        for cat, total in categories_totals.items():
            bar_groups.append(
                ft.BarChartGroup(
                    x=x_value,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=total,
                            width=20,
                            color=Colors.BLUE_400,
                            tooltip=f"{cat}: ${total:.2f}",
                            text_above_rod=ft.Text(f"${total:.2f}", size=12),
                        )
                    ],
                )
            )
            x_value += 1

        max_y_value = max(categories_totals.values()) + 10 if categories_totals else 100

        reports_content.controls = [
            ft.Text("Reports", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Expenses by Category:", size=18, weight=ft.FontWeight.BOLD),
            ft.BarChart(
                bar_groups=bar_groups,
                border=ft.BorderSide(1, Colors.GREY_400),
                expand=True,
                max_y=max_y_value,
            )
        ]
        page.update()

    # Settings content
    settings_content = ft.Column([
        ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Configure your expense tracker settings."),
        ft.ElevatedButton("Export Data", on_click=lambda e: print("Exporting data..."))
    ])

    # Navigation handling
    content = ft.Container(content=dashboard_content, expand=True, padding=20)

    def on_nav_change(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            content.content = dashboard_content
        elif selected_index == 1:
            content.content = expenses_content
            update_expenses_list()
        elif selected_index == 2:
            content.content = reports_content
            update_reports_chart()
        elif selected_index == 3:
            content.content = settings_content
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationBarDestination(icon=ft.Icons.MONEY, label="Expenses"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="Reports"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
        ],
        on_change=on_nav_change,
    )

    # Compose page
    page.add(content, nav_bar)

    # Initialize
    update_expenses_list()
    update_total()
    update_dashboard()

ft.app(target=main)
