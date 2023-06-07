import io
from dataclasses import dataclass
from enum import Enum

import pandas as pd
import polars as pl
import pyarrow.csv as csv
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from xlsx2csv import Xlsx2csv

SUPPORTED_TYPES = ["csv", "xlsx", "parquet"]


class TypeExtension(str, Enum):
    CSV = "csv"
    XLSX = "xlsx"
    PARQUET = "parquet"


@dataclass
class OptionsUpload:
    format: str | None = None
    encoding: str | None = None
    sheet_name: str | None = None


def get_extension(file: UploadedFile) -> str:
    return file.name.split(".")[-1].lower()


def get_dataframe(df: pl.DataFrame | pl.Series) -> pl.DataFrame:
    if isinstance(df, pl.DataFrame):
        return df

    return pl.DataFrame(df)


def read_csv_fr(file: UploadedFile, encoding: str) -> pl.DataFrame:
    pa_df = csv.read_csv(
        file,
        parse_options=csv.ParseOptions(delimiter=";"),
        convert_options=csv.ConvertOptions(decimal_point=","),
        read_options=csv.ReadOptions(encoding=encoding),
    )

    df = pl.from_arrow(pa_df)
    return get_dataframe(df)


def read_csv_en(file: UploadedFile, encoding: str) -> pl.DataFrame:
    pa_df = csv.read_csv(
        file,
        read_options=csv.ReadOptions(encoding=encoding),
    )

    df = pl.from_arrow(pa_df)
    return get_dataframe(df)


def read_csv(file: UploadedFile, options: OptionsUpload) -> pl.DataFrame:
    assert options.encoding is not None
    if options.format == "French":
        return read_csv_fr(file, options.encoding)

    return read_csv_en(file, options.encoding)


def read_xlsx(file: UploadedFile, sheet_name: str | None) -> pl.DataFrame:
    if sheet_name is None:
        return pl.read_excel(file)

    return pl.read_excel(file, sheet_name=sheet_name)


def read_parquet(file: UploadedFile) -> pl.DataFrame:
    return pl.read_parquet(file)


def read_btn(file: UploadedFile, options: OptionsUpload):
    extension = get_extension(file)
    if extension == TypeExtension.CSV:
        return read_csv(file, options)

    if extension == TypeExtension.XLSX:
        return read_xlsx(file, options.sheet_name)

    if extension == TypeExtension.PARQUET:
        return read_parquet(file)

    return None


def get_options(file: UploadedFile | None, var: str):
    if file is None:
        st.write("")
        st.write("")
        st.write("")
        return OptionsUpload()

    extension = get_extension(file)

    if extension == TypeExtension.CSV:
        formats = ["French", "International"]
        format_data = st.selectbox("Format", formats, key=f"format_{var}")
        encodings = ["latin1", "utf8"]
        encoding_data = st.selectbox("Encoding", encodings, key=f"encoding_{var}")
        return OptionsUpload(format=format_data, encoding=encoding_data)

    if extension == TypeExtension.XLSX:
        excel_file = Xlsx2csv(file)
        sheet_names = [s["name"] for s in excel_file.workbook.sheets]
        sheet_name = st.selectbox("Sheet", sheet_names, key=f"sheet_{var}")
        return OptionsUpload(sheet_name=sheet_name)

    if extension == TypeExtension.PARQUET:
        st.write("")
        st.write("")
        st.write("")
        return OptionsUpload()

    return OptionsUpload()


def upload_file_fn(file: UploadedFile | None, var: str):
    options = get_options(file, var)
    btn_read = st.button("Read", disabled=(file is None), key=f"read_{var}")

    if btn_read:
        assert file is not None
        st.session_state[var] = read_btn(file, options)
        st.session_state[f"{var}_columns"] = st.session_state[var].columns
        st.session_state[f"{var}_columns_str"] = (
            st.session_state[var].select(pl.col(pl.Utf8)).columns
        )


def export_xlsx(df: pl.DataFrame):
    df_pandas = df.to_pandas()
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_pandas.to_excel(writer, sheet_name="Matching", index=False)
        worksheet = writer.sheets["Matching"]
        worksheet.autofit()
    return buffer
