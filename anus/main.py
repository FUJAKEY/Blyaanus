import argparse
import asyncio
from anus.core.orchestrator import AgentOrchestrator
from anus.ui.cli import CLI

async def main():
    """Main entry point for the ANUS framework."""
    parser = argparse.ArgumentParser(description="ANUS - Autonomous Networked Utility System")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to configuration file")
    parser.add_argument("--mode", type=str, default="single", choices=["single", "multi"], help="Agent mode")
    parser.add_argument("--task", type=str, help="Task description")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Initialize CLI and display welcome message
    cli = CLI(verbose=args.verbose)
    cli.display_welcome()
    
    # Create the orchestrator with the provided configuration
    orchestrator = AgentOrchestrator(config_path=args.config)
    
    # Execute task if provided, otherwise start interactive mode
    if args.task:
        result = await orchestrator.execute_task(args.task, mode=args.mode)
        cli.display_result(result)
    else:
        await cli.start_interactive_mode(orchestrator)

if __name__ == "__main__":
    asyncio.run(main())
