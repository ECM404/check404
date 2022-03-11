#!/usr/bin/python
import os
import yaml
import json
import coloredlogs
import verboselogs
from ctypes import CDLL
from collections.abc import Iterable
import ctypes
if os.name == 'nt':
    from wexpect.wexpect_util import EOF, TIMEOUT
    import wexpect as pexpect
else:
    from pexpect import EOF, TIMEOUT
    import pexpect

logger = verboselogs.VerboseLogger(__name__)
log_fmt = "%(levelname)-10s %(message)s"
coloredlogs.install(level='DEBUG', logger=logger, fmt=log_fmt)


def run_varcheck(command, stdin, function, vartype):
    file = command.replace("./", "")
    restype, func_name, argtypes = function.split()
    if len(vartype) > 1:
        vartype = vartype.split(',')
    if len(argtypes) > 1:
        argtypes = argtypes.split(',')
    if not os.path.isfile(file):
        logger.critical(f"O arquivo {file} não existe.")
        logger.warning("Verifique se não houve erro de compilação.")
        return "nofile_err"
    logger.info(f"Verificando com input: {stdin}.")
    logger.debug(f"Iniciando verificacao da funcao: {function}")
    shared_lib = CDLL(file)
    test_function = getattr(shared_lib, func_name)
    if restype != "void":
        test_function.restype = getattr(ctypes, restype)
    test_function.argtypes = [getattr(ctypes, x) if x[0] != '*'
                              else ctypes.POINTER(getattr(ctypes, x[1:]))
                              for x in argtypes]
    checked_vars = []
    for i, var in enumerate(vartype):
        value = stdin.pop(i)
        logger.debug(f"Testando variavel do tipo {var}, valor {value}.")
        if len(value) > 1:
            checked_vars.append((getattr(ctypes, var[1:])*len(value))(*value))
        else:
            checked_vars.append(ctypes.POINTER(getattr(ctypes, var[1:]))(value))
    test_function(*(checked_vars + [x
                                    if type(x) != list
                                    else (getattr(ctypes, argtypes[i][1:])
                                          * len(stdin[i]))(*stdin[i])
                                    for i, x in enumerate(stdin)]))
    return [list(x) for x in checked_vars]


def run_function(command, stdin, function):
    file = command.replace("./", "")
    restype, func_name, argtypes = function.split()
    if len(argtypes) > 1:
        argtypes = argtypes.split(',')
    if not os.path.isfile(file):
        logger.critical(f"O arquivo {file} não existe.")
        logger.warning("Verifique se não houve erro de compilação.")
        return "nofile_err"
    logger.info(f"Verificando com input: {stdin}.")
    logger.debug(f"Iniciando verificacao da funcao: {function}")
    shared_lib = CDLL(file)
    test_function = getattr(shared_lib, func_name)
    if restype != "void":
        test_function.restype = getattr(ctypes, restype)
    test_function.argtypes = [getattr(ctypes, x) if x[0] != '*'
                              else ctypes.POINTER(getattr(ctypes, x[1:]))
                              for x in argtypes]
    return getattr(shared_lib,
                   func_name)(
                           *[x
                             if type(x) != list
                             else (getattr(ctypes, argtypes[i][1:])
                                   * len(stdin[i]))(*stdin[i])
                             for i, x in enumerate(stdin)])


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
        stdout = child.read().replace("\r\n", "")
    else:
        stdout = child.read().decode('utf-8').replace("\r\n", "")
    return stdout


def runner(problem_set):
    results = {"tests": {}}
    for name, problem in problem_set.items():
        print(f"\n{'*'*12} Verificando {name} {'*'*12}\n")
        weight = problem['weight']
        if "prompts" in problem:
            prompts = problem['prompts']
        command = problem['command']
        results["tests"][name] = {"weight": weight, "status": "fail"}
        for i, stdout in enumerate(problem['stdout']):
            stdin = problem['stdin'][i]
            hint = problem['hints'][i]
            if 'function' in problem:
                function = problem['function']
                if "vartype" in problem:
                    vartype = problem["vartype"]
                    out = run_varcheck(command, stdin, function, vartype)
                else:
                    out = run_function(command, stdin, function)
            else:
                out = run_check(command, stdin, prompts)
            if out == "nofile_err":
                break
            check_aprox = False
            if type(stdout) == str and stdout[0] == "~":
                stdout = float(stdout[1:])
                check_aprox = True
            if stdout == out or \
               (check_aprox and (abs(stdout - out) < 0.1)) or \
               (isinstance(out, Iterable) and stdout in out):
                logger.success("Teste concluído com sucesso =)")
                results["tests"][name]['status'] = "pass"
            else:
                logger.error("Teste apresentou um erro =(")
                if check_aprox:
                    logger.warning(f"Esperava: aprox '{stdout}'. Recebido: '{out}'")
                else:
                    logger.warning(f"Esperava: '{stdout}'. Recebido: '{out}'")
                if hint != "":
                    logger.notice(f"Dica: {hint}")
    return results


def check_results(results):
    total = {"total_tests": len(results["tests"]),
             "passed": 0,
             "total_weights": 0}
    tests = results["tests"]
    grade = 0
    for problem, result in tests.items():
        if result["status"] == "pass":
            total["passed"] += 1
            grade += result["weight"]
        total["total_weights"] += result["weight"]
    total["grade"] = grade * (10/total["total_weights"])
    results["total"] = total
    return results


def main():
    with open("tests/test.yml", "r") as stream:
        try:
            checks = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    results = runner(checks)
    results = check_results(results)
    total = results["total"]
    print()
    logger.info("Testes concluidos.")
    message = f"Passou em {total['passed']}/{total['total_tests']} testes. \
Nota final - {total['grade']:.2f}/10."
    if total["grade"] < 6.0:
        logger.critical(message)
    else:
        logger.success(message)
    with open("tests/results.json", "w") as out:
        json.dump(results, out)


if __name__ == "__main__":
    main()
