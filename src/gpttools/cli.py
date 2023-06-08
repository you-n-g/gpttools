"""Command Line Interface."""
import re
from pathlib import Path

import typer
from tqdm.auto import tqdm

from gpttools.llm import APIBackend

app = typer.Typer()


@app.command()
def run() -> None:
    """Run command."""


@app.command()
def tex_convert() -> None:
    print("Converting tex: you can use following command to convert it to text first")
    print(
        'docker run --rm --volume "`pwd`:/data" --user `id -u`:`id -g` pandoc/latex:2.6 <all things after pandoc command, e.g.  "-s example4.tex -o example5.md">',
    )
    print("pdftotext input.pdf output.txt")
    print("sudo apt-get install texlive-extra-utils && detex input.tex > output.txt")


'''
def stop(line):
    if line.strip() in {"REFERENCES"}:
        return True
    return False


def keep_block(block):

    if len(block) < 2:
        return False

    max_line_len = max([len(line) for line in block])
    if max_line_len < 30:
        return False

    return True


def process_block(block):
    block = [line.strip() for line in block]
    return " ".join(block).replace("  ", " ")


@app.command()
def post_process_pdftotext(path: str):
    """
    After converting the pdf to output.txt via pdftotext. The lines are splits and the content is hard to read
    So we need to post process it to make it more readable
    """
    path = Path(path)
    with path.open("r") as f:
        lines = f.readlines()
    blocks = []
    cur = []
    for line in lines:
        print(line)

        if line.strip() == "" or stop(line):
            if keep_block(cur):
                blocks.append(cur)
            else:
                print(cur)
                print("-" * 20, "filtered")
            cur = []
        else:
            cur.append(line)

        if stop(line):
            __import__('ipdb').set_trace()
            print(cur)
            print(line)
            break

    for block in blocks:
        print(process_block(block))
        print()
'''


def keep_line(line):
    if len(line.strip()) <= 1:
        return False

    if re.match(r".*</[^>]+>.*", line):
        return False
    return True


def is_start(line):
    if line.strip() in {"Introduction"}:
        return True
    return False


@app.command()
def post_process(path: str):
    path = Path(path)
    with path.open("r") as f:
        lines = f.readlines()

    start = False
    for line in lines:
        if not start and is_start(line):
            start = True
        if start and keep_line(line):
            print(line.strip())

def _fix_cases(text):
    return re.sub(r" +", r" ", text).strip()

@app.command()
def fix_grammar(path: str, start: int = 0):
    path = Path(path)
    with path.open("r") as f:
        lines = f.readlines()
    ab = APIBackend()

    align_path = path.with_suffix(".algin.txt")
    new_path = path.with_suffix(".out.txt")
    if start == 0:
        for p in align_path, new_path:
            if p.exists():
                p.unlink()

    for i, line in tqdm(list(enumerate(lines))):
        line = _fix_cases(line)
        if i < start:
            continue
        system_prompt = """
Act as a language expert, proofread my paper on the above content while putting a focus on grammar and punctuation. Just output the corrected content. Don't give any explanation. Please keep the markdown and latex format.

Example input:
Content:
```
I is a pig.
```

Example output:
I am a pig.
"""
        user_prompt = """Content:
```
{context}
```""".format(
            context=line,
        )
        print(user_prompt)
        response = ab.build_messages_and_create_chat_completion(
            user_prompt,
            system_prompt,
        )
        print(f"{response}")

        with new_path.open("a") as f:
            if response.startswith("Corrected content:"):
                response = response.replace("Corrected content:", "")
            f.write(f"--- Line {i}: ---\n")
            f.write(response + "\n")

        with align_path.open("a") as f:
            f.write(f"--- Line {i}: ---\n")
            f.write(line.strip() + "\n")

@app.command()
def run_all():
    print("detex sample-authordraft.tex > sample-authordraft.detex.txt")
    print("gpttools-cli post-process sample-authordraft.detex.txt > sample-authordraft.detex.processed.txt")
    print("gpttools-cli fix-grammar sample-authordraft.detex.processed.txt")
    print("vim -d sample-authordraft.detex.processed.out.txt sample-authordraft.detex.processed.algin.txt")

typer_click_object = typer.main.get_command(app)

if __name__ == "__main__":
    app()  # pragma: no cover
