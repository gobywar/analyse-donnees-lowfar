import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table


# -------------------
# Config
# -------------------

st.set_page_config(
    page_title="LOFAR RM Histograms",
    page_icon="🌍"
)

# -------------------
# Data loading
# -------------------

# @st.cache_data
# def load_data():

#     with fits.open("./DR3_RMGrid_v1.0.fits") as f:
#         table = Table(f[1].data)

#     RM = table["RM"][:-1].data
#     GLAT = table["glat_pol"][:-1].data

#     idx = np.arange(len(RM))

#     return RM, GLAT, idx


# -------------------
# Sidebar controls
# -------------------

with st.sidebar:

    st.header("Parameters")

    latitude = st.slider(
        "Latitude cut",
        0,
        80,
        0
    )

    bins = st.slider(
        "Bins",
        20,
        300,
        100
    )

    xmax = st.slider(
        "x range",
        10,
        500,
        200
    )

    exclusion = st.slider(
        "Exclusion interval",
        -10.0,
        10.0,
        (-3.0, 1.5)
    )

    inclusion = st.slider(
        "Inclusion interval",
        -300.0,
        300.0,
        (-120.0, 120.0)
    )

    ymax = st.slider(
        "y max",
        50,
        1000,
        300
    )


# -------------------
# Plot
# -------------------

with fits.open("./DR3_RMGrid_v1.0.fits") as f:
    table = Table(f[1].data)

RM = table["RM"][:-1].data
GLAT = table["glat_pol"][:-1].data

idx = np.arange(len(RM))

mask_lat = (GLAT >= latitude) | (GLAT <= -latitude)

RM_lat = RM[mask_lat]
idx_lat = idx[mask_lat]

mask_exclusion = (RM_lat <= exclusion[0]) | (RM_lat >= exclusion[1])
mask_inclusion = (RM_lat >= inclusion[0]) & (RM_lat <= inclusion[1])
final_mask = mask_exclusion & mask_inclusion

RM_excluded_low = RM_lat[~mask_exclusion]
idx_excluded_low = idx_lat[~mask_exclusion]
excluded_low__table = table[idx_excluded_low]
excluded_low__table.write("excluded_low.fits", overwrite=True)


RM_excluded_high = RM_lat[~mask_inclusion]
idx_excluded_high = idx_lat[~mask_inclusion]
excluded_high__table = table[idx_excluded_low]
excluded_high__table.write("excluded_high.fits", overwrite=True)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Low RM exclusion")
        st.metric(
            label="Sources à faible RM exclues ",
            value=len(RM_excluded_low),
            delta=f"{len(RM_excluded_low)/len(RM_lat):.1%}"
        )
        with open("excluded_low.fits", "rb") as f:
            st.download_button("Download FITS file of low RM excluded sources", f, file_name="excluded_low.fits")

    with col2:
        st.subheader("High RM exclusion")
        st.metric(
            label="Sources à fort RM exclues ",
            value=len(RM_excluded_high),
            delta=f"{len(RM_excluded_high)/len(RM_lat):.1%}"
        )
        with open("excluded_high.fits", "rb") as f:
            st.download_button("Download FITS file of high RM excluded sources", f, file_name="excluded_high.fits")




RM_final = RM_lat[final_mask]
idx_final = idx_lat[final_mask]


fig, ax = plt.subplots(figsize=(8, 6))

ax.hist(
    RM_final,
    bins=bins,
    density = True
)

ax.axvline(
    exclusion[0],
    linestyle="--"
)

ax.axvline(
    exclusion[1],
    linestyle="--"
)

ax.set_xlim(-xmax, xmax)
ax.set_ylim(0, ymax)

ax.set_xlabel("RM")
ax.set_ylabel("Count")

st.pyplot(fig)

st.metric(
    "Selected sources",
    len(RM_final)
)
