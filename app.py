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
    expense_amount = ft.TextField(hint_text="Amount", width=150)
    expense_category = ft.Dropdown(
        width=150,
        options=[
            ft.dropdown.Option("Food"),
            ft.dropdown.Option("Transport"),
            ft.dropdown.Option("Entertainment"),
            ft.dropdown.Option("Utilities"),
            ft.dropdown.Option("Other"),
        ],
    )
    expense_description = ft.TextField(hint_text="Description", width=200)
    expense_date = ft.TextField(hint_text="Date (YYYY-MM-DD)", width=150)

    def add_expense(e):
        if expense_amount.value and expense_category.value:
            try:
                amount = float(expense_amount.value)
                expenses.append({
                    "amount": amount,
                    "category": expense_category.value,
                    "description": expense_description.value,
                    "date": expense_date.value or datetime.now().strftime("%Y-%m-%d")
                })
                expense_amount.value = ""
                expense_description.value = ""
                expense_date.value = ""
                update_dashboard()
                update_expenses_list()
                update_reports_chart()
                page.snack_bar = ft.SnackBar(ft.Text("Expense added!"))
                page.snack_bar.open = True
                page.update()
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("Invalid amount!"))
                page.snack_bar.open = True
                page.update()

    expenses_list = ft.Column()

    def update_expenses_list():
        expenses_list.controls = [
            ft.Row([
                ft.Text(f"{exp['category']}: ${exp['amount']:.2f} - {exp['description']} ({exp['date']})"),
                ft.IconButton(ft.Icons.DELETE, on_click=lambda e, i=i: delete_expense(i))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            for i, exp in enumerate(expenses)
        ]
        page.update()

    def delete_expense(i):
        expenses.pop(i)
        update_dashboard()
        update_expenses_list()
        update_reports_chart()

    expenses_content = ft.Column([
        ft.Text("Expenses", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([expense_amount, expense_category]),
        ft.Row([expense_description, expense_date]),
        ft.ElevatedButton("Add", on_click=add_expense),
        ft.Text("Your Expenses:", size=18, weight=ft.FontWeight.BOLD),
        expenses_list
    ])

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
            content.controls = [dashboard_content]
        elif selected_index == 1:
            content.controls = [expenses_content]
            update_expenses_list()
        elif selected_index == 2:
            content.controls = [reports_content]
            update_reports_chart()
        elif selected_index == 3:
            content.controls = [settings_content]
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
