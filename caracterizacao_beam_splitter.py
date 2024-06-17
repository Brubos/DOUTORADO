#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 20:46:32 2024

@author: bruno
"""
# Este código lê dados de um arquivo Excel, processa-os e gera gráficos com a razão entre as potências de saída FV e FB. 
# Ele utiliza pandas para carregar dados das abas 'BM1', 'BM2', 'BM3' e 'BM4' e converte-os em dicionários. 
# Configurações globais definem variáveis de controle para salvar figuras e exibir barras de erro. 
# Os dados são processados para calcular a razão FV/FB e suas incertezas. 
# A função plot_data gera gráficos da razão FV/FB em função da potência do laser, com ou sem barras de erro. 
# Se configurado, o gráfico é salvo em um arquivo PNG. Finalmente, o gráfico é exibido com uma linha de referência horizontal no valor de razão 1.

# Importação de bibliotecas
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Função para ler planilhas e converter em dicionários
def ler_planilhas_para_dicionarios(arquivo):
    try:
        # Carregar o arquivo Excel
        xls = pd.ExcelFile(arquivo)
        print(f"Abrindo arquivo: {arquivo}")
        abas_desejadas = ['BM1', 'BM2', 'BM3', 'BM4']
        dicionarios = {}
        
        # Iterar sobre as abas desejadas e ler os dados
        for aba in abas_desejadas:
            if aba in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=aba, usecols=range(5))
                dicionarios[aba] = df.to_dict(orient='list')
                print(f"Leitura da aba {aba} concluída.")
            else:
                print(f"Aba {aba} não encontrada no arquivo.")
                
        return dicionarios
    
    except FileNotFoundError:
        print(f"Arquivo {arquivo} não encontrado.")
        return {}
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return {}

# Configurações e variáveis globais
arquivo = '/home/bruno/GITHUB/DOUTORADO/BEAMSPLITTER.xlsx'  # Caminho do arquivo Excel
SAVE_FIG = 0  # Variável para controlar se os gráficos serão salvos
SHOW_ERRORBARS = 0  # Variável para controlar a exibição das barras de erro

# Variáveis de controle para plotar ou omitir as abas
BM1 = 1
BM2 = 1
BM3 = 1
BM4 = 1

# Leitura das planilhas
dicionarios = ler_planilhas_para_dicionarios(arquivo)

# Dicionário para verificar quais abas plotar
aberto = {'BM1': BM1, 'BM2': BM2, 'BM3': BM3, 'BM4': BM4}

# Cores para as linhas dos gráficos
cores = ['b', 'g', 'r', 'c']

# Configurar o gráfico principal
plt.figure(figsize=(12, 6))

# Iteração sobre as abas e plotagem dos dados
for i, (aba, dados) in enumerate(dicionarios.items()):
    if aberto[aba]:  # Verifica se a aba está ativada
        # Leitura dos dados de entrada (potência do laser) e das saídas (detector FV e FB)
        Pot_laser = dados['POTÊNCIA DO LASER [mW]']
        FV = dados['POTÊNCIA DETECTOR - FV [µW]']
        FB = dados['POTÊNCIA DETECTOR - FB [µW]']
        incerteza_FV = dados['INCERTEZA - FV [µW]']
        incerteza_FB = dados['INCERTEZA - FB [µW]']
        
        # Conversão de unidades de µW para mW
        FV_mW = np.array(FV) / 1000
        FB_mW = np.array(FB) / 1000
        incerteza_FV_mW = np.array(incerteza_FV) / 1000
        incerteza_FB_mW = np.array(incerteza_FB) / 1000
        
        # Cálculo da razão entre as potências do fio vermelho (FV) e fio branco (FB)
        razao_FV_FB = FV_mW / FB_mW
        
        # Cálculo da incerteza da razão utilizando a fórmula de propagação de incertezas
        incerteza_razao = np.sqrt((incerteza_FV_mW / FV_mW)**2 + (incerteza_FB_mW / FB_mW)**2) * razao_FV_FB
        
        # Exibição dos resultados no console
        print(f"Razão FV/FB para {aba}:", razao_FV_FB)
        print(f"Incerteza da Razão FV/FB para {aba}:", incerteza_razao)
        
        # Plotagem da razão FV/FB em função da potência do laser com barras de erro (se ativadas)
        if SHOW_ERRORBARS:
            plt.errorbar(Pot_laser, razao_FV_FB, yerr=incerteza_razao, label=f'Razão FV/FB - {aba}', marker='o', color=cores[i], capsize=5, ecolor='gray')
        else:
            plt.plot(Pot_laser, razao_FV_FB, label=f'Razão FV/FB - {aba}', marker='o', color=cores[i])

# Adicionar linha horizontal preta no valor de razão 1
plt.axhline(y=1, color='k', linestyle='--', label='Razão = 1')

# Configurações do gráfico
plt.xlabel('Potência do Laser [mW]')
plt.ylabel('Razão FV/FB')
plt.title('Razão entre as Potências de saída FV e FB - Beam Splitter (BM)')
plt.legend()
plt.grid(True)

# Opção para salvar o gráfico
if SAVE_FIG:
    # Criação do nome do arquivo de acordo com as abas ativadas
    nome_arquivo = 'razao_fv_fb_' + '_'.join([aba for aba in aberto if aberto[aba]]) + '_com_incertezas.png'
    plt.savefig(nome_arquivo)

# Mostrar o gráfico
plt.show()

