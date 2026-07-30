import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md(
        r"""
        # FFOLayer reproduction: evidence first

        | Result | Reproduced evidence |
        | --- | --- |
        | Final loss, FFOLayer − LPGD | 95% CI `[-0.000874, 0.001898]` |
        | Clean-run complete runtime | log-ratio CI `[0.0301, 0.3364]` |
        | Independent rerun complete runtime | log-ratio CI `[-1.3542, 0.8221]` |
        | Verdict on “consistently outperforms LPGD” | **BLOCKED** |

        Both runs converge to matched held-out decision loss. Their decisive
        runtime directions disagree, so selecting only the clean falsification
        run would be post-hoc evidence selection.
        """
    )
    return (mo,)


@app.cell
def _(mo):
    seed = mo.ui.slider(1, 5, value=1, label="Paired seed")
    seed
    return (seed,)


@app.cell
def _(mo, seed):
    ffo_seconds = [482.978, 433.108, 366.244, 409.158, 365.154]
    lpgd_seconds = [405.877, 494.556, 312.713, 309.241, 2230.444]
    index = seed.value - 1
    ratio = ffo_seconds[index] / lpgd_seconds[index]
    mo.md(
        f"""
        For seed **{seed.value}**, FFOLayer took **{ffo_seconds[index]:.1f}s**
        and LPGD took **{lpgd_seconds[index]:.1f}s**: a ratio of
        **{ratio:.3f}×**.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Why this tests the paper's claim

    The comparison uses the released 2,000-sample generator,
    `input_dim=640`, the smallest `y_dim=200` reported in Figure 5,
    batch size 8, Adam at 0.001, five epochs (1,000 updates), FFOLayer
    tolerance `1e-6`, and actual LPGD at the appendix-required `1e-12`.
    Execution order alternates by seed.

    A favorable result at one dimension could only corroborate the broad
    word “consistently.” A stable contradiction could falsify it, but the
    complete independent rerun did not preserve the runtime direction.

    ## Other claims

    Claims 1, 2, 3, and 5 are verified. Claim 4's “substantially faster
    backward” conjunct is also falsified by an eight-seed, paper-dimensional
    qpth comparison. See the repository report for every contract, control,
    raw-data link, and limitation.
    """)
    return


if __name__ == "__main__":
    app.run()
