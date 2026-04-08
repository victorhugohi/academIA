"""Interactive CLI demo for academIA — designed for live conference presentations."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from src.data.schemas import Student
    from src.engine.embedder import student_to_query
    from src.engine.recommender import Recommender
    from src.llm.client import LLMClient
except ImportError as e:
    print(f"Import error: {e}")
    print("Run from the project root: python demo/cli.py")
    print("Make sure dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import IntPrompt, Confirm
    from rich.table import Table
    console = Console()
    RICH = True
except ImportError:
    RICH = False


BANNER = """\
╔═══════════════════════════════════╗
║         [bold green]AcademIA v1.0[/]            ║
║   Course Recommendation Engine    ║
║    [dim]Powered by open-source AI[/]     ║
╚═══════════════════════════════════╝"""

BANNER_PLAIN = """\
╔═══════════════════════════════════╗
║         AcademIA v1.0             ║
║   Course Recommendation Engine    ║
║    Powered by open-source AI      ║
╚═══════════════════════════════════╝"""


def load_students() -> list[Student]:
    raw = json.loads(Path("data/raw/students.json").read_text(encoding="utf-8"))
    return [Student(**s) for s in raw]


def run_rich(students: list[Student], recommender: Recommender, llm: LLMClient) -> None:
    """Rich-formatted interactive demo."""
    console.print(BANNER)
    console.print()

    # Ollama status
    ollama_up = llm.is_available()
    if ollama_up:
        console.print(f"  [green][✓][/] Ollama is running — LLM explanations enabled ({llm.model})")
    else:
        console.print(f"  [yellow][!][/] Ollama not found — running in offline mode")
    console.print()

    while True:
        # Student list
        table = Table(show_header=True, header_style="bold dim", show_lines=False)
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="bold")
        table.add_column("Major")
        table.add_column("Year", justify="center")
        table.add_column("Interests", style="italic dim")

        for i, s in enumerate(students, 1):
            interests = ", ".join(s.interests[:3])
            table.add_row(str(i), s.name, s.major, str(s.year), interests)

        console.print(table)
        console.print()

        choice = IntPrompt.ask(
            "Select a student",
            choices=[str(i) for i in range(1, len(students) + 1)],
        )
        student = students[choice - 1]
        query = student_to_query(student)

        # Profile box
        interests_str = ", ".join(student.interests)
        profile_text = (
            f"[bold green]{student.name}[/] · {student.major} · Year {student.year}\n"
            f"[dim]Completed: {len(student.completed_courses)} courses[/]\n"
            f'[italic]"{interests_str}"[/]'
        )
        console.print(Panel(profile_text, border_style="green", width=60))
        console.print()

        # Run recommendation pipeline
        console.print(f"  [dim]Query:[/] [green]\"{query}\"[/]\n")

        total_start = time.perf_counter()

        with console.status("[bold green]Step 1/3 — Filtering & embedding...", spinner="dots"):
            results = recommender.recommend(student, top_k=5)

        # Print pipeline steps
        stats = recommender.last_stats
        console.print("  [dim]── Pipeline ──────────────────────────────[/]")
        for step in stats.steps:
            duration = f"{step.duration_ms:.0f}ms" if step.duration_ms < 1000 else f"{step.duration_ms/1000:.1f}s"
            console.print(f"  [dim]│[/] [bold]{step.name:<15}[/] [yellow]{duration:>7}[/]  {step.detail}")

        # LLM explanations
        llm_start = time.perf_counter()
        explanations: dict[str, str] = {}
        ollama_used = False

        with console.status("[bold green]Step 2/3 — Generating explanations...", spinner="dots"):
            explanations, llm_ms, ollama_used = llm.explain_recommendations(student, results)

        llm_label = "Ollama" if ollama_used else "Fallback"
        llm_time = f"{llm_ms:.0f}ms" if llm_ms < 1000 else f"{llm_ms/1000:.1f}s"
        console.print(f"  [dim]│[/] [bold]{'llm_explain':<15}[/] [yellow]{llm_time:>7}[/]  {llm_label}: {len(explanations)} explanations")

        total_ms = (time.perf_counter() - total_start) * 1000
        console.print(f"  [dim]│[/]")
        console.print(f"  [dim]└─[/] [green]TOTAL: {total_ms:.0f}ms[/]")
        console.print()

        # Results
        console.print("  [bold green]── Recommended Courses ──────────────────────[/]\n")

        for i, (course, score) in enumerate(results, 1):
            bar_len = int(score * 20)
            bar = "[green]" + "█" * bar_len + "[/]" + "░" * (20 - bar_len)
            expl = explanations.get(course.id, "")

            console.print(f"  {i}. [bold]{course.title}[/] ({course.id})")
            console.print(f"     {bar} [bold]{score:.2f}[/]  [dim]{course.department} · {course.difficulty}[/]")
            if expl:
                console.print(f"     [italic]{expl}[/]")
            console.print()

        console.print(f"  [dim]Completed in {total_ms/1000:.1f}s "
                       f"(LLM: {llm_time} · FAISS: {stats.steps[-1].duration_ms if stats.steps else 0:.0f}ms)[/]\n")

        if not Confirm.ask("Try another student?", default=True):
            break
        console.print()

    console.print("\n[green]Thanks for watching![/] 🎓\n")


def run_plain(students: list[Student], recommender: Recommender, llm: LLMClient) -> None:
    """Plain text fallback when rich is not installed."""
    print(BANNER_PLAIN)
    print()

    ollama_up = llm.is_available()
    status = "[✓] Ollama running" if ollama_up else "[!] Ollama offline"
    print(f"  {status}")
    print()

    while True:
        print("Available students:")
        for i, s in enumerate(students, 1):
            interests = ", ".join(s.interests[:3])
            print(f"  {i:2d}. {s.name} ({s.major}, Year {s.year}) — {interests}")

        print()
        try:
            choice = int(input(f"Select a student [1-{len(students)}]: ")) - 1
        except (ValueError, EOFError):
            break
        if not (0 <= choice < len(students)):
            print("Invalid selection.")
            continue

        student = students[choice]
        query = student_to_query(student)
        print(f'\n  Query: "{query}"\n')

        total_start = time.perf_counter()
        results = recommender.recommend(student, top_k=5)

        for step in recommender.last_stats.steps:
            print(f"  │ {step.name:<15} {step.duration_ms:>7.0f}ms  {step.detail}")

        explanations, llm_ms, ollama_used = llm.explain_recommendations(student, results)
        llm_label = "Ollama" if ollama_used else "Fallback"
        print(f"  │ {'llm_explain':<15} {llm_ms:>7.0f}ms  {llm_label}")

        total_ms = (time.perf_counter() - total_start) * 1000
        print(f"  └─ TOTAL: {total_ms:.0f}ms\n")

        print("  Recommendations:\n")
        for i, (course, score) in enumerate(results, 1):
            expl = explanations.get(course.id, "")
            print(f"  {i}. [{score:.2f}] {course.id} — {course.title}")
            if expl:
                print(f"     {expl}")
            print()

        answer = input("Try another student? [Y/n]: ").strip().lower()
        if answer == "n":
            break
        print()

    print("\nDone.")


def main() -> None:
    students = load_students()
    recommender = Recommender()
    llm = LLMClient()

    if RICH:
        run_rich(students, recommender, llm)
    else:
        run_plain(students, recommender, llm)


if __name__ == "__main__":
    main()
