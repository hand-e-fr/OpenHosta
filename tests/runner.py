import subprocess as sp
import sys
import time
import threading

if len(sys.argv) != 2:
    sys.exit("Error: Missing required arguments\nUsage: runner.py [SPINNER_TYPE]")

SPINNERS = {
    'classic': ['/', '-', '\\', '|'],
    'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
    'arrows': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
    'balloons': ['．', 'o', 'O', '@', '*'],
    'bouncing': ['⠁', '⠂', '⠄', '⠂'],
    'clock': ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛'],
    'simple': ['.  ', '.. ', '...', ' ..', '  .', '   '],
    'box': ['▖', '▘', '▝', '▗'],
    'star': ['✶', '✸', '✹', '✺', '✹', '✷'],
}

def spinner(stop_event, message):
    chars = SPINNERS[sys.argv[1]]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f'\r{message} {chars[i % len(chars)]}')
        sys.stdout.flush()
        time.sleep(0.2)
        i += 1
    sys.stdout.write('\r' + ' ' * (len(message) + 2) + '\r')
    sys.stdout.flush()

def run_with_spinner(command, message, **kwargs):
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=(stop_spinner, message))
    spinner_thread.start()
    
    result = sp.run(command, **kwargs)
    
    stop_spinner.set()
    spinner_thread.join()
    print(f'\r{message} ✓')
    return result

run_with_spinner(
    "make clean", 
    "Cleaning repository", 
    stdout=sp.DEVNULL
)
run_with_spinner(
    "py -3.12 -m pip install .[dev,pydantic]", 
    "Installing dependencies", 
    stdout=sp.DEVNULL
)

run_with_spinner(
    "py -3.12 -m autopep8 --recursive --in-place src/OpenHosta",
    "Running autopep8",
    check=False,
    shell=True,
)

with open("tests/reports/pyflakes_report.txt", 'w', encoding='utf-8') as file:
    run_with_spinner(
        "py -3.12 -m pyflakes src/OpenHosta/",
        "Running pyflakes",
        check=False,
        shell=True,
        stdout=file,
        stderr=file
    )

with open("tests/reports/isort_report.txt", 'w', encoding='utf-8') as file:
    run_with_spinner(
        "py -3.12 -m isort --check-only src/OpenHosta",
        "Running isort",
        check=False,
        shell=True,
        stdout=file,
        stderr=file
    )

with open("tests/reports/mypy_report.txt", 'w', encoding='utf-8') as file:
    run_with_spinner(
        "py -3.12 -m mypy src/OpenHosta",
        "Running mypy",
        check=False,
        shell=True,
        stdout=file,
        stderr=file
    )

with open("tests/reports/pylint_report.txt", 'w', encoding='utf-8') as file:
    run_with_spinner(
        "py -3.12 -m pylint --rcfile=pyproject.toml src/OpenHosta",
        "Running pylint",
        check=False,
        shell=True,
        stdout=file,
        stderr=file
    )
    
with open("tests/reports/bandit_report.txt", 'w', encoding='utf-8') as file:
    run_with_spinner(
        "py -3.12 -m bandit -c pyproject.toml -r src/OpenHosta",
        "Running bandit",
        check=False,
        shell=True,
        stdout=file,
        stderr=file
    )
    
with open("tests/reports/unittest_report.txt", 'w', encoding='utf-8') as file:
    run_with_spinner(
        "py -3.12 -m pytest tests/unitTests -v --cov=OpenHosta.core",
        "Running unit-tests",
        check=False,
        shell=True,
        stdout=file,
        stderr=file
    )
    
with open("tests/reports/functest_report.txt", 'w', encoding='utf-8') as file:
    run_with_spinner(
        "py -3.12 -m pytest tests/functionnalTests -v --cov=OpenHosta",
        "Running functionnal-tests",
        check=False,
        shell=True,
        stdout=file,
        stderr=file
    )
    
run_with_spinner("py -3.12 -m pip uninstall -y OpenHosta", "Uninstalling dependencies", stdout=sp.DEVNULL)


# filename = ""
# color = lambda x: 'red' if str(x) == " error" else ('blue' if str(x) == " note" else 'white')

# with open(file="mypy/stdout.txt", mode='r', encoding='utf-8') as src:
#     with open(file="mypy/parsed.md", mode='w', encoding='utf-8') as tar:
#         for line in src:
#             s_line = line.split(':', 3)
#             try: 
#                 len(s_line) 
#                 s_line[3]
#             except: continue
    
#             if s_line[0] == "C": continue
            
#             if s_line[0] != filename:
#                 filename = s_line[0]
#                 tar.write(f"\n### {filename.split('/')[-1].replace('_', '-')}\n\n")
#             tar.write(f"- <font color=\'{color(s_line[2])}\'>[line: {s_line[1]}]</font>")
#             tar.write(f": {s_line[3]}\n")
    

    