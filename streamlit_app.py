from numpy._core.numerictypes import int16
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

# Data selection

def selection(ech1,ech2,exclusion_interval,inclusion_interval):
    a,b=exclusion_interval
    c,d=inclusion_interval
    somme=ech1+ech2
    sl=((c<=somme)&(somme<=a)) | ((b<=somme)&(somme<=d))
    return (ech1[sl],ech2[sl])

def histUpper(data,bins,density):
    counts, bins = np.histogram(data, bins=bins, density=density)
    return counts.max()
# -------------------
# Sidebar controls
# -------------------

with st.sidebar:

    st.header("Parameters")

    latitude = st.slider(
        "Latitude cut",
        0,
        80,
        0,
        key="latitude_cut"
    )

    bins = st.slider(
        "Bins",
        20,
        300,
        100,
        key="bins"
    )

    xmax = st.slider(
        "x range",
        10,
        500,
        200,
        key="xmax"
    )

    exclusion = st.slider(
        "Exclusion interval",
        -10.0,
        10.0,
        (-3.0, 1.5),
        key="exclusion"
    )

    inclusion = st.slider(
        "Inclusion interval",
        -300.0,
        300.0,
        (-120.0, 120.0),
        key="inclusion"
    )

    xrange = st.slider(
        "x range in 2nd plot",
        50,
        1000,
        100,
        key="xrange"
    )

    yrange = st.slider(
        "y range in 2nd plot",
        50,
        1000,
        60,
        key="yrange"
    )
# -------------------
# Plot
# -------------------

with fits.open("./DR3_RMGrid_v1.0.fits") as f:
    table = Table(f[1].data)

RM = table["RM"][:-1].data
GRM = table["RRM2022"][:-1].data
RRM = table["GRM2022"][:-1].data
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
excluded_high__table = table[idx_excluded_high]
excluded_high__table.write("excluded_high.fits", overwrite=True)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Low RM exclusion")
        st.metric(
            label = "",
            value=len(RM_excluded_low),
            delta=f"{len(RM_excluded_low)/len(RM_lat):.1%}"
        )
        with open("excluded_low.fits", "rb") as f:
            st.download_button("Download FITS file of low RM excluded sources", f, file_name="excluded_low.fits",key="download_low")

    with col2:
        st.subheader("High RM exclusion")
        st.metric(
            label = "",
            value=len(RM_excluded_high),
            delta=f"{len(RM_excluded_high)/len(RM_lat):.1%}"
        )
        with open("excluded_high.fits", "rb") as f:
            st.download_button("Download FITS file of high RM excluded sources", f, file_name="excluded_high.fits",key="download_high")




RM_final = RM_lat[final_mask]
idx_final = idx_lat[final_mask]

density = st.sidebar.checkbox("Normalize (density)", value=False)
fig, ax = plt.subplots(figsize=(8, 6))



counts, _, _ = ax.hist(
    RM_final,
    bins=bins,
    density = density
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
ax.set_ylim(0, np.nanmax(counts) *1.1)

ax.set_xlabel("RM")
ax.set_ylabel("Count")

st.pyplot(fig)

st.metric(
    "Selected sources",
    len(RM_final)
)

# Figure triangle
#
GRMs = GRM[idx_final]
RRMs = RRM[idx_final]
a,b = exclusion
c,d = inclusion
plt.style.use('default')
fontsize=12
labelsize=14
ticksize=5
x=np.linspace(-xmax,xmax,240)
# bins=100
fig, axs = plt.subplots(2,2, figsize=(13,11))
axs[0,1].set_visible(False)

#ax.set_title("GRM measures")
ax=axs[0,0]
counts, _, _ =ax.hist(GRMs,bins=bins,color='blue')#,label='13h field')
ax.set_ylabel('Number', fontsize=fontsize)
ax.tick_params(axis="y",direction="in",labelsize=labelsize,size=ticksize)

ax.set_ylim(0,np.nanmax(counts) * 1.1)
ax_right_ticks=ax.twinx()
ax_right_ticks.set_ylim(ax.get_ylim())
ax_right_ticks.set_xticks(ax.get_xticks())
ax_right_ticks.tick_params(axis="y",direction="in",size=5)
ax_right_ticks.set_yticklabels([])

#ax.set_xlabel('', fontsize=fontsize)
ax.set_xlim(-xrange,xrange)
xticks=np.linspace(-xrange, xrange, 6)
ax.set_xticks(xticks)
ax.tick_params(axis="x",direction="out",labelsize=labelsize,size=ticksize)
ax_top_ticks=ax.twiny()
ax_top_ticks.set_xlim(ax.get_xlim())
ax_top_ticks.set_xticks(ax.get_xticks())
ax_top_ticks.tick_params(axis="x",direction="in",size=5)
ax_top_ticks.set_xticklabels([])
ax.legend()

#ax.set_title("GRM vs RRM")
ax=axs[1,0]
ax.scatter(GRMs,RRMs,c='blue',marker='.',s=10, alpha=1) #,label='13h field')
ax.set_xlim((-xrange,xrange))
ax.set_ylim((-yrange,yrange))
ax.plot(x,a-0.1-x,color='grey',linestyle='dashed',alpha=1)
ax.plot(x,b+0.1-x,color='grey',linestyle='dashed',alpha=1)
ax.plot(x,d-x,color='grey',linestyle='dashed',alpha=1)
ax.plot(x,c-x,color='grey',linestyle='dashed',alpha=1)

ax.fill_between(x,  a-0.1-x,b+0.1-x,color='grey', alpha=0.2)
ax.fill_between(x, -yrange-x, c-x,color='grey', alpha=0.2)
ax.fill_between(x, d-x, yrange-x,color='grey', alpha=0.2)

ax.set_ylabel('RRM (rad m$^{-2}$)', fontsize=fontsize)
ax.tick_params(axis="y",direction="in",labelsize=labelsize,size=ticksize)
ax_right_ticks=ax.twinx()
ax_right_ticks.set_ylim(ax.get_ylim())
ax_right_ticks.set_xticks(ax.get_xticks())
ax_right_ticks.tick_params(axis="y",direction="in",size=ticksize)
ax_right_ticks.set_yticklabels([])

ax.set_xlabel('GRM (rad m$^{-2}$)', fontsize=fontsize)
# ax.set_xlim(-40,40)
# xticks=np.linspace(-100, 100, 5)
ax.set_xticks(xticks)
ax.tick_params(axis="x",direction="out",labelsize=labelsize,size=ticksize)
ax.xaxis.set_ticks_position('both')
ax.tick_params(axis="x",direction="in",size=5)
ax.yaxis.set_ticks_position('both')
ax.tick_params(axis="y",direction="in",size=5)
ax.legend()

ax=axs[1,1]
#ax.set_title("RRM measures")
counts, _, _ = ax.hist(RRMs,bins=bins,color='blue', orientation='horizontal') #,label='13h field'


ax.tick_params(axis="y",direction="out",labelsize=labelsize,size=ticksize)
ax.set_ylim(-yrange,yrange)
ax_right_ticks=ax.twinx()
ax_right_ticks.set_ylim(ax.get_ylim())
ax_right_ticks.set_xticks(ax.get_xticks())
ax_right_ticks.tick_params(axis="y",direction="in",size=5)
ax_right_ticks.set_yticklabels([])

ax.set_xlim(0,np.nanmax(counts) * 1.1)
xticks=np.linspace(0, np.nanmax(counts), 8).astype(int16)
ax.set_xticks(xticks)

ax.set_xlabel('Number', fontsize=fontsize)
ax.tick_params(axis="x",direction="in",labelsize=labelsize,size=ticksize)
ax_top_ticks=ax.twiny()
ax_top_ticks.set_xlim(ax.get_xlim())
ax_top_ticks.set_xticks(ax.get_xticks())
ax_top_ticks.tick_params(axis="x",direction="in",size=5)
ax_top_ticks.set_xticklabels([])
ax.legend()
# left, center, right = st.columns([1, 8, 1])
# with center:
#     st.pyplot(fig, use_container_width=True)
#
st.pyplot(fig, use_container_width=False)
from numpy._core.numerictypes import int16
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

# Data selection

def selection(ech1,ech2,exclusion_interval,inclusion_interval):
    a,b=exclusion_interval
    c,d=inclusion_interval
    somme=ech1+ech2
    sl=((c<=somme)&(somme<=a)) | ((b<=somme)&(somme<=d))
    return (ech1[sl],ech2[sl])

def histUpper(data,bins,density):
    counts, bins = np.histogram(data, bins=bins, density=density)
    return counts.max()
# -------------------
# Sidebar controls
# -------------------

with st.sidebar:

    st.header("Parameters")

    latitude = st.slider(
        "Latitude cut",
        0,
        80,
        0,
        key="latitude_cut"
    )

    bins = st.slider(
        "Bins",
        20,
        300,
        100,
        key="bins"
    )

    xmax = st.slider(
        "x range",
        10,
        500,
        200,
        key="xmax"
    )

    exclusion = st.slider(
        "Exclusion interval",
        -10.0,
        10.0,
        (-3.0, 1.5),
        key="exclusion"
    )

    inclusion = st.slider(
        "Inclusion interval",
        -300.0,
        300.0,
        (-120.0, 120.0),
        key="inclusion"
    )

    xrange = st.slider(
        "x range in 2nd plot",
        50,
        1000,
        100,
        key="xrange"
    )

    yrange = st.slider(
        "y range in 2nd plot",
        50,
        1000,
        60,
        key="yrange"
    )
# -------------------
# Plot
# -------------------

with fits.open("./DR3_RMGrid_v1.0.fits") as f:
    table = Table(f[1].data)

RM = table["RM"][:-1].data
GRM = table["RRM2022"][:-1].data
RRM = table["GRM2022"][:-1].data
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
excluded_high__table = table[idx_excluded_high]
excluded_high__table.write("excluded_high.fits", overwrite=True)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Low RM exclusion")
        st.metric(
            label = "",
            value=len(RM_excluded_low),
            delta=f"{len(RM_excluded_low)/len(RM_lat):.1%}"
        )
        with open("excluded_low.fits", "rb") as f:
            st.download_button("Download FITS file of low RM excluded sources", f, file_name="excluded_low.fits")

    with col2:
        st.subheader("High RM exclusion")
        st.metric(
            label = "",
            value=len(RM_excluded_high),
            delta=f"{len(RM_excluded_high)/len(RM_lat):.1%}"
        )
        with open("excluded_high.fits", "rb") as f:
            st.download_button("Download FITS file of high RM excluded sources", f, file_name="excluded_high.fits")




RM_final = RM_lat[final_mask]
idx_final = idx_lat[final_mask]

density = st.sidebar.checkbox("Normalize (density)", value=False)
fig, ax = plt.subplots(figsize=(8, 6))



counts, _, _ = ax.hist(
    RM_final,
    bins=bins,
    density = density
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
ax.set_ylim(0, np.nanmax(counts) *1.1)

ax.set_xlabel("RM")
ax.set_ylabel("Count")

st.pyplot(fig)

st.metric(
    "Selected sources",
    len(RM_final)
)

# Figure triangle
#
GRMs = GRM[idx_final]
RRMs = RRM[idx_final]
a,b = exclusion
c,d = inclusion
plt.style.use('default')
fontsize=12
labelsize=14
ticksize=5
x=np.linspace(-xmax,xmax,240)
# bins=100
fig, axs = plt.subplots(2,2, figsize=(13,11))
axs[0,1].set_visible(False)

#ax.set_title("GRM measures")
ax=axs[0,0]
counts, _, _ =ax.hist(GRMs,bins=bins,color='blue')#,label='13h field')
ax.set_ylabel('Number', fontsize=fontsize)
ax.tick_params(axis="y",direction="in",labelsize=labelsize,size=ticksize)

ax.set_ylim(0,np.nanmax(counts) * 1.1)
ax_right_ticks=ax.twinx()
ax_right_ticks.set_ylim(ax.get_ylim())
ax_right_ticks.set_xticks(ax.get_xticks())
ax_right_ticks.tick_params(axis="y",direction="in",size=5)
ax_right_ticks.set_yticklabels([])

#ax.set_xlabel('', fontsize=fontsize)
ax.set_xlim(-xrange,xrange)
xticks=np.linspace(-xrange, xrange, 6)
ax.set_xticks(xticks)
ax.tick_params(axis="x",direction="out",labelsize=labelsize,size=ticksize)
ax_top_ticks=ax.twiny()
ax_top_ticks.set_xlim(ax.get_xlim())
ax_top_ticks.set_xticks(ax.get_xticks())
ax_top_ticks.tick_params(axis="x",direction="in",size=5)
ax_top_ticks.set_xticklabels([])
ax.legend()

#ax.set_title("GRM vs RRM")
ax=axs[1,0]
ax.scatter(GRMs,RRMs,c='blue',marker='.',s=10, alpha=1) #,label='13h field')
ax.set_xlim((-xrange,xrange))
ax.set_ylim((-yrange,yrange))
ax.plot(x,a-0.1-x,color='grey',linestyle='dashed',alpha=1)
ax.plot(x,b+0.1-x,color='grey',linestyle='dashed',alpha=1)
ax.plot(x,d-x,color='grey',linestyle='dashed',alpha=1)
ax.plot(x,c-x,color='grey',linestyle='dashed',alpha=1)

ax.fill_between(x,  a-0.1-x,b+0.1-x,color='grey', alpha=0.2)
ax.fill_between(x, -yrange-x, c-x,color='grey', alpha=0.2)
ax.fill_between(x, d-x, yrange-x,color='grey', alpha=0.2)

ax.set_ylabel('RRM (rad m$^{-2}$)', fontsize=fontsize)
ax.tick_params(axis="y",direction="in",labelsize=labelsize,size=ticksize)
ax_right_ticks=ax.twinx()
ax_right_ticks.set_ylim(ax.get_ylim())
ax_right_ticks.set_xticks(ax.get_xticks())
ax_right_ticks.tick_params(axis="y",direction="in",size=ticksize)
ax_right_ticks.set_yticklabels([])

ax.set_xlabel('GRM (rad m$^{-2}$)', fontsize=fontsize)
# ax.set_xlim(-40,40)
# xticks=np.linspace(-100, 100, 5)
ax.set_xticks(xticks)
ax.tick_params(axis="x",direction="out",labelsize=labelsize,size=ticksize)
ax.xaxis.set_ticks_position('both')
ax.tick_params(axis="x",direction="in",size=5)
ax.yaxis.set_ticks_position('both')
ax.tick_params(axis="y",direction="in",size=5)
ax.legend()

ax=axs[1,1]
#ax.set_title("RRM measures")
counts, _, _ = ax.hist(RRMs,bins=bins,color='blue', orientation='horizontal') #,label='13h field'


ax.tick_params(axis="y",direction="out",labelsize=labelsize,size=ticksize)
ax.set_ylim(-yrange,yrange)
ax_right_ticks=ax.twinx()
ax_right_ticks.set_ylim(ax.get_ylim())
ax_right_ticks.set_xticks(ax.get_xticks())
ax_right_ticks.tick_params(axis="y",direction="in",size=5)
ax_right_ticks.set_yticklabels([])

ax.set_xlim(0,np.nanmax(counts) * 1.1)
xticks=np.linspace(0, np.nanmax(counts), 8).astype(int16)
ax.set_xticks(xticks)

ax.set_xlabel('Number', fontsize=fontsize)
ax.tick_params(axis="x",direction="in",labelsize=labelsize,size=ticksize)
ax_top_ticks=ax.twiny()
ax_top_ticks.set_xlim(ax.get_xlim())
ax_top_ticks.set_xticks(ax.get_xticks())
ax_top_ticks.tick_params(axis="x",direction="in",size=5)
ax_top_ticks.set_xticklabels([])
ax.legend()
# left, center, right = st.columns([1, 8, 1])
# with center:
#     st.pyplot(fig, use_container_width=True)
#
st.pyplot(fig, use_container_width=False)
from numpy._core.numerictypes import int16
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

# Data selection

def selection(ech1,ech2,exclusion_interval,inclusion_interval):
    a,b=exclusion_interval
    c,d=inclusion_interval
    somme=ech1+ech2
    sl=((c<=somme)&(somme<=a)) | ((b<=somme)&(somme<=d))
    return (ech1[sl],ech2[sl])

def histUpper(data,bins,density):
    counts, bins = np.histogram(data, bins=bins, density=density)
    return counts.max()
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

    xrange = st.slider(
        "x range in 2nd plot",
        50,
        1000,
        100
    )

    yrange = st.slider(
        "y range in 2nd plot",
        50,
        1000,
        60
    )
# -------------------
# Plot
# -------------------

with fits.open("./DR3_RMGrid_v1.0.fits") as f:
    table = Table(f[1].data)

RM = table["RM"][:-1].data
GRM = table["RRM2022"][:-1].data
RRM = table["GRM2022"][:-1].data
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
excluded_high__table = table[idx_excluded_high]
excluded_high__table.write("excluded_high.fits", overwrite=True)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Low RM exclusion")
        st.metric(
            label = "",
            value=len(RM_excluded_low),
            delta=f"{len(RM_excluded_low)/len(RM_lat):.1%}"
        )
        with open("excluded_low.fits", "rb") as f:
            st.download_button("Download FITS file of low RM excluded sources", f, file_name="excluded_low.fits")

    with col2:
        st.subheader("High RM exclusion")
        st.metric(
            label = "",
            value=len(RM_excluded_high),
            delta=f"{len(RM_excluded_high)/len(RM_lat):.1%}"
        )
        with open("excluded_high.fits", "rb") as f:
            st.download_button("Download FITS file of high RM excluded sources", f, file_name="excluded_high.fits")




RM_final = RM_lat[final_mask]
idx_final = idx_lat[final_mask]

density = st.sidebar.checkbox("Normalize (density)", value=False)
fig, ax = plt.subplots(figsize=(8, 6))



counts, _, _ = ax.hist(
    RM_final,
    bins=bins,
    density = density
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
ax.set_ylim(0, np.nanmax(counts) *1.1)

ax.set_xlabel("RM")
ax.set_ylabel("Count")

st.pyplot(fig)

st.metric(
    "Selected sources",
    len(RM_final)
)

# Figure triangle
#
GRMs = GRM[idx_final]
RRMs = RRM[idx_final]
a,b = exclusion
c,d = inclusion
plt.style.use('default')
fontsize=12
labelsize=14
ticksize=5
x=np.linspace(-xmax,xmax,240)
# bins=100
fig, axs = plt.subplots(2,2, figsize=(13,11))
axs[0,1].set_visible(False)

#ax.set_title("GRM measures")
ax=axs[0,0]
counts, _, _ =ax.hist(GRMs,bins=bins,color='blue')#,label='13h field')
ax.set_ylabel('Number', fontsize=fontsize)
ax.tick_params(axis="y",direction="in",labelsize=labelsize,size=ticksize)

ax.set_ylim(0,np.nanmax(counts) * 1.1)
ax_right_ticks=ax.twinx()
ax_right_ticks.set_ylim(ax.get_ylim())
ax_right_ticks.set_xticks(ax.get_xticks())
ax_right_ticks.tick_params(axis="y",direction="in",size=5)
ax_right_ticks.set_yticklabels([])

#ax.set_xlabel('', fontsize=fontsize)
ax.set_xlim(-xrange,xrange)
xticks=np.linspace(-xrange, xrange, 6)
ax.set_xticks(xticks)
ax.tick_params(axis="x",direction="out",labelsize=labelsize,size=ticksize)
ax_top_ticks=ax.twiny()
ax_top_ticks.set_xlim(ax.get_xlim())
ax_top_ticks.set_xticks(ax.get_xticks())
ax_top_ticks.tick_params(axis="x",direction="in",size=5)
ax_top_ticks.set_xticklabels([])
ax.legend()

#ax.set_title("GRM vs RRM")
ax=axs[1,0]
ax.scatter(GRMs,RRMs,c='blue',marker='.',s=10, alpha=1) #,label='13h field')
ax.set_xlim((-xrange,xrange))
ax.set_ylim((-yrange,yrange))
ax.plot(x,a-0.1-x,color='grey',linestyle='dashed',alpha=1)
ax.plot(x,b+0.1-x,color='grey',linestyle='dashed',alpha=1)
ax.plot(x,d-x,color='grey',linestyle='dashed',alpha=1)
ax.plot(x,c-x,color='grey',linestyle='dashed',alpha=1)

ax.fill_between(x,  a-0.1-x,b+0.1-x,color='grey', alpha=0.2)
ax.fill_between(x, -yrange-x, c-x,color='grey', alpha=0.2)
ax.fill_between(x, d-x, yrange-x,color='grey', alpha=0.2)

ax.set_ylabel('RRM (rad m$^{-2}$)', fontsize=fontsize)
ax.tick_params(axis="y",direction="in",labelsize=labelsize,size=ticksize)
ax_right_ticks=ax.twinx()
ax_right_ticks.set_ylim(ax.get_ylim())
ax_right_ticks.set_xticks(ax.get_xticks())
ax_right_ticks.tick_params(axis="y",direction="in",size=ticksize)
ax_right_ticks.set_yticklabels([])

ax.set_xlabel('GRM (rad m$^{-2}$)', fontsize=fontsize)
# ax.set_xlim(-40,40)
# xticks=np.linspace(-100, 100, 5)
ax.set_xticks(xticks)
ax.tick_params(axis="x",direction="out",labelsize=labelsize,size=ticksize)
ax.xaxis.set_ticks_position('both')
ax.tick_params(axis="x",direction="in",size=5)
ax.yaxis.set_ticks_position('both')
ax.tick_params(axis="y",direction="in",size=5)
ax.legend()

ax=axs[1,1]
#ax.set_title("RRM measures")
counts, _, _ = ax.hist(RRMs,bins=bins,color='blue', orientation='horizontal') #,label='13h field'


ax.tick_params(axis="y",direction="out",labelsize=labelsize,size=ticksize)
ax.set_ylim(-yrange,yrange)
ax_right_ticks=ax.twinx()
ax_right_ticks.set_ylim(ax.get_ylim())
ax_right_ticks.set_xticks(ax.get_xticks())
ax_right_ticks.tick_params(axis="y",direction="in",size=5)
ax_right_ticks.set_yticklabels([])

ax.set_xlim(0,np.nanmax(counts) * 1.1)
xticks=np.linspace(0, np.nanmax(counts), 8).astype(int16)
ax.set_xticks(xticks)

ax.set_xlabel('Number', fontsize=fontsize)
ax.tick_params(axis="x",direction="in",labelsize=labelsize,size=ticksize)
ax_top_ticks=ax.twiny()
ax_top_ticks.set_xlim(ax.get_xlim())
ax_top_ticks.set_xticks(ax.get_xticks())
ax_top_ticks.tick_params(axis="x",direction="in",size=5)
ax_top_ticks.set_xticklabels([])
ax.legend()
# left, center, right = st.columns([1, 8, 1])
# with center:
#     st.pyplot(fig, use_container_width=True)
#
st.pyplot(fig, use_container_width=False)
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

    # ymax = st.slider(
    #     "y max",
    #     50,
    #     1000,
    #     300
    # )


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
            label = "",
            value=len(RM_excluded_low),
            delta=f"{len(RM_excluded_low)/len(RM_lat):.1%}"
        )
        with open("excluded_low.fits", "rb") as f:
            st.download_button("Download FITS file of low RM excluded sources", f, file_name="excluded_low.fits")

    with col2:
        st.subheader("High RM exclusion")
        st.metric(
            label = "",
            value=len(RM_excluded_high),
            delta=f"{len(RM_excluded_high)/len(RM_lat):.1%}"
        )
        with open("excluded_high.fits", "rb") as f:
            st.download_button("Download FITS file of high RM excluded sources", f, file_name="excluded_high.fits")




RM_final = RM_lat[final_mask]
idx_final = idx_lat[final_mask]

density = st.sidebar.checkbox("Normalize (density)", value=False)
fig, ax = plt.subplots(figsize=(8, 6))

counts, bins = np.histogram(RM_final, bins=bins, density=density)
ymax = counts.max()

ax.hist(
    RM_final,
    bins=bins,
    density = density
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
ax.set_ylim(0, ymax *1.1)

ax.set_xlabel("RM")
ax.set_ylabel("Count")

st.pyplot(fig)

st.metric(
    "Selected sources",
    len(RM_final)
)
