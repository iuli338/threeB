import flet as ft

# --- Page Content Functions ---

def home_view(page: ft.Page):
    """The content for the Home page (route '/')."""
    return ft.View(
        "/",
        [
            ft.Container(
                content=ft.Text("🏠 Welcome to the Home Page!", size=30, weight=ft.FontWeight.BOLD),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )

def settings_view(page: ft.Page):
    """The content for the Settings page (route '/settings')."""
    return ft.View(
        "/settings",
        [
            ft.Container(
                content=ft.Text("⚙️ Adjust your Settings here.", size=30, weight=ft.FontWeight.BOLD),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )

def quiz_view(page: ft.Page):
    """The content for the Quiz page (route '/quiz')."""
    return ft.View(
        "/quiz",
        [
            ft.Container(
                content=ft.Text("📝 Get ready for the Quiz!", size=30, weight=ft.FontWeight.BOLD),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )

# --- Main App Function ---

def main(page: ft.Page):
    # --- Basic App Setup ---
    page.title = "Three Panel Interface with Page Switching"
    page.window_width = 480
    page.window_height = 320
    page.window_resizable = True
    page.theme_mode = ft.ThemeMode.DARK

    # --- Navigation Bar ---
    
    # Corrected button style:
    # 1. Used string keys ("default", "hovered", "pressed") for states (from previous fix).
    # 2. Used hex code ("#FFFFFF") for white text to bypass the 'ft.colors' error.
    button_style = ft.ButtonStyle(
        color={
            "default": "#FFFFFF", # Hex code for white text
        },
        bgcolor={
            "default": "#555555",
            "hovered": "#6a6a6a",
            "pressed": "#404040", 
        },
        shape=ft.ContinuousRectangleBorder(radius=10),
        padding=ft.padding.all(10)
    )

    # Function to handle button clicks and change the route (page)
    def navigate(route):
        page.go(route)
        page.update()

    button_data = [
        ("Home", "/"),
        ("Settings", "/settings"),
        ("Quiz", "/quiz"),
    ]

    nav_row = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        controls=[
            ft.Container(
                content=ft.ElevatedButton(
                    text=text,
                    on_click=lambda e, r=route: navigate(r),
                    style=button_style,
                    height=50,
                ),
                padding=ft.padding.only(left=5, right=5),
                expand=True
            )
            for text, route in button_data
        ]
    )

    # --- Routing Logic ---
    
    def route_change(route):
        page.views.clear()
        
        # Navigation Row container
        nav_container = ft.Container(
            content=nav_row, 
            padding=ft.padding.only(left=5, right=5, top=20, bottom=20),
            height=90 
        )

        # Map the routes to the view functions
        if page.route == "/":
            view = home_view(page)
        elif page.route == "/settings":
            view = settings_view(page)
        elif page.route == "/quiz":
            view = quiz_view(page)
        else:
            view = home_view(page)
        
        # Add the Navigation Row at the top of the controls list
        view.controls.insert(0, nav_container) 
        
        page.views.append(view)
        page.update()

    page.on_route_change = route_change
    
    # Start on the Home page
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)