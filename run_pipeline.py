#!/usr/bin/env python3
"""
Master Orchestrator - VietNews Vietnamese Tech News to Audio Pipeline
Runs all three modules in sequence to generate audio news bulletins
"""
import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_step(step_num, total_steps, text):
    """Print formatted step"""
    print(f"{Colors.OKCYAN}{Colors.BOLD}[Step {step_num}/{total_steps}] {text}{Colors.ENDC}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")

def run_module(module_name, module_path, command, description):
    """
    Run a module and return success status
    
    Args:
        module_name: Name of the module (e.g., "Module 01")
        module_path: Path to the module directory
        command: Command to execute
        description: Description of what the module does
        
    Returns:
        True if successful, False otherwise
    """
    print_info(f"{description}")
    print(f"  Command: {' '.join(command)}")
    print(f"  Working directory: {module_path}")
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            cwd=module_path,
            capture_output=False,  # Show output in real-time
            text=True,
            check=True
        )
        
        duration = time.time() - start_time
        print_success(f"{module_name} completed in {duration:.1f}s")
        return True
        
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        print_error(f"{module_name} failed after {duration:.1f}s")
        print_error(f"Exit code: {e.returncode}")
        return False
        
    except FileNotFoundError:
        print_error(f"Python executable not found. Ensure Python is installed.")
        return False
        
    except KeyboardInterrupt:
        print_warning(f"\n{module_name} interrupted by user")
        return False

def check_prerequisites(project_root):
    """Check if all required files and directories exist"""
    print_step(0, 3, "Checking Prerequisites")
    
    issues = []
    
    # Check module directories
    for module in ['module_01', 'module_02', 'module_03']:
        module_path = project_root / module
        if not module_path.exists():
            issues.append(f"Module directory not found: {module_path}")
        else:
            main_py = module_path / 'main.py'
            if not main_py.exists():
                issues.append(f"main.py not found in {module}")
    
    # Check module_02 .env file
    env_file = project_root / 'module_02' / '.env'
    if not env_file.exists():
        print_warning(f".env file not found in module_02")
        print_warning(f"Please create {env_file} with GEMINI_API_KEY")
        issues.append("Missing .env file in module_02")
    
    # Check module_03 cookies (optional but recommended)
    cookies_file = project_root / 'module_03' / 'colab_cookies.json'
    if not cookies_file.exists():
        print_warning(f"colab_cookies.json not found in module_03")
        print_warning("You may need to authenticate manually during execution")
    
    if issues:
        print_error("Prerequisites check failed:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    
    print_success("All prerequisites met")
    return True

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run the complete Vietnamese Tech News to Audio pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline for yesterday's news
  python run_pipeline.py
  
  # Run full pipeline for a specific date
  python run_pipeline.py --date 2025-11-15
  
  # Run only specific modules
  python run_pipeline.py --modules 1 2
  
  # Skip module 1 (use existing database)
  python run_pipeline.py --skip-scraping
  
  # Dry run (show what would be executed)
  python run_pipeline.py --dry-run
        """
    )
    
    parser.add_argument(
        '--date',
        type=str,
        default='yesterday',
        help='Target date (yesterday, today, or YYYY-MM-DD). Default: yesterday'
    )
    
    parser.add_argument(
        '--modules',
        type=int,
        nargs='+',
        choices=[1, 2, 3],
        default=[1, 2, 3],
        help='Modules to run (1, 2, 3). Default: all modules'
    )
    
    parser.add_argument(
        '--skip-scraping',
        action='store_true',
        help='Skip module 1 (news scraping). Use existing database.'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run module 3 browser in headless mode (default: True)'
    )
    
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run module 3 browser with GUI (for debugging)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be executed without running'
    )
    
    parser.add_argument(
        '--continue-on-error',
        action='store_true',
        help='Continue to next module even if current module fails'
    )
    
    return parser.parse_args()

def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Determine project root
    project_root = Path(__file__).parent.absolute()
    
    # Convert date string to actual date
    if args.date == 'yesterday':
        target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    elif args.date == 'today':
        target_date = datetime.now().strftime('%Y-%m-%d')
    else:
        # Validate date format
        try:
            datetime.strptime(args.date, '%Y-%m-%d')
            target_date = args.date
        except ValueError:
            print_error(f"Invalid date format: {args.date}. Use YYYY-MM-DD, 'yesterday', or 'today'")
            sys.exit(1)
    
    # Print header
    print_header("VIETNEWS - VIETNAMESE TECH NEWS TO AUDIO PIPELINE")
    print(f"Project root: {project_root}")
    print(f"Date: {target_date}")
    print(f"Modules to run: {args.modules}")
    if args.dry_run:
        print_warning("DRY RUN MODE - No commands will be executed")
    print()
    
    # Override modules if skip-scraping is set
    if args.skip_scraping and 1 in args.modules:
        args.modules = [m for m in args.modules if m != 1]
        print_info("Skipping module 1 (news scraping) as requested")
    
    # Check prerequisites
    if not args.dry_run:
        if not check_prerequisites(project_root):
            print_error("\nPrerequisites check failed. Please fix the issues above.")
            sys.exit(1)
    
    # Track execution
    start_time = time.time()
    results = {}
    
    # Module 1: News Scraper
    if 1 in args.modules:
        print_step(1, 3, "MODULE 01 - News Scraper & Aggregator")
        
        module_path = project_root / 'module_01'
        command = [sys.executable, 'main.py']
        
        if args.dry_run:
            print_info(f"Would execute: {' '.join(command)} in {module_path}")
            results['module_01'] = True
        else:
            results['module_01'] = run_module(
                "Module 01",
                module_path,
                command,
                "Collecting news from Vietnamese RSS feeds and scraping full content"
            )
            
            if not results['module_01'] and not args.continue_on_error:
                print_error("\nModule 01 failed. Stopping pipeline.")
                sys.exit(1)
    
    # Module 2: AI Bulletin Generator
    if 2 in args.modules:
        print_step(2, 3, "MODULE 02 - AI Bulletin Generator")
        
        module_path = project_root / 'module_02'
        command = [sys.executable, 'main.py', '--date', target_date]
        
        if args.dry_run:
            print_info(f"Would execute: {' '.join(command)} in {module_path}")
            results['module_02'] = True
        else:
            results['module_02'] = run_module(
                "Module 02",
                module_path,
                command,
                "Generating AI-powered Vietnamese news bulletin with Gemini"
            )
            
            if not results['module_02'] and not args.continue_on_error:
                print_error("\nModule 02 failed. Stopping pipeline.")
                sys.exit(1)
    
    # Module 3: TTS Automation
    if 3 in args.modules:
        print_step(3, 3, "MODULE 03 - TTS Automation via Google Colab")
        
        module_path = project_root / 'module_03'
        command = [sys.executable, 'main.py', '--date', target_date]
        
        # Add headless flag
        if args.no_headless:
            command.append('--no-headless')
        elif args.headless:
            command.append('--headless')
        
        if args.dry_run:
            print_info(f"Would execute: {' '.join(command)} in {module_path}")
            results['module_03'] = True
        else:
            results['module_03'] = run_module(
                "Module 03",
                module_path,
                command,
                "Converting bulletin to speech using Google Colab TTS"
            )
            
            if not results['module_03'] and not args.continue_on_error:
                print_error("\nModule 03 failed. Stopping pipeline.")
                sys.exit(1)
    
    # Print summary
    total_time = time.time() - start_time
    print_header("PIPELINE EXECUTION SUMMARY")
    
    all_success = all(results.values())
    
    for module, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        color = Colors.OKGREEN if success else Colors.FAIL
        print(f"{color}{module}: {status}{Colors.ENDC}")
    
    print(f"\nTotal execution time: {total_time:.1f}s")
    
    if all_success:
        print_success("\n🎉 Pipeline completed successfully!")
        
        # Show output locations
        print("\nOutput files:")
        if 1 in args.modules:
            db_path = project_root / 'module_01' / 'output' / 'news.db'
            print(f"  • Database: {db_path}")
        
        if 2 in args.modules:
            json_path = project_root / 'module_02' / 'output' / f'{target_date}.json'
            txt_path = project_root / 'module_02' / 'output' / f'{target_date}.txt'
            print(f"  • Bulletin (JSON): {json_path}")
            print(f"  • Bulletin (TXT): {txt_path}")
        
        if 3 in args.modules:
            audio_path = project_root / 'module_03' / 'output' / f'{target_date}.wav'
            print(f"  • Audio: {audio_path}")
        
        sys.exit(0)
    else:
        print_error("\n❌ Pipeline completed with errors")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nPipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
