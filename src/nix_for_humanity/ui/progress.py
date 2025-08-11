"""
Progress indicators for Nix for Humanity

Provides user feedback during long operations.
"""

import logging
import sys
import threading
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)


class Spinner:
    """
    Simple terminal spinner for showing progress
    """

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str = "Processing"):
        """
        Initialize spinner

        Args:
            message: Message to display with spinner
        """
        self.message = message
        self.running = False
        self.thread: threading.Thread | None = None
        self.frame_index = 0

    def _spin(self):
        """Spin animation loop"""
        while self.running:
            frame = self.FRAMES[self.frame_index]
            sys.stdout.write(f"\r{frame} {self.message}...")
            sys.stdout.flush()
            self.frame_index = (self.frame_index + 1) % len(self.FRAMES)
            time.sleep(0.1)

    def start(self):
        """Start the spinner"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._spin, daemon=True)
            self.thread.start()

    def stop(self, final_message: str | None = None):
        """
        Stop the spinner

        Args:
            final_message: Optional message to display after stopping
        """
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=0.5)

            # Clear the line
            sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")

            # Display final message if provided
            if final_message:
                sys.stdout.write(f"{final_message}\n")
            sys.stdout.flush()

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is None:
            self.stop("✓ Done")
        else:
            self.stop("✗ Failed")
        return False


class ProgressBar:
    """
    Simple progress bar for operations with known steps
    """

    def __init__(self, total: int, message: str = "Progress", width: int = 40):
        """
        Initialize progress bar

        Args:
            total: Total number of steps
            message: Message to display
            width: Width of the progress bar in characters
        """
        self.total = total
        self.message = message
        self.width = width
        self.current = 0

    def update(self, current: int | None = None, message: str | None = None):
        """
        Update progress bar

        Args:
            current: Current step number (or increment by 1 if None)
            message: Optional message update
        """
        if current is not None:
            self.current = min(current, self.total)
        else:
            self.current = min(self.current + 1, self.total)

        if message:
            self.message = message

        # Calculate progress
        progress = self.current / self.total if self.total > 0 else 0
        filled = int(self.width * progress)
        empty = self.width - filled

        # Create bar
        bar = "█" * filled + "░" * empty
        percent = int(progress * 100)

        # Display
        sys.stdout.write(f"\r{self.message}: [{bar}] {percent}%")
        sys.stdout.flush()

        # Add newline if complete
        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def finish(self, message: str | None = None):
        """
        Finish the progress bar

        Args:
            message: Optional completion message
        """
        self.current = self.total
        self.update(message=message or f"✓ {self.message} complete")


class PhaseProgress:
    """
    Progress indicator for multi-phase operations
    """

    def __init__(self, phases: list[str]):
        """
        Initialize phase progress

        Args:
            phases: List of phase names
        """
        self.phases = phases
        self.current_phase = 0
        self.spinner: Spinner | None = None

    def start_phase(self, phase_index: int | None = None):
        """
        Start a new phase

        Args:
            phase_index: Index of phase to start (or next if None)
        """
        # Stop previous spinner if running
        if self.spinner:
            self.spinner.stop("✓")

        # Update phase
        if phase_index is not None:
            self.current_phase = phase_index
        else:
            self.current_phase += 1

        if self.current_phase < len(self.phases):
            phase_name = self.phases[self.current_phase]
            phase_num = self.current_phase + 1
            total = len(self.phases)

            message = f"[{phase_num}/{total}] {phase_name}"
            self.spinner = Spinner(message)
            self.spinner.start()

    def complete(self, message: str = "All phases complete"):
        """
        Complete all phases

        Args:
            message: Completion message
        """
        if self.spinner:
            self.spinner.stop()
        print(f"✨ {message}")

    def error(self, message: str = "Operation failed"):
        """
        Handle error during phases

        Args:
            message: Error message
        """
        if self.spinner:
            self.spinner.stop()
        print(f"❌ {message}")


def with_spinner(message: str = "Processing"):
    """
    Decorator to add spinner to a function

    Args:
        message: Message to display with spinner
    """

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            with Spinner(message):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def show_progress(operation: str):
    """
    Simple helper to show progress for an operation

    Args:
        operation: Description of the operation

    Returns:
        Spinner context manager
    """
    return Spinner(operation)


# Example usage
if __name__ == "__main__":
    # Test spinner
    print("Testing spinner...")
    with Spinner("Loading packages"):
        time.sleep(2)

    # Test progress bar
    print("\nTesting progress bar...")
    bar = ProgressBar(10, "Installing")
    for i in range(10):
        time.sleep(0.2)
        bar.update()

    # Test phase progress
    print("\nTesting phase progress...")
    phases = ["Evaluating", "Building", "Installing", "Configuring"]
    progress = PhaseProgress(phases)

    for i in range(len(phases)):
        progress.start_phase(i)
        time.sleep(1)
    progress.complete()
