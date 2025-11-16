#!/usr/bin/env python3
"""
Main script for TTS automation using Google Colab
Orchestrates the entire workflow from reading bulletin to downloading audio
"""
import argparse
import sys
import time
from pathlib import Path
from datetime import datetime

# Add module to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from utils.logger import setup_logger, log_section, log_step
from utils.date_utils import get_date_from_arg, format_duration
from utils.retry_handler import RetryHandler
from input_handler.bulletin_reader import BulletinReader
from colab_automation.browser_driver import BrowserDriver
from colab_automation.auth_handler import AuthHandler
from colab_automation.colab_interface import ColabInterface
from colab_automation.cell_executor import CellExecutor
from output_handler.audio_downloader import AudioDownloader
from output_handler.file_manager import FileManager


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="TTS Automation for Vietnamese News Bulletins using Google Colab"
    )
    
    parser.add_argument(
        "--date",
        type=str,
        default="yesterday",
        help="Date of bulletin to process (yesterday, today, or YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--colab-url",
        type=str,
        default=config.COLAB_NOTEBOOK_URL,
        help="Google Colab notebook URL"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        default=config.HEADLESS,
        help="Run browser in headless mode"
    )
    
    parser.add_argument(
        "--auth-method",
        type=str,
        choices=["manual", "cookies"],
        default=config.AUTH_METHOD,
        help="Authentication method"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=config.LOG_LEVEL,
        help="Logging level"
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=config.OUTPUT_DIR,
        help="Output directory for audio files"
    )
    
    return parser.parse_args()


def main():
    """Main execution function"""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logger
    logger = setup_logger(
        name="module_03",
        log_file=config.LOG_FILE,
        log_level=args.log_level
    )
    
    log_section(logger, "TTS AUTOMATION - VIETNAMESE NEWS BULLETIN")
    logger.info(f"Date: {args.date}")
    logger.info(f"Colab URL: {args.colab_url}")
    logger.info(f"Headless: {args.headless}")
    logger.info(f"Auth method: {args.auth_method}")
    logger.info("")
    
    start_time = time.time()
    
    try:
        # ====================================================================
        # STEP 1: Read Bulletin
        # ====================================================================
        log_step(logger, 1, 8, "Reading bulletin from module_02")
        
        bulletin_reader = BulletinReader(config.MODULE_02_OUTPUT)
        
        # Get target date
        if args.date.lower() == "yesterday":
            bulletin_text, bulletin_date = bulletin_reader.read_yesterday_bulletin()
        elif args.date.lower() == "latest":
            bulletin_text, bulletin_date = bulletin_reader.read_latest_bulletin()
        else:
            target_date = get_date_from_arg(args.date)
            bulletin_text = bulletin_reader.read_bulletin(target_date)
            bulletin_date = target_date
        
        logger.info(f"✓ Bulletin loaded for {bulletin_date.strftime('%Y-%m-%d')}")
        logger.info(f"  Text length: {len(bulletin_text)} characters")
        
        # Validate bulletin
        if not bulletin_reader.validate_bulletin(bulletin_text):
            raise ValueError("Bulletin validation failed")
        
        # ====================================================================
        # STEP 2: Initialize Browser
        # ====================================================================
        log_step(logger, 2, 8, "Initializing browser")
        
        browser = BrowserDriver(
            headless=args.headless,
            download_dir=str(args.output_dir),
            window_width=config.WINDOW_WIDTH,
            window_height=config.WINDOW_HEIGHT
        )
        
        driver = browser.start()
        logger.info("✓ Browser started")
        
        try:
            # ================================================================
            # STEP 3: Authenticate with Google
            # ================================================================
            log_step(logger, 3, 8, "Authenticating with Google")
            
            auth_handler = AuthHandler(
                driver=driver,
                cookies_file=config.COOKIES_FILE,
                auth_method=args.auth_method
            )
            
            # Authenticate and navigate to Colab in one step (for cookie method)
            if not auth_handler.authenticate(colab_url=args.colab_url):
                raise RuntimeError("Authentication failed")
            
            logger.info("✓ Authenticated successfully")
            
            # If using manual auth, we need to navigate to Colab
            if args.auth_method == "manual":
                log_step(logger, 4, 8, "Navigating to Google Colab")
                browser.navigate(args.colab_url, wait=5)
                logger.info("✓ Navigated to Colab notebook")
            else:
                logger.info("✓ Already at Colab notebook (via cookie auth)")
            
            # ================================================================
            # STEP 5: Load Notebook and Connect Runtime
            # ================================================================
            log_step(logger, 5, 8, "Loading notebook and connecting runtime")
            
            colab = ColabInterface(driver, config.COLAB_PAGE_LOAD_TIMEOUT)
            
            if not colab.wait_for_notebook_load():
                raise RuntimeError("Notebook failed to load")
            
            logger.info("✓ Notebook loaded")
            
            if not colab.connect_runtime(config.COLAB_RUNTIME_CONNECT_TIMEOUT):
                raise RuntimeError("Failed to connect to runtime")
            
            logger.info("✓ Runtime connected")
            
            # ================================================================
            # STEP 6: Modify Text Cell with Bulletin
            # ================================================================
            log_step(logger, 6, 8, "Inserting bulletin text into notebook")
            
            # Prepare the complete cell content with bulletin
            cell_content = f'''# Generate Vietnamese speech
import torch

# === TEXT INPUT FOR AUTOMATION ===
TEXT_TO_SYNTHESIZE = """{bulletin_text}"""
# === END TEXT INPUT ===

OUTPUT_WAV = "/content/output_vietnamese.wav"

# Parameters
NUM_STEP = 16
SPEED = 0.85
REMOVE_LONG_SIL = False
MAX_DURATION = 100

print("="*70)
print("GENERATING SPEECH")
print("="*70)
print(f"Text: {{TEXT_TO_SYNTHESIZE[:60]}}...")
print(f"Output: {{OUTPUT_WAV}}")
print(f"Params: num_step={{NUM_STEP}}, speed={{SPEED}}")
print("="*70)

print("✓ GENERATION_STARTED")

# Generate
with torch.inference_mode():
    metrics = generate_sentence(
        save_path=OUTPUT_WAV,
        prompt_text=PROMPT_TEXT,
        prompt_wav=PROMPT_WAV,
        text=TEXT_TO_SYNTHESIZE,
        model=model,
        vocoder=vocoder,
        tokenizer=tokenizer,
        feature_extractor=feature_extractor,
        device=device,
        num_step=NUM_STEP,
        guidance_scale=1.0,
        speed=SPEED,
        t_shift=0.5,
        target_rms=0.1,
        feat_scale=0.1,
        sampling_rate=config["feature"]["sampling_rate"],
        max_duration=MAX_DURATION,
        remove_long_sil=REMOVE_LONG_SIL,
    )

print("="*70)
print("✅ COMPLETE")
print("="*70)
print(f"Duration: {{metrics['wav_seconds']:.2f}}s | Time: {{metrics['t']:.2f}}s | RTF: {{metrics['rtf']:.3f}}x")
print(f"Chunks: {{metrics['num_chunks']}} | Saved: {{OUTPUT_WAV}}")
print("="*70)

print("✓ GENERATION_COMPLETE")'''
            
            if not colab.modify_cell_text(config.TEXT_INPUT_CELL_INDEX, cell_content):
                raise RuntimeError("Failed to modify text cell")
            
            logger.info(f"✓ Bulletin inserted into cell {config.TEXT_INPUT_CELL_INDEX}")
            
            time.sleep(2)  # Give Colab time to process the change
            
            # ================================================================
            # STEP 7: Execute All Cells
            # ================================================================
            log_step(logger, 7, 8, "Executing all notebook cells (Run All)")
            
            executor = CellExecutor(
                driver=driver,
                cell_timeout=config.CELL_EXECUTION_TIMEOUT,
                check_interval=config.CHECK_INTERVAL
            )
            
            # Use "Run all" for faster execution
            if not executor.run_all_cells(timeout=config.GENERATION_TIMEOUT):
                logger.warning("Run all may have timed out, checking for output anyway...")
            
            logger.info("✓ Cell execution complete")
            
            # ================================================================
            # STEP 8: Download Audio
            # ================================================================
            log_step(logger, 8, 8, "Downloading generated audio")
            
            downloader = AudioDownloader(driver, config.DOWNLOAD_TIMEOUT)
            file_manager = FileManager(args.output_dir)
            
            # The download cell was already executed as part of "Run All"
            # Just wait for the file to appear in downloads
            logger.info("Waiting for audio file download...")
            logger.info(f"Download directory: {args.output_dir}")
            
            expected_filename = Path(config.COLAB_OUTPUT_PATH).name
            logger.info(f"Expected filename: {expected_filename}")
            
            # Wait for download to complete
            downloaded_file = downloader.wait_for_download_complete(
                args.output_dir,
                expected_filename
            )
            
            if not downloaded_file:
                logger.error("Download timed out. File may not have been generated.")
                logger.error("Check Colab notebook for errors in the generation step.")
                raise RuntimeError("Download failed or timed out")
            
            logger.info(f"✓ Audio downloaded: {downloaded_file}")
            
            # Verify audio file
            if not downloader.verify_audio_file(downloaded_file):
                logger.warning("Audio file verification failed")
            
            # Save with proper naming
            final_path = file_manager.save_audio_file(
                downloaded_file,
                bulletin_date,
                config.OUTPUT_FILENAME_FORMAT
            )
            
            if final_path:
                logger.info(f"✓ Audio saved: {final_path}")
                
                # Clean up downloaded file if different from final path
                if downloaded_file != final_path:
                    file_manager.cleanup_download_file(downloaded_file)
            
            # ================================================================
            # SUCCESS
            # ================================================================
            elapsed = time.time() - start_time
            
            log_section(logger, "✅ TTS AUTOMATION COMPLETE")
            logger.info(f"Bulletin date: {bulletin_date.strftime('%Y-%m-%d')}")
            logger.info(f"Output file: {final_path}")
            logger.info(f"Total time: {format_duration(elapsed)}")
            logger.info("")
            
            return 0
            
        finally:
            # Close browser
            browser.close()
    
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"TTS automation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
