import pandas as pd
import numpy as np

# 1. Cargar los datos (detecta si es CSV con extensión .xls o Excel real)
input_file = "./Data/hr_data_raw.xls"

try:
    # Como se ve en la captura que es texto CSV separado por comas:
    df = pd.read_csv(input_file)
except Exception:
    try:
        df = pd.read_excel(input_file, engine="openpyxl")
    except Exception as e:
        raise RuntimeError(f"No se pudo cargar el archivo: {e}")

# Mapeo de nombres de columnas
column_mapping = {
    'Empleador ID': 'employee_id',
    'Primer Nombre': 'first_name',
    'Segundo Nombre': 'last_name',
    'Género': 'gender',
    'Edad': 'age',
    'Departamento': 'department',
    'Nombre del Curro': 'job_title',
    'Salario': 'salary',
    'Fecha de contratacion': 'hire_date',
    'Email': 'email',
    'Ciudad': 'city',
    'Calidad de trabajo': 'performance_rating'
}

# Si el CSV ya viene con encabezados en inglés o español, renombrar lo existente
df = df.rename(columns=column_mapping)

# --- LIMPIEZA Y TRANSFORMACIÓN DE COLUMNAS ---

# 1. employee_id: Texto "E" + 5 dígitos
if 'employee_id' in df.columns:
    df['employee_id'] = df['employee_id'].astype(str).str.strip().str.upper()

# 2. first_name & 3. last_name: Title Case
if 'first_name' in df.columns:
    df['first_name'] = df['first_name'].astype(str).str.strip().str.title()
if 'last_name' in df.columns:
    df['last_name'] = df['last_name'].astype(str).str.strip().str.title()

# 4. gender: Mantiene categorías
if 'gender' in df.columns:
    df['gender'] = df['gender'].astype(str).str.strip()

# 5. age: Entero
if 'age' in df.columns:
    df['age'] = pd.to_numeric(df['age'], errors='coerce').astype('Int64')

# 6. department: Estandarizar a 10 categorías
def clean_department(dept):
    if pd.isna(dept) or str(dept).strip() == "":
        return "Unknown"
    dept = str(dept).strip().lower()
    if any(k in dept for k in ['sale', 'saless']):
        return "Sales"
    elif any(k in dept for k in ['mktg', 'markting', 'marketing']):
        return "Marketing"
    elif any(k in dept for k in ['engg', 'enginering', 'engineering']):
        return "Engineering"
    elif any(k in dept for k in ['fin.', 'finanace', 'finance']):
        return "Finance"
    elif any(k in dept for k in ['ops', 'operatons', 'operations']):
        return "Operations"
    elif any(k in dept for k in ['i.t.', 'information technology', 'it']):
        return "IT"
    elif any(k in dept for k in ['hr', 'human resource', 'human resources']):
        return "Human Resources"
    elif any(k in dept for k in ['cust', 'customer']):
        return "Customer Support"
    elif any(k in dept for k in ['r&d', 'r & d', 'rnd', 'research']):
        return "Research & Development"
    elif any(k in dept for k in ['legall', 'legal']):
        return "Legal"
    else:
        return "Unknown"

if 'department' in df.columns:
    df['department'] = df['department'].apply(clean_department)

# 7. job_title: Title Case y "VP"
def clean_job_title(title):
    if pd.isna(title):
        return title
    title = " ".join(str(title).split()).title()
    words = [word.upper() if word.lower() == 'vp' else word for word in title.split()]
    return " ".join(words)

if 'job_title' in df.columns:
    df['job_title'] = df['job_title'].apply(clean_job_title)

# 8. salary: salary_usd (float) y salary (formateado)
def process_salary_usd(val):
    if pd.isna(val):
        return np.nan
    s_val = str(val).replace('$', '').replace(',', '').strip()
    try:
        num_val = float(s_val)
    except ValueError:
        return np.nan
    if num_val == 999999:
        return np.nan
    return abs(num_val)

if 'salary' in df.columns:
    df['salary_usd'] = df['salary'].apply(process_salary_usd)
    df['salary'] = df['salary_usd'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else np.nan)

# 9. hire_date: YYYY-MM-DD
def parse_date(date_str):
    if pd.isna(date_str):
        return np.nan
    date_str = str(date_str).strip()
    try:
        if '/' in date_str:
            return pd.to_datetime(date_str, format='%d/%m/%Y').strftime('%Y-%m-%d')
        elif '-' in date_str:
            return pd.to_datetime(date_str, format='%m-%d-%Y').strftime('%Y-%m-%d')
        else:
            return pd.to_datetime(date_str).strftime('%Y-%m-%d')
    except Exception:
        return np.nan

if 'hire_date' in df.columns:
    df['hire_date'] = df['hire_date'].apply(parse_date)

# 10. email: Minúsculas
if 'email' in df.columns:
    df['email'] = df['email'].astype(str).str.strip().str.lower()

# 11. city
if 'city' in df.columns:
    df['city'] = df['city'].astype(str).str.strip()

# 12. performance_rating
if 'performance_rating' in df.columns:
    df['performance_rating'] = pd.to_numeric(df['performance_rating'], errors='coerce').astype('Int64')

# Reordenar columnas si existen
desired_columns = [
    'employee_id', 'first_name', 'last_name', 'gender', 'age',
    'department', 'job_title', 'salary_usd', 'salary', 'hire_date',
    'email', 'city', 'performance_rating'
]
existing_cols = [c for c in desired_columns if c in df.columns]
df = df[existing_cols]

# --- GUARDAR EN FORMATO EXCEL (.xlsx) ---
output_file = "./CleanData/Data_Raw_Limpia.xlsx"
df.to_excel(output_file, index=False, engine="openpyxl")

print(f"Limpieza completada con éxito. Archivo guardado como '{output_file}'.")