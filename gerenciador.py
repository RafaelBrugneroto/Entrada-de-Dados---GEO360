import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import pandas as pd
import re
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

        # --- Interface do Usuário ---
        self.setup_ui()

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
        self.notebook.add(self.geo_design_frame, text="Dimensionamento Geot\u00e9cnico")

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
            
            self.dados_sondagens[nome] = {'NA': 0.0, 'Cota_Terreno': 0.0, 'Camadas': []}
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

        cota_terreno_sondagem = self.dados_sondagens[sondagem_name].get('Cota_Terreno', 0.0)
        last_prof_final = 0.0
        if self.dados_sondagens[sondagem_name]['Camadas']:
            last_prof_final = self.dados_sondagens[sondagem_name]['Camadas'][-1]['Prof_Final']
        
        last_cota_final = cota_terreno_sondagem - last_prof_final

        row = 0
        ttk.Label(dialog, text="Cota Inicial (m):").grid(row=row, column=0, padx=5, pady=2, sticky='w')
        cota_inicial_entry = ttk.Entry(dialog)
        cota_inicial_entry.grid(row=row, column=1, padx=5, pady=2, sticky='ew')
        cota_inicial_entry.insert(0, f"{last_cota_final:.2f}")
        row += 1

        ttk.Label(dialog, text="Cota Final da Camada (m):").grid(row=row, column=0, padx=5, pady=2, sticky='w')
        cota_final_entry = ttk.Entry(dialog)
        cota_final_entry.grid(row=row, column=1, padx=5, pady=2, sticky='ew')
        cota_final_entry.insert(0, f"{last_cota_final - 1.0:.2f}")
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
                cota_inicial = float(cota_inicial_entry.get().replace(',', '.'))
                cota_final = float(cota_final_entry.get().replace(',', '.'))
                intervalo = float(interval_entry.get().replace(',', '.'))
                tipo_solo = tipo_solo_combo.get()

                if cota_final >= cota_inicial or intervalo <= 0:
                    messagebox.showerror("Erro", "Cota Final deve ser menor que a Inicial e o Intervalo deve ser positivo.")
                    return

                camadas_atuais = self.dados_sondagens[sondagem_name]['Camadas']
                cota_terreno = self.dados_sondagens[sondagem_name].get('Cota_Terreno', 0.0)

                # Mantém camadas que não se sobrepõem ao novo intervalo
                camadas_mantidas = []
                for camada in camadas_atuais:
                    cota_camada_inicial = cota_terreno - camada['Prof_Inicial']
                    cota_camada_final = cota_terreno - camada['Prof_Final']
                    if cota_camada_final >= cota_inicial or cota_camada_inicial <= cota_final:
                        camadas_mantidas.append(camada)
                
                # Gera novas camadas
                novas_camadas = []
                cota_atual = cota_inicial
                while cota_atual > cota_final:
                    proxima_cota = max(cota_atual - intervalo, cota_final)
                    prof_inicial_seg = round(cota_terreno - cota_atual, 2)
                    prof_final_seg = round(cota_terreno - proxima_cota, 2)
                    
                    novas_camadas.append({
                        'Prof_Inicial': prof_inicial_seg, 'Prof_Final': prof_final_seg,
                        'Tipo_Solo': tipo_solo, 'NSPT': 0
                    })
                    cota_atual = proxima_cota
                
                todas_camadas = sorted(camadas_mantidas + novas_camadas, key=lambda x: x['Prof_Final'])
                
                # Reajusta Prof_Inicial para garantir continuidade
                if todas_camadas:
                    todas_camadas[0]['Prof_Inicial'] = 0.0
                    for i in range(1, len(todas_camadas)):
                        todas_camadas[i]['Prof_Inicial'] = todas_camadas[i-1]['Prof_Final']
                
                self.dados_sondagens[sondagem_name]['Camadas'] = [c for c in todas_camadas if c['Prof_Final'] > c['Prof_Inicial']]
                
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
        """Recria as abas de sondagem e atualiza a exibição."""
        # Limpa abas existentes
        for tab in self.sondagem_notebook.tabs():
            self.sondagem_notebook.forget(tab)
        
        # Cria uma aba para cada sondagem
        for nome in self.dados_sondagens:
            frame = ttk.Frame(self.sondagem_notebook)
            self.sondagem_notebook.add(frame, text=nome)
            
            cols = ("Cota", "Prof.", "Tipo de Solo", "N")
            tree = ttk.Treeview(frame, columns=cols, show="headings")
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor="center")
            tree.pack(expand=True, fill="both")
            
            ttk.Button(frame, text="Salvar Alterações na Sondagem", command=lambda n=nome, t=tree: self.save_sondagem_changes(n, t)).pack(pady=5)
            self.make_treeview_editable(tree, nome)
            self.refresh_sondagem_treeview(nome)

    def save_sondagem_changes(self, sondagem_name, tree):
        """Salva as alterações feitas diretamente na tabela de uma sondagem."""
        try:
            camadas_novas = []
            cota_terreno = self.dados_sondagens[sondagem_name]['Cota_Terreno']
            
            for child in tree.get_children():
                valores = tree.item(child, 'values')
                prof_final = float(valores[1])
                prof_inicial = camadas_novas[-1]['Prof_Final'] if camadas_novas else 0.0

                camadas_novas.append({
                    'Prof_Inicial': prof_inicial, 'Prof_Final': prof_final,
                    'Tipo_Solo': valores[2], 'NSPT': int(valores[3])
                })
            
            self.dados_sondagens[sondagem_name]['Camadas'] = camadas_novas
            self.refresh_sondagem_treeview(sondagem_name) # Re-ordena e re-exibe
            messagebox.showinfo("Sucesso", f"Alterações em {sondagem_name} salvas.")
        except (ValueError, IndexError) as e:
            messagebox.showerror("Erro", f"Dados inválidos na tabela. Verifique os valores. Erro: {e}")

    def refresh_sondagem_treeview(self, sondagem_name):
        """Atualiza a tabela de uma sondagem específica."""
        for tab_id in self.sondagem_notebook.tabs():
            if self.sondagem_notebook.tab(tab_id, "text") == sondagem_name:
                frame = self.sondagem_notebook.nametowidget(tab_id)
                tree = next(w for w in frame.winfo_children() if isinstance(w, ttk.Treeview))
                
                tree.delete(*tree.get_children())
                sondagem_data = self.dados_sondagens[sondagem_name]
                cota_terreno = sondagem_data.get('Cota_Terreno', 0.0)
                
                # Ordena camadas pela profundidade final
                camadas_sorted = sorted(sondagem_data.get('Camadas', []), key=lambda x: x['Prof_Final'])
                
                for camada in camadas_sorted:
                    prof_final = float(camada['Prof_Final'])
                    cota_camada = cota_terreno - prof_final
                    tree.insert("", "end", values=[
                        f"{cota_camada:.2f}", f"{prof_final:.2f}",
                        camada["Tipo_Solo"], camada["NSPT"]
                    ])
                break

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
                    new_cota = cota_terreno - float(new_value.replace(',', '.'))
                    current_values[0] = f"{new_cota:.2f}"
                
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

if __name__ == "__main__":
    app = App()
    app.mainloop()
