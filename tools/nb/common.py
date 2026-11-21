"""Shared building blocks for the lab notebooks.

A lab is a list of Cell objects. Each code cell can contain TODO lines
written as

    @@ <solved code> ||| <unsolved code with a # TODO comment>

The builder writes the solved notebook with the left side and the
unsolved notebook with the right side. Extra-task answer cells carry an
explicit `unsolved=` source. Every cell also carries the spec columns
used to generate content/notebooks-spec.md, so the spec and the
notebooks are always in the same order.
"""

REPO = 'mibnrashid/SDAIA_ComputerVision'
RAW = f'https://raw.githubusercontent.com/{REPO}/main'


class Cell:
    def __init__(self, kind, src, what, expect='—', breaks='—', unsolved=None, run=False, extra=False):
        self.kind = kind            # 'md' or 'code'
        self.src = src.strip('\n')
        self.what = what
        self.expect = expect
        self.breaks = breaks
        self.unsolved = unsolved.strip('\n') if unsolved is not None else None
        self.run = run              # Musa must run this on Colab before class
        self.extra = extra

    @property
    def is_todo(self):
        return '@@ ' in self.src

    def source(self, solved):
        if self.unsolved is not None and not solved:
            return self.unsolved
        out = []
        for line in self.src.split('\n'):
            stripped = line.lstrip()
            if stripped.startswith('@@ '):
                indent = line[:len(line) - len(stripped)]
                left, right = stripped[3:].split(' ||| ', 1)
                out.append(indent + (left if solved else right))
            else:
                out.append(line)
        return '\n'.join(out)

    def todo_lines(self):
        return [l.strip()[3:].split(' ||| ', 1)[1] for l in self.src.split('\n') if l.strip().startswith('@@ ')]


def md(src, what='Explains the next step', **kw):
    return Cell('md', src, what, **kw)


def code(src, what, expect='—', breaks='—', **kw):
    return Cell('code', src, what, expect, breaks, **kw)


def how_to_use(lab, title, goal, day_block, minutes, colab_gpu=True):
    gpu = ('Switch the runtime to a **T4 GPU** first: *Runtime → Change runtime type → T4 GPU*.'
           if colab_gpu else 'A GPU is not needed for this lab; the CPU runtime is fine.')
    return md(f'''# Lab {lab} · {title}

**Computer Vision for Developers** · {day_block} · by **Musa Ibn Rashid**, SDAIA Academy

**Goal:** {goal}

## How to use this notebook

1. {gpu}
2. Run the cells **from top to bottom** with *Shift + Enter*. Do not skip cells: later cells use variables from earlier ones.
3. Cells with a **TODO** comment need **one line** from you. The cell right after each TODO is a check: it prints ✅ when your line is right, or a hint when it is not.
4. Nobody writes a cell from empty. If you are stuck for more than five minutes, open the *solved* version of this notebook and compare.
5. Colab forgets files when the session ends. If you come back later, run everything again from the top.
6. The **Extra tasks** at the end are optional and are not graded.

Expected time: about {minutes} minutes in class; finish the rest at home.''',
              'Title, goal and how to work through the notebook')


def gpu_check(fast_note='smaller settings'):
    return code(f'''# GPU check, with a CPU fallback
import os, torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
if DEVICE == "cuda":
    print("✅ GPU:", torch.cuda.get_device_name(0))
else:
    print("⚠️ No GPU found. Runtime → Change runtime type → T4 GPU, then Runtime → Restart.")
    print("   You can keep going on CPU: the notebook switches to {fast_note}.")
# FAST mode shrinks data and epochs so everything still finishes on a CPU.
FAST = DEVICE == "cpu" or os.environ.get("CVD_FAST") == "1"
print("DEVICE =", DEVICE, "| FAST =", FAST)''',
                'Detects the GPU; sets DEVICE and the FAST flag for the CPU fallback',
                '"✅ GPU: Tesla T4" and "DEVICE = cuda | FAST = False" (on CPU: a warning and FAST = True)',
                'No GPU assigned (Colab quota) → keep going in FAST mode, or try again later')


def check(cond, ok, hint, setup=''):
    """An assert cell that prints ✅ or a hint, never a traceback."""
    body = (setup + '\n' if setup else '')
    return code(f'''# Check
{body}try:
    assert {cond}
    print({("✅ " + ok)!r})
except Exception as e:
    print({("❌ Not yet. Hint: " + hint)!r})''',
                'Checks the TODO above and prints ✅ or a hint',
                f'✅ {ok}', 'Prints the hint until the TODO line is right')
