"""Functions that pull glue tables from the PUDL DB for output.

The glue tables hold information that relates our different datasets to each
other, for example mapping the FERC plants to EIA generators, or the EIA
boilers to EIA generators, or EPA smokestacks to EIA generators.

"""

import pandas as pd
import sqlalchemy as sa

import pudl


def boiler_generator_assn(pudl_engine, pt, start_date=None, end_date=None):
    """Pulls the more complete PUDL/EIA boiler generator associations.

    Args:
        pudl_engine (sqlalchemy.engine.Engine): SQLAlchemy connection engine
            for the PUDL DB.
        pt (immutabledict): a sqlalchemy metadata dictionary of pudl tables
        start_date (date): Date to begin retrieving data.
        end_date (date): Date to end retrieving data.

    Returns:
        pandas.DataFrame: A DataFrame containing the more complete PUDL/EIA
        boiler generator associations.

    """
    bga_eia_tbl = pt['boiler_generator_assn_eia860']
    bga_eia_select = sa.sql.select([bga_eia_tbl])

    if start_date is not None:
        start_date = pd.to_datetime(start_date)
        bga_eia_select = bga_eia_select.where(
            bga_eia_tbl.c.report_date >= start_date
        )
    if end_date is not None:
        end_date = pd.to_datetime(end_date)
        bga_eia_select = bga_eia_select.where(
            bga_eia_tbl.c.report_date <= end_date
        )
    bga_eia_df = pd.read_sql(bga_eia_select, pudl_engine)
    out_df = pudl.helpers.extend_annual(bga_eia_df,
                                        start_date=start_date,
                                        end_date=end_date)
    return out_df
