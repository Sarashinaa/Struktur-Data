import pandas as pd
import os

# Configuration
google_sheets_csv_url = 'https://docs.google.com/spreadsheets/d/17ru4XAU2NloE9Dfxr2PC1BVcsYkLLT5r7nPSsiOFlvQ/export?format=csv'
excel_header_row = 0

# Dataset columns
COLUMNS_TO_FETCH = [
    'no', 'nim', 'nama_mahasiswa', 'sumber_database',
    'fokus_kata_kunci_pilih_no1_atau_2_atau_3_sesuai_yg_ada_di_soal',
    'judul_paper', 'tahun_terbit', 'nama_penulis',
    'abstrak_langusung_copas_dari_paper',
    'kesimpulan_langusung_copas_dari_paper', 'link_paper'
]

COL_JUDUL = 'judul_paper'
COL_TAHUN = 'tahun_terbit'
COL_PENULIS = 'nama_penulis'

def erase_display():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_data_from_csv(csv_url, header_row):
    print(f"Mengambil data dari Google Sheets (CSV)...")
    df = pd.read_csv(csv_url, header=header_row)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace(r'[^a-z0-9_]', '', regex=True)
    data = df.to_dict(orient='records')
    print(f"Berhasil mengambil {len(data)} baris data.")
    return data

def sequential_search(data_list, search_term, column_key):
    results = []
    search_term_clean = str(search_term).strip().lower()
    
    if not search_term_clean:
        print("Kata kunci pencarian kosong.")
        return []
    
    # Untuk pencarian tahun, gunakan exact match
    if column_key == COL_TAHUN:
        try:
            search_term_num = float(search_term_clean)
            for item in data_list:
                if column_key in item and item[column_key] is not None:
                    try:
                        value_num = float(str(item[column_key]).strip())
                        if value_num == search_term_num:
                            results.append(item)
                    except (ValueError, TypeError):
                        continue
        except (ValueError, TypeError):
            print(f"Error: Nilai tahun '{search_term}' tidak valid.")
            return []
    else:
        # Untuk kolom teks, gunakan substring search
        for item in data_list:
            if column_key in item and item[column_key] is not None:
                value_str_clean = str(item[column_key]).strip().lower()
                if search_term_clean in value_str_clean:
                    results.append(item)
    
    return results

def dichotomous_search(sorted_data, search_term, column_key):
    results = []
    search_term_clean = str(search_term).strip().lower()
    
    if not search_term_clean:
        print("Kata kunci pencarian kosong.")
        return []
    
    # Untuk tahun dan lainnya, gunakan binary search
    # Tetapi karena binary search hanya bekerja untuk exact match, untuk teks
    # kita perlu menggunakan full scan untuk substring match
    
    if column_key == COL_TAHUN:
        try:
            search_term_num = float(search_term_clean)
            # Full scan implementation for exactness
            for item in sorted_data:
                if column_key in item and item[column_key] is not None:
                    try:
                        if float(str(item[column_key]).strip()) == search_term_num:
                            results.append(item)
                    except (ValueError, TypeError):
                        continue
        except (ValueError, TypeError):
            print(f"Error: Nilai tahun '{search_term}' tidak valid.")
            return []
    else:
        # Binary search dengan exact match untuk teks
        for item in sorted_data:
            if column_key in item and item[column_key] is not None:
                value_str = str(item[column_key]).strip().lower()
                if value_str == search_term_clean:
                    results.append(item)
    
    return results

def display_result(row, i):
    print(f"\n#{i}")
    for col in COLUMNS_TO_FETCH:
        val = row.get(col, 'N/A')
        
        # Rename the focus keyword column for display
        display_col = col
        if col == 'fokus_kata_kunci_pilih_no1_atau_2_atau_3_sesuai_yg_ada_di_soal':
            display_col = 'Fokus Kata Kunci'
        else:
            display_col = col.replace('_', ' ').title()
        
        # Add extra line breaks before abstrak and kesimpulan
        if col == 'abstrak_langusung_copas_dari_paper':
            print()  # Empty line before abstract
        elif col == 'kesimpulan_langusung_copas_dari_paper':
            print()  # Empty line before conclusion
            
        print(f"  {display_col:<50}: {val}")
    print("-" * 60)

if __name__ == "__main__":
    erase_display()
    print("--- Program Pencarian Data Paper dari Google Sheets ---")
    
    try:
        all_data = load_data_from_csv(google_sheets_csv_url, excel_header_row)
    except Exception as e:
        print(f"Error saat membaca data: {e}")
        input("Tekan Enter untuk keluar...")
        exit()

    if not all_data:
        print("\nTidak ada data yang bisa diproses. Program berhenti.")
        input("Tekan Enter untuk keluar...")
    else:
        while True:
            erase_display()
            print("\n--- Menu Pencarian ---")
            print("Pilih kolom untuk pencarian:")
            print("1. Judul Paper")
            print("2. Tahun Terbit")
            print("3. Nama Penulis")
            choice_col = input("Masukkan nomor kolom (atau ketik 'q' untuk keluar): ")

            if choice_col.lower() == 'q':
                break

            if choice_col == '1':
                search_key = COL_JUDUL
            elif choice_col == '2':
                search_key = COL_TAHUN
            elif choice_col == '3':
                search_key = COL_PENULIS
            else:
                print("Pilihan kolom tidak valid.")
                input("Tekan Enter untuk mencoba lagi...")
                continue

            search_value = input(f"\nMasukkan kata kunci pencarian untuk '{search_key}': ").strip()
            if not search_value:
                print("Kata kunci tidak boleh kosong.")
                input("Tekan Enter untuk mencoba lagi...")
                continue

            print("\nPilih metode pencarian:")
            print("1. Linear Search")
            print("2. Binary Search")
            choice_method = input("Masukkan pilihan metode (1/2): ")

            results = []
            if choice_method == '1':
                print("\nMelakukan Linear Search...")
                results = sequential_search(all_data, search_value, search_key)
            elif choice_method == '2':
                print("\nMelakukan Binary Search...")
                filtered = [item for item in all_data if item.get(search_key) is not None]
                
                # Mengurutkan data
                def sort_key(item):
                    v = item.get(search_key)
                    if v is None:
                        return float('-inf') if search_key == COL_TAHUN else ""
                    try:
                        if search_key == COL_TAHUN:
                            return float(str(v).strip())
                        else:
                            return str(v).strip().lower()
                    except (ValueError, TypeError):
                        return float('-inf') if search_key == COL_TAHUN else ""
                
                sorted_data = sorted(filtered, key=sort_key)
                results = dichotomous_search(sorted_data, search_value, search_key)
            else:
                print("Pilihan metode tidak valid.")

            print(f"\n--- Hasil Pencarian ('{search_value}' di kolom '{search_key}') ---")
            if results:
                # Sort results for display
                if search_key == COL_TAHUN:
                    results.sort(key=lambda x: float(str(x.get(search_key, '0')).strip()) 
                                if x.get(search_key) is not None else float('-inf'))
                else:
                    results.sort(key=lambda x: str(x.get(search_key, '')).strip().lower() 
                                if x.get(search_key) is not None else '')
                
                print(f"Ditemukan {len(results)} hasil:")
                for i, row in enumerate(results, start=1):
                    display_result(row, i)
            else:
                print("Tidak ada hasil yang ditemukan.")

            input("\nTekan Enter untuk pencarian berikutnya...")
    print("\nProgram selesai.")