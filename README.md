Projeto e Implementação de um Robô com Sistema de Rastreamento para Monitoramento de Nadadores

Este repositório contém o código-fonte e os arquivos de projeto desenvolvidos para o Trabalho de Conclusão de Curso em Engenharia Mecatrônica na Universidade Federal de Uberlândia. O projeto consiste em um robô móvel autônomo projetado para acompanhar nadadores de alto desempenho em tempo real, automatizando a coleta de métricas biomecânicas.
Visão Geral

O sistema utiliza processamento de visão computacional embarcado para detectar alvos e um sistema de controle em malha fechada para ajustar a velocidade dos motores, mantendo o nadador centralizado no campo de visão da câmera.
Componentes Principais

    Processamento de Visão: Raspberry Pi 4 (8 GB RAM) executando modelos YOLOv8n.

    Controle de Baixo Nível: Microcontrolador ESP32 para controle PWM dos motores e leitura de encoders.

    Atuadores: Motores CC JGY-370

    Estrutura: Chassi fabricado em impressão 3D (PLA/ABS) e perfis de alumínio.

    Interface: Webserver baseado em Flask para operação remota e monitoramento.

Arquitetura de Software

O software está dividido em scripts principais que gerenciam desde a coleta de dados até a inferência final:

    dataSampling.py: Interface para captura de frames e criação de datasets rotulados.

    model.py: Utilizado para ensaios de resposta ao degrau e identificação do modelo físico da planta.

    inference.py: Script de operação final que executa a rede neural e a malha de controle PID.

    Firmware ESP32: Gerencia o algoritmo PID, funções anti-windup e a comunicação serial com o Raspberry Pi.

Como Utilizar
Requisitos de Conexão

O acesso ao sistema embarcado é feito via protocolo SSH: ssh user@[IP_DO_ROBO]

Execução via Scripts Shell

Foram criados scripts facilitadores para iniciar as diferentes etapas do projeto:

    Para coleta de dados: ./run_data.sh

    Para modelagem do sistema: ./run_model.sh

    Para operação em malha fechada: ./run_inference.sh 

Transferência de Arquivos

Para baixar vídeos, logs em .csv ou imagens geradas, utilize o comando SCP:
Bash

scp -r user@[IP_DO_ROBO]:/home/user/swimfollower-robot/[PATH] [DESTINO_LOCAL]

Modelo de Controle

A planta foi identificada como um sistema integrador com ganho estático médio Kmedio ​= 1,011. O controlador PID projetado utiliza os seguintes ganhos para garantir um regime superamortecido (ξ=1,42) e evitar oscilações na filmagem:

    Kp: 2,0

    Ki: 0,4

    Kd: 0,25
