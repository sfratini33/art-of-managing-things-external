"""Interactive questionnaire for the Jupyter notebook."""

from __future__ import annotations

from pathlib import Path

import ipywidgets as W
from IPython.display import display

from .examples import EXAMPLES_DIR
from .io_data import load_bytes, load_file, parse_list, sample_from_summary, sample_from_values
from .report import format_report
from .spec import StudySpec
from .tests import run_test


def analyze(spec: StudySpec, sample_a, sample_b=None) -> str:
    result = run_test(spec, sample_a, sample_b)
    return format_report(result, spec)


def show_chooser():
    """Display the Section 5 questionnaire in a Jupyter notebook."""
    parameter = W.Dropdown(
        options=[
            ("One mean", "one_mean"),
            ("Two means", "two_means"),
            ("One proportion", "one_proportion"),
            ("Two proportions", "two_proportions"),
        ],
        description="Parameter:",
        style={"description_width": "160px"},
        layout=W.Layout(width="480px"),
    )
    paired = W.Dropdown(
        options=[("Independent samples", False), ("Paired / matched", True)],
        description="Pairing:",
        style={"description_width": "160px"},
        layout=W.Layout(width="480px"),
    )
    sigma_known = W.Dropdown(
        options=[("Unknown (use s)", False), ("Known (use σ)", True)],
        description="Population SD:",
        style={"description_width": "160px"},
        layout=W.Layout(width="480px"),
    )
    sigma = W.FloatText(value=1.0, description="σ:", style={"description_width": "160px"})
    equal_var = W.Dropdown(
        options=[("Assume equal variances (pooled t)", True), ("Do not assume equal (Welch t)", False)],
        description="Variances:",
        style={"description_width": "160px"},
        layout=W.Layout(width="520px"),
    )
    large_z = W.Checkbox(
        value=False,
        description="If n > 30 and σ is unknown, use the book's large-sample z approximation",
        indent=False,
    )
    alternative = W.Dropdown(
        options=[
            ("Two-sided (≠)", "two-sided"),
            ("Upper-tailed (>)", "greater"),
            ("Lower-tailed (<)", "less"),
        ],
        description="Alternative:",
        style={"description_width": "160px"},
        layout=W.Layout(width="480px"),
    )
    hypothesized = W.FloatText(
        value=0.0,
        description="H0 value:",
        style={"description_width": "160px"},
    )
    alpha = W.FloatText(value=0.05, description="α:", style={"description_width": "160px"})
    design = W.Dropdown(
        options=[("Observational study", False), ("Designed experiment", True)],
        description="How collected:",
        style={"description_width": "160px"},
        layout=W.Layout(width="480px"),
    )
    data_mode = W.Dropdown(
        options=[
            ("Type summaries (n, mean, s or successes)", "summary"),
            ("Paste a list of numbers", "paste"),
            ("Load a CSV or Excel file", "file"),
        ],
        description="Data entry:",
        style={"description_width": "160px"},
        layout=W.Layout(width="520px"),
    )
    name_a = W.Text(value="Sample A", description="Name A:", style={"description_width": "160px"})
    name_b = W.Text(value="Sample B", description="Name B:", style={"description_width": "160px"})
    n_a = W.IntText(value=30, description="n A:", style={"description_width": "160px"})
    mean_a = W.FloatText(value=0.0, description="mean A:", style={"description_width": "160px"})
    sd_a = W.FloatText(value=1.0, description="s A:", style={"description_width": "160px"})
    succ_a = W.IntText(value=0, description="successes A:", style={"description_width": "160px"})
    n_b = W.IntText(value=30, description="n B:", style={"description_width": "160px"})
    mean_b = W.FloatText(value=0.0, description="mean B:", style={"description_width": "160px"})
    sd_b = W.FloatText(value=1.0, description="s B:", style={"description_width": "160px"})
    succ_b = W.IntText(value=0, description="successes B:", style={"description_width": "160px"})
    paste_a = W.Textarea(
        placeholder="Numbers separated by commas, spaces, or new lines",
        layout=W.Layout(width="90%", height="80px"),
    )
    paste_b = W.Textarea(
        placeholder="Second sample, if needed",
        layout=W.Layout(width="90%", height="80px"),
    )
    file_path = W.Text(
        value=str(EXAMPLES_DIR / "batteries.csv"),
        description="File path:",
        style={"description_width": "160px"},
        layout=W.Layout(width="90%"),
    )
    upload = W.FileUpload(accept=".csv,.xlsx,.xls,.txt", multiple=False)
    run_btn = W.Button(description="Choose and run the test", button_style="primary")
    status = W.HTML()
    out = W.Output()

    two_box = W.VBox([paired, equal_var, name_b])
    mean_box = W.VBox([sigma_known, sigma, large_z])
    summary_a = W.HBox([n_a, mean_a, sd_a, succ_a])
    summary_b = W.HBox([n_b, mean_b, sd_b, succ_b])
    paste_box = W.VBox([W.HTML("<b>Pasted lists</b>"), paste_a, paste_b])
    file_box = W.VBox(
        [
            W.HTML("<b>File</b> — one sample per column, optional header. Or upload below."),
            file_path,
            upload,
        ]
    )
    summary_box = W.VBox(
        [
            W.HTML("<b>Summaries</b> — for a proportion, fill n and successes; mean and s can be left as they are."),
            summary_a,
            summary_b,
        ]
    )

    def _needs_two() -> bool:
        return parameter.value in {"two_means", "two_proportions"}

    def _refresh(_=None):
        two_box.layout.display = None if parameter.value == "two_means" else "none"
        mean_box.layout.display = None if parameter.value == "one_mean" else "none"
        sigma.layout.display = None if sigma_known.value else "none"
        equal_var.layout.display = None if (parameter.value == "two_means" and not paired.value) else "none"
        summary_b.layout.display = None if _needs_two() else "none"
        paste_b.layout.display = None if _needs_two() else "none"
        name_b.layout.display = None if _needs_two() else "none"
        mode = data_mode.value
        summary_box.layout.display = None if mode == "summary" else "none"
        paste_box.layout.display = None if mode == "paste" else "none"
        file_box.layout.display = None if mode == "file" else "none"

    for w in (parameter, paired, sigma_known, data_mode):
        w.observe(_refresh, names="value")

    def _on_run(_):
        out.clear_output()
        status.value = ""
        try:
            spec = StudySpec(
                parameter=parameter.value,
                alternative=alternative.value,
                hypothesized=float(hypothesized.value),
                alpha=float(alpha.value),
                designed_experiment=bool(design.value),
                paired=bool(paired.value),
                sigma_known=bool(sigma_known.value),
                sigma=float(sigma.value) if sigma_known.value else None,
                equal_variances=bool(equal_var.value),
                large_sample_z=bool(large_z.value),
                sample_a_name=name_a.value or "Sample A",
                sample_b_name=name_b.value or "Sample B",
            )
            sample_a = sample_b = None
            if data_mode.value == "summary":
                if spec.parameter in {"one_proportion", "two_proportions"}:
                    sample_a = sample_from_summary(spec.sample_a_name, int(n_a.value), successes=int(succ_a.value))
                    if _needs_two():
                        sample_b = sample_from_summary(spec.sample_b_name, int(n_b.value), successes=int(succ_b.value))
                else:
                    sample_a = sample_from_summary(
                        spec.sample_a_name, int(n_a.value), mean=float(mean_a.value), sd=float(sd_a.value)
                    )
                    if _needs_two():
                        sample_b = sample_from_summary(
                            spec.sample_b_name, int(n_b.value), mean=float(mean_b.value), sd=float(sd_b.value)
                        )
            elif data_mode.value == "paste":
                sample_a = sample_from_values(spec.sample_a_name, parse_list(paste_a.value))
                if _needs_two():
                    sample_b = sample_from_values(spec.sample_b_name, parse_list(paste_b.value))
            else:
                samples = None
                if upload.value:
                    uploaded = upload.value
                    if isinstance(uploaded, dict):
                        item = next(iter(uploaded.values()))
                        fname = item.get("metadata", {}).get("name", "upload.csv")
                        content = item["content"]
                    else:
                        rec = uploaded[0]
                        fname = rec.name
                        content = rec.content
                    samples = load_bytes(bytes(content), fname)
                else:
                    samples = load_file(Path(file_path.value))
                if not samples:
                    raise ValueError("No numeric columns were found in the file.")
                sample_a = samples[0]
                sample_a.name = spec.sample_a_name
                if _needs_two():
                    if len(samples) < 2:
                        raise ValueError("A two-sample test needs two numeric columns.")
                    sample_b = samples[1]
                    sample_b.name = spec.sample_b_name
            text = analyze(spec, sample_a, sample_b)
            with out:
                print(text)
        except Exception as exc:
            status.value = f"<p style='color:#b00020'><b>{type(exc).__name__}:</b> {exc}</p>"

    run_btn.on_click(_on_run)
    _refresh()
    form = W.VBox(
        [
            W.HTML("<h3>Section 5 questionnaire</h3><p>Answer the questions, then supply the data. You do not write any code.</p>"),
            parameter,
            two_box,
            mean_box,
            alternative,
            hypothesized,
            alpha,
            design,
            name_a,
            name_b,
            data_mode,
            summary_box,
            paste_box,
            file_box,
            run_btn,
            status,
            out,
        ]
    )
    display(form)
