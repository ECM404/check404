#!/usr/bin/python
import yaml
import pexpect


def runner(checks):
    for _, check in checks.items():
        child = pexpect.spawn(check['command'])
        print(f"Running command {check['command']}")
        prompts = check['stdin']['prompts']
        responses = check['stdin']['responses']
        if prompts:
            for prompt, response in zip(prompts, responses):
                print(f"Waiting for prompt: {prompt}")
                index = child.expect([prompt, pexpect.TIMEOUT], timeout=1)
                print("Prompt received")
                if index:
                    print("Timed out at prompt...")
                    exit()
                print(f"Sending '{response}'")
                child.sendline(response)
                print("Sent. Flushing stdout")
                child.readline()
        stdout = child.readline().decode('utf-8').replace("\r\n", "")
        if stdout == check['stdout']:
            print("Test Passed!")


def main():
    with open("tests/test.yml", "r") as stream:
        try:
            checks = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    runner(checks)


if __name__ == "__main__":
    main()
