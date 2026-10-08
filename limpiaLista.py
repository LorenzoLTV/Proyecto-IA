import pandas as pd
import numpy as np

# 1. Cargar los datos especificando el motor o intentando alternativas
input_file = "hr_data_raw.xls"

try:
    # Intentar con el motor por defecto para .xls antiguo
    df = pd.read_excel(input_file, engine="xlrd")
except Exception:
    try:
        # Si en realidad es un .xlsx renombrado a .xls
        df = pd.read_excel(input_file, engine="openpyxl")
    except Exception:
        # Si en realidad es un archivo CSV separado por comas o tabulaciones con extensión .xls
        try:
            df = pd.read_csv(input_file, sep=None, engine="python")
        except Exception as e:
            raise RuntimeError(f"No se pudo leer el archivo con ningún motor. Detalle: {e}")

# Mapeo de nombres de columnas originales a las nuevas
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
df = df.rename(columns=column_mapping)

# --- LIMPIEZA Y TRANSFORMACIÓN DE COLUMNAS ---

# 1. employee_id: Texto "E" + 5 dígitos, sin espacios, mayúsculas
df['employee_id'] = df['employee_id'].astype(str).str.strip().str.upper()

# 2. first_name: Title Case, sin espacios sobrantes
df['first_name'] = df['first_name'].astype(str).str.strip().str.title()

# 3. last_name: Title Case, sin espacios sobrantes
df['last_name'] = df['last_name'].astype(str).str.strip().str.title()

# 4. gender: Mantiene consistencia (Male, Female, Non-binary)
df['gender'] = df['gender'].astype(str).str.strip()

# 5. age: Convertir a entero
df['age'] = pd.to_numeric(df['age'], errors='coerce').astype('Int64')

# 6. department: Estandarización a 10 categorías
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

df['department'] = df['department'].apply(clean_department)

# 7. job_title: Title Case, corrección de dobles espacios y "VP"
def clean_job_title(title):
    if pd.isna(title):
        return title
    title = " ".join(str(title).split()).title()
    words = [word.upper() if word.lower() == 'vp' else word for word in title.split()]
    return " ".join(words)

df['job_title'] = df['job_title'].apply(clean_job_title)

# 8. salary: Limpieza, corrección de negativos y centinela (999999)
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

df['salary_usd'] = df['salary'].apply(process_salary_usd)
df['salary'] = df['salary_usd'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else np.nan)

# 9. hire_date: Parseo condicional ("/" -> dd/mm/aaaa, "-" -> mm-dd-aaaa)
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

df['hire_date'] = df['hire_date'].apply(parse_date)

# 10. email: Minúsculas
df['email'] = df['email'].astype(str).str.strip().str.lower()

# 11. city: Limpieza de espacios
df['city'] = df['city'].astype(str).str.strip()

# 12. performance_rating: Convertir a entero (1-5)
df['performance_rating'] = pd.to_numeric(df['performance_rating'], errors='coerce').astype('Int64')

# Reorganizar columnas
column_order = [
    'employee_id', 'first_name', 'last_name', 'gender', 'age',
    'department', 'job_title', 'salary_usd', 'salary', 'hire_date',
    'email', 'city', 'performance_rating'
]
df = df[column_order]

# --- GUARDAR ARCHIVO LIMPIO ---
output_file = "Data_Raw_Limpia.xlsx"
df.to_excel(output_file, index=False)

print(f"Limpieza completada con éxito. Archivo guardado como '{output_file}'.")