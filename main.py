from bs4 import BeautifulSoup, NavigableString
import opencc
import sys
import os
import glob
import logging
import traceback
import time

from dotenv import load_dotenv

load_dotenv()

LOGS_DIR = os.getenv("LOGS_DIR", "logs")
INPUT_DIR = os.getenv("INPUT_DIR", "input")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

INPUT_ENCODING = os.getenv("INPUT_ENCODING", "gbk")
OUTPUT_ENCODING = os.getenv("OUTPUT_ENCODING", "utf-8")

logger = logging.getLogger(__name__)

streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setLevel(logging.INFO)

def convert_html(file : str, encoding: str = INPUT_ENCODING):
  with open(file, encoding = encoding, errors = "ignore") as fp:
    converter = opencc.OpenCC('s2t.json')
    soup = BeautifulSoup(fp, 'html.parser', from_encoding = encoding)

    # for node in list(filter(lambda x: x.string, soup.descendants)):
    for node in soup.find_all(string=True):
      original = str(node.string)

      if not original.strip():
          continue

      converted = converter.convert(original)
      logger.debug(f"{original} -> {converted}")

      node.replace_with(converted)
      # if type(node) is not NavigableString:
      #   node.string = converted
      # else:
      #   pass

    # Save the converted HTML to output file
    output_file = file.replace(INPUT_DIR, OUTPUT_DIR).replace(".htm", ".htm")

    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "+wb") as output_fp:
      output_fp.write(soup.prettify().encode(OUTPUT_ENCODING))

      logger.info(f"Converted file saved to: {output_file}")

if __name__ == "__main__":
  if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

  if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

  logging.basicConfig(
    level = logging.DEBUG,
    format = "[%(asctime)s][%(levelname)s] %(name)s | %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
    handlers=[
      logging.FileHandler(
        time.strftime(
          f"{LOGS_DIR}/%Y-%m-%d_%H-%M-%S.log",
          time.localtime(time.time())
        ),
      ),
      streamHandler
    ]
  )

  # Echo out env vars
  logger.debug("Environment Variables:")
  logger.debug(f"LOGS_DIR: {LOGS_DIR}")
  logger.debug(f"INPUT_DIR: {INPUT_DIR}")
  logger.debug(f"OUTPUT_DIR: {OUTPUT_DIR}")
  logger.debug(f"INPUT_ENCODING: {INPUT_ENCODING}")
  logger.debug(f"OUTPUT_ENCODING: {OUTPUT_ENCODING}")

  # input_files = glob.glob(os.path.join(INPUT_DIR, "*/*/*.htm"), recursive=True)
  input_files = glob.glob(os.path.join(INPUT_DIR, "001/make/*.htm"), recursive=True)

  if not input_files:
    logger.error("No input files found in the input directory.")
    sys.exit(1)

  for file in input_files:
    logger.info(f"Processing file: {file}")
    try:
      convert_html(file)
    except Exception as e:
      logger.error(f"Error processing {file}: {e}")
      logger.debug(f"{traceback.format_exc()}")
      continue
