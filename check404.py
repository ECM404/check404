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
    file = command.replace("./", "")
    if not os.path.isfile(file):
        logger.critical(f"O arquivo {file} não existe.")
        logger.warning("Verifique se não houve erro de compilação.")
        return "nofile_err"
    logger.info(f"Verificando com input: {stdin}.")
    logger.debug(f"Iniciando processo com comando: {command}.")
    child = pexpect.spawn(command)
    logger.debug(f"Prompts detectados: {prompts}.")
    if prompts:
        for prompt, response in zip(prompts, stdin):
            logger.verbose(f"Esperando pelo prompt: '{prompt}'.")
            try:
                child.expect([prompt], timeout=1)
                logger.verbose("Prompt recebido!")
                logger.verbose(f"Enviando '{response}'.")
                child.sendline(response)
                logger.verbose("Resposta enviada. Limpando stdout.")
                child.readline()
            except EOF:
                logger.critical("Stdout retornou EOF.")
                break
            except TIMEOUT:
                logger.critical("Timeout esperando pela resposta.")
                break
        logger.verbose("Esperando pela resposta.")
    if os.name == 'nt':
        stdout = child.readline().replace("\r\n", "")
    else:
        stdout = child.readline().decode('utf-8').replace("\r\n", "")
    return stdout


def runner(problem_set):
    for name, problem in problem_set.items():
        print(f"\n{'*'*12} Verificando {name} {'*'*12}\n")
        prompts = problem['prompts']
        command = problem['command']
        for i, stdout in enumerate(problem['stdout']):
            stdin = problem['stdin'][i]
            hint = problem['hints'][i]
            out = run_check(command, stdin, prompts)
            if out == "nofile_err":
                break
            if stdout == out:
                logger.success("Teste concluído com sucesso =)")
            else:
                logger.error("Teste apresentou um erro =(")
                logger.warning(f"Esperava: '{stdout}'. Recebido: '{out}'")
                if hint != "":
                    logger.notice(f"Dica: {hint}")


def main():
    with open("tests/test.yml", "r") as stream:
        try:
            checks = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    runner(checks)


if __name__ == "__main__":
    main()
