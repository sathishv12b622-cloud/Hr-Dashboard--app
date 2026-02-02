import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="HR Dashboard", page_icon=":bookmark_tabs:", layout="wide")

st.markdown("""
    <h1 style='text-align: center;'>
        📑 <span style='background: linear-gradient(90deg, 
                     #9B2C6D 0%,
                     #6B4F3C 25%, 
                     #4A4A4A 40%,
                     #6B5D1E 60%, 
                     #9B7B2C 85%,
                     #8B6B1E 100%);
                     -webkit-background-clip: text;
                     -webkit-text-fill-color: transparent;
                     background-clip: text;
                     font-weight: bold;'>HR Dashboard report</span>
    </h1>
""", unsafe_allow_html=True)

st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# File upload
fl = st.file_uploader(":file_folder: Upload your CSV or xlsx file", type=["csv", "xlsx"])

if fl is not None:
    filename = fl.name
    st.write(filename)
    
    # Check file type and read accordingly
    if filename.endswith('.csv'):
        df = pd.read_csv(fl)
    else:
        df = pd.read_excel(fl)
else:
    # Use absolute path or handle missing file gracefully
    default_file = r"E:\loyalwings\hr analyst\March6onboarding.xlsx"
    
    if os.path.exists(default_file):
        df = pd.read_excel(default_file)
    else:
        st.warning("⚠️ Please upload a file to view the dashboard")
        st.stop()  # This stops execution here
        
# If user applied edits from the worksheet, prefer that edited dataframe
if "edited_df" in st.session_state:
    try:
        df = st.session_state["edited_df"].copy()
        st.info("Loaded edited worksheet data (applied to charts)")
    except Exception:
        pass

# Detect name-like column names (prefer common variants)
name_col = None
for cand in ["Name", "Full Name", "Employee", "Employee Name", "Emp Name"]:
    if cand in df.columns:
        name_col = cand
        break
if not name_col:
    name_cols = [c for c in df.columns if 'NAME' in c.upper()]
    if name_cols:
        name_col = name_cols[0]

#search box for name
NAME = st.sidebar.text_input("Search Name Here:")
if NAME:
    if name_col:
        df = df[df[name_col].str.contains(NAME, case=False, na=False)]
    else:
        st.warning("No name-like column found — search by name is disabled.")

df["DOJ"] = pd.to_datetime(df["DOJ"])
df["DOJ_Month_Year"] = df["DOJ"].dt.strftime("%B %Y")  # Format: "March 2025"

#Filter heading 
st.sidebar.header("Filter Here:")
#Gender Filter
Gender = st.sidebar.multiselect("Pick Gender", df["Gender"].unique())
if not Gender:
    df2 = df.copy()
else:
    df2 = df[df["Gender"].isin(Gender)]

#Role Filter
ROLE = st.sidebar.multiselect("Pick Role", df2["ROLE"].unique())
if not ROLE:
    df3 = df2.copy()
else:
    df3 = df2[df2["ROLE"].isin(ROLE)]

#Level of Professional work Filter
Level = st.sidebar.multiselect("Pick Level", df3["Level"].unique())
if not Level:
    df4 = df3.copy()
else:
    df4 = df3[df3["Level"].isin(Level)]

# DOJ Month-Year Filter (sorted chronologically)
DOJ_options = sorted(df4["DOJ_Month_Year"].unique(), 
                     key=lambda x: pd.to_datetime(x, format="%B %Y"))
DOJ = st.sidebar.multiselect("Pick Month-Year of Joining", DOJ_options)

#fitler the dataframe 
# All 16 combinations for 4 filters: Gender, ROLE, Level, DOJ

if not Gender and not ROLE and not Level and not DOJ:
    # Case 1: No filters (0000)
    filter_df = df.copy()

elif Gender and not ROLE and not Level and not DOJ:
    # Case 2: Only Gender (1000)
    filter_df = df[df["Gender"].isin(Gender)]

elif not Gender and ROLE and not Level and not DOJ:
    # Case 3: Only ROLE (0100)
    filter_df = df[df["ROLE"].isin(ROLE)]

elif not Gender and not ROLE and Level and not DOJ:
    # Case 4: Only Level (0010)
    filter_df = df[df["Level"].isin(Level)]

elif not Gender and not ROLE and not Level and DOJ:
    # Case 5: Only DOJ (0001)
    filter_df = df[df["DOJ_Month_Year"].isin(DOJ)]

elif Gender and ROLE and not Level and not DOJ:
    # Case 6: Gender + ROLE (1100)
    filter_df = df[df["Gender"].isin(Gender) & df["ROLE"].isin(ROLE)]

elif Gender and not ROLE and Level and not DOJ:
    # Case 7: Gender + Level (1010)
    filter_df = df[df["Gender"].isin(Gender) & df["Level"].isin(Level)]

elif Gender and not ROLE and not Level and DOJ:
    # Case 8: Gender + DOJ (1001)
    filter_df = df[df["Gender"].isin(Gender) & df["DOJ_Month_Year"].isin(DOJ)]

elif not Gender and ROLE and Level and not DOJ:
    # Case 9: ROLE + Level (0110)
    filter_df = df[df["ROLE"].isin(ROLE) & df["Level"].isin(Level)]

elif not Gender and ROLE and not Level and DOJ:
    # Case 10: ROLE + DOJ (0101)
    filter_df = df[df["ROLE"].isin(ROLE) & df["DOJ_Month_Year"].isin(DOJ)]

elif not Gender and not ROLE and Level and DOJ:
    # Case 11: Level + DOJ (0011)
    filter_df = df[df["Level"].isin(Level) & df["DOJ_Month_Year"].isin(DOJ)]

elif Gender and ROLE and Level and not DOJ:
    # Case 12: Gender + ROLE + Level (1110)
    filter_df = df[df["Gender"].isin(Gender) & df["ROLE"].isin(ROLE) & df["Level"].isin(Level)]

elif Gender and ROLE and not Level and DOJ:
    # Case 13: Gender + ROLE + DOJ (1101)
    filter_df = df[df["Gender"].isin(Gender) & df["ROLE"].isin(ROLE) & df["DOJ_Month_Year"].isin(DOJ)]

elif Gender and not ROLE and Level and DOJ:
    # Case 14: Gender + Level + DOJ (1011)
    filter_df = df[df["Gender"].isin(Gender) & df["Level"].isin(Level) & df["DOJ_Month_Year"].isin(DOJ)]

elif not Gender and ROLE and Level and DOJ:
    # Case 15: ROLE + Level + DOJ (0111)
    filter_df = df[df["ROLE"].isin(ROLE) & df["Level"].isin(Level) & df["DOJ_Month_Year"].isin(DOJ)]

elif Gender and ROLE and Level and DOJ:
    # Case 16: All filters (1111)
    filter_df = df[df["Gender"].isin(Gender) & df["ROLE"].isin(ROLE) & df["Level"].isin(Level) & df["DOJ_Month_Year"].isin(DOJ)]

# Layout the page

# --- Scorecards: Total pipeline, Will to Join, Experienced, Filtered names (boxed layout) ---
# Detect name column (prefer columns containing 'name')
name_cols = [c for c in filter_df.columns if 'NAME' in c.upper()]
name_col = name_cols[0] if name_cols else None

# Total pipeline (unique names if name column exists, else total rows)
if name_col:
    total_pipeline = int(filter_df[name_col].nunique())
else:
    total_pipeline = int(len(filter_df))

# Detect 'will to join' column (common keywords)
will_candidates = [c for c in filter_df.columns if ('WILL' in c.upper() and 'JOIN' in c.upper())]
if not will_candidates:
    will_candidates = [c for c in filter_df.columns if 'JOIN' in c.upper() or 'WILL' in c.upper() or 'JOINING' in c.upper()]
will_col = will_candidates[0] if will_candidates else None

# Helper to interpret yes-like values
def _is_yes(val):
    try:
        s = str(val).strip().upper()
        return s in ("YES", "Y", "TRUE", "1") or s.startswith("YES")
    except Exception:
        return False

will_count = int(filter_df[will_col].apply(lambda v: _is_yes(v)).sum()) if will_col is not None else 0

# Experienced count (based on Level column)
experienced_count = int(filter_df['Level'].str.contains('EXPER', case=False, na=False).sum()) if 'Level' in filter_df.columns else 0

# Unique roles count (distinct ROLE values after filters)
unique_roles_count = int(filter_df['ROLE'].nunique()) if 'ROLE' in filter_df.columns else 0

# Boxed card CSS and layout
st.markdown("""
<style>
:root {
    --accent-green-top: #5cdb95;
    --accent-green-bottom: #8ee4af;
    --heading-dark: #05386b;
    --muted: #379683;
}
.container{max-width:1200px;margin:0 auto;padding:0 12px}
.cards-row{display:flex;gap:16px;align-items:stretch;margin-bottom:18px;justify-content:center;flex-wrap:wrap}
.card{flex:0 1 260px;border-radius:20px;padding:18px 18px;background:linear-gradient(180deg, #5cdb95, #8ee4af);border:none;box-shadow:0 8px 16px rgba(0,0,0,0.1);text-align:center;display:flex;flex-direction:column;justify-content:center;align-items:center;color:var(--heading-dark)}
.card .title{font-size:18px;color:#05386b;margin:0 0 6px;text-align:center;font-weight:600}
.card .value{font-size:22px;font-weight:700;color:#05386b;margin:0;text-align:center}
.card .sub{font-size:12px;color:#379683;margin-top:6px;text-align:center}
.chart-box{border:1px solid #5cdb95;padding:8px;border-radius:8px;background:#ffffff;box-shadow:0 2px 8px rgba(92,219,149,0.2);}
</style>
""", unsafe_allow_html=True)

cards_html = f"""
<div class='cards-row'>
  <div class='card'>
    <div class='title'>Total Pipeline</div>
    <div class='value'>{total_pipeline}</div>
    <div class='sub'>Total Applied</div>
  </div>
  <div class='card'>
    <div class='title'>Will to Join</div>
    <div class='value'>{will_count} {'('+str(round(will_count/total_pipeline*100,1))+'%)' if total_pipeline else ''}</div>
    <div class='sub'>Applicant Who Answered Yes</div>
  </div>
  <div class='card'>
    <div class='title'>Experienced</div>
    <div class='value'>{experienced_count} {'('+str(round(experienced_count/total_pipeline*100,1))+'%)' if total_pipeline else ''}</div>
    <div class='sub'>Level contains 'Experienced'</div>
  </div>
  <div class='card'>
    <div class='title'>Total Roles</div>
    <div class='value'>{unique_roles_count}</div>
    <div class='sub'>Count ROLE</div>
  </div>
</div>
"""

st.markdown(cards_html, unsafe_allow_html=True)

# Continue with charts
col1, col2= st.columns(2)

# Prefer an explicit 'Name' column (case-insensitive) if present
role_count_col = None
name_cols = [c for c in filter_df.columns if 'NAME' in c.upper()]
if name_cols:
    role_count_col = name_cols[0]
else:
    # Otherwise pick a reasonable non-email, non-meta text column
    candidates = []
    for c in filter_df.columns:
        cu = c.upper()
        if cu in ["ROLE", "DOJ", "LEVEL", "GENDER"]:
            continue
        try:
            ser = filter_df[c].astype(str)
        except Exception:
            continue
        # exclude columns that are mainly emails
        if ser.str.contains('@', na=False).mean() < 0.5:
            candidates.append(c)
    if candidates:
        role_count_col = candidates[0]

# Create concise role labels (short form) and group counts by them
if 'ROLE' in filter_df.columns:
    def _short_role_label(role_str):
        if pd.isna(role_str):
            return 'Unknown'
        parts = [p.strip() for p in str(role_str).split(',') if p.strip()]
        mapping = {
            'frontend': 'Frontend',
            'backend': 'Backend',
            'software testing': 'Testing',
            'software test': 'Testing',
            'wordpress': 'WordPress',
            'webdesign': 'Design',
            'web designing': 'Design',
            'digital marketing': 'Marketing',
            'digital': 'Marketing',
            'web designing': 'Design'
        }
        out = []
        for p in parts:
            key = p.lower()
            found = None
            for k, v in mapping.items():
                if k in key:
                    found = v
                    break
            if not found:
                # fallback: take first two words title-cased
                found = ' '.join(p.title().split()[:2])
            out.append(found)
        return ' / '.join(out) if out else 'Unknown'

    filter_df = filter_df.copy()
    filter_df['RoleShort'] = filter_df['ROLE'].apply(_short_role_label)
    if role_count_col:
        Role_df = filter_df.groupby('RoleShort')[role_count_col].count().reset_index(name='Count')
    else:
        Role_df = filter_df.groupby('RoleShort').size().reset_index(name='Count')
else:
    st.warning("No 'ROLE' column found — role chart will be empty.")
    Role_df = pd.DataFrame(columns=['RoleShort', 'Count'])

# Sort so bars display with largest counts at the bottom
Role_df = Role_df.sort_values('Count', ascending=True)

with col1:
    st.markdown("<h4 style='text-align:center;margin-bottom:6px;font-size:18px'>Employees by Role</h4>", unsafe_allow_html=True)
    fig_role = px.bar(Role_df, x='Count', y='RoleShort', orientation='h', text='Count', template='seaborn', color='RoleShort')
    fig_role.update_traces(texttemplate='%{text}', textposition='outside')
    fig_role.update_layout(showlegend=False, xaxis_title='Applied', yaxis_title='Role')
    st.plotly_chart(fig_role, use_container_width=True, height=500)

with col2:
    st.markdown("<h3 style='text-align:center;margin-bottom:8px'>Gender Ratio</h3>", unsafe_allow_html=True)
    if "Gender" in filter_df.columns:
        def _normalize_gender(g):
            try:
                s = str(g).strip().lower()
                if s in ("male", "m", "man"):
                    return "Male"
                if s in ("female", "f", "woman", "fem"):
                    return "Female"
                if s in ("unknown", "nan", ""):
                    return "Unknown"
                return "Other"
            except Exception:
                return "Unknown"

        gender_series = filter_df["Gender"].fillna("Unknown").apply(_normalize_gender)
        gender_counts = gender_series.value_counts().reset_index()
        gender_counts.columns = ["Gender", "Count"]

        # Map Male -> blue, Female -> pink, other categories get neutral colors
        color_map = {"Male": "#1f77b4", "Female": "#ff69b4", "Other": "#8c8c8c", "Unknown": "#6c6c6c"}
        fig = px.pie(gender_counts, names="Gender", values="Count", hole=0.5, color="Gender", color_discrete_map=color_map)
        fig.update_traces(textinfo='value+percent', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, height=500)
    else:
        st.warning("No 'Gender' column found to plot Gender Ratio.")

# --- Worksheet / editable table connected to filters & search ---
st.markdown("<h1 style='text-align: center;'>📝 <span style='background: linear-gradient(90deg, #1f77b4, #ff69b4); 5px;'>WORKSHEET</span></h1>", unsafe_allow_html=True)
# The worksheet uses the main sidebar search and filters — no separate worksheet search bar.
if NAME:
    st.info(f"Name filter active: {NAME}")

# Start with filtered dataframe from filters/search
display_df = filter_df.copy()

st.markdown("<div style='max-width:1200px;margin:0 auto;'>", unsafe_allow_html=True)
# Show editable table if available
try:
    edited = st.data_editor(display_df, num_rows="dynamic")
    display_for_download = edited.copy()
except Exception:
    st.dataframe(display_df, use_container_width=True)
    display_for_download = display_df.copy()

# Buttons: Apply edits to charts and download
col_dl1, col_dl2, col_dl3 = st.columns([1,1,1])
with col_dl1:
    if st.button("Apply worksheet changes to charts"):
        st.session_state["edited_df"] = display_for_download.copy()
        st.success("Applied worksheet edits to charts. Re-running app...")
        st.experimental_rerun()
with col_dl2:
    try:
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            display_for_download.to_excel(writer, index=False, sheet_name="Sheet1")
        buffer.seek(0)
        st.download_button("Download filtered data as Excel", data=buffer,
                           file_name="filtered_data.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception:
        st.warning("openpyxl not available — Excel download disabled.")
with col_dl3:
    csv = display_for_download.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", data=csv,
                       file_name="filtered_data.csv", mime="text/csv")

st.markdown("</div>", unsafe_allow_html=True)

