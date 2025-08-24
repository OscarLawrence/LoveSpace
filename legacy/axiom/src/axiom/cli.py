#!/usr/bin/env python3
"""
Axiom CLI - Interactive chat with Claude Sonnet 4 using formal contracts.
Pure, coherent interface with no system message pollution.
"""

import asyncio
import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from .anthropic_client import (
    AnthropicClient,
    AnthropicMessage,
    create_anthropic_client,
    load_system_message,
)
from .contracts import ChatSessionContract, ContractViolation, contract_enforced

console = Console()


class ChatSession:
    """
    Interactive chat session with Claude Sonnet 4.

    Maintains conversation history and enforces formal contracts
    for all interactions.
    """

    def __init__(self, client: AnthropicClient) -> None:
        """Initialize chat session with Anthropic client."""
        self.client = client
        self.messages: list[AnthropicMessage] = []
        self.session_active = True

        # Load system message
        try:
            self.system_message = load_system_message()
            console.print("[dim]✓ System message loaded[/dim]")
        except ContractViolation as e:
            console.print(f"[yellow]Warning: {e}[/yellow]")
            self.system_message = None

    @contract_enforced(ChatSessionContract())
    async def run_interactive_session(self) -> None:
        """
        Run the main interactive chat loop with formal contract enforcement.

        Raises:
            ContractViolation: If any formal contract is violated
        """
        # Display welcome message
        console.print(
            Panel.fit(
                "[bold blue]Axiom CLI[/bold blue]\n"
                "Interactive chat with Claude Sonnet 4\n"
                "[dim]Type 'exit' or 'quit' to end session[/dim]",
                border_style="blue",
            )
        )

        try:
            while self.session_active:
                # Get user input with contract validation
                user_input = await self._get_user_input()

                if not user_input:
                    continue

                # Check for exit commands
                if user_input.lower().strip() in ["exit", "quit", "q"]:
                    console.print("[yellow]Ending session...[/yellow]")
                    break

                # Add user message to history
                user_message = AnthropicMessage(role="user", content=user_input)
                self.messages.append(user_message)

                # Get Claude's response
                await self._get_claude_response()

        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted by user[/yellow]")
        except ContractViolation as e:
            console.print(f"[red]Contract violation: {e}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            raise
        finally:
            await self.client.close()

    async def _get_user_input(self) -> str:
        """
        Get user input with validation.

        Returns:
            Validated user input string
        """
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]", default="")

            # Contract validation: input must be non-empty after stripping
            if not user_input.strip():
                return ""

            return user_input.strip()

        except EOFError:
            console.print("\n[yellow]EOF received, ending session[/yellow]")
            self.session_active = False
            return ""

    async def _get_claude_response(self) -> None:
        """
        Get response from Claude Sonnet 4 and display it.

        Raises:
            ContractViolation: If response validation fails
        """
        try:
            # Show thinking indicator
            with console.status("[bold blue]Axiom is thinking...", spinner="dots"):
                response = await self.client.send_message(
                    self.messages, system_message=self.system_message
                )

            # Extract response content
            if not response.content or len(response.content) == 0:
                raise ContractViolation("Empty response from Claude")

            # Get the text content from the first content block
            content_block = response.content[0]
            if content_block.get("type") != "text":
                raise ContractViolation("Unexpected response format from Claude")

            claude_text = content_block.get("text", "")
            if not claude_text.strip():
                raise ContractViolation("Empty text content from Claude")

            # Add Claude's response to message history
            claude_message = AnthropicMessage(role="assistant", content=claude_text)
            self.messages.append(claude_message)

            # Display Axiom's response
            console.print("\n[bold blue]Axiom[/bold blue]")
            console.print(
                Panel(Markdown(claude_text), border_style="blue", padding=(1, 2))
            )

            # Display token usage
            usage = response.usage
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            console.print(
                f"[dim]Tokens: {input_tokens} input, {output_tokens} output[/dim]"
            )

        except ContractViolation:
            raise
        except Exception as e:
            console.print(f"[red]Error getting Claude response: {e}[/red]")
            raise ContractViolation(f"Failed to get valid response: {e}")


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose output")
def main(debug: bool) -> None:
    """
    Axiom CLI - Interactive chat with Claude Sonnet 4.

    A minimal, coherent interface with formal contract enforcement
    and no system message pollution.
    """
    if debug:
        console.print("[dim]Debug mode enabled[/dim]")

    try:
        # Run the async chat session
        asyncio.run(_run_chat_session())
    except ContractViolation as e:
        console.print(f"[red]Contract violation: {e}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)


async def _run_chat_session() -> None:
    """
    Initialize and run the chat session with formal contracts.

    Raises:
        ContractViolation: If any formal contract is violated
    """
    # Create Anthropic client with contract validation
    client = await create_anthropic_client()

    # Create and run chat session
    session = ChatSession(client)
    await session.run_interactive_session()


if __name__ == "__main__":
    main()
