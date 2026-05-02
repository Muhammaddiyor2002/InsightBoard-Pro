"""Helpers shared across pages."""

from __future__ import annotations

import flet as ft

from app.ui.theme import AppTheme


def page_header(theme: AppTheme, title: str, subtitle: str = "") -> ft.Control:
    children: list[ft.Control] = [
        ft.Text(
            title,
            color=theme.text,
            weight=ft.FontWeight.BOLD,
            size=24,
        )
    ]
    if subtitle:
        children.append(ft.Text(subtitle, color=theme.muted, size=13))
    return ft.Column(controls=children, spacing=2)


def empty_state(theme: AppTheme, title: str, subtitle: str = "") -> ft.Control:
    return ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.UPLOAD_FILE, color=theme.muted, size=48),
                ft.Text(title, color=theme.text, weight=ft.FontWeight.W_600, size=18),
                ft.Text(subtitle, color=theme.muted, text_align=ft.TextAlign.CENTER),
            ],
            spacing=10,
        ),
    )
