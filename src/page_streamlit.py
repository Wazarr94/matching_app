from dataclasses import dataclass

import streamlit as st
from io_operations import SUPPORTED_TYPES, export_xlsx, upload_file_fn
from matching import DataMatch, get_distance, match_df

st.set_page_config(
    page_title="Matching app",
    page_icon="🧩",
)


@dataclass
class InfoTab:
    title: str
    upload_prompt: str


@dataclass
class DataTab:
    variable: str
    info: InfoTab


def read_database(data_tab: DataTab) -> DataMatch | None:
    st.write(data_tab.info.title)

    var = data_tab.variable
    var_columns_str = f"{var}_columns_str"
    var_columns = f"{var}_columns"
    var_column = f"{var}_column"
    var_column_id = f"{var}_column_id"

    col1, col2 = st.columns([6, 3])

    data_file = col1.file_uploader(data_tab.info.upload_prompt, type=SUPPORTED_TYPES)
    with col2:
        upload_file_fn(data_file, var)

    if var in st.session_state and st.session_state[var].height > 0:
        st.write("#### Data preview")
        height_df = st.session_state[var].height
        st.write(st.session_state[var].sample(max(5, height_df)).to_pandas())

    if var_columns not in st.session_state:
        return None

    col1, col2 = st.columns(2)

    column_select = col1.selectbox(
        "Column used for matching", st.session_state[var_columns_str]
    )
    column_id = col2.selectbox(
        "Column id to be added for matching",
        [None] + st.session_state[var_columns],
    )

    confirm_col = st.button("Confirm selection", key=f"confirm_{var}")
    if confirm_col:
        st.session_state[var_column] = column_select
        st.session_state[var_column_id] = column_id
        st.success("Column selected")

    if var_column not in st.session_state:
        return None

    return DataMatch(
        st.session_state[var],
        st.session_state[var_column],
        st.session_state[var_column_id],
    )


def get_matching_options():
    st.write("### Matching options")

    distance_fn = get_distance()
    limit = st.selectbox(
        "Number of matches per name",
        options=list(range(1, 10 + 1)),
        index=(3 - 1),
    )

    return distance_fn, limit


def validate_mapping(
    info_match: DataMatch,
    col_map_match: str | None,
    info_known: DataMatch,
    col_map_known: str | None,
):
    if col_map_match is None and col_map_known is None:
        return True

    if col_map_match is not None and col_map_known is not None:
        type_map_match = info_match.df.select(col_map_match).to_series().dtype
        type_map_known = info_known.df.select(col_map_known).to_series().dtype

        if type_map_match != type_map_known:
            st.error("The columns you selected don't have the same type")
            return False

        return True

    st.error("You must fill both mapping columns")
    return False


def get_matching_results(
    info_match: DataMatch | None,
    info_known: DataMatch | None,
):
    if info_match is None or info_known is None:
        st.error("Please complete the previous tabs to use this tab")
        return

    distance_fn, limit = get_matching_options()

    match_btn = st.button("Match")
    if match_btn:
        assert limit is not None and info_match is not None and info_known is not None
        st.session_state.matches = match_df(info_match, info_known, distance_fn, limit)

    display_matching_results()


def display_matching_results():
    if "matches" in st.session_state:
        st.write("#### Matches")
        st.write(st.session_state.matches.to_pandas())
        st.download_button(
            label="Download results as Excel",
            data=export_xlsx(st.session_state.matches),
            file_name="matching_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def main():
    st.write("# Matching dashboard")

    tab_match, tab_known, tab_results = st.tabs(["To match", "Known", "Results"])
    with tab_match:
        info_match = InfoTab(
            title="## Data to match",
            upload_prompt="Upload the database you want to match",
        )
        data_match = DataTab("match", info_match)
        info_match = read_database(data_match)

    with tab_known:
        info_known = InfoTab(
            title="## Data known",
            upload_prompt="Upload the known database",
        )
        data_known = DataTab("known", info_known)
        info_known = read_database(data_known)

    with tab_results:
        get_matching_results(info_match, info_known)


if __name__ == "__main__":
    main()
