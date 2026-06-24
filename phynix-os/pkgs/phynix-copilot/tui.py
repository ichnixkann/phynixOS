#!/usr/bin/env python3
"""
PHYNIX Copilot TUI — Textual-based interactive interface
"""

from textual.app import ComposeResult, on
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static, RichLog, Button
from textual.app import App
from textual.binding import Binding
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
import json
from pathlib import Path

from agent import PhynixCopilot


class StatusBar(Static):
    """Display agent status"""

    def __init__(self, copilot: PhynixCopilot):
        super().__init__()
        self.copilot = copilot
        self.update_status()

    def update_status(self):
        status = f"🤖 Backend: {self.copilot.llm_backend} | Ready"
        self.update(status)


class QueryPanel(Container):
    """Query input and processing panel"""

    def __init__(self):
        super().__init__()
        self.query_input = Input(
            id="query_input",
            placeholder="Enter query (e.g., 'search nixpkgs for git')"
        )

    def compose(self) -> ComposeResult:
        yield self.query_input


class OutputPanel(Static):
    """Display query results"""

    def __init__(self):
        super().__init__()
        self.console = Console()

    def display_result(self, result: dict):
        """Format and display result"""
        output = f"Query: {result.get('query', 'N/A')}\n"
        output += f"Backend: {result.get('backend', 'N/A')}\n\n"

        if "response" in result:
            output += f"Response: {json.dumps(result['response'], indent=2)}\n\n"

        if "rag_context" in result:
            output += f"Context:\n{result['rag_context']}"

        self.update(output)


class AuditLog(Static):
    """Display audit log entries"""

    def __init__(self, copilot: PhynixCopilot):
        super().__init__()
        self.copilot = copilot
        self.refresh_log()

    def refresh_log(self):
        """Load and display recent audit entries"""
        try:
            with open(self.copilot.audit_log, "r") as f:
                entries = [json.loads(line) for line in f.readlines()[-10:]]

            table = Table(title="Recent Audit Log")
            table.add_column("Timestamp", style="cyan")
            table.add_column("Action", style="green")
            table.add_column("Status", style="yellow")

            for entry in entries:
                table.add_row(
                    entry.get("timestamp", "")[:19],
                    entry.get("action", ""),
                    entry.get("status", "")
                )

            console = Console()
            with console.capture() as capture:
                console.print(table)
            self.update(capture.getvalue())
        except FileNotFoundError:
            self.update("No audit log found")


class PhynixCopilotTUI(App):
    """PHYNIX Copilot Terminal UI"""

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+l", "clear_output", "Clear", show=True),
        Binding("tab", "next_focus", "Next", show=False),
        Binding("shift+tab", "previous_focus", "Previous", show=False),
    ]

    CSS = """
    Screen {
        layout: vertical;
    }

    Header {
        dock: top;
        height: 3;
    }

    Footer {
        dock: bottom;
    }

    #status_bar {
        dock: top;
        height: 1;
        background: $boost;
        color: $text;
    }

    #query_panel {
        height: 3;
        border: solid $accent;
    }

    #query_input {
        width: 1fr;
        height: 1;
    }

    #output_panel {
        height: 1fr;
        border: solid $primary;
    }

    #audit_log {
        height: 5;
        border: solid $secondary;
    }
    """

    def __init__(self):
        super().__init__()
        self.copilot = PhynixCopilot()

    def compose(self) -> ComposeResult:
        yield Header()
        yield StatusBar(self.copilot, id="status_bar")
        yield QueryPanel(id="query_panel")
        yield OutputPanel(id="output_panel")
        yield AuditLog(self.copilot, id="audit_log")
        yield Footer()

    @on(Input.Submitted)
    def on_query_submitted(self, message: Input.Submitted) -> None:
        """Handle query submission"""
        query = message.value
        if not query:
            return

        # Process query
        result = self.copilot.process_query(query)

        # Display result
        output_panel = self.query_by_id("output_panel", OutputPanel)
        output_panel.display_result(result)

        # Refresh audit log
        audit_log = self.query_by_id("audit_log", AuditLog)
        audit_log.refresh_log()

        # Clear input
        message.input.value = ""

    def action_clear_output(self) -> None:
        """Clear output panel"""
        output_panel = self.query_by_id("output_panel", OutputPanel)
        output_panel.update("")


if __name__ == "__main__":
    app = PhynixCopilotTUI()
    app.run()
