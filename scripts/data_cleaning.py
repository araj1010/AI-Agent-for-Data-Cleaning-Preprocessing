import pandas as pd
import numpy as np

class DataCleaning:

    def handle_missing_values(self, df, strategy="mean"):
        df = df.copy()

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if not df[col].mode().empty:
                df[col] = df[col].fillna(df[col].mode()[0])
            else:
                df[col] = df[col].fillna("Unknown")

        return df

    def remove_duplicates(self, df):
        return df.drop_duplicates()

    def fix_data_types(self, df):
        df = df.copy()

        for col in df.columns:
            try:
                converted = pd.to_numeric(df[col])
                if not converted.isna().all():
                    df[col] = converted
            except:
                pass

        return df

    def clean_data(self, df):
        df = self.handle_missing_values(df)
        df = self.remove_duplicates(df)
        df = self.fix_data_types(df)
        return df