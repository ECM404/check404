#!/usr/bin/python
import os
import yaml
import coloredlogs
import verboselogs
if os.name == 'nt':
    from wexpect.wexpect_util import EOF, TIMEOUT
    import wexpect as pexpect
else:
    from pexpect import EOF, TIMEOUT
    import pexpect

logger = verboselogs.VerboseLogger(__name__)
log_fmt = "%(levelname)-10s %(message)s"
coloredlogs.install(level='INFO', logger=logger, fmt=log_fmt)


def run_check(command, stdin, prompts):
    logger.info(f">>>> Starting check with input: {stdin}.")
    logger.debug(f"Spawning process {command}")
    child = pexpect.spawn(command)
    logger.debug(f"Prompts detected: {prompts}")
    if prompts:
        for prompt, response in zip(prompts, stdin):
            logger.verbose(f"Waiting for prompt '{prompt}'")
            try:
                child.expect([prompt], timeout=1)
                logger.verbose("Prompt received!")
                logger.verbose(f"Sending '{response}'")
                child.sendline(response)
                logger.verbose("Response sent. Flushing stdout.")
                child.readline()
            except EOF:
                logger.critical("Program returned EOF.")
                break
            except TIMEOUT:
                logger.critical("Timed out waiting for prompt.")
                break
        logger.verbose("Waiting for stdout.")
    if os.name == 'nt':
        stdout = child.readline().replace("\r\n", "")
    else:
        stdout = child.readline().decode('utf-8').replace("\r\n", "")
    return stdout


def runner(problem_set):
    for name, problem in problem_set.items():
        logger.info(f">> Starting check on {name}")
        prompts = problem['prompts']
        command = problem['command']
        for i, stdout in enumerate(problem['stdout']):
            stdin = problem['stdin'][i]
            hint = problem['hints'][i]
            out = run_check(command, stdin, prompts)
            if stdout == out:
                logger.success("Test passed")
            else:
                logger.error("Test failed.")
                logger.warning(f"Expected '{stdout}'. Got '{out}'")
                if hint != "":
                    logger.notice(f"Hint: {hint}")


def main():
    with open("tests/test.yml", "r") as stream:
        try:
            checks = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    runner(checks)


if __name__ == "__main__":
    main()
