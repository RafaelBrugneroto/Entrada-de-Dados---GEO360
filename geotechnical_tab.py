import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import math

class GeotechnicalDesignTab(ttk.Frame):
    """Aba para configuracoes e calculos geotecnicos."""

    def __init__(self, parent, main_app=None):
        super().__init__(parent)
        self.main_app = main_app
        # Inicializa a estrutura de dados para os parametros de calculo
        self.params = {
            "decourt_quaresma_alpha": {
                "headers": ["Tipo de Solo", "Cravada a céu aberto", "Escavada a fluido", "Hélice Contínua", "Raiz", "Injetada sob pressão", "Franki"],
                "data": {
                    "Argilas": ["1.0", "0.6", "0.6", "0.85", "1.0", "0.0"],
                    "Argilas Intermediárias": ["1.0", "0.65", "0.75", "1.0", "1.0", "0.0"],
                    "Areias": ["1.0", "0.5", "0.5", "0.3", "0.5", "1.0"]
                }
            },
            "decourt_quaresma_beta": {
                "headers": ["Tipo de Solo", "Cravada a céu aberto", "Escavada a fluido", "Hélice Contínua", "Raiz", "Injetada sob pressão", "Franki"],
                "data": {
                    "Argilas": ["1.0", "0.8", "0.9", "1.0", "1.5", "0.0"],
                    "Argilas Intermediárias": ["1.0", "0.65", "0.75", "1.0", "1.5", "0.0"],
                    "Areias": ["1.0", "0.5", "0.5", "0.3", "0.5", "0.0"]
                }
            },
            "aoki_velloso_k": {
                "headers": ["Tipo de Solo", "K (KPa)"],
                "data": {
                    "Argila": ["200.0"],
                    "Argila Arenosa": ["350.0"],
                    "Argila Siltosa": ["220.0"],
                    "Silte Argiloso": ["400.0"],
                    "Silte Arenoso": ["550.0"],
                    "Areia Siltosa": ["800.0"],
                    "Areia Argilosa": ["600.0"],
                    "Areia": ["1000.0"]
                }
            },
            "aoki_velloso_alpha_f1": {
                "headers": ["Pré-moldada", "Metálica", "Escavada a céu aberto", "Escavada a fluido", "Hélice Contínua", "Raiz", "Injetada sob pressão", "Franki"],
                "data": {
                    "F1": ["1+3/D.8", "3.5", "3.0", "2.0", "2.0", "0.0", "2.5"]
                }
            },
            "aoki_velloso_alpha_f2": {
                "headers": ["Pré-moldada", "Metálica", "Escavada a céu aberto", "Escavada a fluido", "Hélice Contínua", "Raiz", "Injetada sob pressão", "Franki"],
                "data": {
                    "F2": ["#VALOR!", "6.0", "4.0", "4.0", "0.0", "5.0"]
                }
            },
            "normative_parameters": {
                 "headers": ["", "5", "6", "8", "9", "10"], # Assumindo que sao cabeçalhos de coluna, talvez Ncpu
                 "data": {
                     "ξ": ["1.42", "1.35", "1.33", "1.31", "1.29", "1.27"],
                     "ζ": ["1.42", "1.27", "1.23", "1.20", "1.15", "1.12"]
                 }
            },
            "section_parameters": {
                "headers": ["", "", "", "", "", "", ""],
                "data": {
                    "Pré-moldada Redonda": ["", "", "", "", "", "", ""],
                    "Pré-moldada Quadrada": ["", "", "", "", "", "", ""],
                    "Escavada a céu aberto": ["20", "25", "30", "35", "40", "50", "60"],
                    "Escavada a fluido": ["20", "25", "30", "40", "50", "60", "70"],
                    "Hélice Contínua": ["30", "40", "50", "60", "70", "80", "100"],
                    "Raiz": ["12", "18", "20", "25", "30", "40", ""],
                    "Injetada sob pressão": ["20", "30", "40", "50", "60", "70", "80"],
                    "Franki": ["60", "80", "100", "120", "150", "180", "200"]
                }
            }
        }
        self.setup_ui()

    def setup_ui(self):
        """Cria sub-abas basicas de configuracao e metodos de calculo."""
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both", padx=5, pady=5)

        config_frame = ttk.Frame(notebook)
        self.setup_config_tab(config_frame)
        notebook.add(config_frame, text="Configurações")

        dq_frame = ttk.Frame(notebook)
        self.setup_de_court_tab(dq_frame)
        notebook.add(dq_frame, text="Décourt-Quaresma (1996)")

    def setup_config_tab(self, parent_frame):
        """Configura os campos editáveis para os parametros de calculo com rolagem."""
        # Cria um Canvas e uma Scrollbar para permitir a rolagem
        canvas = tk.Canvas(parent_frame)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel for scrolling
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

        # Adiciona as tabelas ao frame rolável

        # Frame para Décourt-Quaresma Alpha
        alpha_frame = ttk.LabelFrame(scrollable_frame, text="Décourt-Quaresma (1996) - α")
        alpha_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self._create_editable_table(alpha_frame, self.params["decourt_quaresma_alpha"])

        # Frame para Décourt-Quaresma Beta
        beta_frame = ttk.LabelFrame(scrollable_frame, text="Décourt-Quaresma (1996) - β")
        beta_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self._create_editable_table(beta_frame, self.params["decourt_quaresma_beta"])

        # Frame para Aoki e Velloso K
        aoki_k_frame = ttk.LabelFrame(scrollable_frame, text="Aoki e Velloso (1975) - K (KPa)")
        aoki_k_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self._create_editable_table(aoki_k_frame, self.params["aoki_velloso_k"])

        # Frame para Aoki e Velloso F1
        aoki_f1_frame = ttk.LabelFrame(scrollable_frame, text="Aoki e Velloso (1975) - F1")
        aoki_f1_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self._create_editable_table(aoki_f1_frame, self.params["aoki_velloso_alpha_f1"])
        
        # Frame para Aoki e Velloso F2
        aoki_f2_frame = ttk.LabelFrame(scrollable_frame, text="Aoki e Velloso (1975) - F2")
        aoki_f2_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self._create_editable_table(aoki_f2_frame, self.params["aoki_velloso_alpha_f2"])

        # Frame para Parâmetros Normativos (Tabela 2)
        norm_params_frame = ttk.LabelFrame(scrollable_frame, text="Tabela 2 - Fatores L e fc (Normativa)")
        norm_params_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self._create_editable_table(norm_params_frame, self.params["normative_parameters"])

        # Frame para Parâmetros de Seção
        section_params_frame = ttk.LabelFrame(scrollable_frame, text="Tabela de SEÇÃO")
        section_params_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self._create_editable_table(section_params_frame, self.params["section_parameters"])


    def _create_editable_table(self, parent_frame, table_data_dict):
        """Cria uma tabela de campos editáveis (Entry) e exibe o valor padrão se for alterado.
        A primeira coluna é para o nome da linha, as demais são campos de entrada.
        """
        headers = table_data_dict["headers"]
        data_rows = table_data_dict["data"]

        # Linha de cabeçalho
        # Column 0 is for the row name
        # Other headers span 2 columns (Entry and Default_Label)
        for col_idx, header_text in enumerate(headers):
            if col_idx == 0:
                ttk.Label(parent_frame, text=header_text, font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=5, pady=2)
            else:
                # Headers for data columns. Each spans 2 physical columns (Entry and Default_Label).
                # Only create a label if header_text is not empty.
                if header_text:
                    # Logical column index `col_idx` maps to physical start column `(col_idx - 1) * 2 + 1`.
                    ttk.Label(parent_frame, text=header_text, font=('Arial', 9, 'bold')).grid(
                        row=0, column=(col_idx - 1) * 2 + 1, columnspan=2, padx=5, pady=2
                    )

        # Linhas de dados
        for row_idx, (row_name, values) in enumerate(data_rows.items()):
            # Primeira coluna é o nome da linha (ex: "Argilas")
            ttk.Label(parent_frame, text=row_name).grid(row=row_idx + 1, column=0, padx=5, pady=2, sticky="w")

            # As colunas restantes são campos de entrada editáveis com indicador de default
            for col_idx_data, value in enumerate(values):
                original_value = value.replace(',', '.') # Valor padrão original

                # Physical column for Entry: (col_idx_data * 2) + 1
                # Physical column for Default Label: (col_idx_data * 2) + 2
                entry_col = (col_idx_data * 2) + 1
                label_col = (col_idx_data * 2) + 2

                entry_var = tk.StringVar(value=original_value)
                entry = ttk.Entry(parent_frame, textvariable=entry_var)
                entry.grid(row=row_idx + 1, column=entry_col, padx=2, pady=2, sticky="ew") # sticky="ew"

                default_label = ttk.Label(parent_frame, text="", foreground="red")
                default_label.grid(row=row_idx + 1, column=label_col, padx=(0, 5), pady=2, sticky="w") # padx=(left, right)

                def check_change(event, current_var=entry_var, default_val=original_value, label_widget=default_label):
                    if current_var.get() != default_val:
                        label_widget.config(text=f"(Padrão: {default_val})")
                    else:
                        label_widget.config(text="")

                entry.bind("<FocusOut>", check_change)
                entry.bind("<Return>", check_change)

        # Configure columns to expand
        parent_frame.grid_columnconfigure(0, weight=0) # Row name column: fixed width

        # For each data column (Entry + Label), configure weights
        num_data_columns = len(headers) - 1
        for i in range(num_data_columns):
            entry_physical_col = (i * 2) + 1
            label_physical_col = (i * 2) + 2
            parent_frame.grid_columnconfigure(entry_physical_col, weight=3) # Entry takes more space
            parent_frame.grid_columnconfigure(label_physical_col, weight=1) # Label takes less space

    def setup_de_court_tab(self, parent_frame):
        """Configura a interface para o metodo Décourt-Quaresma (1996) com sub-abas por sondagem."""
        self.de_court_notebook = ttk.Notebook(parent_frame)
        self.de_court_notebook.pack(padx=10, pady=10, fill="both", expand=True)

        self._populate_de_court_tabs()

    def _populate_de_court_tabs(self):
        # Limpa abas existentes
        for tab in self.de_court_notebook.tabs():
            self.de_court_notebook.forget(tab)

        if self.main_app and self.main_app.dados_sondagens:
            for sondagem_name, sondagem_data in self.main_app.dados_sondagens.items():
                # Passa o nome da sondagem e os dados para a nova classe de frame
                sondagem_frame = BoreholeCalculationFrame(
                    self.de_court_notebook,
                    self.main_app,
                    sondagem_name,
                    sondagem_data,
                    self.params
                )
                self.de_court_notebook.add(sondagem_frame, text=sondagem_name)
        else:
            empty_frame = ttk.Frame(self.de_court_notebook)
            self.de_court_notebook.add(empty_frame, text="Nenhuma Sondagem")
            ttk.Label(empty_frame, text="Nenhuma sondagem cadastrada. Vá para a aba 'Sondagens' para adicionar dados.", wraplength=400).pack(pady=20)


class BoreholeCalculationFrame(ttk.Frame):
    def __init__(self, parent, main_app, sondagem_name, sondagem_data, params):
        super().__init__(parent)
        self.main_app = main_app
        self.sondagem_name = sondagem_name
        self.sondagem_data = sondagem_data
        self.params = params # Parâmetros de cálculo (alpha, beta, K, etc.)
        self._setup_ui()

    def _setup_ui(self):
        # Seção de Entrada de Dados
        input_frame = ttk.LabelFrame(self, text=f"Dados para a Sondagem {self.sondagem_name}")
        input_frame.pack(padx=10, pady=10, fill="x", expand=False)

        # Campos de entrada para dados da estaca
        form_frame = ttk.Frame(input_frame)
        form_frame.pack(padx=5, pady=5, fill="x")

        # Diâmetro da Estaca
        ttk.Label(form_frame, text="Diâmetro da Estaca (cm):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.diameter_entry = ttk.Entry(form_frame)
        self.diameter_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.diameter_entry.insert(0, "40") # Valor padrão

        # Cota de Arrasamento
        ttk.Label(form_frame, text="Cota de Arrasamento (m):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.top_level_entry = ttk.Entry(form_frame)
        self.top_level_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.top_level_entry.insert(0, "0.0") # Valor padrão

        # Comprimento da Estaca
        ttk.Label(form_frame, text="Comprimento da Estaca (m):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.pile_length_entry = ttk.Entry(form_frame)
        self.pile_length_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.pile_length_entry.insert(0, "15.0") # Valor padrão
        self.pile_length_entry.bind("<FocusOut>", self._update_pile_length_display)
        self.pile_length_entry.bind("<Return>", self._update_pile_length_display)

        # Cota da Ponta da Estaca (apenas display)
        ttk.Label(form_frame, text="Cota da Ponta da Estaca (m):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.pile_tip_level_display = ttk.Label(form_frame, text="")
        self.pile_tip_level_display.grid(row=3, column=1, padx=5, pady=2, sticky="w")
        self._update_pile_length_display() # Atualiza o display inicial

        # Tipo de Estaca
        ttk.Label(form_frame, text="Tipo de Estaca:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.pile_type_combobox = ttk.Combobox(form_frame,
                                               values=["Cravada a céu aberto", "Escavada a fluido", "Hélice Contínua", "Raiz", "Injetada sob pressão", "Franki", "Pré-moldada Redonda", "Pré-moldada Quadrada"])
        self.pile_type_combobox.grid(row=4, column=1, padx=5, pady=2, sticky="ew")
        self.pile_type_combobox.set("Hélice Contínua") # Valor padrão
        self.pile_type_combobox.bind("<<ComboboxSelected>>", lambda e: self._update_pile_length_display())


        # Botão de Cálculo
        calculate_button = ttk.Button(input_frame, text="Calcular Carga Admissível", command=self._execute_de_court_calculation)
        calculate_button.pack(pady=10)

        # Frame para o Treeview de resultados e o Canvas do gráfico
        results_and_plot_frame = ttk.Frame(self)
        results_and_plot_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Treeview para exibir os resultados detalhados por metro
        self.results_tree = ttk.Treeview(results_and_plot_frame, columns=("Profundidade", "N_SPT_Med", "Alfa", "Beta", "qp", "ql", "Pdqm"), show="headings")
        self.results_tree.heading("Profundidade", text="Prof. (m)")
        self.results_tree.heading("N_SPT_Med", text="N_SPT Médio")
        self.results_tree.heading("Alfa", text="α")
        self.results_tree.heading("Beta", text="β")
        self.results_tree.heading("qp", text="qp (kPa)")
        self.results_tree.heading("ql", text="ql (kPa)")
        self.results_tree.heading("Pdqm", text="Pdqm (kN)")
        
        # Define as larguras das colunas
        self.results_tree.column("Profundidade", width=70, anchor="center")
        self.results_tree.column("N_SPT_Med", width=90, anchor="center")
        self.results_tree.column("Alfa", width=50, anchor="center")
        self.results_tree.column("Beta", width=50, anchor="center")
        self.results_tree.column("qp", width=70, anchor="center")
        self.results_tree.column("ql", width=70, anchor="center")
        self.results_tree.column("Pdqm", width=80, anchor="center")

        # Configura as tags para as cores das linhas
        self.results_tree.tag_configure('oddrow', background='#E0E0E0')
        self.results_tree.tag_configure('evenrow', background='#FFFFFF')

        self.results_tree.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Canvas para a representação gráfica
        self.canvas = tk.Canvas(results_and_plot_frame, bg="white", bd=2, relief="sunken")
        self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.bind("<Configure>", self._draw_soil_profile_only) # Redesenha ao redimensionar
        self._draw_soil_profile_only() # Desenha o perfil do solo inicialmente

    def _update_pile_length_display(self, event=None):
        try:
            cota_arrasamento = float(self.top_level_entry.get().replace(',', '.'))
            comprimento_estaca = float(self.pile_length_entry.get().replace(',', '.'))
            cota_ponta = cota_arrasamento - comprimento_estaca
            self.pile_tip_level_display.config(text=f"{cota_ponta:.2f}")
            
            # Redesenha o gráfico apenas do perfil do solo quando o comprimento da estaca muda,
            # para dar um feedback visual imediato antes mesmo do cálculo.
            self._draw_soil_profile_only()

        except ValueError:
            self.pile_tip_level_display.config(text="Erro de valor")

    def _execute_de_court_calculation(self):
        # --- PASSO 1: COLETAR DADOS ---
        try:
            diametro_cm = float(self.diameter_entry.get().replace(',', '.'))
            cota_arrasamento = float(self.top_level_entry.get().replace(',', '.'))
            comprimento_estaca = float(self.pile_length_entry.get().replace(',', '.'))
            tipo_estaca = self.pile_type_combobox.get()
            diametro_m = diametro_cm / 100.0 # Converter diâmetro para metros
            cota_ponta = cota_arrasamento - comprimento_estaca

            # Cota do terreno natural (assumimos a primeira cota de sondagem como o nível do terreno)
            # ou um valor padrão se não houver dados de sondagem
            cota_terreno = 0.0
            if self.sondagem_data and self.sondagem_data.get('camadas'):
                # Encontra a menor profundidade inicial para estimar a cota do terreno
                # Profundidade inicial 0m corresponde à cota do terreno
                cota_terreno = max([layer['cota_inicial'] for layer in self.sondagem_data['camadas']]) # Invertendo para ter a cota mais "alta" (menor profundidade)

            if not self.sondagem_data or not self.sondagem_data.get('camadas'):
                messagebox.showwarning("Dados Ausentes", "Nenhum dado de sondagem disponível para esta sub-aba. Por favor, adicione dados na aba 'Sondagens'.")
                return

        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos para diâmetro, cota de arrasamento e comprimento.")
            return
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao coletar dados: {e}")
            return

        # Limpar resultados anteriores
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # --- PASSO 2: CÁLCULO DE RESISTÊNCIA DE PONTA (Pp) ---
        # A cota da ponta da estaca é cota_arrasamento - comprimento_estaca
        
        # Ajusta cota da ponta se a estaca for "Pré-moldada" ou "Metálica"
        # Para fins de cálculo, consideramos a penetração um pouco maior.
        if "Pré-moldada" in tipo_estaca or tipo_estaca == "Metálica":
            cota_ponta_calculo = cota_ponta - (0.05 * diametro_m) # 5% do diâmetro a mais
        else:
            cota_ponta_calculo = cota_ponta

        def _get_nspt_and_soil(cota_target):
            """Retorna o Nspt e o tipo de solo para uma dada cota (profundidade)."""
            if not self.sondagem_data or not self.sondagem_data.get('camadas'):
                return None, None
            
            # Converte cota_target para profundidade
            profundidade_target = cota_terreno - cota_target

            for camada in self.sondagem_data['camadas']:
                # Verifica se a profundidade alvo está dentro da camada
                # camada['prof_inicial'] é a profundidade de início da camada
                # camada['prof_final'] é a profundidade de fim da camada
                if camada['prof_inicial'] <= profundidade_target <= camada['prof_final_camada']:
                    return float(camada['n_spt']), camada['tipo_solo']
            return None, None # Se a cota não estiver em nenhuma camada

        # Nspt médio na ponta da estaca (média dos 4 últimos valores do SPT dentro do bulbo)
        # Bulbo de pressão: de Zp (cota da ponta) a Zp + 2D (cota acima da ponta)
        # Nspt médio na ponta: média dos Nspt dos últimos 4 metros acima da ponta e 1 metro abaixo da ponta
        # Vamos simplificar para pegar o Nspt da camada onde a ponta se encontra para o cálculo de qp
        nspt_ponta, tipo_solo_ponta = _get_nspt_and_soil(cota_ponta_calculo) # Usar a cota de cálculo da ponta

        if nspt_ponta is None:
            messagebox.showwarning("Dados Incompletos", f"Não foi possível encontrar dados de SPT para a cota da ponta da estaca ({cota_ponta_calculo:.2f} m).")
            return

        # Obter qp da tabela
        qp = 0.0
        # Simplificação: para Décourt, qp é Nspt * Coeficiente (pode ser específico do tipo de solo ou genérico)
        # Para solos granulares (areias), qp = K * Nspt (onde K varia de 250 a 350 kN/m2)
        # Para solos coesivos (argilas), qp = K * Nspt (onde K varia de 120 a 180 kN/m2)
        
        # Para a formulação padrão de Décourt-Quaresma (1996) a ser implementada:
        # qp = C_p * Nspt (onde C_p é um coeficiente que depende do tipo de solo na ponta)

        # Usando valores de referência para C_p (kN/m²/golpe) - simplificação didática
        C_p_areia = 250
        C_p_argila = 120

        if "Areia" in tipo_solo_ponta:
            qp = C_p_areia * nspt_ponta
        elif "Argila" in tipo_solo_ponta:
            qp = C_p_argila * nspt_ponta
        elif "Silte" in tipo_solo_ponta:
            qp = C_p_argila * nspt_ponta # Para silte, assumir comportamento similar a argila
        else:
            qp = C_p_areia * nspt_ponta # Default para tipo de solo não especificado

        # Área da ponta da estaca (Ap)
        area_ponta = math.pi * (diametro_m / 2)**2

        # Resistência de ponta (Pp)
        Pp = qp * area_ponta

        # --- PASSO 3: CÁLCULO DE RESISTÊNCIA LATERAL (Pl) ---
        Pl = 0.0
        # A resistência lateral é a soma das resistências laterais de cada camada atravessada pela estaca
        # Vamos iterar por cada metro de comprimento da estaca para calcular a resistência lateral.
        # Considerar os Nspt a cada metro para o cálculo de ql

        # Gera uma lista de profundidades (a cada 1m) ao longo da estaca
        # A estaca vai de cota_arrasamento até cota_ponta
        # Itera de cota_arrasamento para baixo
        
        # Garante que a iteração é pela profundidade (positiva)
        prof_arrasamento = cota_terreno - cota_arrasamento
        prof_ponta = cota_terreno - cota_ponta

        # A iteração deve ser da profundidade de arrasamento até a profundidade da ponta
        # Vamos iterar a cada 1 metro de profundidade
        
        detailed_results = [] # Para armazenar resultados detalhados por metro/camada

        current_prof = math.floor(prof_arrasamento) # Começa da profundidade de arrasamento (arredonda para baixo)
        
        while current_prof < prof_ponta:
            prof_inicial_segmento = current_prof
            prof_final_segmento = min(current_prof + 1, prof_ponta) # Garante que não ultrapasse a ponta da estaca

            if prof_inicial_segmento >= prof_final_segmento: # Evita segmentos vazios ou invertidos
                current_prof += 1
                continue

            # Encontrar a camada ou camadas que o segmento atravessa
            # Para simplificar, vamos usar o Nspt da profundidade central do segmento
            
            prof_central_segmento = (prof_inicial_segmento + prof_final_segmento) / 2.0
            
            # Converte a profundidade central para cota para _get_nspt_and_soil
            cota_central_segmento = cota_terreno - prof_central_segmento
            
            nspt_segmento, tipo_solo_segmento = _get_nspt_and_soil(cota_central_segmento)

            if nspt_segmento is None:
                # Se não há dados SPT para este segmento, pula ou trata como 0
                ql_segmento = 0.0
                alfa_segmento = 0.0
                beta_segmento = 0.0
            else:
                # Obter alpha e beta da tabela de parâmetros (simplificado)
                # Adaptação para usar as tabelas de self.params
                alpha_data = self.params["decourt_quaresma_alpha"]["data"]
                beta_data = self.params["decourt_quaresma_beta"]["data"]
                
                alfa_segmento = 0.0
                beta_segmento = 0.0

                # Mapeia tipo de estaca para o índice da coluna
                # Headers: ["Tipo de Solo", "Cravada a céu aberto", "Escavada a fluido", "Hélice Contínua", "Raiz", "Injetada sob pressão", "Franki"]
                # Assumindo que "Pré-moldada Redonda" e "Pré-moldada Quadrada" se enquadram em "Cravada a céu aberto" para alpha/beta
                col_idx_map = {
                    "Cravada a céu aberto": 1,
                    "Escavada a fluido": 2,
                    "Hélice Contínua": 3,
                    "Raiz": 4,
                    "Injetada sob pressão": 5,
                    "Franki": 6,
                    "Pré-moldada Redonda": 1, # Mapeia para "Cravada a céu aberto"
                    "Pré-moldada Quadrada": 1  # Mapeia para "Cravada a céu aberto"
                }

                tipo_estaca_col_idx = col_idx_map.get(tipo_estaca, 1) # Default para Cravada a céu aberto

                # Encontra a linha de solo correspondente para alpha e beta
                # Mapeia o tipo de solo para a chave da tabela
                # Ex: "Argila Arenosa" -> "Argilas Intermediárias"
                solo_key = None
                if "Areia" in tipo_solo_segmento:
                    solo_key = "Areias"
                elif "Argila" in tipo_solo_segmento:
                    solo_key = "Argilas"
                elif "Silte" in tipo_solo_segmento: # Silte pode ser intermediário
                    solo_key = "Argilas Intermediárias"
                
                if solo_key and solo_key in alpha_data and solo_key in beta_data:
                    try:
                        alfa_segmento = float(alpha_data[solo_key][tipo_estaca_col_idx - 1].replace(',', '.'))
                        beta_segmento = float(beta_data[solo_key][tipo_estaca_col_idx - 1].replace(',', '.'))
                    except (ValueError, IndexError):
                        alfa_segmento = 0.0
                        beta_segmento = 0.0
                    except Exception as e:
                        messagebox.showerror("Erro de Cálculo", f"Erro ao obter alpha/beta: {e}")
                        alfa_segmento = 0.0
                        beta_segmento = 0.0

            # ql = alfa * Nspt + beta (Décourt-Quaresma simplificado)
            ql_segmento = alfa_segmento * nspt_segmento + beta_segmento
            Pl_trecho_kN = ql_segmento * area_ponta
            Pl += Pl_trecho_kN
            ql_ult_kPa = ql_segmento
            ql_ult_tf_m2 = ql_segmento / 9.81 # Convertendo kPa para tf/m2
            Pl_trecho_tf = Pl_trecho_kN / 9.81

            detailed_results.append([
                f"{prof_inicial_segmento:.2f} a {prof_final_segmento:.2f}",
                nspt_segmento,
                tipo_solo_segmento,
                ql_ult_kPa,
                ql_ult_tf_m2,
                Pl_trecho_tf
            ])

            current_prof += 1 # Move para o próximo segmento

        # --- PASSO 4: CÁLCULO DA CARGA ADMISSÍVEL (Pdqm) ---
        # Formulação de Décourt-Quaresma: Pdqm = (Pp + Pl) / 2
        # Fator de segurança implícito de 2.0 (Décourt-Quaresma utiliza Fs=2)
        # Aqui estou assumindo FSL = 1 e FSP = 1 para a fórmula de Décourt-Quaresma
        # Se houver outros fatores de segurança, eles devem ser aplicados.
        FSL = 1.0 # Fator de Segurança para Resistência Lateral
        FSP = 1.0 # Fator de Segurança para Resistência de Ponta
        # Para Décourt-Quaresma (1996), a fórmula já incorpora o fator de segurança
        Pdqm = (Pp + Pl) / 2.0

        # Exibir resultados detalhados no Treeview
        for i, row_data in enumerate(detailed_results):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.results_tree.insert("", "end", values=(
                row_data[0],
                row_data[1],
                row_data[2],
                row_data[3],
                row_data[4],
                row_data[5],
                "" # Deixando a última coluna vazia para Pdqm total
            ), tags=(tag,))

        # Adicionar a carga admissível final no final
        self.results_tree.insert("", "end", values=("", "", "", "", "", "Pdqm Total (kN)", f"{Pdqm:.2f}"), tags=('total_row'))
        self.results_tree.tag_configure('total_row', background='#D3EDF8', font=('Arial', 10, 'bold'))


        messagebox.showinfo("Cálculo Concluído", f"A Carga Admissível (Pdqm) para a estaca é: {Pdqm:.2f} kN")

        # Desenhar o gráfico após o cálculo
        self._draw_pile_and_soil_profile(
            sondagem_data=self.sondagem_data,
            cota_terreno=cota_terreno, # Passa a cota do terreno
            cota_arrasamento=cota_arrasamento,
            cota_ponta=cota_ponta,
            diametro_m=diametro_m,
            tipo_estaca=tipo_estaca
        )

    def _draw_soil_profile_only(self, event=None):
        # Desenha apenas o perfil do solo quando a aba é carregada ou redimensionada
        self.canvas.delete("all")
        if not self.sondagem_data or not self.sondagem_data.get('camadas'):
            ttk.Label(self.canvas, text="Nenhum dado de sondagem disponível para desenhar.").place(relx=0.5, rely=0.5, anchor="center")
            return

        cota_terreno = 0.0 # Assumindo 0.0 para o nível do terreno
        
        camadas = sorted(self.sondagem_data['camadas'], key=lambda x: x['cota_inicial'], reverse=True) # Ordena pela cota inicial (maior cota = menor profundidade)

        canvas_height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 400
        canvas_width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 300

        # Encontra a cota mais baixa (maior profundidade) para determinar a escala
        min_cota = min([layer['cota_final_camada'] for layer in camadas])
        max_cota = max([layer['cota_inicial'] for layer in camadas] + [cota_terreno]) # Cota mais alta (menor profundidade, geralmente 0 ou perto de 0)

        # Se a cota do terreno for a mais alta, ajusta o max_cota
        if cota_terreno > max_cota:
            max_cota = cota_terreno

        cota_range = max_cota - min_cota
        if cota_range == 0: # Evita divisão por zero se houver apenas uma camada ou profundidade zero
            cota_range = 1 # Define um range mínimo para escala

        # Margens para o gráfico
        margin_top = 20
        margin_bottom = 20
        plot_height = canvas_height - margin_top - margin_bottom

        # Escala vertical: pixels por metro de cota
        scale_y = plot_height / cota_range

        def cota_to_y(cota):
            # Converte cota para coordenada Y no canvas
            # A cota mais alta (ex: 0m) deve estar no topo do gráfico (y pequeno)
            # A cota mais baixa (ex: -20m) deve estar na parte inferior do gráfico (y grande)
            return margin_top + (max_cota - cota) * scale_y

        # Desenhar o nível do terreno
        y_terreno = cota_to_y(cota_terreno)
        self.canvas.create_line(0, y_terreno, canvas_width, y_terreno, fill="green", width=2, tags="terreno_level")
        self.canvas.create_text(10, y_terreno - 10, anchor="nw", text=f"Nível do Terreno (Cota {cota_terreno:.1f}m)", fill="green", font=("Arial", 8))

        # Desenhar as camadas de solo
        for camada in camadas:
            y_start = cota_to_y(camada['cota_inicial'])
            y_end = cota_to_y(camada['cota_final_camada'])

            # Evita desenhar se as coordenadas não são válidas
            if y_start is None or y_end is None:
                continue

            # Desenhar o retângulo da camada
            self.canvas.create_rectangle(50, y_start, canvas_width - 50, y_end,
                                         fill="#D2B48C", outline="black", tags="solo_layer") # Cor genérica de solo
            self.canvas.create_line(50, y_end, canvas_width - 50, y_end, fill="black", width=1) # Linha divisória da camada

            # Adicionar texto da camada
            mid_y = (y_start + y_end) / 2
            self.canvas.create_text(canvas_width / 2, mid_y, text=f"{camada['tipo_solo']} (N={camada['n_spt']})",
                                    fill="black", font=("Arial", 8), tags="solo_text")
            
            # Adicionar cota inicial e final da camada
            self.canvas.create_text(45, y_start, anchor="e", text=f"{camada['cota_inicial']:.1f}m", font=("Arial", 7))
            self.canvas.create_text(45, y_end, anchor="e", text=f"{camada['cota_final_camada']:.1f}m", font=("Arial", 7))


    def _draw_pile_and_soil_profile(self, sondagem_data, cota_terreno, cota_arrasamento, cota_ponta, diametro_m, tipo_estaca):
        self.canvas.delete("all") # Limpa o canvas antes de redesenhar

        if not sondagem_data or not sondagem_data.get('camadas'):
            ttk.Label(self.canvas, text="Nenhum dado de sondagem disponível para desenhar.").place(relx=0.5, rely=0.5, anchor="center")
            return

        camadas = sorted(sondagem_data['camadas'], key=lambda x: x['cota_inicial'], reverse=True)

        canvas_height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 400
        canvas_width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 300

        # Encontra a cota mais baixa (maior profundidade) e mais alta
        min_cota = min([layer['cota_final_camada'] for layer in camadas] + [cota_ponta])
        max_cota = max([layer['cota_inicial'] for layer in camadas] + [cota_arrasamento, cota_terreno])

        # Adiciona uma pequena margem para cima e para baixo do perfil total
        plot_cota_range = (max_cota - min_cota)
        if plot_cota_range == 0:
            plot_cota_range = 1.0 # Evita divisão por zero

        margin_top = 30 # Mais espaço para o título/nível do terreno
        margin_bottom = 20
        plot_height = canvas_height - margin_top - margin_bottom

        scale_y = plot_height / plot_cota_range
        
        # Ajuste da largura para acomodar texto e ter uma proporção melhor
        plot_width = canvas_width * 0.7 # Ocupa 70% da largura para o perfil do solo/estaca
        x_offset = (canvas_width - plot_width) / 2 # Centraliza o perfil

        def cota_to_y(cota):
            return margin_top + (max_cota - cota) * scale_y

        def cota_to_y_relative(cota, base_cota):
            # Converte cota para coordenada Y relativa a uma base (ex: cota_terreno)
            return margin_top + (base_cota - cota) * scale_y


        # Desenhar o nível do terreno
        y_terreno = cota_to_y(cota_terreno)
        self.canvas.create_line(0, y_terreno, canvas_width, y_terreno, fill="green", width=2, tags="terreno_level")
        self.canvas.create_text(10, y_terreno - 10, anchor="nw", text=f"Nível do Terreno (Cota {cota_terreno:.1f}m)", fill="green", font=("Arial", 8))

        # Desenhar as camadas de solo
        for camada in camadas:
            y_start = cota_to_y(camada['cota_inicial'])
            y_end = cota_to_y(camada['cota_final_camada'])

            if y_start >= canvas_height or y_end <= 0: # Otimização: não desenha camadas fora da visão
                continue

            # Desenhar o retângulo da camada
            self.canvas.create_rectangle(x_offset, y_start, x_offset + plot_width, y_end,
                                         fill="#D2B48C", outline="black", tags="solo_layer")
            self.canvas.create_line(x_offset, y_end, x_offset + plot_width, y_end, fill="black", width=1) # Linha divisória da camada

            # Adicionar texto da camada
            mid_y = (y_start + y_end) / 2
            self.canvas.create_text(x_offset + plot_width / 2, mid_y, text=f"{camada['tipo_solo']} (N={camada['n_spt']})",
                                    fill="black", font=("Arial", 8), tags="solo_text")
            
            # Adicionar cotas ao lado esquerdo
            self.canvas.create_text(x_offset - 5, y_start, anchor="e", text=f"{camada['cota_inicial']:.1f}m", font=("Arial", 7))
            self.canvas.create_text(x_offset - 5, y_end, anchor="e", text=f"{camada['cota_final_camada']:.1f}m", font=("Arial", 7))
        
        # Desenhar a estaca
        # A estaca é desenhada com base na cota de arrasamento e cota da ponta
        # Sua largura é proporcional ao diâmetro
        pile_center_x = canvas_width / 2 # Centro horizontal para a estaca
        pile_width_pixels = diametro_m * scale_y * 0.5 # Escala do diâmetro, ajuste para visualização

        x1_pile = pile_center_x - (pile_width_pixels / 2)
        x2_pile = pile_center_x + (pile_width_pixels / 2)

        y_arrasamento = cota_to_y(cota_arrasamento)
        y_ponta = cota_to_y(cota_ponta)

        self.canvas.create_rectangle(x1_pile, y_arrasamento, x2_pile, y_ponta, fill="grey", outline="black", tags="pile")

        # Adicionar texto para cota de arrasamento e cota da ponta da estaca
        self.canvas.create_text(x2_pile + 10, y_arrasamento, anchor="w", text=f"Arrasamento: {cota_arrasamento:.1f}m", font=("Arial", 8))
        self.canvas.create_text(x2_pile + 10, y_ponta, anchor="w", text=f"Ponta: {cota_ponta:.1f}m", font=("Arial", 8))
        self.canvas.create_text(x2_pile + 10, (y_arrasamento + y_ponta) / 2, anchor="w", text=f"Tipo: {tipo_estaca}", font=("Arial", 8))
        self.canvas.create_text(x2_pile + 10, (y_arrasamento + y_ponta) / 2 + 15, anchor="w", text=f"Diâm: {diametro_m:.2f}m", font=("Arial", 8))
        self.canvas.create_text(x2_pile + 10, (y_arrasamento + y_ponta) / 2 + 30, anchor="w", text=f"Comp: {(cota_arrasamento - cota_ponta):.2f}m", font=("Arial", 8))

        # Desenhar bloco da fundação (simplificado - um pequeno retângulo no arrasamento)
        block_height_pixels = 20 # Altura visual do bloco
        block_width_pixels = pile_width_pixels * 1.5 # Largura maior que a estaca
        self.canvas.create_rectangle(pile_center_x - (block_width_pixels / 2), y_arrasamento - block_height_pixels,
                                     pile_center_x + (block_width_pixels / 2), y_arrasamento, fill="brown", outline="black", tags="foundation_block")
        
        # Adicionar legendas para o gráfico
        legend_x = canvas_width - 10 # Canto superior direito
        legend_y = margin_top

        self.canvas.create_text(legend_x, legend_y, anchor="ne", text="Legenda:", font=("Arial", 9, "bold"))
        self.canvas.create_rectangle(legend_x - 70, legend_y + 10, legend_x - 60, legend_y + 20, fill="#D2B48C", outline="black")
        self.canvas.create_text(legend_x - 55, legend_y + 15, anchor="w", text="Solo", font=("Arial", 8))
        self.canvas.create_rectangle(legend_x - 70, legend_y + 25, legend_x - 60, legend_y + 35, fill="grey", outline="black")
        self.canvas.create_text(legend_x - 55, legend_y + 30, anchor="w", text="Estaca", font=("Arial", 8))
        self.canvas.create_rectangle(legend_x - 70, legend_y + 40, legend_x - 60, legend_y + 50, fill="brown", outline="black")
        self.canvas.create_text(legend_x - 55, legend_y + 45, anchor="w", text="Bloco", font=("Arial", 8))

