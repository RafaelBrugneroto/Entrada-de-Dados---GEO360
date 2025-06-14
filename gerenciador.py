import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import pandas as pd
import re
import json
from geotechnical_tab import GeotechnicalDesignTab

# Constante de tipos de solo, útil para a aba de Sondagens
SOIL_TYPES = ["Argila", "Argila Arenosa", "Argila Siltosa", "Silte Argiloso", "Silte Arenoso", "Areia Siltosa", "Areia Argilosa", "Areia"]

class App(tk.Tk):
    """
    Aplicação para gerenciamento de dados de Pilares e Sondagens.
    Funcionalidades de cálculo e resultados foram removidas conforme solicitado.
    """
    def __init__(self):
        super().__init__()
        self.title("Gerenciador de Pilares e Sondagens")
        self.geometry("1000x600")

        # --- Estrutura de Dados Principal ---
        self.dados_pilares = {}
        self.dados_sondagens = {}
        self.current_sondagem_name = None # Rastreia a sondagem atualmente selecionada
        self.last_pilares_excel_path = None # Armazena o caminho do último Excel de pilares importado
        self.sondagem_treeviews = {} # Dicionário para armazenar as Treeviews das sondagens

        # --- Interface do Usuário ---
        self.setup_ui()
        self.load_sondagem_data() # Carrega os dados das sondagens ao iniciar

        # --- Protocolo de Fechamento ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Configura a interface principal com abas."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)

        # Aba de Pilares
        self.pilar_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pilar_frame, text="Pilares")
        self.setup_pilar_tab()

        # Aba de Sondagens
        self.sondagem_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sondagem_frame, text="Sondagens")
        self.setup_sondagem_tab()

        # Aba de Dimensionamento Geotecnico
        self.geo_design_frame = GeotechnicalDesignTab(self.notebook, self)
        self.notebook.add(self.geo_design_frame, text="Dimensionamento Geotécnico")

    def setup_pilar_tab(self):
        """Configura a aba 'Pilares'."""
        btn_frame = ttk.Frame(self.pilar_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(btn_frame, text="Adicionar Pilar", command=self.add_pilar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Importar Excel", command=self.importar_excel_pilares).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atualizar Tabela", command=lambda: self.importar_excel_pilares(reimport=True)).pack(side="left", padx=5)

        cols = ("Nome", "Secao X", "Secao Y", "N max", "N min", "Mx max", "My max", "Fx max", "Fy max", "Mz")
        self.pilar_tree = ttk.Treeview(self.pilar_frame, columns=cols, show="headings")

        for col in cols:
            self.pilar_tree.heading(col, text=col)
            self.pilar_tree.column(col, width=100, anchor="center")

        self.pilar_tree.pack(expand=True, fill="both", padx=5, pady=5)

        # Scrollbars
        scroll_y = ttk.Scrollbar(self.pilar_frame, orient="vertical", command=self.pilar_tree.yview)
        scroll_x = ttk.Scrollbar(self.pilar_frame, orient="horizontal", command=self.pilar_tree.xview)
        self.pilar_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

    def setup_sondagem_tab(self):
        """Configura a aba 'Sondagens'."""
        btn_frame = ttk.Frame(self.sondagem_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(btn_frame, text="Adicionar Sondagem", command=self.add_sondagem).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Remover Sondagem", command=self.remove_sondagem).pack(side="left", padx=5)

        config_frame = ttk.LabelFrame(self.sondagem_frame, text="Configurações da Sondagem Ativa")
        config_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(config_frame, text="N.A. (m):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.na_var_display = tk.StringVar(value="0.0")
        self.na_entry = ttk.Entry(config_frame, textvariable=self.na_var_display, width=10)
        self.na_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

        ttk.Label(config_frame, text="Cota Terreno (m):").grid(row=0, column=2, padx=5, pady=2, sticky='w')
        self.cota_terreno_var_display = tk.StringVar(value="0.0")
        self.cota_terreno_entry = ttk.Entry(config_frame, textvariable=self.cota_terreno_var_display, width=10)
        self.cota_terreno_entry.grid(row=0, column=3, padx=5, pady=2, sticky='ew')

        ttk.Button(config_frame, text="Adicionar/Modificar Camadas", command=lambda: self._create_add_layer_dialog(self.current_sondagem_name)).grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky='ew')

        self.sondagem_notebook = ttk.Notebook(self.sondagem_frame)
        self.sondagem_notebook.pack(expand=True, fill="both", padx=5, pady=5)
        self.sondagem_notebook.bind("<<NotebookTabChanged>>", self.on_sondagem_tab_change)
        
        # Binds para salvar automaticamente ao sair do campo
        self.na_entry.bind("<FocusOut>", self.on_na_change)
        self.na_entry.bind("<Return>", self.on_na_change)
        self.cota_terreno_entry.bind("<FocusOut>", self.on_cota_terreno_change)
        self.cota_terreno_entry.bind("<Return>", self.on_cota_terreno_change)

    def add_pilar(self):
        """Adiciona um novo pilar manually."""
        nome = simpledialog.askstring("Novo Pilar", "Nome do Pilar (ex: P1):")
        if nome and nome not in self.dados_pilares:
            self.dados_pilares[nome] = {
                "Nome": nome, "Secao_X": "20", "Secao_Y": "50",
                "N_max": "0.000", "N_min": "0.000", "Mx_max": "0.000",
                "My_max": "0.000", "Fx_max": "0.000", "Fy_max": "0.000",
                "Mz": "0.000"
            }
            self.update_pilar_tree()

    def add_sondagem(self):
        """Adiciona uma nova sondagem."""
        sondagem_num_str = simpledialog.askstring("Nova Sondagem", "Número da Sondagem (ex: 1 para SP-1):")
        if sondagem_num_str and sondagem_num_str.isdigit():
            nome = f"SP-{sondagem_num_str}"
            if nome in self.dados_sondagens:
                messagebox.showwarning("Aviso", f"Sondagem '{nome}' já existe.")
                return
            
            self.dados_sondagens[nome] = {'NA': 0.0, 'Cota_Terreno': 0.0, 'camadas': []}
            self.update_sondagem_display()
            
            # Seleciona a nova aba criada
            for i, tab_id in enumerate(self.sondagem_notebook.tabs()):
                if self.sondagem_notebook.tab(tab_id, "text") == nome:
                    self.sondagem_notebook.select(i)
                    self.current_sondagem_name = nome
                    break
        elif sondagem_num_str:
            messagebox.showerror("Erro", "Por favor, insira um número válido para a sondagem.")

    def remove_sondagem(self):
        """Remove a sondagem atualmente selecionada."""
        if not self.current_sondagem_name:
            messagebox.showerror("Erro", "Nenhuma sondagem selecionada para remover.")
            return

        if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover a sondagem {self.current_sondagem_name}?"):
            del self.dados_sondagens[self.current_sondagem_name]
            self.update_sondagem_display()
            # Limpa os campos de configuração se não houver mais sondagens
            if not self.dados_sondagens:
                self.current_sondagem_name = None
                self.na_var_display.set("0.0")
                self.cota_terreno_var_display.set("0.0")

    def on_sondagem_tab_change(self, event):
        """Lida com a mudança de abas de sondagem."""
        try:
            selected_tab_id = self.sondagem_notebook.select()
            if selected_tab_id:
                new_tab_name = self.sondagem_notebook.tab(selected_tab_id, "text")
                self.current_sondagem_name = new_tab_name
                
                # Carrega os dados da nova aba selecionada
                sondagem_data = self.dados_sondagens[new_tab_name]
                self.na_var_display.set(str(sondagem_data.get('NA', 0.0)))
                self.cota_terreno_var_display.set(str(sondagem_data.get('Cota_Terreno', 0.0)))
        except tk.TclError:
            # Ocorre quando a última aba é fechada.
            self.current_sondagem_name = None
            self.na_var_display.set("0.0")
            self.cota_terreno_var_display.set("0.0")

    def on_na_change(self, event):
        """Salva a alteração no valor de N.A."""
        if self.current_sondagem_name:
            try:
                new_na = float(self.na_var_display.get().replace(',', '.'))
                self.dados_sondagens[self.current_sondagem_name]['NA'] = new_na
            except (ValueError, KeyError):
                messagebox.showerror("Erro de Entrada", "N.A. deve ser um número válido.")
                # Reverte para o valor anterior
                self.na_var_display.set(str(self.dados_sondagens[self.current_sondagem_name].get('NA', 0.0)))

    def on_cota_terreno_change(self, event):
        """Salva a alteração na cota do terreno e atualiza a tabela."""
        if self.current_sondagem_name:
            try:
                new_cota = float(self.cota_terreno_var_display.get().replace(',', '.'))
                self.dados_sondagens[self.current_sondagem_name]['Cota_Terreno'] = new_cota
                self.refresh_sondagem_treeview(self.current_sondagem_name)
            except (ValueError, KeyError):
                messagebox.showerror("Erro de Entrada", "Cota do terreno deve ser um número válido.")
                self.cota_terreno_var_display.set(str(self.dados_sondagens[self.current_sondagem_name].get('Cota_Terreno', 0.0)))
    
    def _create_add_layer_dialog(self, sondagem_name):
        """Cria um diálogo para adicionar ou modificar camadas de solo."""
        if not sondagem_name:
            messagebox.showerror("Erro", "Selecione ou adicione uma sondagem primeiro.")
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Adicionar/Modificar Camadas em {sondagem_name}")
        dialog.transient(self)
        dialog.grab_set()

        # Obter a última profundidade final das camadas para preenchimento inicial
        last_prof_final = 0.0
        if self.dados_sondagens[sondagem_name]['camadas']:
            last_prof_final = self.dados_sondagens[sondagem_name]['camadas'][-1]['prof_final_camada']
        
        row = 0
        ttk.Label(dialog, text="Prof. Inicial (m):").grid(row=row, column=0, padx=5, pady=2, sticky='w')
        prof_inicial_entry = ttk.Entry(dialog)
        prof_inicial_entry.grid(row=row, column=1, padx=5, pady=2, sticky='ew')
        prof_inicial_entry.insert(0, f"{last_prof_final:.2f}")
        row += 1

        ttk.Label(dialog, text="Prof. Final da Camada (m):").grid(row=row, column=0, padx=5, pady=2, sticky='w')
        prof_final_entry = ttk.Entry(dialog)
        prof_final_entry.grid(row=row, column=1, padx=5, pady=2, sticky='ew')
        prof_final_entry.insert(0, f"{last_prof_final + 1.0:.2f}") # Sugere 1m a mais de profundidade
        row += 1

        ttk.Label(dialog, text="Intervalo (m):").grid(row=row, column=0, padx=5, pady=2, sticky='w')
        interval_entry = ttk.Entry(dialog)
        interval_entry.grid(row=row, column=1, padx=5, pady=2, sticky='ew')
        interval_entry.insert(0, "1.00")
        row += 1

        ttk.Label(dialog, text="Tipo de Solo:").grid(row=row, column=0, padx=5, pady=2, sticky='w')
        tipo_solo_combo = ttk.Combobox(dialog, values=SOIL_TYPES, state='readonly')
        tipo_solo_combo.grid(row=row, column=1, padx=5, pady=2, sticky='ew')
        if SOIL_TYPES:
            tipo_solo_combo.set(SOIL_TYPES[0])
        row += 1

        def add_layer_action():
            try:
                prof_inicial_input = float(prof_inicial_entry.get().replace(',', '.'))
                prof_final_input = float(prof_final_entry.get().replace(',', '.'))
                intervalo = float(interval_entry.get().replace(',', '.'))
                tipo_solo = tipo_solo_combo.get()

                if prof_final_input <= prof_inicial_input or intervalo <= 0:
                    messagebox.showerror("Erro", "Profundidade Final deve ser maior que a Inicial e o Intervalo deve ser positivo.")
                    return

                camadas_atuais = self.dados_sondagens[sondagem_name]['camadas']
                
                # Mantém camadas que NÃO se sobrepõem ao novo intervalo de PROFUNDIDADE
                camadas_mantidas = []
                for camada in camadas_atuais:
                    # Condição para NÃO sobreposição: a camada existente termina antes da nova começar OU começa depois da nova terminar
                    if camada['prof_final_camada'] <= prof_inicial_input or camada['prof_inicial'] >= prof_final_input:
                        camadas_mantidas.append(camada)
                
                # Gera novas camadas no intervalo especificado
                novas_camadas = []
                prof_atual = prof_inicial_input
                while prof_atual < prof_final_input:
                    proxima_prof = min(prof_atual + intervalo, prof_final_input)
                    
                    novas_camadas.append({
                        'prof_inicial': round(prof_atual, 2),
                        'prof_final_camada': round(proxima_prof, 2),
                        'tipo_solo': tipo_solo,
                        'n_spt': 0 # NSPT é preenchido manualmente após a adição
                    })
                    prof_atual = proxima_prof
                
                # Combina e reordena todas as camadas pela profundidade inicial (key=lambda x: x['prof_inicial'])
                todas_camadas = sorted(camadas_mantidas + novas_camadas, key=lambda x: x['prof_inicial'])
                
                # Reajusta Prof_Inicial para garantir continuidade (se a primeira camada começar do zero)
                # Este bloco garante que não haja lacunas no início se a primeira camada deve ser 0.0
                if todas_camadas and todas_camadas[0]['prof_inicial'] != 0.0:
                    # If the first layer doesn't start at 0, and we want to ensure continuity from 0
                    # this part needs to be very careful not to accidentally overwrite user's initial 0
                    # For now, let's keep it simple: if the first layer's Prof_Inicial is > 0, we don't force it to 0.
                    # The user can edit the Prof_Inicial of the first layer to 0 if needed.
                    pass # Keep initial values as entered by user for now.

                # Garante continuidade das camadas subsequentes (se não houver lacunas por remoção)
                if todas_camadas:
                    current_prof_end = 0.0
                    for i, camada in enumerate(todas_camadas):
                        if i == 0:
                            # A primeira camada pode ter sua Prof_Inicial definida pelo usuário (ex: 0.0)
                            # ou manter a Prof_Inicial original se for uma camada existente não alterada.
                            pass 
                        else:
                            # Ajusta a Prof_Inicial da camada atual para ser igual à Prof_Final da camada anterior.
                            todas_camadas[i]['prof_inicial'] = todas_camadas[i-1]['prof_final_camada']
                
                # Filtra camadas inválidas e atualiza os dados da sondagem
                self.dados_sondagens[sondagem_name]['camadas'] = [c for c in todas_camadas if c['prof_final_camada'] > c['prof_inicial']]
                
                self.refresh_sondagem_treeview(sondagem_name)
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Erro de Entrada", f"Valores inválidos: {e}")

        ttk.Button(dialog, text="Confirmar", command=add_layer_action).grid(row=row, column=0, padx=5, pady=5)
        ttk.Button(dialog, text="Cancelar", command=dialog.destroy).grid(row=row, column=1, padx=5, pady=5)
        self.wait_window(dialog)


    def importar_excel_pilares(self, file_path=None, reimport=False):
        """Importa dados dos pilares de um arquivo Excel."""
        if not file_path and reimport and self.last_pilares_excel_path:
            file_path = self.last_pilares_excel_path
        elif not file_path:
            file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])

        if file_path:
            try:
                df = pd.read_excel(file_path)
                self.last_pilares_excel_path = file_path
                self.dados_pilares = {}

                def normalize_col(col):
                    """Normaliza os nomes das colunas para facilitar a importação."""
                    col = str(col).strip().lower()
                    col = re.sub(r'[^a-z0-9_]+', '_', col)
                    return col.strip('_')

                df.columns = [normalize_col(col) for col in df.columns]

                # Mapeamento flexível de colunas
                mapping = {
                    'Nome': ['nome', 'pilar'], 'Secao_X': ['secao_x'], 'Secao_Y': ['secao_y'],
                    'N_max': ['n_max', 'nmax'], 'N_min': ['n_min', 'nmin'], 'Mx_max': ['mx_max'],
                    'My_max': ['my_max'], 'Fx_max': ['fx_max'], 'Fy_max': ['fy_max'], 'Mz': ['mz']
                }

                # Encontra a coluna de nome do pilar
                nome_col = next((c for p in mapping['Nome'] for c in df.columns if p in c), None)
                if not nome_col:
                    messagebox.showerror("Erro", "Coluna de nome do pilar ('Nome', 'Pilar') não encontrada.")
                    return
                
                for _, row in df.iterrows():
                    nome = str(row[nome_col])
                    if not nome or pd.isna(row[nome_col]): continue
                    
                    self.dados_pilares[nome] = {'Nome': nome}
                    for key, possible_names in mapping.items():
                        if key == 'Nome': continue
                        col_found = next((c for p in possible_names for c in df.columns if p in c), None)
                        if col_found and pd.notna(row[col_found]):
                            self.dados_pilares[nome][key] = str(row[col_found]).replace(',', '.')
                        else:
                            # Valores padrão para colunas não encontradas
                            self.dados_pilares[nome][key] = "0"
                
                self.update_pilar_tree()
                messagebox.showinfo("Sucesso", "Dados dos pilares importados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar arquivo: {e}")

    def update_pilar_tree(self):
        """Atualiza a tabela de pilares com os dados carregados."""
        self.pilar_tree.delete(*self.pilar_tree.get_children())
        for pilar in self.dados_pilares.values():
            try:
                values = [
                    pilar["Nome"], pilar["Secao_X"], pilar["Secao_Y"],
                    f"{float(pilar.get('N_max', 0)):.3f}", f"{float(pilar.get('N_min', 0)):.3f}",
                    f"{float(pilar.get('Mx_max', 0)):.3f}", f"{float(pilar.get('My_max', 0)):.3f}",
                    f"{float(pilar.get('Fx_max', 0)):.3f}", f"{float(pilar.get('Fy_max', 0)):.3f}",
                    f"{float(pilar.get('Mz', 0)):.3f}"
                ]
                self.pilar_tree.insert("", "end", values=values)
            except (ValueError, KeyError) as e:
                print(f"Aviso: Pulando pilar '{pilar.get('Nome', 'N/A')}' devido a dados inválidos. Erro: {e}")

    def update_sondagem_display(self):
        """Atualiza a Treeview de sondagens e o notebook de abas."""
        # Limpa as abas existentes
        for tab in self.sondagem_notebook.tabs():
            self.sondagem_notebook.forget(tab)
        self.sondagem_treeviews.clear() # Limpa as referências dos Treeviews antigos

        if not self.dados_sondagens:
            empty_frame = ttk.Frame(self.sondagem_notebook)
            self.sondagem_notebook.add(empty_frame, text="Nenhuma Sondagem")
            ttk.Label(empty_frame, text="Nenhuma sondagem cadastrada.", wraplength=300).pack(pady=20)
            self.current_sondagem_name = None
            self.na_var_display.set("0.0")
            self.cota_terreno_var_display.set("0.0")
        else:
            for nome_sondagem in sorted(self.dados_sondagens.keys()):
                sondagem_detail_frame = ttk.Frame(self.sondagem_notebook)
                self.sondagem_notebook.add(sondagem_detail_frame, text=nome_sondagem)

                # Cria o Treeview para esta sondagem e o armazena
                cols = ("Cota", "Prof.", "Tipo de Solo", "N")
                tree = ttk.Treeview(sondagem_detail_frame, columns=cols, show="headings")
                for col in cols:
                    tree.heading(col, text=col)
                    tree.column(col, width=150, anchor="center")
                tree.pack(expand=True, fill="both")
                self.sondagem_treeviews[nome_sondagem] = tree # Armazena a referência

                # Adiciona o botão Salvar Alterações na Sondagem
                ttk.Button(sondagem_detail_frame, text="Salvar Alterações na Sondagem", command=lambda n=nome_sondagem: self.save_sondagem_changes(n)).pack(pady=5)

                self.make_treeview_editable(tree, nome_sondagem)
                self.refresh_sondagem_treeview(nome_sondagem)

            # Seleciona a primeira aba ou mantém a selecionada se existir
            if self.dados_sondagens:
                if self.current_sondagem_name and self.current_sondagem_name in self.dados_sondagens:
                    # Tenta re-selecionar a aba que estava ativa
                    for i, tab_id in enumerate(self.sondagem_notebook.tabs()):
                        if self.sondagem_notebook.tab(tab_id, "text") == self.current_sondagem_name:
                            self.sondagem_notebook.select(i)
                            break
                else:
                    # Seleciona a primeira aba se a atual não existir mais ou for nula
                    first_tab_id = self.sondagem_notebook.tabs()[0] if self.sondagem_notebook.tabs() else None
                    if first_tab_id:
                        self.sondagem_notebook.select(first_tab_id)
                        self.current_sondagem_name = self.sondagem_notebook.tab(first_tab_id, "text")
                    else:
                        self.current_sondagem_name = None

            # Garante que os campos de N.A. e Cota do Terreno reflitam a sondagem selecionada
            if self.current_sondagem_name:
                sondagem_data = self.dados_sondagens[self.current_sondagem_name]
                self.na_var_display.set(str(sondagem_data.get('NA', 0.0)))
                self.cota_terreno_var_display.set(str(sondagem_data.get('Cota_Terreno', 0.0)))
            else:
                self.na_var_display.set("0.0")
                self.cota_terreno_var_display.set("0.0")
        
        # *** Chamar o método para popular as abas de dimensionamento geotécnico ***
        if hasattr(self, 'geo_design_frame') and self.geo_design_frame:
            self.geo_design_frame._populate_de_court_tabs()

    def save_sondagem_changes(self, sondagem_name):
        """Salva as alterações feitas diretamente na tabela de uma sondagem."""
        if sondagem_name not in self.sondagem_treeviews:
            messagebox.showerror("Erro", "Treeview da sondagem não encontrada.")
            return
        
        tree = self.sondagem_treeviews[sondagem_name]
        try:
            camadas_novas = []
            cota_terreno = self.dados_sondagens[sondagem_name]['Cota_Terreno']
            
            for child in tree.get_children():
                valores = tree.item(child, 'values')
                # Valores na Treeview: Cota, Prof., Tipo de Solo, N
                # Precisamos de Prof_Inicial, Prof_Final_Camada, Tipo_Solo, N_SPT
                prof_final_camada = float(valores[1]) # Profundidade final é o segundo valor
                n_spt = int(valores[3]) # N é o quarto valor
                tipo_solo = valores[2] # Tipo de Solo é o terceiro valor

                # A profundidade inicial de uma camada é a profundidade final da camada anterior
                # Ou 0.0 se for a primeira camada
                prof_inicial = camadas_novas[-1]['prof_final_camada'] if camadas_novas else 0.0
                
                camadas_novas.append({
                    'prof_inicial': prof_inicial, 
                    'prof_final_camada': prof_final_camada,
                    'tipo_solo': tipo_solo, 
                    'n_spt': n_spt
                })
            
            self.dados_sondagens[sondagem_name]['camadas'] = camadas_novas # Ajusta para 'camadas' em minúsculas
            self.refresh_sondagem_treeview(sondagem_name) # Re-ordena e re-exibe
            messagebox.showinfo("Sucesso", f"Alterações em {sondagem_name} salvas.")
        except (ValueError, IndexError) as e:
            messagebox.showerror("Erro", f"Dados inválidos na tabela. Verifique os valores. Erro: {e}")

    def refresh_sondagem_treeview(self, sondagem_name):
        """Atualiza a tabela de uma sondagem específica."""
        if sondagem_name not in self.sondagem_treeviews:
            # Isso pode acontecer se a aba foi limpa mas o refresh foi chamado antes da recriação
            return
        
        tree = self.sondagem_treeviews[sondagem_name]
                
        tree.delete(*tree.get_children())
        sondagem_data = self.dados_sondagens[sondagem_name]
        cota_terreno = sondagem_data.get('Cota_Terreno', 0.0)
        
        # Ordena camadas pela profundidade inicial (agora é 'prof_inicial')
        camadas_sorted = sorted(sondagem_data.get('camadas', []), key=lambda x: x['prof_inicial'])
        
        for camada in camadas_sorted:
            prof_inicial = float(camada['prof_inicial'])
            prof_final_camada = float(camada['prof_final_camada'])
            cota_inicial = cota_terreno - prof_inicial
            cota_final_camada = cota_terreno - prof_final_camada

            tree.insert("", "end", values=[
                f"{cota_inicial:.2f}", f"{prof_final_camada:.2f}",
                camada["tipo_solo"], camada["n_spt"]
            ])

    def make_treeview_editable(self, tree, sondagem_name):
        """Permite a edição das células da tabela de sondagem."""
        def on_double_click(event):
            region = tree.identify("region", event.x, event.y)
            if region != "cell": return
            
            column_id = tree.identify_column(event.x)
            item_id = tree.identify_row(event.y)
            col_index = int(column_id.replace('#', '')) - 1
            col_name = tree.heading(column_id)['text']

            if col_name == "Cota": return # Cota não é editável

            x, y, width, height = tree.bbox(item_id, column_id)
            current_value = tree.item(item_id, 'values')[col_index]

            editor = None
            if col_name == "Tipo de Solo":
                editor = ttk.Combobox(tree, values=SOIL_TYPES, state='readonly')
                editor.set(current_value)
            else:
                editor = ttk.Entry(tree)
                editor.insert(0, current_value)
            
            editor.place(x=x, y=y, width=width, height=height)
            editor.focus_set()

            def on_editor_finish(event):
                new_value = editor.get()
                editor.destroy()

                # Validação
                try:
                    if col_name == "Prof.": float(new_value.replace(',', '.'))
                    if col_name == "N": int(new_value)
                except ValueError:
                    messagebox.showerror("Erro", f"Valor inválido para a coluna '{col_name}'.")
                    return
                
                current_values = list(tree.item(item_id, 'values'))
                current_values[col_index] = new_value

                # Recalcula cota se a profundidade mudar
                if col_name == "Prof.":
                    cota_terreno = self.dados_sondagens[sondagem_name]['Cota_Terreno']
                    # A coluna "Prof." agora é a profundidade final da camada
                    new_prof_final = float(new_value.replace(',', '.'))
                    current_values[1] = f"{new_prof_final:.2f}" # Atualiza a profundidade final
                    new_cota_final = cota_terreno - new_prof_final
                    current_values[0] = f"{new_cota_final:.2f}" # Atualiza a cota da profundidade final

                    # Também preciso atualizar a profundidade inicial da PRÓXIMA camada, se houver
                    next_item = tree.next(item_id)
                    if next_item:
                        next_values = list(tree.item(next_item, 'values'))
                        next_values[1] = f"{new_prof_final:.2f}" # Atualiza a profundidade inicial da próxima camada
                        tree.item(next_item, values=next_values)

                tree.item(item_id, values=current_values)

                # Navegação com Enter na coluna 'N'
                if col_name == "N" and event.keysym == "Return":
                    next_item = tree.next(item_id)
                    if next_item:
                        tree.selection_set(next_item)
                        tree.focus(next_item)
                        # Abre editor na mesma coluna da próxima linha
                        self.after(50, lambda: on_double_click_on_item(next_item, column_id))

            def on_double_click_on_item(item, col):
                # Simula um evento de duplo clique para abrir o editor
                x, y, _, _ = tree.bbox(item, col)
                dummy_event = tk.Event()
                dummy_event.x = x + 5
                dummy_event.y = y + 5
                on_double_click(dummy_event)

            editor.bind("<Return>", on_editor_finish)
            editor.bind("<FocusOut>", on_editor_finish)

        tree.bind("<Double-1>", on_double_click)

    def load_sondagem_data(self):
        """Carrega os dados de sondagem de um arquivo JSON."""
        try:
            with open("sondagens.json", "r", encoding="utf-8") as f:
                self.dados_sondagens = json.load(f)
            self.update_sondagem_display() # Atualiza a UI com os dados carregados
            messagebox.showinfo("Dados Carregados", "Dados de sondagem carregados com sucesso!")
        except FileNotFoundError:
            messagebox.showinfo("Início", "Nenhum arquivo de sondagem existente. Iniciando com dados vazios.")
        except Exception as e:
            messagebox.showerror("Erro de Carregamento", f"Erro ao carregar dados de sondagem: {e}")

    def save_sondagem_data(self):
        """Salva os dados de sondagem em um arquivo JSON."""
        try:
            with open("sondagens.json", "w", encoding="utf-8") as f:
                json.dump(self.dados_sondagens, f, indent=4)
            # messagebox.showinfo("Dados Salvos", "Dados de sondagem salvos com sucesso!") # Pode ser muito intrusivo
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Erro ao salvar dados de sondagem: {e}")

    def on_closing(self):
        """Chamado quando a janela é fechada. Salva os dados e fecha o app."""
        if messagebox.askyesno("Sair", "Deseja salvar os dados de sondagem antes de sair?"):
            self.save_sondagem_data()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
