#!/usr/bin/env python3

import gpiozero
import sys
import time
import pipes
import logging
import logging.handlers
from datetime import datetime

INPUT_LOG_FILE='/home/pi/log.csv'
OUTPUT_LOG_FILE='/home/pi/tempwatch.log'
MAX_LOG_SIZE=1024*100
MAX_LOG_BACKUPS=3

SLEEP_TIME=60

MAX_RECORD_AGE=60*15 # 15 minutes
TARGET_TEMP=69.8 # 21ºC
HEATER_CONTROL_PIN=26

logging.raiseException = True
logging.basicConfig(
    format='%(levelname)s:%(asctime)s:%(lineno)d %(message)s',
    level=logging.DEBUG,
    handlers=[logging.handlers.RotatingFileHandler(
                                                    OUTPUT_LOG_FILE,
                                                    maxBytes=MAX_LOG_SIZE,
                                                    backupCount=MAX_LOG_BACKUPS,
                                                    encoding='UTF-8')]
)
heat_switch = gpiozero.DigitalOutputDevice(HEATER_CONTROL_PIN)

def last_line(filename):
    pipeline = pipes.Template()
    pipeline.append('tail -n1', '--')
    infile = pipeline.open(filename, 'r')
    line = infile.readline()
    infile.close()
    logging.debug(f"Read line «{line}»")
    return line


def read_time(timestr):
    try:
        return datetime.strptime(timestr, "%m/%d/%Y  %I:%M:%S %p").timestamp()
    except ValueError:
        logging.warning(f"Unable to parse time string «{timestr}». Returning zero.")
        return 0


def read_temp(tempstr):
    try:
        return float(tempstr)
    except ValueError:
        logging.warning(f"Temperature string «{tempstr}» is not a valid float. Pretending like we hit our target.")
        return TARGET_TEMP


def read_line(line):
    line = line.split(',')
    return {"timestamp":read_time(line[0]), "temp": read_temp(line[2])}


def heat_off(reason):
    logging.info(f"Received heat_off(current {heat_switch.value}): {reason}")
    if heat_switch.value == 1:
        logging.debug("Turning heat off.")
        heat_switch.off()
    else:
        logging.debug("Heat was already off.")


def heat_on(reason):
    logging.info(f"Received heat_on(current {heat_switch.value}): {reason}")
    if heat_switch.value == 0:
        logging.debug("Turning heat on.")
        heat_switch.on()
    else:
        logging.debug("Heat was already on.")


def main():
    logging.info("Startup.")
    heat_switch.off()

    while 1:
        logging.debug(f"Loop starting by sleeping for {SLEEP_TIME}.")
        time.sleep(SLEEP_TIME)
        logging.debug("Waking.")
        record = read_line(last_line(INPUT_LOG_FILE))
        if record.get('timestamp', 0) < (datetime.now().timestamp() - MAX_RECORD_AGE):
            heat_off("Too long since last record")
            continue
        elif record.get('temp', TARGET_TEMP) < TARGET_TEMP:
            heat_on("Below target temperature")
            continue
        else:
            heat_off("Temperature is fine")
            continue

    logging.info("Exited loop, shutting down.")


if __name__ == "__main__":
    main()
