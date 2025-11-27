import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.window.width = 390
    page.window.height = 844
    page.window.resizable = False
    page.title = "Expense Tracker"

    # Sample data for expenses
    expenses = []

    # Dashboard Content
    def update_dashboard():
        total = sum(expense["amount"] for expense in expenses)
        recent = expenses[-3:] if expenses else []
        dashboard_content.controls = [
            ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(f"Total Expenses: ${total:.2f}", size=20),
            ft.Text("Recent Expenses:", size=18, weight=ft.FontWeight.BOLD),
            ft.Column([ft.Text(f"- {exp['description']}: ${exp['amount']:.2f}") for exp in recent]),
            ft.ElevatedButton("Add Expense", on_click=lambda e: show_expenses(e))
        ]
        page.update()

    dashboard_content = ft.Column()

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
                ft.IconButton(ft.icons.DELETE, on_click=lambda e, i=i: delete_expense(i))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            for i, exp in enumerate(expenses)
        ]
        page.update()

    def delete_expense(i):
        expenses.pop(i)
        update_dashboard()
        update_expenses_list()

    expenses_content = ft.Column([
        ft.Text("Expenses", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([expense_amount, expense_category]),
        ft.Row([expense_description, expense_date]),
        ft.ElevatedButton("Add", on_click=add_expense),
        ft.Text("Your Expenses:", size=18, weight=ft.FontWeight.BOLD),
        expenses_list
    ])

    # Reports Content
    reports_content = ft.Column([
        ft.Text("Reports", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Expenses by Category:", size=18, weight=ft.FontWeight.BOLD),
        ft.BarChart(
            groups=[ft.BarChartGroup(
                x=cat,
                bars=[ft.BarChartBar(value=sum(exp["amount"] for exp in expenses if exp["category"] == cat), color=ft.colors.BLUE)]
            ) for cat in set(exp["category"] for exp in expenses)],
            border=ft.BorderSide(1, ft.Colors.GREY_400),
            expand=True
        )
    ])

    # Settings Content
    settings_content = ft.Column([
        ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Configure your expense tracker settings."),
        ft.ElevatedButton("Export Data", on_click=lambda e: print("Exporting data..."))
    ])

    def show_dashboard(e):
        page.controls[1] = dashboard_content
        update_dashboard()

    def show_expenses(e):
        page.controls[1] = expenses_content
        update_expenses_list()

    def show_reports(e):
        page.controls[1] = reports_content

    def show_settings(e):
        page.controls[1] = settings_content

    # AppBar
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET),
        leading_width=40,
        title=ft.Text("Expense Tracker"),
        center_title=False,
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
        actions=[
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="Dashboard", on_click=show_dashboard),
                    ft.PopupMenuItem(text="Expenses", on_click=show_expenses),
                    ft.PopupMenuItem(text="Reports", on_click=show_reports),
                    ft.PopupMenuItem(),  # divider
                    ft.PopupMenuItem(text="Settings", on_click=show_settings),
                ]
            ),
        ],
    )

    # Initialize
    page.add(page.appbar, dashboard_content)
    update_dashboard()

ft.app(target=main)
