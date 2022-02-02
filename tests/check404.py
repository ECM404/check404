#!/usr/bin/python
import yaml
import pexpect
import coloredlogs
import verboselogs

logger = verboselogs.VerboseLogger(__name__)
log_fmt = "%(levelname)-10s %(message)s"
coloredlogs.install(level='DEBUG', logger=logger, fmt=log_fmt)


def runner(checks):
    for name, check in checks.items():
        logger.info(f">> Starting check on {name}")
        child = pexpect.spawn(check['command'])
        logger.debug(f"Spawning process {check['command']}")
        prompts = check['stdin']['prompts']
        logger.debug(f"Prompts detected: {prompts}")
        responses = check['stdin']['responses']
        logger.debug(f"Responses detected: {responses}")
        if prompts:
            for prompt, response in zip(prompts, responses):
                logger.verbose(f"Waiting for prompt '{prompt}'")
                index = child.expect([prompt, pexpect.TIMEOUT], timeout=1)
                logger.verbose("Prompt received!")
                if index:
                    logger.critical("Timed out waiting for prompt.")
                    logger.warning("Expected pattern: {prompt}")
                    exit()
                logger.verbose(f"Sending '{response}'")
                child.sendline(response)
                logger.verbose("Response sent.")
                child.readline()
        stdout = child.readline().decode('utf-8').replace("\r\n", "")
        if stdout == check['stdout']:
            logger.success("Test passed")
        else:
            logger.error("Test failed.")
            logger.warning(f"Expected '{stdout}'. Got '{check['stdout']}'")


def main():
    with open("tests/test.yml", "r") as stream:
        try:
            checks = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    runner(checks)


if __name__ == "__main__":
    main()
