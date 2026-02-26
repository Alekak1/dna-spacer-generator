import PySimpleGUI as sg
from secrets import choice
from pathlib import Path

# Parameters
MIN_LENGTH = 10
MAX_LENGTH = 5000
GC_MIN = 1
GC_MAX = 99

# Image path relative to this script
IMG_PATH = Path(__file__).resolve().parent / "img/dna5.png"

# Visual settings
sg.theme("SystemDefault")
FONT_LABEL = ("Arial", 12)
FONT_INPUT = ("Arial", 12)
FONT_BTN   = ("Arial", 12, "bold")

# Engin
def generate_spacer(length: int, target_gc: int):
    """Generate spacer with exact-ish target GC% (rounded down by int)."""
    gc_number = int((target_gc / 100) * length)
    at_number = length - gc_number

    GC = ["G", "C"]
    AT = ["A", "T"]
    groups = [GC, AT]
    spacer = []

    while len(spacer) < length:
        group = choice(groups)
        if group is GC:
            spacer.append(choice(GC))
            gc_number -= 1
            if gc_number <= 0 and GC in groups:
                groups.remove(GC)
        else:
            spacer.append(choice(AT))
            at_number -= 1
            if at_number <= 0 and AT in groups:
                groups.remove(AT)

    spacer_dna = "".join(spacer)
    A_count = spacer_dna.count("A")
    T_count = spacer_dna.count("T")
    G_count = spacer_dna.count("G")
    C_count = spacer_dna.count("C")
    gc_content = (G_count + C_count) / length * 100

    return spacer_dna, gc_content, A_count, T_count, G_count, C_count

# Input column
left = [
    [sg.Text("Length", size=(12, 1), font=FONT_LABEL, justification="right"),
     sg.Input(size=(14, 1), font=FONT_INPUT, enable_events=True, key="-LENGTH-")],

    [sg.Text("GC %", size=(12, 1), font=FONT_LABEL, justification="right"),
     sg.Input("50", size=(14, 1), font=FONT_INPUT, enable_events=True, key="-GC-")],

    [sg.Checkbox("5' and 3' marks", key="-MARKS-", enable_events=True, font=FONT_LABEL)],

    [sg.Button("Generate Spacer", key="-GENERATE-", font=FONT_BTN, expand_x=True, size=(20, 1))],

    [sg.Button("Copy Sequence", key="-COPY-", font=FONT_BTN, expand_x=True, size=(20, 1), disabled=True)],

    [sg.HSeparator()],

    [sg.Text("", expand_x=True, justification="center", font=FONT_LABEL,
             text_color="brown", key="-ERROR-", size=(25, 2))]
]

# Results column
right = [
    [sg.Text("Spacer sequence", font=("Segoe UI", 12, "bold"))],
    [sg.Multiline(
        "", key="-SPACER-", size=(50, 5),
        font=("Consolas", 11),
        disabled=True, expand_x=True, expand_y=True
    )],
    [sg.Text("", key="-PARAM1-", font=("Segoe UI", 10))],
    [sg.Text("", key="-PARAM2-", font=("Segoe UI", 10))],
]

image_col = [
    [sg.Image(filename=str(IMG_PATH) if IMG_PATH.exists() else None, key="-IMG-", pad=(0,0))],
    [sg.Text("dna5.png not found" if not IMG_PATH.exists() else "", text_color="gray", justification="center", pad=(0,0))]
]

layout = [
    [
        sg.Frame("Parameters", left, expand_y=True, pad=(0, 0)),
        sg.Column(image_col, element_justification="center",
                  vertical_alignment="top", pad=(0, 0)),
        sg.Frame("Output", right, expand_x=True, expand_y=True, pad=(0, 0)),
    ]
]

window = sg.Window("Spacer DNA Generator", layout, resizable=True, margins=(5, 5), finalize=True)
# I-beam
for key in ("-LENGTH-", "-GC-"):
    window[key].Widget.configure(cursor="xterm")
# Arrow
window["-SPACER-"].Widget.configure(cursor="arrow")

last_spacer = ""

# Main loop
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break

    if event == "-GENERATE-":
        window["-ERROR-"].update("")
        
        # Input validation
        errors = []

        try:
            length = int(values["-LENGTH-"])
            if not (MIN_LENGTH <= length <= MAX_LENGTH):
                errors.append(f"Length must be {MIN_LENGTH}-{MAX_LENGTH} bp")
        except:
            errors.append("Enter a valid integer length")

        try:
            gc = int(values["-GC-"])
            if not (GC_MIN <= gc <= GC_MAX):
                errors.append(f"GC must be {GC_MIN}-{GC_MAX}%")
        except:
            errors.append("Enter a valid integer GC%")

        if errors:
            window["-ERROR-"].update("\n".join(errors), text_color="firebrick")
            continue
        
        # Generate spacer
        spacer_dna, gc_content, A, T, G, C = generate_spacer(length, gc)

        # End markers
        if values["-MARKS-"]:
            shown = f"5' {spacer_dna} 3'"
        else:
            shown = spacer_dna

        # Spacer metrics
        last_spacer = spacer_dna
        window["-SPACER-"].update(shown)
        window["-PARAM1-"].update(f"GC content: {gc_content:.2f}%")
        window["-PARAM2-"].update(f"A: {A}   T: {T}   G: {G}   C: {C}")
        window["-COPY-"].update(disabled=False)
        window["-ERROR-"].update("Completed!", text_color="darkgreen")

    if event == "-MARKS-" and last_spacer:
        window["-SPACER-"].update(f"5' {last_spacer} 3'" if values["-MARKS-"] else last_spacer)

    if event == "-COPY-" and last_spacer:
        sg.clipboard_set(last_spacer if not values["-MARKS-"] else f"5' {last_spacer} 3'")
        sg.popup("Sequence copied to clipboard")

window.close()