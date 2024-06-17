#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 15:10:27 2024

@author: bruno
"""
# Este código lê dados de um arquivo Excel, processa-os e gera gráficos. 
# Ele utiliza pandas para carregar dados das abas 'AT1_AT2_1V' e 'AT1_AT2_2V' e converte-os em dicionários. 
# Configurações globais definem variáveis de controle, cores e marcadores para os gráficos, além de valores de tempo e incertezas. 
# A função plot_data cria gráficos de perda em decibéis ou potência detectada, com ou sem barras de erro, e pode salvar os gráficos em arquivos PNG.
# A função gerar_nome_arquivo cria nomes de arquivos baseados nos atenuadores ativos. Finalmente, a função plot_graphs exibe os gráficos conforme as configurações definidas.


# Importação de bibliotecas
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from math import log10

# Função para ler planilhas e converter em dicionários
def ler_planilhas_para_dicionarios(arquivo):
    xls = pd.ExcelFile(arquivo)
    abas_desejadas = ['AT1_AT2_1V', 'AT1_AT2_2V']
    dicionarios = {}
    
    for aba in abas_desejadas:
        if aba in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=aba, usecols=range(6))
            dicionarios[aba] = df.to_dict(orient='list')
            
    return dicionarios.get('AT1_AT2_1V', {}), dicionarios.get('AT1_AT2_2V', {})

# Configurações e variáveis globais
arquivo = '/home/bruno/GITHUB/DOUTORADO/ATENUADORES.xlsx'
SAVE_FIG = 0
SHOW_ERRORBARS = 1  # Variável para controlar a exibição das barras de erro

ATENUADORES = {'AT1_AT2_1V': 1, 'AT1_AT2_2V': 1}
CORES = ['r', 'g', 'b', 'm', 'c']
MARCADORES = ['o', 's', '^', 'D', 'v']
T = np.linspace(0, 5, num=11)
deltaT = np.full(11, 0.1)
deltaP_0 = 1  # Incerteza associada à potência inicial (1 µW)

# Leitura dos dados das planilhas
dicionario_at1_at2_1v, dicionario_at1_at2_2v = ler_planilhas_para_dicionarios(arquivo)

POT_INICIAL = dicionario_at1_at2_1v['POTÊNCIA LASER [µW]'][0]  # Potência do laser inicial 1200 µW
POTENCIAS = {
    'AT1_AT2_1V': dicionario_at1_at2_1v['POTÊNCIA DETECTOR [µW]'],
    'AT1_AT2_2V': dicionario_at1_at2_2v['POTÊNCIA DETECTOR [µW]']
    }

INCERTEZAS = {
    'AT1_AT2_1V': dicionario_at1_at2_1v['INCERTEZA [µW]'],
    'AT1_AT2_2V': dicionario_at1_at2_2v['INCERTEZA [µW]']   
}

# Função para plotar dados
def plot_data(T, data, uncertainties, POT_INICIAL, ylabel, title, show_errorbars=True, filename=None):
    plt.figure(figsize=(10, 5))
    for i, (key, active) in enumerate(ATENUADORES.items()):
        if active:
            if ylabel == 'Perda em decibéis':
                ydata = [10 * log10(p / POT_INICIAL) for p in data[key]]
                yerr = [4.34 * np.sqrt((uncertainties[key][j] / p) ** 2 + (deltaP_0 / POT_INICIAL) ** 2) for j, p in enumerate(data[key])]
            else:
                ydata = data[key]
                yerr = uncertainties[key]

            if show_errorbars:
                plt.errorbar(T, ydata, yerr=yerr, color=CORES[i % len(CORES)], marker=MARCADORES[i % len(MARCADORES)], linestyle='-', label=f'Atenuador {key}', alpha=0.5, capsize=5, ecolor='black', elinewidth=2, markeredgewidth=2)
            else:
                plt.plot(T, ydata, color=CORES[i % len(CORES)], marker=MARCADORES[i % len(MARCADORES)], linestyle='-', label=f'Atenuador {key}', alpha=0.5)

    if show_errorbars:
        # Adiciona a barra de erro preta à legenda manualmente
        plt.errorbar([], [], yerr=1, capsize=5, ecolor='black', elinewidth=1, label='Incerteza')
    
    plt.title(title)
    plt.xlabel('Tensão [V]')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(np.arange(0, 5.5, step=0.5))
    if filename:
        plt.savefig(filename, dpi=300)
    plt.show()

# Função para gerar o nome do arquivo com base nos atenuadores ativos
def gerar_nome_arquivo(base_name, atenuadores):
    ativos = [key for key, active in atenuadores.items() if active]
    return f"{base_name}_{'_'.join(ativos)}.png" if ativos else f"{base_name}_nenhum_atenuador.png"

# Função para plotar gráficos
def plot_graphs(show_errorbars=True):
    filename = gerar_nome_arquivo('transmissao_atenuadores', ATENUADORES)
    plot_data(T, POTENCIAS, INCERTEZAS, POT_INICIAL, 'Perda em decibéis', 'Transmissão', show_errorbars, filename if SAVE_FIG else None)
    filename = gerar_nome_arquivo('caracterizacao_atenuadores', ATENUADORES)
    plot_data(T, POTENCIAS, INCERTEZAS, POT_INICIAL, 'Potência detectada [µW]', f'AT1 variável e AT2 fixo - Potência inicial do laser = {POT_INICIAL} µW', show_errorbars, filename if SAVE_FIG else None)

# Chama a função para plotar os gráficos com barras de erro
plot_graphs(SHOW_ERRORBARS)
