#!/usr/bin/env python3
"""
🎓 Interactive Tutorial for Luminous Nix

An interactive tutorial that teaches NixOS basics through
guided exercises with Luminous Nix.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.service_simple import LuminousNixService, ServiceOptions


class InteractiveTutorial:
    """Interactive tutorial for new NixOS users"""
    
    def __init__(self):
        """Initialize tutorial"""
        self.service = None
        self.lesson_number = 0
        self.total_lessons = 7
        
    def clear_screen(self):
        """Clear terminal screen"""
        print("\033[2J\033[H")
    
    def print_header(self, title: str):
        """Print a formatted header"""
        self.clear_screen()
        print("🌟 " + "=" * 60 + " 🌟")
        print(f"   {title}")
        print("🌟 " + "=" * 60 + " 🌟")
        print()
    
    def print_box(self, content: str, color: str = ""):
        """Print content in a box"""
        lines = content.strip().split("\n")
        max_length = max(len(line) for line in lines)
        
        print("┌" + "─" * (max_length + 2) + "┐")
        for line in lines:
            print(f"│ {line.ljust(max_length)} │")
        print("└" + "─" * (max_length + 2) + "┘")
    
    def wait_for_enter(self, prompt: str = "Press Enter to continue..."):
        """Wait for user to press Enter"""
        input(f"\n{prompt}")
    
    def get_user_input(self, prompt: str) -> str:
        """Get input from user"""
        return input(f"\n{prompt} ").strip()
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"\n✅ {message}")
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"\nℹ️  {message}")
    
    def print_tip(self, message: str):
        """Print a tip"""
        print(f"\n💡 Tip: {message}")
    
    async def initialize_service(self):
        """Initialize the Luminous Nix service"""
        self.print_info("Initializing Luminous Nix...")
        
        # Use dry-run mode for safety
        options = ServiceOptions(execute=False, interface="tutorial")
        self.service = LuminousNixService(options)
        await self.service.initialize()
        
        self.print_success("Luminous Nix is ready!")
    
    async def execute_command(self, command: str, show_output: bool = True):
        """Execute a command through the service"""
        if show_output:
            print(f"\n🔧 Running: ask-nix \"{command}\"")
            print("   Please wait...")
        
        response = await self.service.execute_command(command)
        
        if show_output:
            if response.success:
                print(f"\n📋 Result:\n{response.text}")
            else:
                print(f"\n❌ Error: {response.text}")
        
        return response
    
    async def lesson_1_introduction(self):
        """Lesson 1: Introduction to Luminous Nix"""
        self.print_header("Lesson 1: Welcome to Luminous Nix!")
        
        print("""
Welcome to the interactive tutorial for Luminous Nix!

Luminous Nix lets you control NixOS using natural language
instead of complex commands. Just describe what you want!

For example, instead of:
  nix-env -iA nixos.firefox

You can simply say:
  ask-nix "install firefox"
        """)
        
        self.wait_for_enter()
        
        print("\nLet's start with a simple command to check your system:")
        
        response = await self.execute_command("show system info")
        
        self.print_success("Great! You just ran your first Luminous Nix command!")
        self.print_tip("You can ask for help anytime with: ask-nix \"help\"")
        
        self.wait_for_enter()
    
    async def lesson_2_searching(self):
        """Lesson 2: Searching for packages"""
        self.print_header("Lesson 2: Finding Software")
        
        print("""
One of the most common tasks is finding software to install.
With Luminous Nix, you don't need to know exact package names!

Let's search for a text editor:
        """)
        
        self.wait_for_enter("Press Enter to search...")
        
        await self.execute_command("search for text editors")
        
        print("\n" + "─" * 60)
        print("\nNow you try! Search for something you're interested in.")
        print("Examples: music player, web browser, terminal, games")
        
        user_search = self.get_user_input("What would you like to search for?")
        
        if user_search:
            await self.execute_command(f"search for {user_search}")
            self.print_success(f"Nice! You searched for {user_search}")
        
        self.print_tip("You can search by description, not just names!")
        self.wait_for_enter()
    
    async def lesson_3_installing(self):
        """Lesson 3: Installing packages (dry-run)"""
        self.print_header("Lesson 3: Installing Software (Safe Mode)")
        
        print("""
Now let's learn how to install software. Don't worry - we're
in "dry-run" mode, so nothing will actually be installed!

This lets you practice safely and see what would happen.

Let's try installing a popular package:
        """)
        
        self.wait_for_enter("Press Enter to simulate installation...")
        
        await self.execute_command("install htop")
        
        print("\n" + "─" * 60)
        print("\nNotice it shows what WOULD be installed, but doesn't do it.")
        print("This is dry-run mode - perfect for learning!")
        
        print("\nYour turn! Pick something to \"install\" (safely):")
        print("Suggestions: vim, git, python, nodejs, firefox")
        
        user_install = self.get_user_input("What would you like to install?")
        
        if user_install:
            await self.execute_command(f"install {user_install}")
            self.print_success(f"Good job! You practiced installing {user_install}")
        
        self.print_tip("Use --dry-run flag to always preview changes first!")
        self.wait_for_enter()
    
    async def lesson_4_generations(self):
        """Lesson 4: Understanding generations"""
        self.print_header("Lesson 4: Time Travel with Generations")
        
        print("""
NixOS has a superpower: Generations!

Every time you change your system, NixOS saves a snapshot
called a "generation". You can always go back if something
breaks. It's like having unlimited undo for your entire OS!

Let's look at your system's history:
        """)
        
        self.wait_for_enter("Press Enter to see generations...")
        
        await self.execute_command("list generations")
        
        print("\n" + "─" * 60)
        print("""
Each generation is a complete system snapshot. You can:
- Boot into any previous generation
- Roll back if an update causes problems
- Compare what changed between generations

This is why NixOS is considered "unbreakable"!
        """)
        
        self.print_tip("Use 'ask-nix rollback' to go back one generation")
        self.wait_for_enter()
    
    async def lesson_5_natural_language(self):
        """Lesson 5: Natural language power"""
        self.print_header("Lesson 5: The Power of Natural Language")
        
        print("""
The real magic of Luminous Nix is that you don't need to
memorize commands or package names. Just describe what you need!

Watch this - instead of knowing package names, just describe:
        """)
        
        examples = [
            ("I need something to edit photos", "gimp, krita, inkscape"),
            ("I want to download youtube videos", "youtube-dl, yt-dlp"),
            ("I need a pdf reader", "evince, okular, zathura"),
        ]
        
        for description, result in examples:
            print(f"\n📝 \"{description}\"")
            self.wait_for_enter("Press Enter to see suggestions...")
            print(f"   → Suggests: {result}")
        
        print("\n" + "─" * 60)
        print("\nNow you practice! Describe what you need (don't use exact names):")
        print("Ideas: 'way to record my screen', 'tool for making music', etc.")
        
        user_description = self.get_user_input("Describe what software you need:")
        
        if user_description:
            await self.execute_command(user_description)
            self.print_success("Perfect! Natural language makes NixOS accessible!")
        
        self.wait_for_enter()
    
    async def lesson_6_system_management(self):
        """Lesson 6: System management"""
        self.print_header("Lesson 6: Managing Your System")
        
        print("""
Let's explore system management commands. These help you
keep your NixOS system healthy and up-to-date.

Common tasks you can do with natural language:
        """)
        
        tasks = [
            "Check for updates",
            "Clean up old packages",
            "Show disk usage",
            "List running services",
        ]
        
        for i, task in enumerate(tasks, 1):
            print(f"\n{i}. {task}")
            choice = self.get_user_input(f"Try this command? (y/N)")
            
            if choice.lower() == 'y':
                await self.execute_command(task.lower())
                time.sleep(1)
        
        self.print_tip("Regular cleanup keeps your system running smoothly!")
        self.wait_for_enter()
    
    async def lesson_7_getting_help(self):
        """Lesson 7: Getting help"""
        self.print_header("Lesson 7: Getting Help")
        
        print("""
Remember: Luminous Nix is here to help! You can always ask
questions in natural language.

Try these helpful commands:
        """)
        
        help_commands = [
            "help",
            "how do I install packages?",
            "what is a flake?",
            "explain generations",
        ]
        
        for cmd in help_commands:
            print(f"\n• ask-nix \"{cmd}\"")
        
        print("\n" + "─" * 60)
        print("\nLuminous Nix can also explain errors:")
        print("• ask-nix \"what does error X mean?\"")
        print("• ask-nix \"why is firefox not starting?\"")
        
        self.print_tip("Don't memorize commands - just ask what you need!")
        self.wait_for_enter()
    
    async def final_exercise(self):
        """Final exercise combining all lessons"""
        self.print_header("Final Exercise: Complete Workflow")
        
        print("""
Let's put it all together! Complete this workflow:

1. Search for a category of software
2. Pick one to "install" (dry-run)
3. Check what generation you're on
4. Ask for help about something

This simulates a real NixOS user's workflow.
        """)
        
        self.wait_for_enter("Press Enter to begin...")
        
        # Step 1
        print("\n📋 Step 1: Search for software")
        search = self.get_user_input("What category to search? (e.g., 'games', 'editors'):")
        if search:
            await self.execute_command(f"search for {search}")
        
        # Step 2
        print("\n📋 Step 2: Install something (dry-run)")
        install = self.get_user_input("What to install from the results?")
        if install:
            await self.execute_command(f"install {install}")
        
        # Step 3
        print("\n📋 Step 3: Check your generation")
        await self.execute_command("current generation")
        
        # Step 4
        print("\n📋 Step 4: Ask for help")
        help_topic = self.get_user_input("What would you like help with?")
        if help_topic:
            await self.execute_command(f"help with {help_topic}")
        
        self.print_success("Excellent work! You've completed the workflow!")
    
    async def conclusion(self):
        """Tutorial conclusion"""
        self.print_header("🎉 Congratulations! Tutorial Complete!")
        
        print("""
You've learned the basics of using NixOS with Luminous Nix!

Key takeaways:
✅ Use natural language instead of complex commands
✅ Dry-run mode lets you practice safely
✅ Generations keep your system safe
✅ Just describe what you need
✅ Help is always available

Next steps:
1. Try the Terminal UI: nix-tui
2. Read the full guide: docs/06-TUTORIALS/NIXOS_FOR_BEGINNERS.md
3. Experiment freely - you can always rollback!

Thank you for learning with Luminous Nix!
        """)
        
        self.print_box("""
    Remember: With NixOS + Luminous Nix,
    you can't break your system permanently.
    Experiment, learn, and have fun!
        """)
        
        print("\n🌟 Happy Nixing! 🌟\n")
    
    async def run(self):
        """Run the complete tutorial"""
        try:
            self.print_header("Luminous Nix Interactive Tutorial")
            
            print("Welcome! This tutorial will teach you NixOS basics")
            print("using natural language commands.")
            print("\nThe tutorial has 7 short lessons (~15 minutes total)")
            print("You can exit anytime with Ctrl+C")
            
            self.wait_for_enter("Press Enter to begin...")
            
            # Initialize service
            await self.initialize_service()
            
            # Run lessons
            lessons = [
                self.lesson_1_introduction,
                self.lesson_2_searching,
                self.lesson_3_installing,
                self.lesson_4_generations,
                self.lesson_5_natural_language,
                self.lesson_6_system_management,
                self.lesson_7_getting_help,
            ]
            
            for i, lesson in enumerate(lessons, 1):
                self.lesson_number = i
                await lesson()
                
                if i < len(lessons):
                    print(f"\n📚 Completed lesson {i} of {self.total_lessons}")
                    continue_choice = self.get_user_input("Continue to next lesson? (Y/n)")
                    if continue_choice.lower() == 'n':
                        print("\nTutorial paused. Run again to continue!")
                        break
            else:
                # All lessons completed
                await self.final_exercise()
                await self.conclusion()
            
        except KeyboardInterrupt:
            print("\n\n👋 Tutorial interrupted. Come back anytime!")
            print("   Run 'python interactive_tutorial.py' to restart")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("   Please report issues at: https://github.com/Luminous-Dynamics/luminous-nix/issues")


def main():
    """Main entry point"""
    tutorial = InteractiveTutorial()
    asyncio.run(tutorial.run())


if __name__ == "__main__":
    main()