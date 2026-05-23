
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from mpl_toolkits.axes_grid1 import make_axes_locatable

def makeAxes(Lranges, single_figure=True):
    nAxes = len(Lranges)
    if single_figure:
        f = plt.figure(figsize=(10, 3 * nAxes)) # Dynamic height
        for idx in range(nAxes):
            ax = f.add_subplot(nAxes, 1, idx + 1)
            yield f, ax
    else:
        for idx in range(nAxes):
            f = plt.figure(figsize=(10, 5))
            ax = f.add_subplot(1, 1, 1)
            yield f, ax


# ==============================================================
# Modelsize vs efficiency for a give learnability range
# ==============================================================
def plotModelCapacity(result_df, Lranges, single_figure=True):
    figures = []
    
    # Use the generator
    for (f, ax), (idx, item) in zip(makeAxes(Lranges, single_figure), enumerate(Lranges)):
        if f not in figures:
            figures.append(f)
            
        L_low, L_high, label = item[0], item[1], item[2]
        color = item[3] if len(item) > 3 else 'blue'
        
        # Explicit check for None to allow 0.0 as a valid bound
        L_min = L_low if L_low is not None else result_df["L_true"].min()
        L_max = L_high if L_high is not None else result_df["L_true"].max()
        
        # Filter data
        mask = (result_df["L_true"] >= L_min) & (result_df["L_true"] < L_max)
        subset_df = result_df.loc[mask]
        
        if subset_df.empty:
            print(f"Warning: No data for range {label} ({L_min} to {L_max})")
            continue

        groups = subset_df.groupby("hidden_layer_width")
        f1_data = groups["f1"].mean()
        eff_data = groups["efficiency"].mean()
        eff_data_raw = groups["efficiency_raw"].mean()
        
        # Explicitly pass x (the index) and y to avoid plotting errors
        ax.plot(f1_data.index, f1_data.values, color=color, marker="x", 
                linestyle="dashed", label=f"{label} - F1", markersize=4)

        ax.plot(eff_data.index, eff_data.values, color=color, marker="o", 
                label=f"{label} - Efficiency (Calibrated)", markersize=4)

        ax.plot(eff_data_raw.index, eff_data_raw.values, color=color, marker="o", 
                linestyle="dotted", label=f"{label} - Efficiency (Uncalibrated)", markersize=4)


        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_ylabel("Metric Value")
        ax.set_ylim(-0.05, 1.05) # Padding for visibility

        ymax = ax.get_ylim()[1]
        ax.axhspan(
            0.95,
            ymax,
            facecolor="green",
            alpha=0.10,
            zorder=0,
        )        
                
        if single_figure:
            if idx == 0:
                ax.set_title("Accuracy remains stable while calibrated efficiency degrades with model size (low-signal regime)")
            if idx == len(Lranges) - 1:
                ax.set_xlabel("Model Size")
            ax.legend(loc='upper right', fontsize='x-small')
        else:
            ax.set_title("Accuracy remains stable while calibrated efficiency degrades with model size (low-signal regime)")
            # ax.set_title(f"Capacity: {label} (L_true {L_min}-{L_max})")
            ax.set_xlabel("Model Size")
            ax.legend()

    for f in figures:
        f.tight_layout()
        
    return figures


# ==============================================
# Average learnability over a range
# ==============================================
def getDataLearnabilitySmooth(result_df, Lmin, Lmax, layer_width):
    df2 = result_df[result_df["L_true"].apply(lambda x: x>=Lmin and x<Lmax)]
    df2 = df2[df2["hidden_layer_width"].apply(lambda x: x==layer_width)]
    if df2.shape[0] == 0 : return None
    L_mean          = df2["L_true"].mean()
    eff_mean        = df2["efficiency"].mean()
    f1_mean         = df2["f1"].mean()
    eff_raw_mean    = df2["efficiency_raw"].mean()

    return (L_mean, eff_mean, eff_raw_mean, f1_mean)


# ============================================
# Plot score vs capacity.
# Boring plot
# ============================================
def plotDataLearnability(result_df, width_range, boldwidth_range):
    # input_dim	out_classes	num_hidden_layers	hidden_layer_width	dropout	activation	dataset	L_true	model_score	nll	efficiency	f1
    # hidden_layer_width = [32  48  64  80  96 112 128 144 160 176 192 208 224 240 256 272 288 304 320 336 352 368 384 400 416 432 448 464 480 496]
    f = plt.figure(figsize=(10,6))
    ax_eff     = f.add_subplot(3,1,1)
    ax_eff_raw = f.add_subplot(3,1,2)
    ax_f1      = f.add_subplot(3,1,3)

    df = result_df    
    # Break down the learnability range in steps of dL
    L_true_min = df["L_true"].min()
    L_true_max = df["L_true"].max()
    dL         = 0.05
    LRange     = np.arange(L_true_min, L_true_max, dL)
    subranges  = [(round(s, 10), round(min(s + dL, L_true_max), 10)) for s in LRange]

    idx2=0
    for idx, width in enumerate(width_range):
        result_smooth = []
        for Lmin, Lmax in subranges:
            result_smooth_ = getDataLearnabilitySmooth(df, Lmin, Lmax, width)
            result_smooth.append(result_smooth_)

        # Start plotting
        result_smooth_df = pd.DataFrame(result_smooth, columns = ["Learnability", "efficiency", "efficiency_raw", "f1"])
        ax_eff.plot    ( result_smooth_df["Learnability"], result_smooth_df["efficiency"]      , color = f"0.8", marker="o",     markersize=3, linewidth=0.5 )
        ax_eff_raw.plot( result_smooth_df["Learnability"], result_smooth_df["efficiency_raw"]  , color = f"0.8", marker="o",     markersize=3, linewidth=0.5 )
        ax_f1.plot     ( result_smooth_df["Learnability"], result_smooth_df["f1"]              , color = f"0.8", marker="o", linestyle="dashed",markersize=3 )

        if width in boldwidth_range:
            ax_eff.plot    ( result_smooth_df["Learnability"], result_smooth_df["efficiency"]    , color = f"C{idx2+1}", marker="o",     markersize=4, label=f"size={width}")
            ax_eff_raw.plot( result_smooth_df["Learnability"], result_smooth_df["efficiency_raw"], color = f"C{idx2+1}", marker="o",     markersize=4, label=f"size={width}")
            ax_f1.plot     ( result_smooth_df["Learnability"], result_smooth_df["f1"]            , color = f"C{idx2+1}", marker="o",     markersize=4, label=f"size={width}" )
            idx2=idx2+1

    ax_eff.grid(True)
    ax_eff_raw.grid(True)
    ax_eff.set_ylabel("Efficiency (Calibrated)")
    ax_eff.set_title("Information extraction capability of models")
    ax_eff.legend()
    ax_eff.set_xlim(0,1)
    ax_eff.set_ylim(0,1)

    ax_eff_raw.grid(True)
    ax_eff_raw.grid(True)
    ax_eff_raw.set_ylabel("Efficiency (Uncalibrated)")
    ax_eff_raw.legend()
    ax_eff_raw.set_xlim(0,1)
    ax_eff_raw.set_ylim(0,1)

    ax_f1.grid(True)
    ax_f1.set_xlabel("Learnability")
    ax_f1.set_ylabel("F1 score behavior")
    ax_f1.legend()
    ax_f1.set_xlim(0,1)
    ax_f1.set_ylim(0,1)

    f.tight_layout()
    return [f]            




# # ============================================
# # Scatter: Learnability vs Efficiency
# # color = hidden_layer_width
# # ============================================
def plotScatter(
    result_df,
    y="efficiency",
    dL=0.1,
    target_eff=0.95,
    ax=None,
    plot_inset=False,
    inset_bounds=(0.58, 0.08, 0.36, 0.36),  # x0, y0, w, h in parent-axis coords
):
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import matplotlib.patheffects as pe

    df = result_df.copy()

    cols_needed = ["L_true", y, "hidden_layer_width"]
    df = df.dropna(subset=cols_needed)
    df = df[(df[y] >= 0.0) & (df[y] <= 1.05)]

    figlist = []

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 7), constrained_layout=False)
        figlist.append(fig)
    else:
        fig = ax.figure

    # -------------------------------------------------
    # If inset requested, create inset INSIDE incoming ax
    # -------------------------------------------------
    is_inset = plot_inset
    if is_inset:
        parent_ax = ax
        ax = parent_ax.inset_axes(inset_bounds)
        ax.set_zorder(10)

    # -------------------------------------------------
    # Color normalization
    # -------------------------------------------------
    widths = df["hidden_layer_width"].values
    norm = mcolors.LogNorm(vmin=max(np.min(widths), 1), vmax=np.max(widths))
    cmap = plt.cm.plasma

    # -------------------------------------------------
    # Shaded desired operating region FIRST
    # -------------------------------------------------
    ax.axhspan(
        target_eff,
        1.05,
        facecolor="green",
        alpha=0.10,
        zorder=0,
    )

    # -------------------------------------------------
    # Scatter
    # -------------------------------------------------
    sc = ax.scatter(
        df["L_true"],
        df[y],
        c=df["hidden_layer_width"],
        cmap=cmap,
        norm=norm,
        s=10 if is_inset else 15,
        alpha=0.75,
        edgecolors="none",
        zorder=2,
    )

    # -------------------------------------------------
    # Vertical bin lines
    # -------------------------------------------------
    xmin = df["L_true"].min()
    xmax = min(1.0, df["L_true"].max())
    xgrid = np.arange(np.floor(xmin / dL) * dL, xmax + dL, dL)

    for x in xgrid:
        ax.axvline(
            x=x,
            linestyle="--",
            linewidth=0.7 if is_inset else 1.0,
            color="black",
            alpha=0.35,
            zorder=1,
        )

    # -------------------------------------------------
    # Target line
    # -------------------------------------------------
    ax.axhline(
        y=target_eff,
        linestyle="--",
        linewidth=1.1 if is_inset else 2.0,
        color="black",
        alpha=0.8,
        label=f"Target = {target_eff:.2f}",
        zorder=3,
    )

    # -------------------------------------------------
    # Limits
    # -------------------------------------------------
    ax.set_xlim(max(0.0, xmin - 0.02), min(1.0, xmax + 0.02))
    ax.set_ylim(0.05, 1.05)

    # -------------------------------------------------
    # Desired-region label
    # -------------------------------------------------
    if not is_inset:
        ax.text(
            0.03,
            1.02,
            "Desired operating region",
            ha="left",
            va="center",
            fontsize=11,
            color="red",
            alpha=0.9,
            fontweight="bold",
        )
    else:
        ax.text(
            0.04,
            1.02,
            "Desired region",
            ha="left",
            va="center",
            fontsize=6,
            color="red",
            alpha=0.9,
            fontweight="bold",
        )

    # -------------------------------------------------
    # Labels / title
    # -------------------------------------------------
    if is_inset:
        ax.set_title(f"{y.upper()} scatter", fontsize=8)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(labelsize=6)
    else:
        # ax.set_title("Learnability vs Efficiency (color = model width)")
        ax.set_title(fr"Low accuracy $\neq$ low efficiency")

        ax.set_xlabel("Learnability (L_true)")
        ax.set_ylabel(y)
        ax.tick_params(labelsize=8)

    # -------------------------------------------------
    # Colorbar ONLY for main plot
    # Explicit cbar axis avoids layout corruption.
    # -------------------------------------------------
    if not is_inset:
        bbox = ax.get_position()
        cax = fig.add_axes([
            bbox.x1 + 0.015,
            bbox.y0,
            0.025,
            bbox.height,
        ])

        cbar = fig.colorbar(sc, cax=cax)
        cbar.set_label("MLP Layer Width")
        cbar.ax.tick_params(labelsize=8)

        ax.legend(loc="lower right")

    # -------------------------------------------------
    # Styling
    # -------------------------------------------------
    ax.set_facecolor("white")

    for spine in ax.spines.values():
        spine.set_edgecolor("gray")
        spine.set_linewidth(1.0)

    if is_inset:
        ax.patch.set_path_effects([
            pe.SimplePatchShadow(offset=(3, -3), alpha=0.18),
            pe.Normal()
        ])

    ax.grid(False)

    return figlist, ax


# ============================================
# Save figures in PDF
# ============================================
def save(args, figlist):
    outdir = os.path.dirname(args.xl)
    outfile= os.path.join(outdir, "report.pdf")

    # Open the PDF file
    with PdfPages(outfile) as pdf:
        for fig in figlist:
            pdf.savefig(fig, bbox_inches='tight')

    print(f"Saved figures in {outfile}")

# =====================================
# Test harness
# =====================================
if __name__ == "__main__":
    import argparse
    def loadArgs():
        ap = argparse.ArgumentParser()
        ap.add_argument(
            "--xl", 
            type=str, 
            required=True, 
            help = f"Location of results.xlsx"
        )
        return  ap.parse_args()

    args = loadArgs()
    df = pd.read_excel(args.xl)
    df = df[df["efficiency"].apply(lambda x: x<=1)]

    Lrange =    [
                    (0.0, 0.2, "Low learnability"   , "orange"),
                    (0.3, 0.5, "Medium learnability", "green"),
                    (0.8, 1.0, "High learnability",   "blue"),
                ]
    figures = []
    figures = figures + plotModelCapacity(df, Lrange, single_figure = True)

    figures = figures + plotModelCapacity(df, Lrange, single_figure = False)


    flist, ax = plotScatter(df, y = "efficiency",  dL=0.05, target_eff=0.95, ax=None)
    figures = figures + flist

    flist, ax = plotScatter(df, y = "f1",  dL=0.05, target_eff=0.95, ax=ax, plot_inset=True)
    figures = figures + flist

    flist, ax = plotScatter(df, y = "f1",  dL=0.05, target_eff=0.95)
    figures = figures + flist


    save(args, figures)
    # plt.show()

