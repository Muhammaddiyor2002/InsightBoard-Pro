"""Tiny route registry mapping a route key to a page-builder callable."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

PageBuilder = Callable[[], ft.Control]


class Router:
    """Resolve route keys to renderable Flet controls."""

    def __init__(self) -> None:
        self._routes: dict[str, PageBuilder] = {}
        self._default: str | None = None

    def register(self, route: str, builder: PageBuilder, *, default: bool = False) -> None:
        self._routes[route] = builder
        if default or self._default is None:
            self._default = route

    def routes(self) -> list[str]:
        return list(self._routes.keys())

    def render(self, route: str) -> ft.Control:
        if route not in self._routes and self._default:
            route = self._default
        if not route:
            return ft.Text("No routes registered")
        return self._routes[route]()
