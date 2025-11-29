import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.window.width = 390
    page.window.height = 844
    page.window.resizable = False
    page.title = "Expense Tracker"

    # Sample data for expenses and income
    expenses = []
    income = []

    # Dashboard Content
    def update_dashboard():
        total_spent = sum(expense["amount"] for expense in expenses)
        total_received = sum(inc["amount"] for inc in income)
        balance = total_received - total_spent

        dashboard_content.controls = [
            ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
            # Cards Row
            ft.Row(
                [
                    # Money Received Card (Green Gradient)
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Money Received", size=14, color="white"),
                                ft.Text(f"${total_received:.2f}", size=20, weight=ft.FontWeight.BOLD, color="white"),
                            ],
                            spacing=5,
                        ),
                        width=100,
                        height=90,
                        padding=10,
                        bgcolor=ft.Colors.GREEN_400,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[ft.Colors.GREEN_400, ft.Colors.GREEN_700],
                        ),
                        border_radius=ft.border_radius.all(10),
                    ),
                    # Money Spent Card (Red Gradient)
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Money Spent", size=14, color="white"),
                                ft.Text(f"${total_spent:.2f}", size=20, weight=ft.FontWeight.BOLD, color="white"),
                            ],
                            spacing=5,
                        ),
                        width=100,
                        height=90,
                        padding=10,
                        bgcolor=ft.Colors.RED_400,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[ft.Colors.RED_400, ft.Colors.RED_700],
                        ),
                        border_radius=ft.border_radius.all(10),
                    ),
                    # Remaining Balance Card (Blue Gradient)
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Balance", size=14, color="white"),
                                ft.Text(f"${balance:.2f}", size=20, weight=ft.FontWeight.BOLD, color="white"),
                            ],
                            spacing=5,
                        ),
                        width=100,
                        height=90,
                        padding=10,
                        bgcolor=ft.Colors.BLUE_400,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[ft.Colors.BLUE_400, ft.Colors.BLUE_700],
                        ),
                        border_radius=ft.border_radius.all(10),
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Text("Recent Expenses:", size=18, weight=ft.FontWeight.BOLD),
            ft.Column([ft.Text(f"- {exp['description']}: ${exp['amount']:.2f}") for exp in expenses[-3:]]),
        ]
        page.update()

    dashboard_content = ft.Column(spacing=20)

    # Expenses Content
    expense_amount = ft.TextField(
        label="Amount",
        hint_text="0.00",
        prefix_text="$",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=150,
        border_color=ft.Colors.BLUE_400
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
        border_color=ft.Colors.BLUE_400
    )

    expense_description = ft.TextField(
        label="Description",
        hint_text="What did you spend on?",
        width=200,
        border_color=ft.Colors.BLUE_400
    )

    expense_date = ft.TextField(
        label="Date",
        hint_text="YYYY-MM-DD",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=150,
        border_color=ft.Colors.BLUE_400
    )

    # Add Expense Button
    def add_expense(e):
        if expense_amount.value and expense_category.value:
            try:
                amount = float(expense_amount.value)
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
                update_dashboard()

                # Show success message
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Expense added successfully!"),
                    bgcolor=ft.Colors.GREEN_400
                )
                page.snack_bar.open = True
                page.update()

            except ValueError:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("❌ Please enter a valid amount!"),
                    bgcolor=ft.Colors.RED_400
                )
                page.snack_bar.open = True
                page.update()
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Please fill in amount and category!"),
                bgcolor=ft.Colors.RED_400
            )
            page.snack_bar.open = True
            page.update()

    add_button = ft.ElevatedButton(
        "Add Expense",
        icon=ft.Icons.ADD_CIRCLE,
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.BLUE_400,
        on_click=add_expense,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    # Expenses List Section
    expenses_list = ft.ListView(
        expand=True,
        spacing=10,
        padding=10
    )

    def update_expenses_list():
        expenses_list.controls.clear()

        if not expenses:
            # Show empty state
            expenses_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.MONEY_OFF, size=48, color=ft.Colors.GREY_400),
                        ft.Text("No expenses yet", size=16, color=ft.Colors.GREY_600),
                        ft.Text("Add your first expense above!", size=14, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                    alignment=ft.alignment.center
                )
            )
        else:
            # Show expenses (newest first)
            for i, exp in enumerate(reversed(expenses)):
                # Get emoji for category
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
                category_name = exp["category"].split(" ")[-1]  # Remove emoji for display

                expenses_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row([
                                # Left side: Emoji and main info
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
                                            color=ft.Colors.GREY_600
                                        ),
                                        ft.Text(
                                            exp["date"],
                                            size=10,
                                            color=ft.Colors.GREY_500
                                        ),
                                    ], spacing=2),
                                ], spacing=15),

                                # Right side: Amount and delete button
                                ft.Row([
                                    ft.Text(
                                        f"${exp['amount']:.2f}",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.RED_600
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color=ft.Colors.RED_400,
                                        icon_size=20,
                                        on_click=lambda e, idx=len(expenses)-1-i: delete_expense(idx),
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

    def delete_expense(index):
        expenses.pop(index)
        update_expenses_list()
        update_dashboard()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("🗑️ Expense deleted!"),
            bgcolor=ft.Colors.ORANGE_400
        )
        page.snack_bar.open = True
        page.update()

    # Total Expenses Summary
    total_expenses_text = ft.Text("Total: $0.00", size=18, weight=ft.FontWeight.BOLD)

    def update_total():
        total = sum(exp["amount"] for exp in expenses)
        total_expenses_text.value = f"Total: ${total:.2f}"
        page.update()

    # Main Expenses Page Layout
    expenses_content = ft.Column([
        # Header
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=ft.Colors.BLUE_400),
                ft.Text("Expenses", size=24, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            padding=ft.padding.only(bottom=20)
        ),

        # Input Form Card
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Add New Expense", size=18, weight=ft.FontWeight.BOLD),

                    # First row of inputs
                    ft.ResponsiveRow([
                        ft.Container(expense_amount, col=6),
                        ft.Container(expense_category, col=6),
                    ]),

                    # Second row of inputs
                    ft.ResponsiveRow([
                        ft.Container(expense_description, col=8),
                        ft.Container(expense_date, col=4),
                    ]),

                    # Add button
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

        # Summary and List
        ft.Container(
            content=ft.Column([
                # Total summary
                ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Text("Total Spent:", size=16),
                            total_expenses_text,
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=15,
                    ),
                    color=ft.Colors.BLUE_50,
                    elevation=1,
                ),

                # Expenses list header
                ft.Row([
                    ft.Text("Your Expenses", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"({len(expenses)})", size=16, color=ft.Colors.GREY_600),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # Expenses list
                ft.Container(
                    content=expenses_list,
                    height=400,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    border_radius=10,
                    padding=10,
                )
            ], spacing=15),
            padding=ft.padding.only(top=20)
        )
    ], scroll=ft.ScrollMode.ADAPTIVE)

    # Reports Content
    def update_reports_chart():
        categories = set(exp["category"] for exp in expenses)
        bars = []
        for cat in categories:
            total = sum(exp["amount"] for exp in expenses if exp["category"] == cat)
            bars.append(
                ft.BarChartRod(
                    from_y=0,
                    to_y=total,
                    width=20,
                    color=ft.Colors.BLUE_400,
                    tooltip=f"{cat}: ${total:.2f}",
                    text_above_rod=ft.Text(f"${total:.2f}", size=12),
                )
            )
        reports_content.controls = [
            ft.Text("Reports", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Expenses by Category:", size=18, weight=ft.FontWeight.BOLD),
            ft.BarChart(
                bar_groups=[
                    ft.BarChartGroup(
                        x=100,
                        bar_rods=bars,
                    )
                ],
                border=ft.BorderSide(1, ft.Colors.GREY_400),
                expand=True,
                max_y=max(exp["amount"] for exp in expenses) + 10 if expenses else 100,
            )
        ]
        page.update()

    reports_content = ft.Column()

    # Settings Content
    settings_content = ft.Column([
        ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Configure your expense tracker settings."),
        ft.ElevatedButton("Export Data", on_click=lambda e: print("Exporting data..."))
    ])

    # Navigation Bar
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

    # Main Content Area
    content = ft.Container(
        content=dashboard_content,
        expand=True,
        padding=20,
    )

    # Add NavigationBar and Content to Page
    page.add(
        content,
        nav_bar,
    )

    # Initialize Dashboard
    update_dashboard()

ft.app(target=main)
