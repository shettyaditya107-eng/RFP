import streamlit as st
from pathlib import Path

from core.pdf_reader import read_document
from core.ai_analyzer import analyze_requirements
from core.quality_check import validate_requirements
from core.report_builder import (
    build_excel,
    build_word,
    build_json
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Requirement Intelligence",
    page_icon="◈",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.hero {
    padding: 24px;
    border-radius: 18px;
    background: linear-gradient(
        135deg,
        #172554,
        #312e81
    );
    color: white;
    margin-bottom: 22px;
}

.hero h1 {
    margin: 0 0 8px 0;
    font-size: 34px;
}

.hero p {
    margin: 0;
    font-size: 16px;
    opacity: 0.9;
}

.card {
    padding: 18px;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    background: #fff;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">
    <h1>◈ RFP Extractor</h1>
    <p>
        Transform complex proposal documents into structured,
        traceable requirements.
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# FILE UPLOAD
# ============================================================

left, right = st.columns([1.4, 1])

with left:

    uploaded = st.file_uploader(
        "Upload proposal / RFP document",
        type=["pdf"]
    )

with right:

    st.info(
        "The analyzer identifies business areas, "
        "requirement groups, capabilities and "
        "individual requirements."
    )


# ============================================================
# ANALYZE DOCUMENT
# ============================================================

if uploaded:

    if st.button(
        "Analyze Document",
        type="primary",
        use_container_width=True
    ):

        # Create input folder
        input_dir = Path("input")
        input_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # Save uploaded PDF
        temp = input_dir / uploaded.name

        temp.write_bytes(
            uploaded.getbuffer()
        )

        try:

            # ------------------------------------------------
            # READ PDF
            # ------------------------------------------------

            with st.spinner(
                "Reading document..."
            ):

                pages = read_document(temp)


            # ------------------------------------------------
            # AI ANALYSIS
            # ------------------------------------------------

            with st.spinner(
                "AI is analyzing requirements..."
            ):

                records = analyze_requirements(
                    pages
                )


            # ------------------------------------------------
            # QUALITY CHECK
            # ------------------------------------------------

            with st.spinner(
                "Validating requirements..."
            ):

                records = validate_requirements(
                    records,
                    len(pages)
                )


            # ------------------------------------------------
            # SAVE TO SESSION
            # ------------------------------------------------

            st.session_state["records"] = records
            st.session_state["pages"] = pages

            st.success(
                f"Analysis completed — "
                f"{len(records)} requirements identified."
            )

        except Exception as exc:

            st.error(
                f"Analysis failed: {exc}"
            )


# ============================================================
# GET RECORDS
# ============================================================

records = st.session_state.get(
    "records",
    []
)


# ============================================================
# ANALYSIS RESULTS
# ============================================================

if records:

    # --------------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------------

    st.subheader(
        "Analysis Overview"
    )

    a, b, c, d = st.columns(4)

    a.metric(
        "Requirements",
        len(records)
    )

    b.metric(
        "Business Areas",
        len(
            set(
                x["business_area"]
                for x in records
            )
        )
    )

    c.metric(
        "Source Pages",
        len(
            set(
                x["page_number"]
                for x in records
            )
        )
    )

    avg_confidence = (
        sum(
            x["confidence"]
            for x in records
        )
        / len(records)
    )

    d.metric(
        "Avg. Confidence",
        f"{avg_confidence:.0%}"
    )


    # --------------------------------------------------------
    # REQUIREMENT EXPLORER
    # --------------------------------------------------------

    st.subheader(
        "Requirement Explorer"
    )

    st.dataframe(
        records,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # EXPORT CENTER
    # --------------------------------------------------------

    st.subheader(
        "Export Center"
    )

    try:

        # Generate files and save them to output folder
        xlsx_path = build_excel(records)

        docx_path = build_word(records)

        json_path = build_json(records)


        # ----------------------------------------------------
        # SHOW OUTPUT LOCATION
        # ----------------------------------------------------

        st.success(
            "Files generated successfully."
        )

        st.code(
            str(
                Path(xlsx_path).parent.resolve()
            )
        )


        # ----------------------------------------------------
        # READ FILES FOR DOWNLOAD
        # ----------------------------------------------------

        with open(
            xlsx_path,
            "rb"
        ) as file:

            xlsx_data = file.read()


        with open(
            docx_path,
            "rb"
        ) as file:

            docx_data = file.read()


        with open(
            json_path,
            "rb"
        ) as file:

            json_data = file.read()


        # ----------------------------------------------------
        # DOWNLOAD BUTTONS
        # ----------------------------------------------------

        c1, c2, c3 = st.columns(3)


        # Excel
        with c1:

            st.download_button(
                label="Download Excel",
                data=xlsx_data,
                file_name="requirement_analysis.xlsx",
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),
                use_container_width=True
            )


        # Word
        with c2:

            st.download_button(
                label="Download Word",
                data=docx_data,
                file_name="requirement_analysis.docx",
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.wordprocessingml.document"
                ),
                use_container_width=True
            )


        # JSON
        with c3:

            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="requirement_analysis.json",
                mime="application/json",
                use_container_width=True
            )


    except Exception as exc:

        st.error(
            f"Could not generate output files: {exc}"
        )
