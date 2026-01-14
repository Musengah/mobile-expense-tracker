# First, let's make sure our app is ready for mobile
# Add this to the beginning of your app.py:

import flet as ft
from datetime import datetime, date
import json
import os
import sys

# Check if running on mobile
def is_mobile():
    return hasattr(ft.Page, "platform") and ft.Page.platform in ["android", "ios"]

def main(page: ft.Page):
    # Adjust window size for mobile
    if not is_mobile():
        page.window.width = 390
        page.window.height = 844
        page.window.resizable = False
    
    page.title = "Expense Tracker"
    
    # ... rest of your existing code ...

def main(page: ft.Page):
    # Adjust window size for mobile
    if not is_mobile():
        page.window.width = 390
        page.window.height = 844
        page.window.resizable = False
    
    page.title = "Expense Tracker"

    # Data files
    data_file = "expenses_data.json"
    prefs_file = "user_prefs.json"
    
    # Load data
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
            expenses = data.get("expenses", [])
            income_sources = data.get("income_sources", [])
            one_time_income = data.get("one_time_income", [])
    else:
        expenses = []
        income_sources = []
        one_time_income = []
    
    # Load user preferences
    if os.path.exists(prefs_file):
        with open(prefs_file, 'r') as f:
            prefs = json.load(f)
    else:
        prefs = {
            "income_hint_dismissed_until": None,
            "income_hint_never_show": False,
            "income_configured": len(income_sources) > 0 or len(one_time_income) > 0,
            "hint_shown_count": 0,
            "first_use_date": date.today().isoformat(),
            "expense_count_since_hint": 0
        }
    
    def save_data():
        with open(data_file, 'w') as f:
            json.dump({
                "expenses": expenses,
                "income_sources": income_sources,
                "one_time_income": one_time_income
            }, f, indent=2)
    
    def save_prefs():
        with open(prefs_file, 'w') as f:
            json.dump(prefs, f, indent=2)
    
    # Calculate totals
    def calculate_totals():
        total_expenses = sum(exp["amount"] for exp in expenses)
        monthly_income = sum(src["amount"] for src in income_sources)
        total_one_time = sum(inc["amount"] for inc in one_time_income)
        total_regular_income = monthly_income * 1
        total_income = total_regular_income + total_one_time
        prefs["income_configured"] = len(income_sources) > 0 or len(one_time_income) > 0
        return total_expenses, total_income, monthly_income
    
    # Dashboard Content
    def update_dashboard():
        total_spent, total_received, monthly_income = calculate_totals()
        balance = total_received - total_spent
        
        # Check if we should show income hint
        show_hint = should_show_income_hint()
        
        dashboard_controls = [
            ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
        ]
        
        # Add hint if needed
        if show_hint:
            dashboard_controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, color=ft.Colors.AMBER),
                                ft.Text("Complete Your Financial Picture", 
                                       weight=ft.FontWeight.BOLD, size=16),
                            ]),
                            ft.Text("Set up your income to see accurate balance and track savings.", 
                                   size=14, color=ft.Colors.GREY_700),
                            ft.Row([
                                ft.OutlinedButton(
                                    "Set Up Income",
                                    icon=ft.Icons.ARROW_FORWARD,
                                    on_click=lambda e: setup_income_click(e)
                                ),
                                ft.TextButton(
                                    "Maybe Later",
                                    on_click=lambda e: dismiss_hint(e, days=7)
                                ),
                            ], spacing=10)
                        ], spacing=10),
                        padding=15,
                    ),
                    color=ft.Colors.AMBER_50,
                    elevation=1,
                )
            )
        
        # Add the main cards
        dashboard_controls.extend([
            ft.Row(
                [
                    # Money Received Card
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
                    
                    # Money Spent Card
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
                    
                    # Balance Card
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
                        bgcolor=ft.Colors.BLUE_400 if balance >= 0 else ft.Colors.ORANGE_400,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[
                                ft.Colors.BLUE_400 if balance >= 0 else ft.Colors.ORANGE_400,
                                ft.Colors.BLUE_700 if balance >= 0 else ft.Colors.ORANGE_700
                            ],
                        ),
                        border_radius=ft.border_radius.all(10),
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            
            ft.Text("Recent Expenses:", size=18, weight=ft.FontWeight.BOLD),
            ft.Column(
                [ft.Text(f"• {exp.get('description', 'Expense')}: ${exp['amount']:.2f}") for exp in expenses[-3:]],
                spacing=5
            ) if expenses else ft.Text("No expenses yet", color=ft.Colors.GREY_600),
        ])
        
        dashboard_content.controls = dashboard_controls
        page.update()
    
    dashboard_content = ft.Column(spacing=20)
    
    # Hint Logic
    def should_show_income_hint():
        if prefs["income_configured"]:
            return False
        if prefs["income_hint_never_show"]:
            return False
        
        # Check if dismissed temporarily
        if prefs["income_hint_dismissed_until"]:
            try:
                dismissed_until = datetime.fromisoformat(prefs["income_hint_dismissed_until"])
                if datetime.now() < dismissed_until:
                    return False
            except:
                pass
        
        # Show hint if user has at least 3 expenses
        if len(expenses) >= 3:
            return True
        
        return False
    
    def setup_income_click(e):
        # Navigate to settings page
        nav_bar.selected_index = 3
        on_nav_change(type('Event', (), {'control': type('Obj', (), {'selected_index': 3})()}))
        page.update()
    
    def dismiss_hint(e, days=None):
        if days:
            # Dismiss for specific days
            dismiss_date = datetime.now().replace(hour=23, minute=59, second=59)
            dismiss_date = dismiss_date.replace(day=dismiss_date.day + days)
            prefs["income_hint_dismissed_until"] = dismiss_date.isoformat()
        else:
            # Never show again
            prefs["income_hint_never_show"] = True
        
        prefs["hint_shown_count"] = prefs.get("hint_shown_count", 0) + 1
        save_prefs()
        update_dashboard()
    
    # Expenses Page
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
        value=date.today().isoformat(),
        width=150,
        border_color=ft.Colors.BLUE_400
    )
    
    def add_expense(e):
        if expense_amount.value and expense_category.value:
            try:
                amount = float(expense_amount.value)
                new_expense = {
                    "amount": amount,
                    "category": expense_category.value,
                    "description": expense_description.value or "No description",
                    "date": expense_date.value or date.today().isoformat()
                }
                expenses.append(new_expense)
                
                # Save data
                save_data()

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
        save_data()
        update_expenses_list()
        update_dashboard()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("🗑️ Expense deleted!"),
            bgcolor=ft.Colors.ORANGE_400
        )
        page.snack_bar.open = True
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
    
    # Reports Page - ENHANCED WITH VISUAL CHARTS
    def update_reports():
        reports_controls = [
            ft.Text("Reports", size=24, weight=ft.FontWeight.BOLD),
        ]
        
        if not expenses:
            # Empty state for reports
            reports_controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.BAR_CHART, size=64, color=ft.Colors.GREY_400),
                        ft.Text("No expense data yet", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Add some expenses to see reports and charts", 
                               color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                    padding=40,
                    alignment=ft.alignment.center
                )
            )
        else:
            # Calculate statistics
            total_spent = sum(exp["amount"] for exp in expenses)
            avg_expense = total_spent / len(expenses) if expenses else 0
            
            # Group by category
            categories = {}
            for exp in expenses:
                cat = exp["category"]
                categories[cat] = categories.get(cat, 0) + exp["amount"]
            
            # Find top categories
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            top_category = sorted_categories[0] if sorted_categories else ("None", 0)
            
            # Monthly spending (simple grouping by month)
            monthly_spending = {}
            for exp in expenses:
                if "date" in exp:
                    try:
                        month = exp["date"][:7]  # YYYY-MM
                        monthly_spending[month] = monthly_spending.get(month, 0) + exp["amount"]
                    except:
                        pass
            
            # Statistics Cards
            reports_controls.extend([
                ft.Text("Statistics", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Total", size=12, color=ft.Colors.GREY_600),
                            ft.Text(f"${total_spent:.2f}", size=18, weight=ft.FontWeight.BOLD),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Average", size=12, color=ft.Colors.GREY_600),
                            ft.Text(f"${avg_expense:.2f}", size=18, weight=ft.FontWeight.BOLD),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=15,
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Count", size=12, color=ft.Colors.GREY_600),
                            ft.Text(str(len(expenses)), size=18, weight=ft.FontWeight.BOLD),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=15,
                        bgcolor=ft.Colors.ORANGE_50,
                        border_radius=10,
                        expand=True,
                    ),
                ], spacing=10),
                
                # Category Breakdown
                ft.Text("Spending by Category", size=20, weight=ft.FontWeight.BOLD),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            # Top category highlight
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text("🏆 Top Category", weight=ft.FontWeight.BOLD),
                                        ft.Text(f"${top_category[1]:.2f}", 
                                               weight=ft.FontWeight.BOLD, color=ft.Colors.RED_600),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    ft.Text(top_category[0].replace("🍔 ", "").replace("🚗 ", "").replace("🎬 ", "").replace("🏠 ", "").replace("🛒 ", "").replace("🏥 ", "").replace("✈️ ", "").replace("📚 ", "").replace("💼 ", "").replace("❓ ", ""), 
                                           color=ft.Colors.GREY_600),
                                ]),
                                padding=15,
                                bgcolor=ft.Colors.AMBER_50,
                                border_radius=10,
                            ),
                            
                            # Category list with percentages
                            ft.Column([
                                ft.Row([
                                    ft.Text("Category", weight=ft.FontWeight.BOLD, expand=2),
                                    ft.Text("Amount", weight=ft.FontWeight.BOLD, expand=1),
                                    ft.Text("%", weight=ft.FontWeight.BOLD, expand=1),
                                ]),
                                ft.Divider(),
                            ] + [
                                ft.Row([
                                    ft.Text(cat.replace("🍔 ", "").replace("🚗 ", "").replace("🎬 ", "").replace("🏠 ", "").replace("🛒 ", "").replace("🏥 ", "").replace("✈️ ", "").replace("📚 ", "").replace("💼 ", "").replace("❓ ", ""), 
                                           expand=2),
                                    ft.Text(f"${amount:.2f}", expand=1),
                                    ft.Text(f"{(amount/total_spent*100):.1f}%", expand=1),
                                ])
                                for cat, amount in sorted_categories[:5]  # Top 5 categories
                            ], spacing=8),
                        ], spacing=15),
                        padding=20,
                    ),
                    elevation=2,
                ),
                
                # Simple Bar Chart (using containers as bars)
                ft.Text("Category Spending Chart", size=20, weight=ft.FontWeight.BOLD),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Column([
                                ft.Row([
                                    ft.Text(cat.replace("🍔 ", "").replace("🚗 ", "").replace("🎬 ", "").replace("🏠 ", "").replace("🛒 ", "").replace("🏥 ", "").replace("✈️ ", "").replace("📚 ", "").replace("💼 ", "").replace("❓ ", "")[:12], 
                                           width=80, size=12),
                                    ft.Container(
                                        content=ft.Container(
                                            bgcolor=ft.Colors.BLUE_400,
                                            border_radius=5,
                                        ),
                                        width=min(amount/total_spent * 200, 200),
                                        height=20,
                                        bgcolor=ft.Colors.BLUE_100,
                                        border_radius=5,
                                    ),
                                    ft.Text(f"${amount:.2f}", size=12, width=60),
                                ], spacing=10)
                                for cat, amount in sorted_categories[:6]  # Top 6 categories
                            ], spacing=10),
                        ]),
                        padding=20,
                    ),
                ),
                
                # Monthly Spending
                ft.Text("Monthly Spending", size=20, weight=ft.FontWeight.BOLD),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Column([
                                ft.Row([
                                    ft.Text(month, width=80),
                                    ft.Text(f"${amount:.2f}", weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=ft.Container(
                                            bgcolor=ft.Colors.GREEN_400,
                                            border_radius=5,
                                        ),
                                        width=min(amount/max(monthly_spending.values(), default=1) * 150, 150),
                                        height=15,
                                        bgcolor=ft.Colors.GREEN_100,
                                        border_radius=5,
                                    ),
                                ], spacing=10)
                                for month, amount in sorted(monthly_spending.items(), reverse=True)[:6]
                            ], spacing=8),
                        ]),
                        padding=20,
                    ),
                ),
            ])
        
        reports_content.controls = reports_controls
        page.update()
    
    reports_content = ft.Column(spacing=20, scroll=ft.ScrollMode.ADAPTIVE)
    
    # Settings Page with Income Configuration
    monthly_salary = ft.TextField(
        label="Monthly Salary",
        hint_text="0.00",
        prefix_text="$",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200
    )
    
    other_income = ft.TextField(
        label="Other Monthly Income",
        hint_text="0.00",
        prefix_text="$",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200
    )
    
    def save_income_settings(e):
        # Save regular income sources
        income_sources.clear()
        
        if monthly_salary.value:
            income_sources.append({
                "name": "Salary",
                "amount": float(monthly_salary.value),
                "type": "monthly"
            })
        
        if other_income.value:
            income_sources.append({
                "name": "Other Income",
                "amount": float(other_income.value),
                "type": "monthly"
            })
        
        save_data()
        
        # Update preference
        prefs["income_configured"] = True
        save_prefs()
        
        # Show success message
        page.snack_bar = ft.SnackBar(
            content=ft.Text("✅ Income settings saved!"),
            bgcolor=ft.Colors.GREEN_400
        )
        page.snack_bar.open = True
        
        # Update dashboard to remove hint
        update_dashboard()
        page.update()
    
    # Income status display
    income_status = ft.Text("No income configured", color=ft.Colors.GREY_600)
    
    def update_income_status():
        total_spent, total_received, monthly = calculate_totals()
        
        if prefs["income_configured"]:
            income_status.value = f"Configured: ${monthly:.2f}/month"
            income_status.color = ft.Colors.GREEN_600
        else:
            income_status.value = "No income configured"
            income_status.color = ft.Colors.GREY_600
    
    # Income expansion tile
    income_expansion = ft.ExpansionTile(
        title=ft.Text("Income Configuration"),
        subtitle=income_status,
        controls=[
            ft.Column([
                ft.Text("Regular Monthly Income", weight=ft.FontWeight.BOLD),
                monthly_salary,
                other_income,
                
                ft.Container(height=20),
                
                ft.ElevatedButton(
                    "Save Income Settings",
                    icon=ft.Icons.SAVE,
                    on_click=save_income_settings,
                    width=250
                )
            ], spacing=15)
        ]
    )
    
    settings_content = ft.Column([
        ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
        
        # Income Configuration Section
        ft.Card(
            content=ft.Container(
                content=income_expansion,
                padding=15,
            ),
            elevation=2,
        ),
        
        ft.Container(height=20),
        
        # App Info
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("App Information", weight=ft.FontWeight.BOLD),
                    ft.Text("Expense Tracker v1.0", color=ft.Colors.GREY_600),
                    ft.Text("Offline-first application", color=ft.Colors.GREY_600),
                    ft.Text(f"Total Expenses: {len(expenses)}", color=ft.Colors.GREY_600),
                    ft.Text(f"Categories Used: {len(set(exp['category'] for exp in expenses))}", 
                           color=ft.Colors.GREY_600),
                ], spacing=10),
                padding=15,
            )
        ),
    ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE)
    
    # Navigation
    def on_nav_change(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            content.content = dashboard_content
            update_dashboard()
        elif selected_index == 1:
            content.content = expenses_content
            update_expenses_list()
        elif selected_index == 2:
            content.content = reports_content
            update_reports()
        elif selected_index == 3:
            content.content = settings_content
            update_income_status()
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
    
    # Main content area
    content = ft.Container(
        content=dashboard_content,
        expand=True,
        padding=20,
    )
    
    # Add everything to page
    page.add(
        content,
        nav_bar,
    )
    
    # Initialize
    update_dashboard()
    update_income_status()

ft.app(target=main)
